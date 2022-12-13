#!/usr/bin/bash

cd ~/projects/JCGen
source ve/bin/activate

cd ~/projects/JCGen/public

python -m http.server 8005
