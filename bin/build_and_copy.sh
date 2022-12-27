#!/usr/bin/bash

# Dec 26, 2022
# ensure that environment is set: cd ~/projects/JCGen; . ve/bin/activate
# THEN
cd ~/projects/CJGen/code
./create.py create --mode remote

cd ../bin
./copy_to_jumpingcow.sh

# log onto render.com
# Manual Deploy

