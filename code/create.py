#!/usr/bin/env python3

import os
import shutil
import requests 
#from bs4 import BeautifulSoup
import json
from tinydb import TinyDB, Query, where
import argparse
import tomli

from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

top = "/home/dg/projects/JCGen/"
public_dir = os.path.join(top, "public")

css_dir_src = os.path.join(top, "static", "css")
css_dir_dst = os.path.join(public_dir, "css")

img_dir_src = os.path.join(top, "static", "img")
img_dir_dst = os.path.join(public_dir, "img")

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

remote_image_url = f"https://{ aws_bucket }.s3.amazonaws.com"

N_DESK_COLUMNS = 3
N_MOBILE_COLUMNS = 1

image_db_path = "image_db.json"

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

galleries = None


def create_site(gallery_names, mode, show_image_name):
    init_config()

    db = TinyDB(image_db_path)

    # delete all
    db.truncate()

    print("gallery_names=", gallery_names)

    if len(gallery_names) == 0 or gallery_names == 'all':
        gallery_list = galleries
    else:
        gallery_list = [gallery for gallery in galleries if gallery['name'] in gallery_names]
    
    print('gallery_list=', gallery_list)

    if len(gallery_list) == 0:
        print("ERROR: need a valid gallery name")
        return

    for gallery in gallery_list:
        print("DOING gallery =", gallery['name'])
        gallery_page(db, gallery, mode, show_image_name)
    
    home_page(db, mode)
    
    copy_dir_contents(css_dir_src, css_dir_dst)
    copy_dir_contents(img_dir_src, img_dir_dst)

    #print("db len=", len(db.all()))
   

def list_db():
    db = TinyDB(image_db_path)
    docs = db.all()
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
    db = TinyDB(image_db_path)
    galleries = get_galleries(db)
    total_size = 0
    total_n = 0
    for gallery in galleries:
        images = db.search(where('gallery_name') == gallery)
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


def get_galleries(db):
    docs = db.all()
    galleries = [doc['gallery_name'] for doc in docs]
    print("galleries=", galleries)
    uniques = list(set(galleries))
    print("uniques=", uniques)
    return uniques


def gallery_page(db, gallery, mode, show_image_name):
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("gallery.j2")

    imagelist = get_imagelist(gallery)
    print("imagelist=", imagelist)

    insert_imagelist_into_db(gallery, db, imagelist)

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

def home_page(db, mode):
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("home.j2")

    

    n_desk_columns = N_DESK_COLUMNS
    n_mobile_columns = N_MOBILE_COLUMNS

    desk_columns = create_columns(galleries, n_desk_columns)
    mobile_columns = create_columns(galleries, n_mobile_columns)

    print("desk_columns", desk_columns)
    print("mobile_columns", mobile_columns)

    update_galleries_from_db(db, mode)

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

def update_galleries_from_db(db, mode):
    """
    Get remote url for home image (toc)
    Get number of files in gallery
    """
    for gallery in galleries:
        gallery['home_image_url_remote'] = get_image_full_url_remote(db, mode, gallery, gallery['src_imageurl_subdir'], gallery['home_image_name'])
        gallery['n_images'] = get_n_images(db, gallery)
        print("gallery after updates=", gallery)

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

def insert_imagelist_into_db(gallery, db, imagelist):
    for i, image in enumerate(imagelist):
        rec = {
            'gallery_name' : gallery['name'],
            'src_image_name' : image['name'],
            'src_image_loc' : gallery.get('imageurl_subdir', gallery['src_imageurl_subdir']),
            'dst_image_name' : get_remote_name(gallery, i),
            'image_size' : image['size'],
        } 
        db.insert(rec)


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

def get_imagelist_jack(gallery):
    with open("jack_imagelist.txt", "r") as f:
        images = f.readlines()
    images = [{ "name": image.strip(), "title":f"jack_{i}"} for i,image in enumerate(images)]
    print("images=", images)
    return images

def get_imagelist_swift(gallery):
    with open("swift_imagelist.txt", "r") as f:
        images = f.readlines()
    images = [{ "name": image.strip(), "title":f"swift_{i}"} for i,image in enumerate(images)]
    print("images=", images)
    return images

def get_imagelist_default(gallery):
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

    #images = [{ 'name': image['name'], 'size': image['size'], 'title':f"{gallery['title']}"} for i,image in enumerate(images)]
    images = [{ 'name': image['name'], 
        'size': image['size'], 
        'remote_name': get_remote_name(gallery, i),
        'title': f"{gallery['title']} #{i}",
        } for i,image in enumerate(images)]


    print("images=", images)


    return images


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

def get_imagelist(gallery):

    #if not gallery.has_key("get_imagelist"):
    #   imagelist_name = 'get_imagelist_default'
    
    imagelist_name = gallery.get('get_imagelist', 'get_imagelist_default')

    #imagelist_name = gallery["get_imagelist"]
    images = globals()[imagelist_name](gallery)
    return images

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

def init_config():
    with open("galleries.toml", mode="rb") as fp:
       config = tomli.load(fp)
    print("config =", config)

    config_galleries = config['galleries']

    global galleries
    galleries = []

    for name, gallery in config_galleries.items():
        print("gallery=", gallery)
        gallery['name'] = name
        galleries.append(gallery)
    print("galleries=", galleries)

    


def main():

    parser = argparse.ArgumentParser(description='Generate static pages')
    #parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                    help='an integer for the accumulator')
    #parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                    const=sum, default=max,
    #                    help='sum the integers (default: find the max)')

    #parser.add_argument('--create', action='store_true' )
    parser.add_argument('operation', choices=['create', 'listdb', 'summary', 'toml'])  # default='create', nargs='?' )
    parser.add_argument('--gallery', default='all', nargs='*')
    parser.add_argument('--mode', choices=['local', 'remote'], default='local', nargs='?')
    parser.add_argument('--show_image_name', action='store_true')
    args = parser.parse_args()
    print("args=", args)
    #print(args.accumulate(args.integers))
    print(f"operation={args.operation}")

    if args.operation == "create":
        print("args.gallery=", args.gallery)
        create_site(args.gallery, args.mode, args.show_image_name)
        #pass
    elif args.operation == "listdb":
        list_db()
    elif args.operation == "summary":
        db_summary()
    elif args.operation == "toml":
        init_config()
    else:
        print("ERROR: need operation")

if __name__ == "__main__":
    main()
