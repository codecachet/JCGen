#!/usr/bin/env python

from pathlib import Path
import os
import json

top = Path("~/projects/JCGen").expanduser()

text_file = Path(top) / 'code' / 'cloudinary_house_init.txt'

gallery_name = 'house'

def fixit():
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


if __name__ == '__main__':
    fixit()