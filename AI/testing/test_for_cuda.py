import torch
print(torch.__file__)  # This will give you the path to the PyTorch installation
print(torch.__version__)  # Check if it includes "cu12" (e.g., '2.2.0+cu121')
print(torch.cuda.is_available())  # Should print True
print(torch.version.cuda)  # Should match CUDA 12.x
print(torch.backends.cudnn.version())  # Should return a version number
