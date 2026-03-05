from PIL import Image
import os

# Pointing exactly to the image you uploaded
image_path = "rube cube.jpg" 

if os.path.exists(image_path):
    img = Image.open(image_path)
    # Convert to standard Windows icon sizes so it scales perfectly on your desktop
    img.save("rube.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    print("✅ rube.ico successfully forged!")
else:
    print(f"❌ Could not find '{image_path}'. Make sure it is in this exact folder!")