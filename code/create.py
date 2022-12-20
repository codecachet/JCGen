#!/usr/bin/env python3

import os
import shutil
import json
from tinydb import TinyDB, Query, where
import datetime
import sys

import argparse
from pathlib import Path

from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

from dotenv import load_dotenv
load_dotenv()

from MyDB import MyDB
from database import build_db, get_images_from_db_active, clear_image_table, get_gallery_names_from_db, print_db, get_galleries
from upload import upload_to_cloudinary

top = "/home/dg/projects/JCGen/"
public_dir = os.path.join(top, "public")

css_dir_src = os.path.join(top, "static", "css")
css_dir_dst = os.path.join(public_dir, "css")

img_dir_src = os.path.join(top, "static", "img")
img_dir_dst = os.path.join(public_dir, "img")

font_dir_src = Path(top) / 'static' / 'fonts'
font_dir_dst = Path(top) / public_dir / 'fonts'

backup_dir = Path(top) / 'backups'  # note: for public, and for db

"""
top (rel to img-samples)
 Abstract
 House
 x Jack
 SpaceWar
 Watches
 Window

swift_output
 x abstract
 x city
 x house
 x music
 x owl
 x robot
 x spacewar (2)
 x surfing
 x train

icloud_downloads
 abstract
 alien
 birdhouse
 bowling
 cars
 music (2)
 robot (2)
"""

WEB_IMAGE_URL = "http://192.168.1.178:8002"   # serves images, plain and simple. This will be changed to, say, AWS
SRC_IMAGE_URL = "http://192.168.1.178:3020"   # has some smarts, to deliver list of images only (no text, subdirs etc)
#SRC_IMAGE_URL = "http://192.168.1.178:8002"

local_image_url = "http://192.168.1.178:8002"

aws_bucket = "jumpingcow-images"

remote_image_url_amazon = f"https://{ aws_bucket }.s3.amazonaws.com"
remote_image_url_cloudinary = "https://res.cloudinary.com/jumpingcow/image/upload"

remote_image_url = remote_image_url_cloudinary

N_DESK_COLUMNS = 3
N_MOBILE_COLUMNS = 1

image_db_path = "image_db.json"
#image_db_path = "test.db"
#gallery_toml_path = "test_galleries.toml"
gallery_toml_path = "galleries.toml"

# set for default
image_url = local_image_url

"""
options:
 create for local, remote, or both
   galleries: all or specific
 list db
 get number of files
 get size of images

"""

"""
./create.py create --mode remote --gallery house spacewar2

"""

def create_site(gallery_names, mode, show_image_name):

    # mydb = MyDB(image_db_path)
    # t_image = mydb.get_table('image')

    print('gallery_names', gallery_names)

    clear_public()
    backup_db(image_db_path)

    galleries, image_t = build_db(gallery_toml_path, image_db_path)

    # note: galleries is a dict, indexed by name

    print("gallery_names=", gallery_names)
    print('galleries=', galleries)

    if len(gallery_names) == 0 or gallery_names == 'all':
        gallery_list = galleries
        gallery_list = list(gallery_list.values())
    else:
        gallery_list = []
        for name in galleries.keys():
            if name in gallery_names:
                gallery_list.append(galleries[name])
        #gallery_list = [gallery[] for gallery in galleries if gallery['name'] in gallery_names]
    
    print('====gallery_list_final=', gallery_list)

    if len(gallery_list) == 0:
        print("ERROR: need a valid gallery name")
        return
    
    

    for gallery in gallery_list:
        print("DOING gallery =", gallery['name'])
        gallery_page(image_t, gallery, mode, show_image_name)
    
    home_page(gallery_list, image_t, mode)

    about_page()
    
    copy_dir_contents(css_dir_src, css_dir_dst)
    copy_dir_contents(img_dir_src, img_dir_dst)
    copy_dir_contents(font_dir_src, font_dir_dst)
   
def copy_public_to_mac():
    src_public = public_dir
    dst_public = Path('/media/psf/parallels_ubuntu_shared/') / 'jcgen_public'

    if dst_public.exists():
        for file in dst_public.iterdir():
            print(f"file={file}")
        
        shutil.rmtree(dst_public)

    #for file in dst_public.iterdir():
    #    print(f"file={file}")
    
    shutil.copytree(src_public, dst_public)

    for file in dst_public.iterdir():
        print(f"file={file}")

def list_db(table_name='image', gallery_name='spacewar2'):
    #db = TinyDB(image_db_path)
    mydb = MyDB(image_db_path)
    image_t = mydb.get_table(table_name)
    if gallery_name == 'all':
        docs = image_t.all()
    else:
        fragment = {
            'gallery_name' : gallery_name
        }
        docs = image_t.search(Query().fragment(fragment))
    for doc in docs:
        print("doc=", doc)

