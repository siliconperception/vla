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

import torch ; print('torch', torch.__version__)
import torch.nn as nn
from torch.nn import functional as F
import numpy as np
import torchinfo ; print('torchinfo',torchinfo.__version__)
import argparse
import os
import queue
import threading
import subprocess
import datetime
import models
from datasets import load_dataset # HF
import random
import string
import ftfy
import re

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--clip', help='gradient clipping',default=None, type=float)
parser.add_argument('--streaming', help='use HF streaming datasets',default=False, action='store_true')
parser.add_argument('--context', help='size of context feature map',default=8, type=int)
#parser.add_argument('--superfreeze', help='freeze embed, lmhead, encoder, decoder layers',default=False, action='store_true')
parser.add_argument('--warmup', help='LR schedule param for warmcool',default=1000, type=int)
parser.add_argument('--hold', help='LR schedule param for warmcool',default=40000, type=int)
parser.add_argument('--warmdown', help='LR schedule param for warmcool',default=40000, type=int)
parser.add_argument('--eps', help='',default=1e-08, type=float)
parser.add_argument('--steps', help='number of gradient steps until exit',default=None, type=int)
parser.add_argument('--amsgrad', help='',default=False, action='store_true')
parser.add_argument('--weight_decay', help='',default=0.0, type=float)
parser.add_argument('--batch', help='batch size',default=50, type=int)
parser.add_argument('--learning_rate', help='',default=0.00001, type=float)
parser.add_argument('--alt', help='{repl,lite,proj}-{base,batchnorm}',default='free-jumbo')
parser.add_argument('--proj_depth', help='number of Conv2d+ReLU layers for the proj projector variant',default=4, type=int)
parser.add_argument('--kernel', help='projection kernel size (odd integer)',default=3, type=int)
parser.add_argument('--beta1', help='second adamw moment coefficient',default=0.9, type=float)
parser.add_argument('--beta2', help='second adamw moment coefficient',default=0.999, type=float)
#parser.add_argument('--freeze', help='freeze embed, lmhead layers',default=False, action='store_true')
parser.add_argument('--momentum', help='',default=0, type=float)
parser.add_argument('--nesterov', help='',default=False, action='store_true')
parser.add_argument('--prompt', help='for periodic model generation during training',default='\x03\x03')
parser.add_argument('--generate', help='sample model interval',default=100, type=int)
parser.add_argument('--monitor', help='number of gradient updates before logging',default=10, type=int)
parser.add_argument('--schedule', help='learning rate schedule',default='linear')
parser.add_argument('--start_factor', help='',default=1.0, type=float)
parser.add_argument('--end_factor', help='',default=1.0, type=float)
parser.add_argument('--period', help='learning rate parameter',default=1000, type=int)
#parser.add_argument('--shuffle', help='',default=False, action='store_true')
parser.add_argument('--dataset', help='tiny, c4',default='c4')
parser.add_argument('--opt', help='pytorch optimizer {sgd, adamw}',default='adamw')
parser.add_argument('--device', help='pytorch execution device',default=None)
parser.add_argument('--load', help='load pytorch state dict',default=None)
parser.add_argument('--checkpoint', help='steps between model checkpoints',default=1000, type=int)
parser.add_argument('--save', help='checkpoint file name',default='checkpoint.pt')
parser.add_argument('--n_hidden', help='',default=256, type=int)
parser.add_argument('--n_embd', help='',default=256, type=int)
parser.add_argument('--n_enc', help='',default=256, type=int)
parser.add_argument('--n_dec', help='',default=64, type=int)
parser.add_argument('--vocab', help='',default=256, type=int)
parser.add_argument('--seed', help='random seed',default=None, type=int)
parser.add_argument('--log', help='log file name',default=None)
parser.add_argument('--verbose', help='',default=False, action='store_true')
args = parser.parse_args()

