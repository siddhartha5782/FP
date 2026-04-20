import torch
import torchvision.models as models

try:
    print("Loading densenet_final.pth...")
    weights = torch.load("densenet_final.pth", map_location="cpu")
    
    # Check if it's a state_dict or full model
    if isinstance(weights, dict):
        print("It's a state_dict.")
        # Find the keys related to the final classifier
        classifier_keys = [k for k in weights.keys() if 'classifier' in k]
        print(f"Classifier keys: {classifier_keys}")
        
        for k in classifier_keys:
            print(f"{k} shape: {weights[k].shape}")
            
    else:
        print("It's a full model object. Type:", type(weights))
        
except Exception as e:
    print(f"Error: {e}")
