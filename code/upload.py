import requests
import os
import tempfile
import datetime
from tinydb import TinyDB, Query, where

from cloudinary.utils import cloudinary_url

import cloudinary_utils

#  upload_to_cloudinary(image_t, iserver_t, WEB_IMAGE_URL, image_recs)

def upload_to_cloudinary(image_t, iserver_t, local_image_server_url, images):
    #init_config()
    #gallery_name = 'house'
    
    images_total = len(images)
    images_to_upload = 0
    images_uploaded = 0

    for image in images:
        if image['remote_url'] != None:
            continue
    
        images_to_upload += 1

        tmp_file_name = get_image_to_local_file(local_image_server_url, image)
        print("tmp_file_name", tmp_file_name)

        #assume cloudinary for now
        result = cloudinary_utils.upload_image(image, tmp_file_name)

        images_uploaded += 1

        url, options = cloudinary_url(result['public_id'], format=result['format'])

        print('url=', url)

        update_iserver_table(iserver_t, result, url)

        update_image_table(image_t, url, image)

        print(f'images_total={images_total}, impages_to_upload={images_to_upload}, images_uploaded={images_uploaded}')


def update_iserver_table(iserver_t, upload_result, url):
    public_id = upload_result['public_id']
    print(f'public_id={public_id}')
    gallery, image_name = public_id.split('/')
    timestamp = datetime.datetime.timestamp(datetime.datetime.now())

    record = {
        'gallery' : gallery,
        'image_name' : image_name,
        'upload_result' : upload_result,
        'cloudinary_url' : url,
        'timestamp' : timestamp,
    }
    print('record=', record)
    iserver_t.insert(record)

def update_image_table(image_t, url, image):
    fragment = {
            'gallery_name' : image['gallery_name'],
            'dst_image_name' : image['dst_image_name'],
        }
    image_t.update({})
    status = image_t.update({'remote_url' : url } , Query().fragment(fragment))
    print('status=', status)

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