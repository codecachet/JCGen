#!/usr/bin/env python3

from tinydb import TinyDB, Query, where
from MyDB import MyDB
import tomli
import requests
import json
import sys

# NOTE: "it" means item table

SRC_IMAGE_URL = "http://192.168.1.178:3020"  # filters for images only, given subdir

class Counts:
    def __init__(self):
        self.total_images_read = 0
        self.total_inserts = 0
        self.total_duplicates = 0
        self.total_galleries = 0
        self.total_original_recs = 0
        self.total_final_recs = 0
        self.total_original_enabled = 0
        self.total_final_enabled = 0
    
    def print_results(self):
        for key in self.__dict__.keys():
            print(f'{key} = {self.__dict__[key]}')

        # print('keys=', self.__dict__.keys())
        # print(f'read={self.total_images_read}')
        # print(f'inserts={self.total_inserts}')
        # print(f'duplicates={self.total_duplicates}')
        # print(f'galleries={self.total_galleries}')
      

def build_db(galleries_toml_file, db_file):

    stats = Counts()

    galleries = get_galleries(galleries_toml_file)

    print("galleries=", galleries)

    db = MyDB(db_file)
    image_t = db.get_table('image')

    stats.total_original_recs = len(image_t.all())
    stats.total_original_enabled = len(image_t.search(Query().is_active == True))

    for gallery_name, gallery in galleries.items():
        gallery['name'] = gallery_name
        update_db_from_gallery(stats, image_t, gallery)

        stats.total_galleries += 1
    
    print_db(image_t)

    stats.total_final_enabled = len(image_t.search(Query().is_active == True))
    stats.total_final_recs = len(image_t.all())
    stats.print_results()

    return galleries, image_t

def update_db_from_gallery(stats, it, gallery):
    print('gallery name =', gallery['name'])
    print("gallery=", gallery)

    images = get_images(gallery)

    next_index = get_next_index(it, gallery)

    disable_all_images(it, gallery)   # default, and will enable if image is in gallery

    print("next_index=", next_index)

    print('images=', images)

    for image in images:
        stats.total_images_read += 1
        rec = is_image_in_db(it, gallery, image)
        print('rec 1=', rec)
        if rec != None:
            stats.total_duplicates += 1
            print('rec=', rec)
            enable_image(it, rec)
        else:
            stats.total_inserts += 1
            newrec = create_new_image_record(it, gallery, image, next_index)
            insert_record(it, newrec)
            next_index += 1

    # rec = {
    #         'gallery_name' : gallery['name'],
    #         'src_image_name' : image['name'],
    #         'src_image_loc' : gallery.get('imageurl_subdir', gallery['src_imageurl_subdir']),
    #         'dst_image_name' : get_remote_name(gallery, i),
    #         'image_size' : image['size'],
    #         'remote_url' : None,
    #         'is_active' : True,
    #         'flubber' : 'blue',
    #     } 

def disable_all_images(it, gallery):
    it.update({'is_active' : False }, Query().gallery_name == gallery['name'])

def enable_image(it, rec):
    Image = Query()
    #qrec = it.search(Image.dst_image_name == rec['dst_image_name'])
    #print('qrec=', qrec)
    it.update({'is_active' : True } , Image.dst_image_name == rec['dst_image_name'])

    #qrec2 = it.search(Image.dst_image_name == rec['dst_image_name'])
    #print('qrec2=', qrec2)

def is_image_in_db(it, gallery, image):
    # image: {name: xyz, size: abc }
    # gallery: {'name': abc, 'title': abc , 'src_imageurl_subdir': abc , 'home_image_name': abc , 'date_updated': datetime.date(2022, 11, 28)}

    fragment = { 
        'gallery_name': gallery['name'], 
        'src_image_loc' : gallery['src_imageurl_subdir'],
        'src_image_name' : image['name'],
    }

    res = it.search(Query().fragment(fragment))
    print('res=', res)
    if len(res) == 0:
        return None
    if len(res) != 1:
        print(f"ERROR - more than one record!, fragment={fragment}")
        exit
        #return None
    print('res[0]=', res[0])
    return res[0]

