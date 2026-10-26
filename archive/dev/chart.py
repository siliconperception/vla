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

import argparse
import numpy as np ; print('numpy ' + np.__version__)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
#from matplotlib.ticker import MultipleLocator
#from matplotlib.ticker import FuncFormatter
import re

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--head', help='remove first head lines from log',default=0, type=int)
parser.add_argument('--log',help='log file name',default='log')
parser.add_argument('--verbose', default=False, action='store_true')
args = parser.parse_args()
print(args)
batch_size=0

def parselog(fn):
    global batch_size
    f = open(fn,'r')
    a=[]
    while True:
        l = f.readline()
        if not l:
            break
        elif l[0:4] == 'STEP':
            b=[]
            for r in l[4:].split():
                try:
                    b.append(float(r))
                except:
                    b.append(0.0)
                if len(b)==17:
                    break
            a.append(b)
        elif l[0:4] == 'ARGS':
            match = re.search(r"batch=(\d+)", l)
            if match:
                batch_size = int(match.group(1))
    return np.transpose(np.array(a))

print('loading log file')
arr = parselog(args.log)
arr = arr[:,args.head:]
print('arr',arr.shape)
print('batch_size',batch_size)

step=arr[1]
loss=arr[6]
grad=arr[8]
lr=arr[10]
mean=arr[12]
std=arr[14]
ex=arr[16]

#grad = np.clip(grad, 0, 10)

window_size = 10
weights = np.ones(window_size) / window_size
loss_mean = np.convolve(loss, weights, mode='same')

#fig = plt.figure(figsize=(10,40))
plt.style.use('dark_background')
fig = plt.figure()
nplots=4
ax1 = fig.add_subplot(nplots,1,1)
ax2 = fig.add_subplot(nplots,1,2, sharex=ax1)
ax3 = fig.add_subplot(nplots,1,3, sharex=ax1)
ax3b = ax3.twinx()
ax4 = fig.add_subplot(nplots,1,4, sharex=ax1)
ax5 = ax4.twinx()
#ax1.set_ylim(bottom=0, top=np.log(50257))
ax1.set_ylim(bottom=0, top=np.log(256))
ax1.plot(step, loss, '.w', linewidth=0.1,alpha=1.0, markersize=1)
#ax1.plot(step, loss_mean, '-w', linewidth=1,alpha=0.8)
ax1.axhline(y=np.min(loss), color='g', linestyle='-',linewidth=1,label='min')
#ax2.set_ylim(bottom=0, top=20)
ax2.plot(step, grad, '-y', linewidth=2.0,alpha=0.5)
#ax3.set_ylim(bottom=0, top=20)
#ax3b.set_ylim(bottom=-1, top=1)
ax3.plot(step, std, '-r', linewidth=1.0,alpha=0.5)
ax3b.plot(step, mean, '-b', linewidth=1.0,alpha=0.5)
ax4.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.7f'))
ax4.plot(step, lr, '-c', linewidth=2.0,alpha=0.5)
ax5.plot(step, ex, '-m', linewidth=2.0,alpha=0.5)

ax1.set_xlabel('batch')
ax1.set_ylabel('loss', color='w')
ax2.set_xlabel('batch')
ax2.set_ylabel('grad', color='y')
ax3.set_xlabel('batch')
ax3.set_ylabel('std', color='r')
ax3b.set_ylabel('mean', color='b')
ax4.set_xlabel('batch')
ax4.set_ylabel('lr', color='c')
ax5.set_xlabel('batch')
ax5.set_ylabel('examples', color='m')
plt.show()
