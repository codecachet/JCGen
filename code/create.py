#!/usr/bin/env python3

import os
import shutil
import requests 
from bs4 import BeautifulSoup
import json

from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

top = "/home/dg/projects/JCGen/"
public_dir = os.path.join(top, "public")

css_dir_src = os.path.join(top, "static", "css")
css_dir_dst = os.path.join(public_dir, "css")

img_dir_src = os.path.join(top, "static", "img")
img_dir_dst = os.path.join(public_dir, "img")

"""
Jack
Trains
Watches
Crow
Window
Abstract
Musicality
House
Aliens
SpaceWar
Running
Coffee
Surfing
Cities
Bots
Owl

in swift:

abstract
spacewar
robot
house
music
surfing
city
owl
train

"""

WEB_IMAGE_URL = "http://192.168.1.178:8002"
SRC_IMAGE_URL = "http://192.168.1.178:3020"

N_DESK_COLUMNS = 3
N_MOBILE_COLUMNS = 1

galleries = [
    {
        "name": "jack",
        "title": "JackO",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "Jack",
        "get_imagelist": "get_imagelist_jack",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "000187.2732763625.png"
    },
    {
        "name": "abstract",
        "title": "Abstractions",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/abstract", # note: swift_output is temp, for testing
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/abstract",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "abstract_56.png"
    },
    {
        "name": "spacewar",
        "title": "SpaceWar",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/spacewar", 
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/spacewar",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "cool_90.png"
    },
    {
        "name": "robot",
        "title": "Bot",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/robot", 
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/robot",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "koi_41.png"
    },
    {
        "name": "house",
        "title": "House",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/house", 
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/house",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "cool_112.png"
    },
    {
        "name": "music",
        "title": "Music",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/music", 
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/music",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "cool_44.png"
    },
    {
        "name": "surfing",
        "title": "Surfing",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/surfing", 
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/surfing",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "cool_20.png"
    },
    {
        "name": "city",
        "title": "City",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/city", 
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/city",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "cool_155.png"
    },
    {
        "name": "owl",
        "title": "Owl",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/owl", 
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/owl",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "cool_27.png"
    },
    {
        "name": "train",
        "title": "Cosmic Train",
        "imageurl": WEB_IMAGE_URL,
        "imageurl_subdir": "swift_output/train", 
        "get_imagelist": "get_imagelist_default",
        "src_imageurl" : SRC_IMAGE_URL,
        "src_imageurl_subdir" : "swift_output/train",
        "n_desk_columns": N_DESK_COLUMNS,
        "n_mobile_columns": N_MOBILE_COLUMNS,
        "home_image_name" : "cool_254.png"
    },
    

]


def doit():
    
    for gallery in galleries:
        
        """ if gallery["name"] == "abstract":
            get_imagelist_default(gallery)
            return
        else:
            continue """
        
        gallery_page(gallery)
    
    home_page()
    
    copy_dir_contents(css_dir_src, css_dir_dst)
    copy_dir_contents(img_dir_src, img_dir_dst)

def gallery_page(gallery):
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("gallery.j2")

    imagelist = get_imagelist(gallery)
    print("imagelist=", imagelist)

    n_desk_columns = gallery["n_desk_columns"]
    n_mobile_columns = gallery["n_mobile_columns"]

    desk_columns = create_columns(imagelist, n_desk_columns)
    mobile_columns = create_columns(imagelist, n_mobile_columns)

    print("desk_columns", desk_columns)
    print("mobile_columns", mobile_columns)


    context = {
        "gallery_title" : gallery["title"],
        "desk_columns" : desk_columns,
        "mobile_columns" : mobile_columns,
        "siteurl" : "",
        "imageurl" : gallery["imageurl"],
        "imageurl_subdir" : gallery["imageurl_subdir"],
        "images" : imagelist,
        "print_image_name" : True
    }

    x = template.render(context)
    #print("x=", x)

    write_to_file(x, f"gallery_{ gallery['name'] }.html", public_dir)

def home_page():
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


    context = {
        "desk_columns" : desk_columns,
        "mobile_columns" : mobile_columns,
        "siteurl" : "",
    }

    x = template.render(context)
    #print("x=", x)

    write_to_file(x, "index.html", public_dir)

       
    
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
    src_imageurl = gallery['src_imageurl']
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

    images = [{ "name": image.strip(), "title":f"{gallery['title']} {i}"} for i,image in enumerate(images)]

    print("images=", images)

    return images


def parse_response_old(html):
    """
    convert li's to list
    """
    soup = BeautifulSoup(html, 'html.parser')
    print("soup=", soup)
    items = soup.find_all('li')
    print("items=", items)
    for item in items:
        print("text=", item.text)
    images = [item.text for item in items]
    return images

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
    imagelist_name = gallery["get_imagelist"]
    images = globals()[imagelist_name](gallery)
    return images

if __name__ == "__main__":
    doit()
