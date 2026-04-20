import os
from google import genai
from google.genai import types

try:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Search Cleveland Clinic or Mayo Clinic for the exact definition, symptoms, and treatment for Atelectasis. Return only a short Markdown summary.',
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.0
        )
    )
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print(f"FAILED: {e}")
