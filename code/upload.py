import requests
import os

import cloudinary_utils

def upload_to_cloudinary(image_t, iserver_t, local_image_server_url, images):
    #init_config()
    #gallery_name = 'house'
    

    for image in images:
        tmp_file_name = get_image_to_local_file(local_image_server_url, image)
        print("tmp_file_name", tmp_file_name)

        #assume cloudinary for now
        result = cloudinary_utils.upload_image(image, tmp_file_name)

def get_image_to_local_file(local_image_server_url, image):
    src_imageurl = local_image_server_url

    src_subdir = image['src_image_loc']
    src_image_name = image['src_image_name']

    url = f"{src_imageurl}/{src_subdir}/{src_image_name}"
    print("url=", url)
   
    response = requests.get(url)
    print("status=", response.status_code)
    print("encoding=", response.encoding)
    print("content-type", response.headers['content-type'])
    #print("text=", response.text)

    #print("response=", response)

    if response.status_code != 200:
        print(f"ERROR: status={response.status_code}")
        return None
    # save as a tmp file
    #with open("/tmp/abc.png", "wb") as f:
    #    f.write(response.content)


    (f, tempfile_name) = tempfile.mkstemp()
    fd = os.fdopen(f, "wb")
    fd.write(response.content)
    fd.close()
    print("tempfile_name=", tempfile_name)
    return tempfile_name