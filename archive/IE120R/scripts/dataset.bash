#!/bin/bash
#
mkdir -p dataset
cd dataset
wget https://image-net.org/data/ILSVRC/2010/ILSVRC2010_devkit-1.0.tar.gz
wget https://image-net.org/data/ILSVRC/2010/ILSVRC2010_images_val.tar
gunzip ILSVRC2010_devkit-1.0.tar.gz
tar xf ILSVRC2010_devkit-1.0.tar
tar xf ILSVRC2010_images_val.tar
ls -1 val | grep '\.J' > val/flist

mkdir -p train
cd train
wget https://image-net.org/data/ILSVRC/2010/ILSVRC2010_images_train.tar
tar xf ILSVRC2010_images_train.tar
# https://raw.githubusercontent.com/pytorch/examples/refs/heads/main/imagenet/extract_ILSVRC.sh
# At this stage imagenet/train will contain 1000 compressed .tar files, one for each category
# For each .tar file: 
#   2. extract and copy contents of .tar file into directory
#   3. remove .tar file
find . -name "n*.tar" | while read NAME ; do tar -xvf "${NAME}" ; rm -f "${NAME}"; done
ls -1 | grep '\.J' > flist
cd ../..
