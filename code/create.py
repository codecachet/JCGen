#!/usr/bin/env python3

import os
import shutil

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

"""

galleries = [
    {
        "name": "jack",
        "title": "JackO",
        "imageurl": "http://192.168.1.178:8002",
        "imageurl_subdir": "Jack",
        "get_imagelist": "get_imagelist_jack",
        "n_desk_columns": 3,
        "n_mobile_columns": 1,
    },
    {
        "name": "swift",
        "title": "Swift Output",
        "imageurl": "http://192.168.1.178:8002",
        "imageurl_subdir": "swift_output",
        "get_imagelist": "get_imagelist_swift",
        "n_desk_columns": 3,
        "n_mobile_columns": 1,
    }
]


def doit():
    for gallery in galleries:
        gallery_page(gallery)
    copy_dir_contents(css_dir_src, css_dir_dst)
    copy_dir_contents(img_dir_src, img_dir_dst)

def gallery_page(gallery):
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("main.j2")

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
        "images" : imagelist
    }

    x = template.render(context)
    #print("x=", x)

    write_to_file(x, f"gallery_{ gallery['name'] }.html", public_dir)

    
    
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

def get_imagelist_jack():
    with open("jack_imagelist.txt", "r") as f:
        images = f.readlines()
    images = [{ "name": image.strip(), "title":f"jack_{i}"} for i,image in enumerate(images)]
    print("images=", images)
    return images

def get_imagelist_swift():
    with open("swift_imagelist.txt", "r") as f:
        images = f.readlines()
    images = [{ "name": image.strip(), "title":f"swift_{i}"} for i,image in enumerate(images)]
    print("images=", images)
    return images

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
    images = globals()[imagelist_name]()
    return images

if __name__ == "__main__":
    doit()
