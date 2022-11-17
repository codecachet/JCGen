#!/usr/bin/env python3

import os
import shutil

from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

top = "/home/dg/projects/JCGen/"
public_dir = os.path.join(top, "public")

css_dir_src = os.path.join(top, "static", "css")
css_dir_dst = os.path.join(public_dir, "css")


def doit():
    env = Environment(
        loader=FileSystemLoader("../templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("main1.j2")

    imagelist = get_imagelist()
    print("imagelist=", imagelist)

    n_desk_columns = 3
    n_mobile_columns = 1

    desk_columns = create_columns(imagelist, n_desk_columns)
    mobile_columns = create_columns(imagelist, n_mobile_columns)

    print("desk_columns", desk_columns)
    print("mobile_columns", mobile_columns)


    context = {
        "gallery_title" : "Jack",
        "desk_columns" : desk_columns,
        "mobile_columns" : mobile_columns,
        "siteurl" : "",
        "imageurl" : "http://192.168.1.178:8002",
        "images" : imagelist
    }

    x = template.render(context)
    #print("x=", x)

    write_to_file(x, "index.html", public_dir)

    copy_dir_contents(css_dir_src, css_dir_dst)
    
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

def get_imagelist():
    with open("imagelist.txt", "r") as f:
        images = f.readlines()
    images = [{ "name": image.strip(), "title":f"jack_{i}"} for i,image in enumerate(images)]
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

if __name__ == "__main__":
    doit()