def db_summary():
    """
    list gallerys
      number of files
      size of gallery
    total files
    total size
    """
    #db = TinyDB(image_db_path)
    mydb = MyDB(image_db_path)
    image_t = mydb.get_table('image')
    gallery_names = get_gallery_names_from_db(image_t)
    total_size = 0
    total_n = 0
    for gallery_name in gallery_names:
        images = image_t.search(where('gallery_name') == gallery_name)

        fragment = {
            'gallery_name' : gallery_name,
            'is_active' : True
        }

        images_enabled = image_t.search(Query().fragment(fragment))
        n_enabled = len(images_enabled)
        n = len(images)
        size = sum([image['image_size'] for image in images])
        print(f"Gallery: {gallery_name}")
        print(f"  n = {n}")
        print(f'    n_enabled = {n_enabled}')
        print(f"  size = {size:,} bytes ({size / 1000000 :.1f} mb)")
        total_size += size
        total_n += n
    print(f"Total n = {total_n:,}")
    print(f"Total size={total_size:,} bytes ({total_size / 1000000 :.1f} mb)")
    print(f"Average file size={total_size / total_n :,.0f}")



# def get_gallery_names(it):
#     docs = it.all()
#     gallery_names = [doc['gallery_name'] for doc in docs]
#     print("gallery_names=", gallery_names)
#     uniques = list(set(gallery_names))
#     print("uniques=", uniques)
#     return uniques


def gallery_page(it, gallery, mode, show_image_name):
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("gallery.j2")

    imagelist = get_imagelist(it, gallery)
    print("imagelist=", imagelist)

    # kludge - get n_images into gallery, for use by home_page
    gallery['n_images'] = len(imagelist)
    gallery['remote_home_image_url'] = get_remote_home_image_url(it, gallery)

    #insert_imagelist_into_db(gallery, db, imagelist)

    n_desk_columns = gallery.get("n_desk_columns", N_DESK_COLUMNS)
    n_mobile_columns = gallery.get("n_mobile_columns", N_MOBILE_COLUMNS)

    desk_columns = create_columns(imagelist, n_desk_columns)
    mobile_columns = create_columns(imagelist, n_mobile_columns)

    print("desk_columns", desk_columns)
    print("mobile_columns", mobile_columns)

    print("mode=", mode)

    context = {
        "gallery_title" : gallery["title"],
        "desk_columns" : desk_columns,
        "mobile_columns" : mobile_columns,
        "siteurl" : "",
        "imageurl" : get_image_url(mode),
        "imageurl_subdir" : get_image_url_subdir(gallery, mode),
        "mode" : mode,   # will affect image name
        "images" : imagelist,
        "show_image_name" : show_image_name,
    }

    x = template.render(context)
   
    write_to_file(x, f"gallery_{ gallery['name'] }.html", public_dir)

def home_page(galleries, it, mode):
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("home.j2")

    print('home_page galleries=', galleries)
    
    n_desk_columns = N_DESK_COLUMNS
    n_mobile_columns = N_MOBILE_COLUMNS

    desk_columns = create_columns(galleries, n_desk_columns)
    mobile_columns = create_columns(galleries, n_mobile_columns)

    print("desk_columns", desk_columns)
    print("mobile_columns", mobile_columns)

    #update_galleries_from_db(db, mode)

    context = {
        "desk_columns" : desk_columns,
        "mobile_columns" : mobile_columns,
        "imageurl" : get_image_url(mode),
        "siteurl" : "",
        "mode" : mode,
    }

    x = template.render(context)
    #print("x=", x)

    write_to_file(x, "index.html", public_dir)


def about_page():
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("about.j2")

    

    context = {
     
    }

    x = template.render(context)
    #print("x=", x)

    write_to_file(x, "about.html", public_dir)


def get_image_full_url_remote(db, mode, gallery, subdir, image_name):
    filename = get_remote_image_name(db, gallery, subdir, image_name)
    return f"{get_image_url(mode)}/{get_image_url_subdir(gallery, mode)}/{filename}"
    
def get_remote_image_name(db, gallery, subdir, image_name):
    fragment = {
        'gallery_name': gallery['name'], 
        'src_image_name': image_name, 
        'src_image_loc' : subdir 
    }

    images = db.search(Query().fragment(fragment))
    print("images found =", images)

    if len(images) != 1:
        print("ERROR: found multiple images, images=", images)
        return None
    return images[0]['dst_image_name']

def get_remote_home_image_url(it, gallery):
    fragment = {
        'gallery_name' : gallery['name'],
        'src_image_name' : gallery['home_image_name'],
        'src_image_loc' : gallery['src_imageurl_subdir'],
    }
    images = it.search(Query().fragment(fragment))
    
    if len(images) == 0:
        print("ERROR: cannot find image for home image, fragment=", fragment)
        return None
    image = images[0]
    return image['remote_url']


