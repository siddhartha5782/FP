import os
import shutil
import json
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from src.assistant import CXRAssistant
from src.database import Base, engine, get_db, User, ScanHistory
from src.auth import verify_password, get_password_hash, create_access_token, get_current_user

# Initialize Database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chest X-Ray Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Initializing Assistant backend...")
assistant = CXRAssistant(model_path="models/sol_metrics/run1_best.pt", kb_path="data/cxr_kb.jsonl")

# Ensure required directories exist
SCANS_DIR = "data/scans"
os.makedirs(SCANS_DIR, exist_ok=True)
os.makedirs("temp", exist_ok=True)

class UserCreate(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    question: str
    context: List[str]
    history_id: int = None

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/api/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/analyze")
async def analyze_xray(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import time
    file_id = int(time.time())
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{current_user.id}_{file_id}{file_ext}"
    file_path = os.path.join(SCANS_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        predictions = assistant.analyze_image(file_path)
        
        heatmaps = {}
        conditions = []
        for pred in predictions:
            condition = pred["condition"]
            conditions.append(condition)
            hm = assistant.generate_heatmap(file_path, condition)
            if hm:
                heatmaps[condition] = hm
                
        initial_question = "Explain these findings and suggest next steps."
        clinical_insight = assistant.get_clinical_insight(initial_question, predicted_labels=conditions)
        
        initial_chat = [{"type": "system", "text": clinical_insight}]
        
        scan_record = ScanHistory(
            user_id=current_user.id,
            image_path=safe_filename,
            findings_json=json.dumps(predictions),
            chat_log=json.dumps(initial_chat),
            heatmaps_json=json.dumps(heatmaps)
        )
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)
        
        import base64
        with open(file_path, "rb") as image_file:
            b64_orig = base64.b64encode(image_file.read()).decode('utf-8')
            
        ext_map = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png"}
        b64_mime = ext_map.get(file_ext.lower(), "jpeg")
        original_b64 = f"data:image/{b64_mime};base64,{b64_orig}"
        
        return JSONResponse({
            "history_id": scan_record.id,
            "predictions": predictions,
            "heatmaps": heatmaps,
            "clinical_insight": clinical_insight,
            "original_image": original_b64
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/chat")
async def chat_with_assistant(req: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        logs = []
        scan = None
        if req.history_id:
            scan = db.query(ScanHistory).filter(ScanHistory.id == req.history_id, ScanHistory.user_id == current_user.id).first()
            if scan:
                logs = json.loads(scan.chat_log) if scan.chat_log else []
                
        response = assistant.get_clinical_insight(req.question, predicted_labels=req.context, history=logs)
        
        if scan:
            logs.append({"type": "user", "text": req.question})
            logs.append({"type": "system", "text": response})
            scan.chat_log = json.dumps(logs)
            db.commit()
                
        return {"response": response}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/history")
def get_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scans = db.query(ScanHistory).filter(ScanHistory.user_id == current_user.id).order_by(ScanHistory.timestamp.desc()).all()
    results = []
    
    import base64
    for scan in scans:
        obj = {
            "id": scan.id,
            "timestamp": scan.timestamp.isoformat(),
            "predictions": json.loads(scan.findings_json) if scan.findings_json else [],
            "chat_log": json.loads(scan.chat_log) if scan.chat_log else [],
            "heatmaps": json.loads(scan.heatmaps_json) if scan.heatmaps_json else {}
        }
        
        file_path = os.path.join(SCANS_DIR, scan.image_path)
        if os.path.exists(file_path):
             with open(file_path, "rb") as image_file:
                 b64_orig = base64.b64encode(image_file.read()).decode('utf-8')
                 ext = os.path.splitext(scan.image_path)[1].lower()
                 b64_mime = "png" if ext == ".png" else "jpeg"
                 obj["original_image"] = f"data:image/{b64_mime};base64,{b64_orig}"
        results.append(obj)
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