# ------------
# log file
# ------------
if args.log is None:
    if not os.path.exists('log'):
        os.makedirs('log')
    args.date = subprocess.check_output(['/usr/bin/date', '+%Y.%m.%d-%H.%M.%S'])
    args.date = args.date.decode("utf-8")
    args.date = args.date.rstrip()
    args.log = 'log/log.{}'.format(args.date)
if args.device is None:
    args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
if args.seed is None:
    args.seed = int.from_bytes(os.urandom(4), byteorder="big")
    print('seed', args.seed)
print(args)
with open(args.log, 'a') as f:
    print('ARGS',args,file=f)
torch.manual_seed(args.seed)

# DATASET LOADER
if args.dataset=='tiny':
    hf_datasets = [load_dataset('roneneldan/TinyStories', streaming=args.streaming)]
    hf_columns = ['text']
    hf_ratios = [1.0]
elif args.dataset=='web':
    hf_datasets = [load_dataset("Skylion007/openwebtext", streaming=args.streaming)]
    hf_columns = ['text']
    hf_ratios = [1.0]
elif args.dataset=='dolma':
    hf_datasets = [load_dataset("allenai/dolma3_mix-150B-1025", streaming=args.streaming)]
    hf_columns = ['text']
    hf_ratios = [1.0]
elif args.dataset=='c4':
    hf_datasets = [load_dataset("allenai/c4", "en", streaming=args.streaming)]
    hf_columns = ['text']
    hf_ratios = [1.0]
elif args.dataset=='codelion':
    finepdfs = load_dataset("codelion/finepdfs-1B", streaming=args.streaming)
    dclm = load_dataset("codelion/dclm-baseline-1B", streaming=args.streaming)
    fineweb_edu = load_dataset("codelion/fineweb-edu-1B", streaming=args.streaming)
    hf_datasets = [finepdfs, dclm, fineweb_edu]
    hf_columns = ['text','text','text']
    hf_ratios = [0.5, 0.3, 0.2]
elif args.dataset=='mix':
    hf_datasets = [load_dataset('roneneldan/TinyStories', streaming=args.streaming), load_dataset("allenai/c4", "en", streaming=args.streaming)]
    hf_columns = ['text','text']
    hf_ratios = [0.1, 0.9]

model = models.CNN_LM(args.n_hidden, args.n_embd, args.n_enc, args.n_dec, args.context, args.vocab, args.alt, proj_depth=args.proj_depth, proj_kernel=args.kernel)
print('vocab_size', model.tokenizer.vocab_size)
sample_example=''
num_examples=0

def worker(stop,q,hf_datasets,hf_columns,hf_ratios,args):
    epoch=1

    for idx in range(len(hf_datasets)):
        if args.streaming:
            hf_datasets[idx] = hf_datasets[idx].shuffle(buffer_size=1e5, seed=args.seed+epoch)
        else:
            hf_datasets[idx] = hf_datasets[idx].shuffle(seed=args.seed+epoch)
    iters = [iter(ds['train']) for ds in hf_datasets]
    global sample_example
    global num_examples
    e = [[] for _ in range(args.batch)]
    while not stop.is_set():
        for i in range(args.batch):
            while len(e[i]) < 2:
                idx = random.choices(range(len(hf_datasets)), weights=hf_ratios, k=1)[0]
                try:
                    example = next(iters[idx])
                except StopIteration:
                    print('EPOCH', epoch, 'idx', idx)
                    with open(args.log, 'a') as f:
                        print('EPOCH',epoch,'idx',idx,file=f)
                    epoch += 1
                    if args.streaming:
                        hf_datasets[idx] = hf_datasets[idx].shuffle(buffer_size=1e5, seed=args.seed+epoch)
                    else:
                        hf_datasets[idx] = hf_datasets[idx].shuffle(seed=args.seed+epoch)
                    iters[idx] = iter(hf_datasets[idx]['train'])
                    example = next(iters[idx])

                example = example[hf_columns[idx]]
                #example = example.replace("\\'", "'")
                sample_example = 'idx {}:'.format(idx) + str(example)
                sample_example = "".join(char for char in sample_example if char.isprintable() or char=='\n' or char=='\t' or char=='\r')
                sample_example = sample_example.replace('\n', '\\n')
                sample_example = sample_example.replace('\t', '\\t')
                sample_example = sample_example.replace('\r', '\\r')
                example = '\x02' + example + '\x03'
                example = model.tokenizer.encode(example, add_special_tokens=False)
                e[i].extend(example)
                num_examples +=1
        x=[]
        y=[]
        flag=[]
        for i in range(args.batch):
            x.append(e[i][0])
            y.append(e[i][1])
            #print('e[{}][0]={}'.format(i, e[i][0]))
            flag.append(e[i][0] == 0x02) # reset context at the start of each example (\x02)
            e[i] = e[i][1:]
        q.put((x,y, flag))

