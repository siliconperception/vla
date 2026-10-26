import numpy as np
import torch
import torch.nn as nn
import torchinfo
import cv2

import siliconperception ; print('siliconperception',siliconperception.__version__)
from siliconperception.IE120R import IE120R,IE120R_HW
ie120r = IE120R.from_pretrained('siliconperception/IE120R')

roi=896
torchinfo.summary(ie120r, input_size=(1, 3, roi, roi))
ie120r_hw = IE120R_HW(ie120r,E=8,M=23,center=1)
torchinfo.summary(ie120r_hw, input_size=(1, 3, roi, roi))
ie120r_hw = ie120r_hw.to('cpu')

# read JPG
img = cv2.imread('ILSVRC2010_val_00000003.JPEG')
# center crop
side = min(img.shape[0],img.shape[1])
img = img[img.shape[0]//2-side//2:img.shape[0]//2+side//2,img.shape[1]//2-side//2:img.shape[1]//2+side//2]
# resize
img = cv2.resize(img,dsize=(roi,roi),interpolation=cv2.INTER_CUBIC)
# transform
dmean = [0.485,0.456,0.406]
dstd =  [0.229,0.224,0.225]
img = np.divide(img,255.)
img = np.subtract(img,dmean)
img = np.divide(img,dstd)
img = np.rollaxis(img,-1,0)
img = img.astype(np.float32)

#img = np.random.normal(size=[1,3,roi,roi]).astype(np.float32)
print('img',img.shape,img.dtype,'min',img.min(),'max',img.max())
x=torch.utils.data.default_convert(img)

ie120r_hw.write_memh(x,fn_prefix='./memh/')
