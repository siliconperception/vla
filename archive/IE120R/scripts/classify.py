# Copyright (c) 2024 Silicon Perception Inc (www.siliconperception.com)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import siliconperception ; print('siliconperception',siliconperception.__version__)
from siliconperception.IE120R import IE120R,IE120R_HW
import torch
import torchinfo
import numpy as np
import timm
import argparse
import cv2
import scipy
import numpy as np
import random
import datetime
import queue
import threading
import subprocess
import os
import torch.nn as nn
from huggingface_hub import PyTorchModelHubMixin
from collections import OrderedDict

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--backbone', help='{resnet18, ie120r}',default='resnet18')
parser.add_argument('--verbose', help='logging',default=False, action='store_true')
parser.add_argument('--show', help='display batches',default=False, action='store_true')
parser.add_argument('--nbatch', help='total training batches',default=10000, type=int)
parser.add_argument('--lr', help='initial learning rate',default=0.00001, type=float)
parser.add_argument('--device', help='pytorch execution device',default='cuda')
parser.add_argument('--dataset', help='imagenet dataset base directory',default='./dataset/')
parser.add_argument('--batch', help='batch size',default=20, type=int)
parser.add_argument('--workers', help='number of threads for batch generation',default=12, type=int)
parser.add_argument('--avg', help='moving average window for lr and grad',default=100, type=int)
parser.add_argument('--seed', help='random seed',default=None, type=int)
args = parser.parse_args()
if args.seed is None:
    random.seed(None) # random seed
    args.seed = random.randint(0,1000000000)
random.seed(args.seed)
args.rng = np.random.default_rng(args.seed)

# --------------------------------------------------------------------------------------------------------------------------
# CLASSIFIER DECODER
# --------------------------------------------------------------------------------------------------------------------------
class Decoder(nn.Module):
    def __init__(self,encoder,alt='resnet18'):
        super(Decoder, self).__init__()
        self.alt=alt
        self.encoder = encoder
        self.layerp = nn.Conv2d(512, 1000, kernel_size=7, stride=1) # linear projection from final 7x7 feature map to 1000 imagenet classes

    def forward(self, x):
        if self.alt=='resnet18':
            fmap = self.encoder(x)[4] # 7x7x512
        if self.alt=='ie120r':
            fmap = self.encoder(x)
        y = self.layerp(fmap)
        return y[:,:,0,0]

if args.backbone=='resnet18':
    resnet18 = timm.create_model('resnet18.a1_in1k', pretrained=True, features_only=True)
    for param in resnet18.parameters():
        param.requires_grad = False
    resnet18 = resnet18.eval()
    model = Decoder(resnet18)
    roi=224
    data_config = timm.data.resolve_model_data_config(resnet18)
    transforms = timm.data.create_transform(**data_config, is_training=False)
    dmean = transforms.transforms[-1].mean.numpy()
    dstd = transforms.transforms[-1].std.numpy()
    print('dmean',dmean,'dstd',dstd)
    print('resnet18 pretrained model loaded from timm')

if args.backbone=='ie120r':
    encoder = IE120R.from_pretrained('siliconperception/IE120R')
    encoder = IE120R_HW(encoder) # merge BN and Conv2D, quantize weights to bfloat18, returns [7,7,512] feature map only
    for param in encoder.parameters():
        param.requires_grad = False
    encoder = encoder.eval()
    model = Decoder(encoder,alt='ie120r')
    roi=896 # image sensor region of interest size
    dmean=[0.485,0.456,0.406]
    dstd=[0.229,0.224,0.225]
    print('ie120r pretrained model loaded from huggingface')

if args.verbose:
    torchinfo.summary(model,col_names=["input_size","output_size","num_params"],input_size=(1,3,roi,roi))

device = torch.device(args.device)
model = model.to(device)

# --------------------------------------------------------------------------------------------------------------------------
# DATASET LOADER
# --------------------------------------------------------------------------------------------------------------------------
synlabel={}
labeltext={}
meta = scipy.io.loadmat('{}/devkit-1.0/data/meta.mat'.format(args.dataset))
synsets = meta['synsets']
for i,s in enumerate(synsets):
    synlabel[s[0][1][0]] = s[0][0][0][0]
    labeltext[s[0][0][0][0]] = s[0][2][0]
print('imagenet metadata loaded')
with open('{}/train/flist'.format(args.dataset), 'r') as f:
    train_flist = f.readlines()
print('imagenet training flist loaded',len(train_flist))
train_label = [synlabel[fn[0:9]] for fn in train_flist]
print('imagenet training labels loaded',len(train_label))
with open('{}/val/flist'.format(args.dataset), 'r') as f:
    val_flist = f.readlines()
print('imagenet flist loaded - VALIDATION DISTRIBUTION',len(val_flist))
with open('{}/devkit-1.0/data/ILSVRC2010_validation_ground_truth.txt'.format(args.dataset), 'r') as f:
    val_label = [int(line) for line in f.readlines()]