stop = threading.Event()
stop.clear()
q = queue.Queue(maxsize=args.batch) # training data generator
w = threading.Thread(target=worker, args=[stop,q,hf_datasets,hf_columns,hf_ratios,args], daemon=False)
w.start()

if args.load is not None:
    model.load_state_dict(torch.load(args.load, weights_only=True))

#if args.superfreeze:
#    for param in model.projector.parameters():
#        param.requires_grad = True
#    for param in model.decoder.parameters():
#        param.requires_grad = False
#    for param in model.encoder.parameters():
#        param.requires_grad = False
#    for param in model.embed.parameters():
#        param.requires_grad = False
#    for param in model.lmhead.parameters():
#        param.requires_grad = False
#
#if args.freeze:
#    for param in model.projector.parameters():
#        param.requires_grad = True
#    for param in model.decoder.parameters():
#        param.requires_grad = True
#    for param in model.encoder.parameters():
#        param.requires_grad = True
#    for param in model.embed.parameters():
#        param.requires_grad = False
#    for param in model.lmhead.parameters():
#        param.requires_grad = False

info = torchinfo.summary(model, col_names=["input_size","output_size","num_params"],
    #input_data=[torch.zeros([1,args.n_enc+args.n_hidden,args.context,args.context]), torch.zeros([1],dtype=torch.int32)])
    #input_data=[torch.zeros([1,args.n_hidden,args.context,args.context]), torch.zeros([1],dtype=torch.int32)])
    input_data=[torch.zeros([1],dtype=torch.int32)])
print(info)
with open(args.log, 'a') as f:
    print('TORCHINFO',info,file=f)

model = model.to(args.device)
print(sum(p.numel() for p in model.parameters())/1e6, 'M parameters')

if args.opt=='adamw':
    optimizer = torch.optim.AdamW([
        {'params': model.projector.parameters(), 'lr': args.learning_rate},
        {'params': model.decoder.parameters(), 'lr': args.learning_rate}
        ], lr=args.learning_rate, betas=(args.beta1,args.beta2), weight_decay=args.weight_decay, amsgrad=args.amsgrad, eps=args.eps)
elif args.opt=='sgd':
    optimizer = torch.optim.SGD([
        {'params': model.projector.parameters(), 'lr': args.learning_rate},
        {'params': model.decoder.parameters(), 'lr': args.learning_rate}
        ], lr=args.learning_rate, momentum=args.momentum, nesterov=args.nesterov) # defaults
elif args.opt=='rms':
    optimizer = torch.optim.RMSprop([
        {'params': model.projector.parameters(), 'lr': args.learning_rate},
        {'params': model.decoder.parameters(), 'lr': args.learning_rate}
        ], lr=args.learning_rate, weight_decay=args.weight_decay, momentum=args.momentum)

if args.schedule=='linear':
    scheduler = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=args.start_factor, end_factor=args.end_factor, total_iters=args.period)
elif args.schedule=='warmup':
    scheduler = torch.optim.lr_scheduler.ConstantLR(optimizer, factor=0.01, total_iters=args.period)
