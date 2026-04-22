import os
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np
import base64
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use the new Google GenAI SDK
try:
    from google import genai
    from google.genai import types
except ImportError:
    pass

from .rag import CXRRag # Relative import since they are both in src/

# Load environment variables (like GEMINI_API_KEY)
load_dotenv()

# Vertex AI configuration can be picked up from environment or ADC
vertex_project = os.getenv("GOOGLE_CLOUD_PROJECT")
vertex_location = os.getenv("GOOGLE_CLOUD_LOCATION")

NIH_CLASSES = [
    "Atelectasis", "Cardiomegaly", "Consolidation", "Edema", "Effusion",
    "Emphysema", "Fibrosis", "Hernia", "Infiltration", "Mass",
    "No Finding", "Nodule", "Pleural_Thickening", "Pneumonia", "Pneumothorax"
]
# THRESHOLDS = {
#     "Atelectasis": 0.70,
#     "Cardiomegaly": 0.90,
#     "Effusion": 0.70,
#     "Infiltration": 0.55,
#     "Mass": 0.80,
#     "Nodule": 0.80,
#     "Pneumonia": 0.85,
#     "Pneumothorax": 0.75,
#     "Consolidation": 0.65,
#     "Edema": 0.90,
#     "Emphysema": 0.85,
#     "Fibrosis": 0.85,
#     "Pleural_Thickening": 0.80,
#     "Hernia": 0.95
# }
THRESHOLDS = {
    "Atelectasis": 0.60,
    "Cardiomegaly": 0.75,
    "Effusion": 0.60,
    "Infiltration": 0.50,
    "Mass": 0.65,
    "Nodule": 0.65,
    "Pneumonia": 0.70,
    "Pneumothorax": 0.65,
    "Consolidation": 0.60,
    "Edema": 0.75,
    "Emphysema": 0.70,
    "Fibrosis": 0.70,
    "Pleural_Thickening": 0.65,
    "Hernia": 0.80
}
NO_FINDING_THRESHOLD = 0.50
class CXRAssistant:
    def __init__(self, model_path: str = "models/densenet_final.pth", kb_path: str = "data/cxr_kb.jsonl"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading assistant on device: {self.device}")
        
        # 1. Initialize Vision Model
        self.model = self._load_vision_model(model_path).to(self.device)
        
        # 2. Initialize RAG
        self.rag = CXRRag(kb_path, top_k=5)
        
        # 3. Initialize LLM Client
        try:
            # When vertexai=True is passed, it uses Google Cloud ADCs instead of api_key
            self.llm_client = genai.Client(vertexai=True, project=vertex_project, location=vertex_location)
        except Exception as e:
            self.llm_client = None
            print(f"WARNING: Failed to initialize Vertex AI client. LLM generation will fail. Error: {e}")
        
        # Preprocessing matching ImageNet
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _load_vision_model(self, path: str):
        # # We use standard DenseNet121 and modify the classifier
        # model = models.densenet121(weights=None)
        # num_ftrs = model.classifier.in_features
        # model.classifier = torch.nn.Linear(num_ftrs, len(NIH_CLASSES))
        
        # try:
        #     checkpoint = torch.load(path, map_location=self.device)

        #     if isinstance(checkpoint, dict) and "labels" in checkpoint:
        #         self.class_names = checkpoint["labels"]
        #     else:
        #         self.class_names = NIH_CLASSES

        #     if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        #         model.load_state_dict(checkpoint["model_state_dict"])
        #         logger.info("Loaded model_state_dict from checkpoint")
        #     else:
        #         model.load_state_dict(checkpoint)
        #         logger.info("Loaded raw state_dict")
        # except Exception as e:
        #     print(f"Error loading model weights from {path}: {e}")
        # model.eval()
        # return model
        print('using model from:',path)
        checkpoint = torch.load(path, map_location=self.device)

        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
            self.class_names = checkpoint.get("labels", NIH_CLASSES)
        else:
            state_dict = checkpoint
            self.class_names = NIH_CLASSES

        if "classifier.weight" in state_dict:
            num_classes = state_dict["classifier.weight"].shape[0]
        elif "module.classifier.weight" in state_dict:
            num_classes = state_dict["module.classifier.weight"].shape[0]
        else:
            raise KeyError("Could not infer classifier size from checkpoint.")

        model = models.densenet121(weights=None)
        num_ftrs = model.classifier.in_features
        model.classifier = torch.nn.Linear(num_ftrs, num_classes)

        try:
            model.load_state_dict(state_dict)
            logger.info(f"Loaded checkpoint with {num_classes} output classes")
        except Exception as e:
            logger.error(f"Error loading model weights from {path}: {e}")
            raise

        model.eval()
        return model

    def analyze_image(self, image_path: str):

        try:
            img = Image.open(image_path).convert("RGB")
        except Exception as e:
            raise ValueError(f"Could not open image {image_path}: {e}")

        tensor = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.sigmoid(outputs).squeeze().cpu().numpy()

        predictions = []
        print('obtained probs:',probs)
        for i, condition in enumerate(self.class_names):
            if condition == "No Finding":
                continue

            prob = float(probs[i])
            if condition in THRESHOLDS and prob >= THRESHOLDS[condition]:
                predictions.append({
                    "condition": condition,
                    "confidence": prob
                })

        if not predictions:
            predictions.append({
                "condition": "No Finding",
                "confidence": 1.0
            })

        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return predictions

    def generate_heatmap(self, image_path: str, condition: str):
        """Generate a CAM heatmap overlay for a specific condition encoded as base64 jpeg."""
        if condition == "No Finding":
            return None
        if condition not in self.class_names:
            return None
            
        try:
            img = Image.open(image_path).convert("RGB")
            original_img = np.array(img)
        except Exception as e:
            print(f"Error loading image for heatmap: {e}")
            return None
            
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        if condition == "No Finding":
            return None

        target_idx = self.class_names.index(condition)
        
        with torch.no_grad():
            features = self.model.features(tensor)
            features = torch.nn.functional.relu(features, inplace=True)
            weight = self.model.classifier.weight[target_idx]
            
            cam = torch.zeros(features.shape[2:], dtype=torch.float32, device=self.device)
            for i, w in enumerate(weight):
                cam += w * features[0, i, :, :]
                
            cam = torch.nn.functional.relu(cam)
            if cam.max() > 0:
                cam = cam - cam.min()
                cam = cam / cam.max()
            cam = cam.cpu().numpy()
            
        cam_resized = cv2.resize(cam, (original_img.shape[1], original_img.shape[0]))
        cam_heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        
        # Convert to BGRA to add alpha channel
        heatmap_bgra = cv2.cvtColor(cam_heatmap, cv2.COLOR_BGR2BGRA)
        
        # Create an alpha channel where low activations are more transparent
        # Threshold out values below 10% activation to remove noise
        alpha_channel = np.uint8(255 * cam_resized)
        alpha_channel = np.where(cam_resized < 0.1, 0, alpha_channel)
        heatmap_bgra[:, :, 3] = alpha_channel
        
        _, buffer = cv2.imencode('.png', heatmap_bgra)
        b64_string = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{b64_string}"

    def get_clinical_insight(self, question: str, predicted_labels: list[str] = None, history: list[dict] = None):
        """Use the RAG module and LLM to answer questions about the findings."""
        if not self.llm_client:
            return "Error: Vertex AI client is not initialized. Cannot connect to LLM."
            
        logger.info("--- Processing New Query ---")
        logger.info(f"User Question: {question}")
        logger.info(f"Predicted Labels: {predicted_labels}")
            
        # 1. Use RAG to fetch context and build the prompt
        rag_output = self.rag.answer(question, predicted_labels=predicted_labels, history=history)
        prompt = rag_output["prompt"]
        retrieved_contexts = rag_output["context"]
        
        logger.info(f"RAG Retrieved {len(retrieved_contexts)} context blocks.")
        for idx, ctx in enumerate(retrieved_contexts):
            logger.info(f"Context [{idx+1}]: {ctx.get('topic')} - {ctx.get('text')[:100]}...")
            
        logger.info(f"Constructed Prompt:\n{prompt}\n---------------------")
        
        # 2. Query Gemini natively using google.genai
        try:
            response = self.llm_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            logger.info(f"LLM Response snippet: {response.text[:100]}...")
            return response.text
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return f"LLM Generation failed: {e}"
