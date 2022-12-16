#!/usr/bin/env python

## NOTE: this is a one-off
## I had updated cloudinary somewhat manually, and am now copying the status into the iserver table from the results on console.


from pathlib import Path
import os
import json
import datetime

from MyDB import MyDB

from tinydb import TinyDB, Query, where
from cloudinary.utils import cloudinary_url
import cloudinary

from dotenv import load_dotenv
load_dotenv()


top = Path("~/projects/JCGen").expanduser()

text_file = Path(top) / 'code' / 'cloudinary_house_init.txt'

gallery_name = 'house'

#image_db_path = "test.db"
image_db_path = "image_db.json"

def read_file():
    print('text_file=', text_file)

    assets = []

    with open(text_file, "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('result='):
            print(line)
            meat = line[8:]
            print(meat)
            meat = meat.replace("'", '"')
            meat = meat.replace('False', 'false')
            meat = meat.replace('True', 'true')
            print('meat after=', meat)
            print('660', meat[660:])
            jmeat = json.loads(meat)
            print('jmeat=', jmeat)
            assets.append(jmeat)
    print('n entries=', len(assets))
    print('assets=', assets)

    return assets

def update_iserver_table():
    assets = read_file()
    db = MyDB(image_db_path)
    iserver_t = db.get_table('iserver')

    iserver_t.truncate()

    for asset in assets:
        public_id = asset['public_id']
        print(f'public_id={public_id}')
        gallery, image_name = public_id.split('/')
        timestamp = datetime.datetime.timestamp(datetime.datetime.now())

        record = {
            'gallery' : gallery,
            'image_name' : image_name,
            'upload_result' : asset,
            'timestamp' : timestamp,
        }
        print('record=', record)
        iserver_t.insert(record)

def update_image_table():
    db = MyDB(image_db_path)
    image_t = db.get_table('image')
    iserver_t = db.get_table('iserver')

    # NOTE: house was inserted into cloudinary with names house_000 .... house_0019

    irecs = iserver_t.all()
    for irec in irecs:
        print(f'gallery={irec["gallery"]}, image_name={irec["image_name"]}, url={irec["upload_result"]["secure_url"]}')

        # get image record
        fragment = {
            'gallery_name' : irec['gallery'],
            'dst_image_name' : irec['image_name'],
        }

        rec = image_t.search(Query().fragment(fragment))

        print(f'fragment={fragment}, rec={rec}')
        #rec['remote_url'] = irec["upload_result"]["secure_url"]
        
        remote_url = irec["upload_result"]["secure_url"]
        print('remote_url=', remote_url)

        status = image_t.update({'remote_url' : remote_url } , Query().fragment(fragment))
        print('status=', status)

def show_results():
    db = MyDB(image_db_path)
    image_t = db.get_table('image')

    images = image_t.search(where('gallery_name') == 'house')

    for image in images:
        print(image)

def check_cloudinary_url_builder():

    load_dotenv()

    cloudinary.config( 
        cloud_name = "jumpingcow", 
        api_key = "874837483274837", 
        api_secret = "a676b67565c6767a6767d6767f676fe1",
        secure = True
    )

    db = MyDB(image_db_path)
    image_t = db.get_table('image')
    iserver_t = db.get_table('iserver')

    irecs = iserver_t.all()

    for irec in irecs:
        result = irec['upload_result']



        results = json.dumps(result)

        url, options = cloudinary_url(result['public_id'], format=result['format'])

        print('result=', result)
        print('url=', url)
        
        print('options=', options)



if __name__ == '__main__':
    #update_iserver_table()

    #update_image_table()

    #show_results()

    check_cloudinary_url_builder()