elif args.schedule=='cyclic':
    scheduler = torch.optim.lr_scheduler.CyclicLR(optimizer, args.learning_rate*args.start_factor, args.learning_rate, step_size_up=args.period, step_size_down=args.period, mode='triangular', gamma=1.0, scale_fn=None, scale_mode='cycle', cycle_momentum=False, base_momentum=0.0, max_momentum=0.0, last_epoch=-1)
elif args.schedule=='decay':
    warm = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=args.start_factor, end_factor=1.0, total_iters=args.warmup)
    decay = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=1.0, end_factor=args.start_factor, total_iters=args.period)
    scheduler = torch.optim.lr_scheduler.SequentialLR(optimizer, schedulers=[warm, decay], milestones=[args.warmup])
elif args.schedule=='piecewise':
    warm = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=args.start_factor, end_factor=1.0, total_iters=args.warmup)
    decay1 = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=1.0, end_factor=10*args.start_factor, total_iters=args.period)
    decay2 = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=10*args.start_factor, end_factor=args.start_factor, total_iters=args.period)
    scheduler = torch.optim.lr_scheduler.SequentialLR(optimizer, schedulers=[warm, decay1, decay2], milestones=[args.warmup, args.warmup+args.period])

print(args)

larr=[]
garr=[]
i=0
try:
    while True:
        if (i%args.checkpoint)==0:
            torch.save(model.state_dict(),args.save)

        # periodically log a sample from the model
        if (i%args.generate)==0:
            model.eval()
            tok,_ = model.generate(args.prompt, 1000 if 'char' in args.alt else 200)
            #s = ''.join(tok)
            #s = ''.join(char for char in tok if char=='\n' or char in string.printable)
            #s = ''.join(char if char=='\n' or char in string.printable else 'X' for char in tok)
            #s = ''.join(tok).encode('utf-8')
            s = ''.join(tok)
            s = "".join(char for char in s if char.isprintable() or char=='\n' or char=='\t' or char=='\r')
            s = s.replace('\n', '\\n')
            s = s.replace('\t', '\\t')
            s = s.replace('\r', '\\r')
            print('\n', s, '\n')
            with open(args.log, 'a') as f:
                print('\n', s, '\n', file=f)

        # predict (next token, next context) given (current token, current context)
        (x0,y0,f0)=q.get()
        #print('f0', sum(f0), f0)
        x = torch.tensor(x0).to(args.device)
        y = torch.tensor(y0).to(args.device)
        #ctx[f0, :, :, :] = 0 # reset context to zero at start of each example
        model.train()
        logits,loss = model(x, y)
        loss.backward()
        if args.clip is not None:
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=args.clip)
        optimizer.step()
        model.eval()
        _,_ = model(x, y) # compute context using updated model
    
        # monitor loss and gradient
        larr.append(loss.item())
        total_norm = 0
        parameters = [p for p in model.parameters() if p.grad is not None and p.requires_grad]
        for p in parameters:
            param_norm = p.grad.detach().data.norm(2)
            total_norm += param_norm.item() ** 2
        total_norm = total_norm ** 0.5
        garr.append(total_norm)
        if (i%args.monitor)==0:
            s = 'STEP {:10} wall {} loss {:12.9f} grad {:12.6f} lr {:10.9f} mean {:12.6f} std {:12.6f} example {:10} {:.110}'.format(
                i, datetime.datetime.now(), np.mean(larr[-args.monitor:]), np.mean(garr[-args.monitor:]), scheduler.get_last_lr()[0],
                torch.mean(model.ctx).item(), torch.std(model.ctx).item(), num_examples, sample_example)
            print(s)
            with open(args.log, 'a') as f:
                print(s,file=f)

        # LR schedulers
        scheduler.step()

        optimizer.zero_grad()
        i+=1
        if args.steps is not None and i > args.steps:
            break

except KeyboardInterrupt:
    pass

print('\nSTOPPING THREADS')
stop.set()
while not q.empty(): # drain
    q.get()
w.join()
print('EXIT MAIN')

