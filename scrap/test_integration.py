from assistant import CXRAssistant
import pprint

def run_test():
    print("Initializing CXRAssistant...")
    assistant = CXRAssistant(model_path="densenet_final.pth", kb_path="cxr_kb.jsonl")
    
    print("\n--- Testing Vision Analysis ---")
    image_path = "test.png"
    print(f"Analyzing {image_path}...")
    try:
        # Lowering threshold just to force some predictions for testing
        predictions = assistant.analyze_image(image_path, threshold=0.01)
        print("Predictions:")
        pprint.pprint(predictions)
    except Exception as e:
        print(f"Error during analysis: {e}")
        predictions = []

    print("\n--- Testing RAG & LLM Integration ---")
    labels = [p["condition"] for p in predictions]
    question = "Based on the findings, what are the recommended next steps?"
    print(f"Question: {question}")
    print(f"Using labels: {labels}")
    
    response = assistant.get_clinical_insight(question, predicted_labels=labels)
    print("\nLLM Response:")
    print(response)

if __name__ == "__main__":
    run_test()
