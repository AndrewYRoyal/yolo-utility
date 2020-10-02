#!/usr/bin/env python

import os
import re
import random
import numpy as np
import shutil
import subprocess
import argparse

parser = argparse.ArgumentParser('Format and export Yolo images and labels')
parser.add_argument('--images', dest='images', required=True, action='store')
parser.add_argument('--labels', dest='labels', required=True, action='store')
parser.add_argument('--names', dest='names', required=True, action='store')
parser.add_argument('--pvalid', dest='pvalid', default=0.2, action='store')
parser.add_argument('--ptest', dest='ptest', default=0.2, action='store')

args = parser.parse_args()

import_dir = {
    'images': f'input/images/{args.images}',
    'labels': f'input/labels/{args.labels}',
    'names': f'input/{args.names}.names'
}


print('Reading data')
# Import Data
#=========================================
images = os.listdir(import_dir['images'])
labels = os.listdir(import_dir['labels'])
r = re.compile('.*txt')
labels = list(filter(r.match, labels))
ids = {
    'all': [re.sub('.png', '', x) for x in images],
    'labelled': [re.sub('.txt', '', x) for x in labels]
}

# Split training, validation and test set
#=========================================
print('Assigning data to groups')
nvalid = len(ids['labelled']) // (1 / args.pvalid)
ntest = len(ids['labelled']) // (1 / args.ptest)
nvalid, ntest = [np.int(x) for x in [nvalid, ntest]]
ids.update(
    {
        'valid': random.sample(
            population=ids['labelled'],
            k=nvalid)
    }
)
ids.update(
    {
        'test': random.sample(
            population=set(ids['labelled']).difference(set(ids['valid'])),
            k=ntest)
    }
)
ids.update(
    {
        'train': set(ids['labelled']).difference(set(ids['valid'] + ids['test']))
    }
)
del ids['labelled']

# Populate Temp Directories
#=========================================
print('Populating temp directory')
if(os.path.exists('temp')):
    shutil.rmtree('temp', ignore_errors=True)
os.mkdir('temp')
for ftype in ['images', 'labels']:
    os.mkdir(f'temp/{ftype}')
    for group in ['train', 'valid', 'test']:
        os.mkdir(f'temp/{ftype}/{group}')
os.mkdir('temp/images/all')

def format_copy(id, ftype, group):
    suffix = 'png' if ftype == 'images' else 'txt'
    export_id = re.sub('\.', '_', id) # needed to comply with yolo formatting
    paths = {
        'src': os.path.join(import_dir[ftype], f'{id}.{suffix}'),
        'dst': f'temp/{ftype}/{group}/{export_id}.{suffix}'
    }
    return paths

for grp, grp_ids in ids.items():
    image_paths = [format_copy(i, 'images', grp) for i in grp_ids]
    label_paths = [format_copy(i, 'labels', grp) for i in grp_ids]
    for im in image_paths:
        shutil.copy(**im)
    if grp != 'all':
        for lbl in label_paths:
            shutil.copy(**lbl)

shutil.copy(import_dir['names'], f'temp/{args.names}.names')

print('Syncing temp directory')
subprocess.run(['C:/Program Files/Git/git-bash.exe', './export_s3.sh'], shell=True)

print('Removing temp directory')
shutil.rmtree('temp', ignore_errors=True)