def create_new_image_record(it, gallery, image, next_index):
    newrec = {
        'gallery_name' : gallery['name'],
        'src_image_name' : image['name'],
        'src_image_loc' : gallery['src_imageurl_subdir'],
        'dst_image_name' : get_remote_name(gallery, next_index),
        'image_size' : image['size'],
        'remote_url' : None,
        'is_active' : True,
        'image_number' : next_index,
        'title' : get_default_image_title(gallery, next_index),
    }
    return newrec
def insert_record(it, newrec):
    it.insert(newrec)

def get_remote_name(gallery, next_index):
    return f"{gallery['name']}_{next_index:03d}"

def get_default_image_title(gallery, next_index):
    return f'{gallery["name"]} #{next_index}'

def get_next_index(it, gallery):
    images = it.search(where('gallery_name') == gallery['name'])
    print("n_images=", len(images))
    
    next_index = -1
    for image in images:
        if image['image_number'] > next_index:
            next_index = image['image_number']
    
    return next_index + 1

def get_galleries(toml_file_path):
    with open(toml_file_path, mode="rb") as fp:
       galleries = tomli.load(fp)
    
    return galleries['galleries']

def get_images(gallery):
    # get list from directory
    #src_imageurl = gallery['src_imageurl']

    src_imageurl = gallery.get('src_imageurl', SRC_IMAGE_URL)

    src_subdir = gallery['src_imageurl_subdir']

    url = f"{src_imageurl}/images?{src_subdir}"
    print("url=", url)
   
    response = requests.get(url)
    print("status=", response.status_code)
    print("text=", response.text)

    print("response=", response)

    if response.status_code != 200:
        print(f"ERROR: status={response.status_code}")
        return []

    images = parse_response(response.text)

    return images


    #images = [{ 'name': image['name'], 'size': image['size'], 'title':f"{gallery['title']}"} for i,image in enumerate(images)]
    
    # images = [{ 'name': image['name'], 
    #     'size': image['size'], 
    #     'remote_name': get_remote_name(gallery, i),
    #     'title': f"{gallery['title']} #{i}",
    #     } for i,image in enumerate(images)]


    # print("images=", images)


    return images

def parse_response(json_str):
    return json.loads(json_str)
   
def get_remote_name(gallery, i):
    return f"{gallery['name']}_{i:03d}"

def clear_image_table(db_file):
    db = MyDB(db_file)
    image_t = db.get_table('image')
    image_t.truncate()

def print_db(table):
    recs = table.all()

    for rec in recs:
        print('recs from db=', rec)
        pass

    # do it by gallery, sorted by dst_image_name
    galleries = get_gallery_names_from_docs(recs)

    print("galleries=", galleries)

    for gallery in galleries:
        print("====== Gallery = ", gallery)
        recs = table.search(Query().gallery_name == gallery)
        print('recs before sort', recs)
        recs.sort(key=lambda x: x['dst_image_name'])
        print('recs AFTER sort=', [ (rec['dst_image_name'], rec['is_active']) for rec in recs] )

def get_gallery_names_from_docs(docs):

    print("docs=", docs)
    
    galleries = [doc['gallery_name'] for doc in docs]
    print("galleries=", galleries)
    uniques = list(set(galleries))
    print("uniques=", uniques)
    return uniques

def get_gallery_names_from_db(it):
    recs = it.all()
    return get_gallery_names_from_docs(recs)

def get_images_from_db_active(it, gallery_name):
    print("serach for gallery_name=", gallery_name)
    # get is_active only?????? %%%
    Image = Query()
    recs = it.search((Image.gallery_name == gallery_name) & (Image.is_active == True))
    return recs

if __name__ == "__main__":
    toml_file = "test_galleries.toml"
    db_file = "test1.db"

    ##clear_image_table(db_file)

    build_db(toml_file, db_file)