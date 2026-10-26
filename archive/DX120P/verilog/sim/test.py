import numpy as np
import torch
import torch.nn as nn
import torchinfo
import siliconperception ; print('siliconperception',siliconperception.__version__)
from siliconperception.DX120P import DX120P,DX120P_HW

dx120p = DX120P()
torchinfo.summary(dx120p, input_size=(1, 512, 112, 112))

dx120p_hw = DX120P_HW(dx120p,E=8,M=23,center=1)
torchinfo.summary(dx120p_hw, input_size=(1, 512, 112, 112))
dx120p_hw = dx120p_hw.to('cpu')

input_data = np.random.normal(size=[512,112,112]).astype(np.float32)
print('input_data',input_data.shape,input_data.dtype,'min',input_data.min(),'max',input_data.max())
x=torch.utils.data.default_convert(input_data)

dx120p_hw.write_memh(x,fn_prefix='./memh/')
