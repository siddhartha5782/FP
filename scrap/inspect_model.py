import torch

try:
    weights = torch.load("densenet_final.pth", map_location="cpu")
    if isinstance(weights, dict):
        print("It's a state_dict with the following keys/shapes (first 5):")
        for i, (k, v) in enumerate(weights.items()):
            if i < 5:
                print(f"  {k}: {v.shape}")
        
        # Look for the last layer to determine num_classes
        last_key = list(weights.keys())[-1]
        print(f"\nLast key: {last_key}")
        print(f"Last layer shape: {weights[last_key].shape}")
    else:
        print("It's a full model object. Type:", type(weights))
        print("Modules inside:")
        print(list(weights.modules())[:3])
except Exception as e:
    print(f"Error loading model: {e}")
