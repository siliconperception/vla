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
import torchinfo ; print('torchinfo',torchinfo.__version__)
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
parser.add_argument('--eta_min', help='LR cosint schedule parameter',default=0.00001, type=float)
parser.add_argument('--tmax', help='LR cosint schedule parameter',default=100, type=float)
parser.add_argument('--verbose', help='logging',default=False, action='store_true')
parser.add_argument('--push', help='push encoder model to HF',default=False, action='store_true')
parser.add_argument('--saveinterval', help='push to HF every saveinterval batches',default=100000, type=int)
parser.add_argument('--saveoffset', help='push to HF every saveinterval batches',default=10000, type=int)
parser.add_argument('--loss', help='loss function',default='pdist')
parser.add_argument('--show', help='display batches',default=False, action='store_true')
parser.add_argument('--log', help='log file name',default=None)
parser.add_argument('--nbatch', help='total training batches',default=1000000000000, type=int)
parser.add_argument('--lr', help='initial learning rate',default=0.001, type=float)
parser.add_argument('--device', help='pytorch execution device',default='cuda')
parser.add_argument('--encoder', help='input encoder model name',default=None)
parser.add_argument('--dataset', help='imagenet dataset base directory',default='./dataset')
parser.add_argument('--batch', help='batch size',default=20, type=int)
parser.add_argument('--workers', help='number of threads for batch generation',default=12, type=int)
parser.add_argument('--save', help='output encoder model name',default=None)
parser.add_argument('--avg', help='moving average window for lr and grad',default=100, type=int)
parser.add_argument('--sched', help='LR scheduler type',default='cos')
parser.add_argument('--nesterov', help='SGD param',default=False, action='store_true')
parser.add_argument('--momentum', help='SGD param',default=0.0, type=float)
parser.add_argument('--opt', help='optimizer type',default='adamw')
parser.add_argument('--weight_decay', help='L2 penalty',default=0.0, type=float)
parser.add_argument('--step', help='LR scheduler batches per step',default=100, type=int)
parser.add_argument('--start_factor', help='LR linear schedule parameter',default=1., type=float)
parser.add_argument('--end_factor', help='LR linear schedule parameter',default=1./50, type=float)
parser.add_argument('--total_iters', help='LR linear schedule parameter',default=10, type=float)
parser.add_argument('--seed', help='random seed',default=None, type=int)
args = parser.parse_args()
if args.seed is None:
    random.seed(None) # random seed
    args.seed = random.randint(0,1000000000)
random.seed(args.seed)
args.rng = np.random.default_rng(args.seed)

if args.log is None:
    if not os.path.exists('log'):
        os.makedirs('log')
    args.date = subprocess.check_output(['/usr/bin/date', '+%Y.%m.%d-%H.%M.%S'])
    args.date = args.date.decode("utf-8")
    args.date = args.date.rstrip()
    args.log = 'log/log.{}'.format(args.date)
print(args)
with open(args.log, 'a') as f:
    print('ARGS',args,file=f)

# --------------------------------------------------------------------------------------------------------------------------
resnet18 = timm.create_model('resnet18.a1_in1k', pretrained=True, features_only=True)
for param in resnet18.parameters():
    param.requires_grad = False
resnet18 = resnet18.eval()
print('resnet18 image encoder model loaded')
if args.verbose:
    s=torchinfo.summary(resnet18,col_names=["input_size","output_size","num_params"],input_size=(1,3,224,224))
    print('RESNET-18',s)
    with open(args.log, 'a') as f:
        print('RESNET-18',s,file=f)
resnet18 = resnet18.to(args.device)

data_config = timm.data.resolve_model_data_config(resnet18)
transforms = timm.data.create_transform(**data_config, is_training=False)
dmean = transforms.transforms[-1].mean.numpy()
dstd = transforms.transforms[-1].std.numpy()
print('dmean',dmean,'dstd',dstd)

# --------------------------------------------------------------------------------------------------------------------------
encoder = IE120R() # randomly initialized weights
if args.verbose:
    s=torchinfo.summary(encoder,col_names=["input_size","output_size","num_params"],input_size=(1,3,896,896))
    print('IE120R',s)
    with open(args.log, 'a') as f:
        print('IE120',s,file=f)
encoder = encoder.to(args.device)
 
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

