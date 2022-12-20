#!/usr/bin/bash

top=~/projects
jcgen=$top/JCGen
jumpingcow=$top/JumpingCow
src=$top/JCGen/public
dst=$top/JumpingCow/public
backups=$jumpingcow/backups

date_now=$(date "+%F-%H-%M-%S")

echo "src=$src"
echo "dst=$dst"
echo "backups=$backups"

mv $dst $backups/public_$date_now

cp -rp $src $jumpingcow

cd $jumpingcow
git add .
git commit -m"another generation"
git push




