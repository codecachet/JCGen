#!/usr/bin/env python3

import os
import shutil
import requests 
#from bs4 import BeautifulSoup
import json
from tinydb import TinyDB, Query, where
from MyDB import MyDB
from database import build_db, get_images_from_db, clear_image_table
import sys

import argparse
import tomli
from pathlib import Path
import tempfile

from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

# remote image storage
import cloudinary_utils

top = "/home/dg/projects/JCGen/"
public_dir = os.path.join(top, "public")

css_dir_src = os.path.join(top, "static", "css")
css_dir_dst = os.path.join(public_dir, "css")

img_dir_src = os.path.join(top, "static", "img")
img_dir_dst = os.path.join(public_dir, "img")

font_dir_src = Path(top) / 'static' / 'fonts'
font_dir_dst = Path(top) / public_dir / 'fonts'

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

#image_db_path = "image_db.json"
image_db_path = "test.db"
gallery_toml_path = "test_galleries.toml"

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

#mode = "LOCAL"   # or "REMOTE"

#galleries = None


def create_site(gallery_names, mode, show_image_name):

    # mydb = MyDB(image_db_path)
    # t_image = mydb.get_table('image')

    clear_public()

    galleries, image_t = build_db(gallery_toml_path, image_db_path)

    print("gallery_names=", gallery_names)
    print('galleries=', galleries)

    if len(gallery_names) == 0 or gallery_names == 'all':
        gallery_list = galleries
    else:
        gallery_list = [gallery for gallery in galleries if gallery['name'] in gallery_names]
    
    print('====gallery_list_final=', gallery_list)

    if len(gallery_list) == 0:
        print("ERROR: need a valid gallery name")
        return
    

    gallery_list = list(gallery_list.values())

    for gallery in gallery_list:
        print("DOING gallery =", gallery['name'])
        gallery_page(image_t, gallery, mode, show_image_name)
    
    home_page(gallery_list, image_t, mode)
    
    copy_dir_contents(css_dir_src, css_dir_dst)
    copy_dir_contents(img_dir_src, img_dir_dst)
    copy_dir_contents(font_dir_src, font_dir_dst)

    #copy_public_to_mac()
    # copy public to mac shared directory
    

    #print("db len=", len(db.all()))
   
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



def list_db(table_name='image'):
    #db = TinyDB(image_db_path)
    mydb = MyDB(image_db_path)
    image_t = mydb.get_table(table_name)
    docs = image_t.all()
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
    gallerie_names = get_galleriy_names(image_t)
    total_size = 0
    total_n = 0
    for gallery_name in gallerie_names:
        images = image_t.search(where('gallery_name') == gallery_name)
        n = len(images)
        size = sum([image['image_size'] for image in images])
        print(f"Gallery: {gallery}")
        print(f"  n = {n}")
        print(f"  size = {size:,} bytes ({size / 1000000 :.1f} mb)")
        total_size += size
        total_n += n
    print(f"Total n = {total_n:,}")
    print(f"Total size={total_size:,} bytes ({total_size / 1000000 :.1f} mb)")
    print(f"Average file size={total_size / total_n :,.0f}")


def get_gallery_names(it):
    docs = it.all()
    gallery_names = [doc['gallery_name'] for doc in docs]
    print("gallery_names=", gallery_names)
    uniques = list(set(gallery_names))
    print("uniques=", uniques)
    return uniques


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
        #"imageurl" : gallery["imageurl"],
        #"imageurl_subdir" : gallery["imageurl_subdir"],

        "imageurl" : get_image_url(mode),
        "imageurl_subdir" : get_image_url_subdir(gallery, mode),
        "mode" : mode,   # will affect image name
        "images" : imagelist,
        "show_image_name" : show_image_name,
    }

    x = template.render(context)
    #print("x=", x)

    write_to_file(x, f"gallery_{ gallery['name'] }.html", public_dir)

def home_page(galleries, it, mode):
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("home.j2")


    #gallery_list = list(galleries.values())

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


def get_image_full_url_remote(db, mode, gallery, subdir, image_name):
    filename = get_remote_image_name(db, gallery, subdir, image_name)
    return f"{get_image_url(mode)}/{get_image_url_subdir(gallery, mode)}/{filename}"
    
def get_remote_image_name(db, gallery, subdir, image_name):
    fragment = {
        'gallery_name': gallery['name'], 'src_image_name': image_name, 'src_image_loc' : subdir 
    }

    images = db.search(Query().fragment(fragment))
    print("images found =", images)

    if len(images) != 1:
        print("ERROR: found multiple images, images=", images)
        return None
    return images[0]['dst_image_name']

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
    image_recs = get_images_from_db(it, gallery['name'])

    print('image_recs=', image_recs)

    #images = [{ 'name': image['name'], 'size': image['size'], 'title':f"{gallery['title']}"} for i,image in enumerate(images)]
    # images = [{ 'name': image['name'], 
    #     'size': image['size'], 
    #     'remote_name': get_remote_name(gallery, i),
    #     'title': f"{gallery['title']} #{i}",
    #     } for i,image in enumerate(images)]


    # print("images=", images)


    return image_recs


"""
def parse_response_old(html):
   
    #convert li's to list
   
    soup = BeautifulSoup(html, 'html.parser')
    print("soup=", soup)
    items = soup.find_all('li')
    print("items=", items)
    for item in items:
        print("text=", item.text)
    images = [item.text for item in items]
    return images
"""

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

def clear_public():
    print('public_dir=', public_dir)
    #shutil.rmtree(public_dir)


# def get_imagelist(gallery):

#     #if not gallery.has_key("get_imagelist"):
#     #   imagelist_name = 'get_imagelist_default'
    
#     imagelist_name = gallery.get('get_imagelist', 'get_imagelist_default')

#     #imagelist_name = gallery["get_imagelist"]
#     images = globals()[imagelist_name](gallery)
#     return images

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

# def init_config():
#     with open("galleries.toml", mode="rb") as fp:
#        config = tomli.load(fp)
#     print("config =", config)

#     config_galleries = config['galleries']

#     global galleries
#     galleries = []

#     for name, gallery in config_galleries.items():
#         print("gallery=", gallery)
#         gallery['name'] = name
#         galleries.append(gallery)
#     print("galleries=", galleries)

# def get_gallery(gallery_name):
#     for gallery in galleries:
#         if gallery['name'] == gallery_name:
#             return gallery
#     return None

def get_image_to_local_file(image):
    src_imageurl = WEB_IMAGE_URL

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


def upload(gallery_name = 'house'):
    #init_config()
    #gallery_name = 'house'
    print('gallery_name=', gallery_name)
    gallery_name = 'house'
    gallery = get_gallery(gallery_name)
    print("gallery=", gallery)
    names = [gallery['name'] for gallery in galleries]
    print('names=', names)

    db = TinyDB(image_db_path)

    images = db.search(where('gallery_name') == gallery_name)
    print("images=", images)

    for image in images:
        tmp_file_name = get_image_to_local_file(image)
        print("tmp_file_name", tmp_file_name)

        #assume cloudinary for now
        result = cloudinary_utils.upload_image(image, tmp_file_name)

def clear_db():
    clear_image_table(image_db_path)


def main():

    parser = argparse.ArgumentParser(description='Generate static pages')
    #parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                    help='an integer for the accumulator')
    #parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                    const=sum, default=max,
    #                    help='sum the integers (default: find the max)')

    #parser.add_argument('--create', action='store_true' )
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