# --------------------------------------------------------------------------------------------------------------------------
def worker(stop,q,args,dist,dmean,dstd,roi):
    while not stop.is_set():
        d = np.zeros([args.batch,3,roi,roi],dtype=np.float32)
        dimg=[]
        for i in range(args.batch):
            img,label = sample_img(dist)
            dimg.append(img)
            d[i]=transform_img(cv2.resize(img,dsize=(roi,roi),interpolation=cv2.INTER_CUBIC),dmean,dstd)
        dref = [transform_img(cv2.resize(img,dsize=(224,224),interpolation=cv2.INTER_CUBIC),dmean,dstd) for img in dimg]
        dref = np.array(dref,dtype=np.float32)
        dref=torch.utils.data.default_convert(dref)
        dref = dref.to(args.device)
        l = resnet18(dref)
        q.put((d,l))

stop = threading.Event()
stop.clear()
workers=[]
roi=896

q0 = queue.Queue(maxsize=args.workers) # training data generator
for _ in range(args.workers):
    w = threading.Thread(target=worker, args=[stop,q0,args,'train',dmean,dstd,roi], daemon=False)
    w.start()
    workers.append(w)
q1 = queue.Queue(maxsize=args.workers) # validation data generator
for _ in range(args.workers):
    w = threading.Thread(target=worker, args=[stop,q1,args,'val',dmean,dstd,roi], daemon=False)
    w.start()
    workers.append(w)

# --------------------------------------------------------------------------------------------------------------------------
model = encoder
if args.verbose:
    s=torchinfo.summary(model,col_names=["input_size","output_size","num_params"],input_size=(1,3,roi,roi))
    print('MODEL',s)
    with open(args.log, 'a') as f:
        print('MODEL',s,file=f)
device = torch.device(args.device)
model = model.to(device)

if args.opt=='adamw':
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr,weight_decay=args.weight_decay)
if args.opt=='sgd':
    optimizer = torch.optim.SGD(model.parameters(), lr=args.lr,momentum=args.momentum, weight_decay=args.weight_decay, nesterov=args.nesterov,dampening=0.0)

abs_loss = torch.nn.L1Loss(reduce='mean')
mse_loss = torch.nn.MSELoss(reduction='mean')
cos_loss = torch.nn.CosineSimilarity(dim=-3)
pdist = nn.PairwiseDistance(p=2,keepdim=True)

if args.sched=='linear':
    scheduler = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=args.start_factor, end_factor=args.end_factor, total_iters=args.total_iters)
if args.sched=='cos':
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.tmax, args.eta_min)
i=0
larr=[] # loss
garr=[] # gradient
aarr=[0] # accuracy
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
    if args.loss=='pdist':
        loss=0
        for j in range(5):
            loss += torch.mean(pdist(torch.flatten(o[j]),torch.flatten(y[j])))
    if args.loss=='mse':
        loss = mse_loss(o[0],y[0])+mse_loss(o[1],y[1])+mse_loss(o[2],y[2])+mse_loss(o[3],y[3])+mse_loss(o[4],y[4])
    if args.loss=='cos':
        loss=0
        for j in range(5):
            loss += torch.mean(torch.acos(cos_loss(o[j],y[j]))/np.pi)
            loss += abs_loss(torch.std(o[j],dim=-3),torch.std(y[j],dim=-3))

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    larr.append(loss.item())
    lavg = np.mean(larr[-args.avg:])
    if (i%args.step)==0:
        scheduler.step()

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
    aavg = np.mean(aarr[-args.avg:])
    s = 'BATCH {:12d} wall {} lr {:12.10f} wd {:12.10f} batch {:6d} loss {:12.6f} {:12.6f} grad {:12.6f} {:12.6f} opt {:15} mse {:12.6f} f4 {:12.6f} {:12.6f} y4 {:12.6f} {:12.6f}'.format(
        i,datetime.datetime.now(),lr,args.weight_decay,args.batch,loss.item(),lavg,total_norm,gavg,args.opt+'_'+args.loss+'_'+args.sched,torch.nn.functional.mse_loss(o[4],y[4]),torch.mean(o[4]),torch.std(o[4]),torch.mean(y[4]),torch.std(y[4]))

    print(s)
    with open(args.log, 'a') as f:
        print(s,file=f)
    
    if args.save is not None and ((i-args.saveoffset)%args.saveinterval)==0:
        torch.save(encoder.state_dict(), '{}'.format(args.save))
        if args.push:
            encoder.save_pretrained('ie120r_{}'.format(siliconperception.__version__))
            #encoder.push_to_hub("siliconperception/IE120R")

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
