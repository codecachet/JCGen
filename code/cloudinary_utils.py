#!/bin/env python3

# Set your Cloudinary credentials
# ==============================
from dotenv import load_dotenv
load_dotenv()

# Import the Cloudinary libraries
# ==============================
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url



# Import to format the JSON responses
# ==============================
import json

# Set configuration parameter: return "https" URLs by setting secure=True  
# ==============================
config = cloudinary.config(secure=True)

# Log the configuration
# ==============================
#print("****1. Set up and configure the SDK:****\nCredentials: ", config.cloud_name, config.api_key, "\n")

# def uploadImage():

#   # Upload the image and get its URL
#   # ==============================

#   # Upload the image.
#   # Set the asset's public ID and allow overwriting the asset with new versions
#   cloudinary.uploader.upload("https://cloudinary-devs.github.io/cld-docs-assets/assets/images/butterfly.jpeg", 
#   public_id="quickstart_butterfly", unique_filename = False, overwrite=True)

#   # Build the URL for the image and save it in the variable 'srcURL'
#   srcURL = cloudinary.CloudinaryImage("quickstart_butterfly").build_url()

#   # Log the image URL to the console. 
#   # Copy this URL in a browser tab to generate the image on the fly.
#   print("****2. Upload an image****\nDelivery URL: ", srcURL, "\n")

def upload_image(image, src_image_path):
    """
    Note: "image" is dict entry from db
    """
    ####src_image_name = image['src_image_name']
    dst_image_name = image['dst_image_name']
    gallery_name = image['gallery_name']
    
    public_id = f"{gallery_name}/{dst_image_name}"

    result = cloudinary.uploader.upload(src_image_path, 
       public_id = public_id)
    print("result=", result)
    return result


if __name__ == "__main__":
    print("will upload...")
    #uploadImage()