print('imagenet labels loaded - VALIDATION DISTRIBUTION',len(val_label))

def sample_img(dist='train'):
    # return center-cropped image from {train,val} distribution
    if dist=='train':
        flist=train_flist
        label=train_label
    if dist=='val':
        flist=val_flist
        label=val_label
    while True:
        i = np.random.randint(len(flist))
        img = cv2.imread('{}/{}/{}'.format(args.dataset,dist,flist[i].rstrip()))
        if img is not None:
            # center crop
            side = min(img.shape[0],img.shape[1])
            img = img[img.shape[0]//2-side//2:img.shape[0]//2+side//2,img.shape[1]//2-side//2:img.shape[1]//2+side//2]
            break
    return img,label[i]

def transform_img(img,dmean=0.0,dstd=1.0):
    d = np.divide(img,255.)
    d = np.subtract(d,dmean)
    d = np.divide(d,dstd)
    d = np.rollaxis(d,-1,0)
    return d

def worker(stop,q,args,dist,dmean,dstd,roi):
    while not stop.is_set():
        d = np.zeros([args.batch,3,roi,roi],dtype=np.float32)
        dimg=[]
        l = np.zeros([args.batch],dtype=np.int64)
        for i in range(args.batch):
            img,label = sample_img(dist)
            dimg.append(img)
            d[i]=transform_img(cv2.resize(img,dsize=(roi,roi),interpolation=cv2.INTER_CUBIC),dmean,dstd)
            l[i]=label-1
        q.put((d,l))

stop = threading.Event()
stop.clear()
workers=[]

# training distribution
q0 = queue.Queue(maxsize=args.workers)
for _ in range(args.workers):
    w = threading.Thread(target=worker, args=[stop,q0,args,'train',dmean,dstd,roi], daemon=False)
    w.start()
    workers.append(w)

# validation distribution
q1 = queue.Queue(maxsize=args.workers)
for _ in range(args.workers):
    w = threading.Thread(target=worker, args=[stop,q1,args,'val',dmean,dstd,roi], daemon=False)
    w.start()
    workers.append(w)

# --------------------------------------------------------------------------------------------------------------------------
# TRAINING LOOP
# --------------------------------------------------------------------------------------------------------------------------
optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
classify = nn.CrossEntropyLoss() # we will use class indices for softmax loss
i=0
larr=[] # loss
garr=[] # gradient
while i<1+args.nbatch:
    cv2.waitKey(1)
    i+=1
    (x,y)=q0.get()
    if args.show and (i%100)==0:
        img,_ = sample_img('train')
        cv2.imshow('show', cv2.resize(img,dsize=(roi,roi),interpolation=cv2.INTER_CUBIC))
        cv2.waitKey(100)
    x=torch.utils.data.default_convert(x)
    x = x.to(device)
    model.train()
    o = model(x)
    y=torch.utils.data.default_convert(y)
    y = y.to(device)
    loss = classify(o,y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    larr.append(loss.item())
    lavg = np.mean(larr[-args.avg:])

    # compute gradient
    total_norm = 0
    parameters = [p for p in model.parameters() if p.grad is not None and p.requires_grad]
    for p in parameters:
        param_norm = p.grad.detach().data.norm(2)
        total_norm += param_norm.item() ** 2
    total_norm = total_norm ** 0.5

    # print batch statistics
    garr.append(total_norm)
    gavg = np.mean(garr[-args.avg:])
    lr = optimizer.param_groups[0]['lr']
    s = 'BATCH {:12d} wall {} lr {:12.10f} batch {:6d} loss {:12.6f} {:12.6f} grad {:12.6f} {:12.6f}'.format(
        i,datetime.datetime.now(),lr,args.batch,loss.item(),lavg,total_norm,gavg)
    print(s)

# --------------------------------------------------------------------------------------------------------------------------
# VALIDATION DISTRIBUTION ACCURACY
# --------------------------------------------------------------------------------------------------------------------------
model.eval()
aarr=[]
for j in range(50000//args.batch):
    (x0,y0)=q1.get() # draw from q1, the validation distribution
    x=torch.utils.data.default_convert(x0)
    x = x.to(device)
    logits = model(x)
    prob = torch.nn.functional.softmax(logits,dim=-1)
    prob = prob.cpu().detach().numpy()
    pred = np.argmax(prob,axis=-1)
    acc = np.mean(pred==y0)
    aarr.append(acc)
s = 'TOP-1 ACCURACY {:12.6f}'.format(np.mean(aarr))
print(s)

print('STOPPING WORKERS')
stop.set()
for w in workers:
    while not q0.empty():
        q0.get()
    while not q1.empty():
        q1.get()
    w.join()
print('EXIT MAIN')
exit()
