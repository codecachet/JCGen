#!/usr/bin/env python

from pathlib import Path
import os
import json
import datetime

from MyDB import MyDB

from tinydb import TinyDB, Query, where


top = Path("~/projects/JCGen").expanduser()

text_file = Path(top) / 'code' / 'cloudinary_house_init.txt'

gallery_name = 'house'

image_db_path = "test.db"

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

def fixit():
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

    irecs = iserver_t.all()
    for irec in irecs:
        print(f'gallery={irec["gallery"]}, image_name={irec["image_name"]}, url={irec["upload_result"]["secure_url"]}')

        # get image record
        fragment = {
            'gallery_name' : irec['gallery'],
            'dst_image_name' : irec['image_name'],
        }

        rec = image_t.search(Query().fragment(fragment))

        print('rec=', rec)
        #rec['remote_url'] = irec["upload_result"]["secure_url"]

        image_t.update({'remote_url' : irec["upload_result"]["secure_url"] } , Query().fragment(fragment))

def show_results():
    db = MyDB(image_db_path)
    image_t = db.get_table('image')

    images = image_t.search(where('gallery_name') == 'house')

    for image in images:
        print(image)


if __name__ == '__main__':
    #fixit()

    update_image_table()

    show_results()