def get_n_images(db, gallery):
    images = db.search(where('gallery_name') == gallery['name'])
    print("n_images=", len(images))
    return len(images)


def create_columns(imagelist, n_columns):
    the_columns = []
    for c in range(n_columns):
        the_columns.append([])
    
    def get_column(columns):
        while(1):
            i = 0
            while i < len(columns):
                yield columns[i]
                i += 1
            
    gen = get_column(the_columns)   
    for image in imagelist:
        col = next(gen)
        #print("col=", col)
        col.append(image)
    return the_columns


def get_imagelist(it, gallery):
    image_recs = get_images_from_db_active(it, gallery['name'])

    print('image_recs=', image_recs)

    return image_recs


def parse_response(json_str):
    return json.loads(json_str)

def write_to_file(str, name, dir):
    path = os.path.join(dir, name)
    print("path=", path)
    with open(path, "w") as f:
        f.write(str)

def copy_dir_contents(dir_src, dir_dst):
    print(f"src={dir_src}, dst={dir_dst}")
    shutil.copytree(dir_src, dir_dst, dirs_exist_ok=True)



def get_image_url(mode):
    if mode == "local":
        return local_image_url
    else:
        return remote_image_url

def get_image_url_subdir(gallery, mode):
    if mode == "local":
        return gallery['src_imageurl_subdir']
    else:
        return gallery["name"]



def get_remote_name(gallery, i):
    return f"{gallery['name']}_{i:03d}"


def upload(gallery_names):
    db = MyDB(image_db_path)
    image_t = db.get_table('image')
    iserver_t = db.get_table('iserver')

    print('gallery_names init', gallery_names)
    if len(gallery_names) == 0:
        print("Need to enter gallery names, or all")
        return

    if gallery_names[0] == 'all_db':
        gallery_names = get_gallery_names_from_db(image_t)
    elif gallery_names[0] == 'all':
        gallery_names = get_gallery_names_from_toml()
    print('gallery_names=', gallery_names)
    
    for gallery_name in gallery_names:
        image_recs = get_images_from_db_active(image_t, gallery_name)
        upload_to_cloudinary(image_t, iserver_t, WEB_IMAGE_URL, image_recs)
    
def get_gallery_names_from_toml():
    galleries = get_galleries(gallery_toml_path)
    return list(galleries.keys())
    
def clear_public():
    #print('public_dir=', public_dir)
    #shutil.rmtree(public_dir)
    src_dir = public_dir
    dst_dir = Path(backup_dir) / 'public'

    if not os.path.exists(src_dir):
        print(f'Directory {src_dir} does not exist, so no backup, creating new empty')
        os.mkdir(public_dir)
        return

    now = datetime.datetime.now()
    ts = datetime.datetime.timestamp(now)
    
    dest = Path(dst_dir) / f'public_{ts}'

    os.rename(src_dir, dest)

    print(f'Moved public to {dest}')

    # make new empty public dir
    os.mkdir(public_dir)


def clear_db():
    backup_db(image_db_path)
    clear_image_table(image_db_path)

def backup_db(db_path):
    src_path = image_db_path
    src_file = os.path.basename(src_path)
    dst_dir = Path(backup_dir) / 'db'

    now = datetime.datetime.now()
    ts = int (datetime.datetime.timestamp(now))

    dest = Path(dst_dir) / f'{src_file}_{ts}'
    print(f'src_path={src_path}, src_file={src_file}, dst={dest}')

    shutil.copyfile(src_path, dest)


def main():

    parser = argparse.ArgumentParser(description='Generate static pages')
    parser.add_argument('operation', choices=['create', 'listdb', 'summary', 'toml', 'copy_to_mac', 'upload', 'clear_db'])  # default='create', nargs='?' )
    parser.add_argument('--gallery', default='all', nargs='*')
    parser.add_argument('--mode', choices=['local', 'remote'], default='local', nargs='?')
    parser.add_argument('--show_image_name', action='store_true')
    args = parser.parse_args()
    print("args=", args)
    #print(args.accumulate(args.integers))
    print(f"operation={args.operation}")

    if args.operation == "create":
        print("args.gallery=", args.gallery)
        print("args.mode=", args.mode)
        create_site(args.gallery, args.mode, args.show_image_name)
        #pass
    elif args.operation == "listdb":
        list_db()
    elif args.operation == "summary":
        db_summary()
    # elif args.operation == "toml":
    #     init_config()
    elif args.operation == "clear_db":
        clear_db()
    elif args.operation == 'copy_to_mac':
        copy_public_to_mac()
    elif args.operation == 'upload':
        upload(args.gallery)
    else:
        print("ERROR: need operation")

if __name__ == "__main__":
    main()


