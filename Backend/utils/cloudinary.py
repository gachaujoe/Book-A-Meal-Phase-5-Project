import cloudinary
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

def upload_image(image_file):
    try:
        # Open the image and resize to 800x800
        img = Image.open(image_file)
        img = img.resize((800, 800))
        
        # Create an in-memory buffer to save the resized image
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)

        # Upload the image to Cloudinary
        result = cloudinary.uploader.upload(buffer)

        # Return the secure URL of the uploaded image
        return result["secure_url"]
    
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None
