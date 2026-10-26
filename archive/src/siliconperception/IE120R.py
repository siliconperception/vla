import numpy as np
import torch
import torch.nn as nn
from huggingface_hub import PyTorchModelHubMixin
from collections import OrderedDict
# PyTorch model for Silicon Perception IE120-R single chip image encoder
# www.siliconperception.com
class IE120R(
    nn.Module,
    PyTorchModelHubMixin, 
    repo_url="https://github.com/siliconperception/devices",
    license="mit",
):
    def __init__(self):
        super().__init__()
        self.layer1  = nn.Sequential(nn.Conv2d(3, 16, kernel_size=3, stride=2, padding=1), nn.BatchNorm2d(16), nn.ReLU())
        self.layer2  = nn.Sequential(nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(16), nn.ReLU())
        self.layer3  = nn.Sequential(nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(16), nn.ReLU())
        self.layer4  = nn.Sequential(nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1), nn.BatchNorm2d(32), nn.ReLU())
        self.layer5  = nn.Sequential(nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(32), nn.ReLU())
        self.layer6  = nn.Sequential(nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(32), nn.ReLU())
        self.layer7  = nn.Sequential(nn.Conv2d(32, 96, kernel_size=3, stride=2, padding=1), nn.BatchNorm2d(96), nn.ReLU())
        self.layer8  = nn.Sequential(nn.Conv2d(96, 96, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(96), nn.ReLU())
        self.layer9  = nn.Sequential(nn.Conv2d(96, 96, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(96), nn.ReLU())
        self.layerf0  = nn.Conv2d(96, 64, kernel_size=1, stride=1, padding=0)
        self.layer10 = nn.Sequential(nn.Conv2d(96, 96, kernel_size=3, stride=2, padding=1), nn.BatchNorm2d(96), nn.ReLU())
        self.layer11 = nn.Sequential(nn.Conv2d(96, 96, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(96), nn.ReLU())
        self.layer12 = nn.Sequential(nn.Conv2d(96, 96, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(96), nn.ReLU())
        self.layerf1  = nn.Conv2d(96, 64, kernel_size=1, stride=1, padding=0)
        self.layer13 = nn.Sequential(nn.Conv2d(96, 192, kernel_size=3, stride=2, padding=1), nn.BatchNorm2d(192), nn.ReLU())
        self.layer14 = nn.Sequential(nn.Conv2d(192, 192, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(192), nn.ReLU())
        self.layer15 = nn.Sequential(nn.Conv2d(192, 192, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(192), nn.ReLU())
        self.layerf2  = nn.Conv2d(192, 128, kernel_size=1, stride=1, padding=0)
        self.layer16 = nn.Sequential(nn.Conv2d(192, 320, kernel_size=3, stride=2, padding=1), nn.BatchNorm2d(320), nn.ReLU())
        self.layer17 = nn.Sequential(nn.Conv2d(320, 320, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(320), nn.ReLU())
        self.layer18 = nn.Sequential(nn.Conv2d(320, 320, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(320), nn.ReLU())
        self.layerf3  = nn.Conv2d(320, 256, kernel_size=1, stride=1, padding=0)
        self.layer19 = nn.Sequential(nn.Conv2d(320, 512, kernel_size=3, stride=2, padding=1), nn.BatchNorm2d(512), nn.ReLU())
        self.layer20 = nn.Sequential(nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(512), nn.ReLU())
        self.layer21 = nn.Sequential(nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1), nn.BatchNorm2d(512), nn.ReLU())
        self.layerf4  = nn.Conv2d(512, 512, kernel_size=1, stride=1, padding=0)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.layer5(out)
        out = self.layer6(out)
        out = self.layer7(out)
        out = self.layer8(out)
        out = self.layer9(out)
        f0 = self.layerf0(out)
        out = self.layer10(out)
        out = self.layer11(out)
        out = self.layer12(out)
        f1 = self.layerf1(out)
        out = self.layer13(out)
        out = self.layer14(out)
        out = self.layer15(out)
        f2 = self.layerf2(out)
        out = self.layer16(out)
        out = self.layer17(out)
        out = self.layer18(out)
        f3 = self.layerf3(out)
        out = self.layer19(out)
        out = self.layer20(out)
        out = self.layer21(out)
        f4 = self.layerf4(out)
        return f0,f1,f2,f3,f4

# create a new PT model 1) 7x7 output only 2) merge batchnorm 3) quantize weights to FP18
# save the new PT model and write .memh files for the weights and bias
class IE120R_HW(nn.Module):
    # M=3,E=4,center=-2
    # M=7,E=8,center=1
    # M=23,E=8,center=1
    def __init__(self,model,M=9,E=8,center=1):
        # merge BN with previous Conv2D, quantize weights to FP18, replace FP32 weights with quantized version
        super().__init__()
        self.merge_batchnorm(model.eval().to('cpu'))
        self.quantize(M,E,center)
        self.dequantize(M,E,center)

    def fuse_conv_and_bn(self,conv,bn):
        fusedconv = torch.nn.Conv2d(conv.in_channels, conv.out_channels, kernel_size=conv.kernel_size, stride=conv.stride, padding=conv.padding, bias=True)
        w_eff = conv.weight.clone()
        b_eff = conv.bias.clone()
        with torch.no_grad():
            for i in range(conv.out_channels):
                w_eff[i,:,:,:] = torch.div(torch.mul(bn.weight[i],w_eff[i,:,:,:]),torch.sqrt(bn.running_var[i]+bn.eps))
                b_eff[i] = torch.add(torch.div(torch.mul(bn.weight[i],torch.sub(b_eff[i],bn.running_mean[i])),torch.sqrt(bn.running_var[i]+bn.eps)),bn.bias[i])
        fusedconv.weight.data = w_eff.data
        fusedconv.bias.data = b_eff.data
        return fusedconv

    def merge_batchnorm(self,model):
        self.layer1 = nn.Sequential(self.fuse_conv_and_bn(model.layer1[0],model.layer1[1]), nn.ReLU())
        self.layer2 = nn.Sequential(self.fuse_conv_and_bn(model.layer2[0],model.layer2[1]), nn.ReLU())
        self.layer3 = nn.Sequential(self.fuse_conv_and_bn(model.layer3[0],model.layer3[1]), nn.ReLU())
        self.layer4 = nn.Sequential(self.fuse_conv_and_bn(model.layer4[0],model.layer4[1]), nn.ReLU())
        self.layer5 = nn.Sequential(self.fuse_conv_and_bn(model.layer5[0],model.layer5[1]), nn.ReLU())
        self.layer6 = nn.Sequential(self.fuse_conv_and_bn(model.layer6[0],model.layer6[1]), nn.ReLU())
        self.layer7 = nn.Sequential(self.fuse_conv_and_bn(model.layer7[0],model.layer7[1]), nn.ReLU())
        self.layer8 = nn.Sequential(self.fuse_conv_and_bn(model.layer8[0],model.layer8[1]), nn.ReLU())
        self.layer9 = nn.Sequential(self.fuse_conv_and_bn(model.layer9[0],model.layer9[1]), nn.ReLU())
        self.layer10 = nn.Sequential(self.fuse_conv_and_bn(model.layer10[0],model.layer10[1]), nn.ReLU())
        self.layer11 = nn.Sequential(self.fuse_conv_and_bn(model.layer11[0],model.layer11[1]), nn.ReLU())
        self.layer12 = nn.Sequential(self.fuse_conv_and_bn(model.layer12[0],model.layer12[1]), nn.ReLU())
        self.layer13 = nn.Sequential(self.fuse_conv_and_bn(model.layer13[0],model.layer13[1]), nn.ReLU())
        self.layer14 = nn.Sequential(self.fuse_conv_and_bn(model.layer14[0],model.layer14[1]), nn.ReLU())
        self.layer15 = nn.Sequential(self.fuse_conv_and_bn(model.layer15[0],model.layer15[1]), nn.ReLU())
        self.layer16 = nn.Sequential(self.fuse_conv_and_bn(model.layer16[0],model.layer16[1]), nn.ReLU())
        self.layer17 = nn.Sequential(self.fuse_conv_and_bn(model.layer17[0],model.layer17[1]), nn.ReLU())
        self.layer18 = nn.Sequential(self.fuse_conv_and_bn(model.layer18[0],model.layer18[1]), nn.ReLU())
        self.layer19 = nn.Sequential(self.fuse_conv_and_bn(model.layer19[0],model.layer19[1]), nn.ReLU())
        self.layer20 = nn.Sequential(self.fuse_conv_and_bn(model.layer20[0],model.layer20[1]), nn.ReLU())
        self.layer21 = nn.Sequential(self.fuse_conv_and_bn(model.layer21[0],model.layer21[1]), nn.ReLU())
        self.layerf4 = model.layerf4

    def fp_quantize(self,x,M,E,center): # float32 -> uint32
        bias = (2**(E-1))-center
        xmin = (1)*2**(1-bias)
        xmax = (1+(1-2**(-M)))*2**(((2**E)-2)-bias)
        if (1+E+M)<32:
            x = x+0.5*xmin*np.sign(x) # round to +-inf
        x = np.maximum(np.abs(x),xmin)*np.sign(x) # clip
        x = np.minimum(np.abs(x),xmax)*np.sign(x) # clip
        x = x.astype(np.float32)
        w = np.frombuffer(x.tobytes(), dtype=np.uint32) # flatten
        s = (w&0x80000000)>>31
        e = (w&0x7f800000)>>23
        e = np.where(e==0,np.zeros(e.shape,dtype=np.uint32),e-127+bias) # handle subnormal zero
        m = (w&0x007fffff)>>(23-M)
        q = (s<<(E+M))|(e<<M)|m
        q = q.reshape(x.shape) # unflatten
        return q

    def fp_dequantize(self,x,M,E,center): # uint32 -> float32
        bias = (2**(E-1))-center
        s = (x&(((2**1)-1)<<(M+E)))>>(M+E)
        e = (x&(((2**E)-1)<<(M)))>>(M)
        m = (x&(((2**M)-1)<<(0)))>>(0)
        e = np.where(e==0,np.zeros(e.shape,dtype=np.uint32),e-bias+127)
        w = (s<<31)|(e<<23)|(m<<(23-M))
        dq = np.frombuffer(w.tobytes(), dtype=np.float32)
        dq = np.copy(dq.reshape(x.shape))
        return dq

    def quantize(self,M,E,center):
        self.weight1 = self.fp_quantize(self.layer1[0].weight.detach().numpy(),M,E,center)
        self.weight2 = self.fp_quantize(self.layer2[0].weight.detach().numpy(),M,E,center)
        self.weight3 = self.fp_quantize(self.layer3[0].weight.detach().numpy(),M,E,center)
        self.weight4 = self.fp_quantize(self.layer4[0].weight.detach().numpy(),M,E,center)
        self.weight5 = self.fp_quantize(self.layer5[0].weight.detach().numpy(),M,E,center)
        self.weight6 = self.fp_quantize(self.layer6[0].weight.detach().numpy(),M,E,center)
        self.weight7 = self.fp_quantize(self.layer7[0].weight.detach().numpy(),M,E,center)
        self.weight8 = self.fp_quantize(self.layer8[0].weight.detach().numpy(),M,E,center)
        self.weight9 = self.fp_quantize(self.layer9[0].weight.detach().numpy(),M,E,center)
        self.weight10 = self.fp_quantize(self.layer10[0].weight.detach().numpy(),M,E,center)
        self.weight11 = self.fp_quantize(self.layer11[0].weight.detach().numpy(),M,E,center)
        self.weight12 = self.fp_quantize(self.layer12[0].weight.detach().numpy(),M,E,center)
        self.weight13 = self.fp_quantize(self.layer13[0].weight.detach().numpy(),M,E,center)
        self.weight14 = self.fp_quantize(self.layer14[0].weight.detach().numpy(),M,E,center)
        self.weight15 = self.fp_quantize(self.layer15[0].weight.detach().numpy(),M,E,center)
        self.weight16 = self.fp_quantize(self.layer16[0].weight.detach().numpy(),M,E,center)
        self.weight17 = self.fp_quantize(self.layer17[0].weight.detach().numpy(),M,E,center)
        self.weight18 = self.fp_quantize(self.layer18[0].weight.detach().numpy(),M,E,center)
        self.weight19 = self.fp_quantize(self.layer19[0].weight.detach().numpy(),M,E,center)
        self.weight20 = self.fp_quantize(self.layer20[0].weight.detach().numpy(),M,E,center)
        self.weight21 = self.fp_quantize(self.layer21[0].weight.detach().numpy(),M,E,center)
        self.weightf4 = self.fp_quantize(self.layerf4.weight.detach().numpy(),M,E,center)

    def dequantize(self,M,E,center):
        self.layer1[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight1,M,E,center))
        self.layer2[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight2,M,E,center))
        self.layer3[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight3,M,E,center))
        self.layer4[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight4,M,E,center))
        self.layer5[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight5,M,E,center))
        self.layer6[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight6,M,E,center))
        self.layer7[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight7,M,E,center))
        self.layer8[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight8,M,E,center))
        self.layer9[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight9,M,E,center))
        self.layer10[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight10,M,E,center))
        self.layer11[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight11,M,E,center))
        self.layer12[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight12,M,E,center))
        self.layer13[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight13,M,E,center))
        self.layer14[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight14,M,E,center))
        self.layer15[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight15,M,E,center))
        self.layer16[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight16,M,E,center))
        self.layer17[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight17,M,E,center))
        self.layer18[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight18,M,E,center))
        self.layer19[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight19,M,E,center))
        self.layer20[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight20,M,E,center))
        self.layer21[0].weight.data = torch.from_numpy(self.fp_dequantize(self.weight21,M,E,center))
        self.layerf4.weight.data = torch.from_numpy(self.fp_dequantize(self.weightf4,M,E,center))

    def write_weight(self,w,fn):
        w = np.moveaxis(w,1,-1) # move ichan to end
        w = w.reshape(w.shape[0],-1) # flatten each ochan
        m=''
        for i in range(w.shape[-1]):
            m+= ''.join(['{:08X}'.format(w[ii,i]) for ii in range(w.shape[0]-1,-1,-1)])
            m+='\n'
        with open(fn,'w') as f:
            print(m,file=f)

    def write_bias(self,bias,fn):
        m=''
        for i in range(len(bias)-1,-1,-1):
            b = np.frombuffer(bias[i].tobytes(), dtype=np.uint32)
            m+='{:08X}'.format(b[0])
        with open(fn,'w') as f:
            print(m,file=f)

    def write_activation(self,x,fn):
        x = np.moveaxis(x,0,-1)
        s=''
        for r in range(x.shape[0]):
            for c in range(x.shape[1]):
                s+= ''.join(['{:08X}'.format(np.frombuffer(x[r,c,i].tobytes(),dtype=np.uint32)[0]) for i in range(x.shape[-1])])
                s+='\n'
        with open(fn,'w') as f:
            print(s,file=f)

    def write_input(self,x,fn):
        x = x.cpu().detach().numpy()
        x = np.moveaxis(x,0,-1)
        x = x.reshape(-1,3)
        x = x.flatten()
        b = np.frombuffer(x.tobytes(),dtype=np.uint32) # float32 -> uint32
        b = b.reshape(-1,3)
        m=''
        m=m.join(['{:08X}{:08X}{:08X}\n'.format(t[2],t[1],t[0]) for t in b])
        with open(fn,'w') as f:
            print(m,file=f)

    # evaluate model using input x, then emit .memh files input.memh, layerN.memh
    def write_memh(self,x,fn_prefix):
        print('input',x.shape,x.dtype)
        self.forward(x) # populate intermediate tensors self.layer*
        self.write_input(x,fn_prefix+'input'+'.memh')

        print('weight1',self.weight1.shape,self.weight1.dtype, 'bias1', self.layer1[0].bias.cpu().detach().numpy().shape,self.layer1[0].bias.cpu().detach().numpy().dtype,'activation',self.out1.shape,self.out1.dtype)
        self.write_weight(self.weight1,fn_prefix+'weight1.memh')
        self.write_bias(self.layer1[0].bias.cpu().detach().numpy(),fn_prefix+'bias1.memh')
        self.write_activation(self.out1.cpu().detach().numpy(),fn_prefix+'activation1.memh')
        print('weight2',self.weight2.shape,self.weight2.dtype, 'bias2', self.layer2[0].bias.cpu().detach().numpy().shape,self.layer2[0].bias.cpu().detach().numpy().dtype,'activation',self.out2.shape,self.out2.dtype)
        self.write_weight(self.weight2,fn_prefix+'weight2.memh')
        self.write_bias(self.layer2[0].bias.cpu().detach().numpy(),fn_prefix+'bias2.memh')
        self.write_activation(self.out2.cpu().detach().numpy(),fn_prefix+'activation2.memh')
        print('weight3',self.weight3.shape,self.weight3.dtype, 'bias3', self.layer3[0].bias.cpu().detach().numpy().shape,self.layer3[0].bias.cpu().detach().numpy().dtype,'activation',self.out3.shape,self.out3.dtype)
        self.write_weight(self.weight3,fn_prefix+'weight3.memh')
        self.write_bias(self.layer3[0].bias.cpu().detach().numpy(),fn_prefix+'bias3.memh')
        self.write_activation(self.out3.cpu().detach().numpy(),fn_prefix+'activation3.memh')
        print('weight4',self.weight4.shape,self.weight4.dtype, 'bias4', self.layer4[0].bias.cpu().detach().numpy().shape,self.layer4[0].bias.cpu().detach().numpy().dtype,'activation',self.out4.shape,self.out4.dtype)
        self.write_weight(self.weight4,fn_prefix+'weight4.memh')
        self.write_bias(self.layer4[0].bias.cpu().detach().numpy(),fn_prefix+'bias4.memh')
        self.write_activation(self.out4.cpu().detach().numpy(),fn_prefix+'activation4.memh')
        print('weight5',self.weight5.shape,self.weight5.dtype, 'bias5', self.layer5[0].bias.cpu().detach().numpy().shape,self.layer5[0].bias.cpu().detach().numpy().dtype,'activation',self.out5.shape,self.out5.dtype)
        self.write_weight(self.weight5,fn_prefix+'weight5.memh')
        self.write_bias(self.layer5[0].bias.cpu().detach().numpy(),fn_prefix+'bias5.memh')
        self.write_activation(self.out5.cpu().detach().numpy(),fn_prefix+'activation5.memh')
        print('weight6',self.weight6.shape,self.weight6.dtype, 'bias6', self.layer6[0].bias.cpu().detach().numpy().shape,self.layer6[0].bias.cpu().detach().numpy().dtype,'activation',self.out6.shape,self.out6.dtype)
        self.write_weight(self.weight6,fn_prefix+'weight6.memh')
        self.write_bias(self.layer6[0].bias.cpu().detach().numpy(),fn_prefix+'bias6.memh')
        self.write_activation(self.out6.cpu().detach().numpy(),fn_prefix+'activation6.memh')
        print('weight7',self.weight7.shape,self.weight7.dtype, 'bias7', self.layer7[0].bias.cpu().detach().numpy().shape,self.layer7[0].bias.cpu().detach().numpy().dtype,'activation',self.out7.shape,self.out7.dtype)
        self.write_weight(self.weight7,fn_prefix+'weight7.memh')
        self.write_bias(self.layer7[0].bias.cpu().detach().numpy(),fn_prefix+'bias7.memh')
        self.write_activation(self.out7.cpu().detach().numpy(),fn_prefix+'activation7.memh')
        print('weight8',self.weight8.shape,self.weight8.dtype, 'bias8', self.layer8[0].bias.cpu().detach().numpy().shape,self.layer8[0].bias.cpu().detach().numpy().dtype,'activation',self.out8.shape,self.out8.dtype)
        self.write_weight(self.weight8,fn_prefix+'weight8.memh')
        self.write_bias(self.layer8[0].bias.cpu().detach().numpy(),fn_prefix+'bias8.memh')
        self.write_activation(self.out8.cpu().detach().numpy(),fn_prefix+'activation8.memh')
        print('weight9',self.weight9.shape,self.weight9.dtype, 'bias9', self.layer9[0].bias.cpu().detach().numpy().shape,self.layer9[0].bias.cpu().detach().numpy().dtype,'activation',self.out9.shape,self.out9.dtype)
        self.write_weight(self.weight9,fn_prefix+'weight9.memh')
        self.write_bias(self.layer9[0].bias.cpu().detach().numpy(),fn_prefix+'bias9.memh')
        self.write_activation(self.out9.cpu().detach().numpy(),fn_prefix+'activation9.memh')
        print('weight10',self.weight10.shape,self.weight10.dtype, 'bias10', self.layer10[0].bias.cpu().detach().numpy().shape,self.layer10[0].bias.cpu().detach().numpy().dtype,'activation',self.out10.shape,self.out10.dtype)
        self.write_weight(self.weight10,fn_prefix+'weight10.memh')
        self.write_bias(self.layer10[0].bias.cpu().detach().numpy(),fn_prefix+'bias10.memh')
        self.write_activation(self.out10.cpu().detach().numpy(),fn_prefix+'activation10.memh')
        print('weight11',self.weight11.shape,self.weight11.dtype, 'bias11', self.layer11[0].bias.cpu().detach().numpy().shape,self.layer11[0].bias.cpu().detach().numpy().dtype,'activation',self.out11.shape,self.out11.dtype)
        self.write_weight(self.weight11,fn_prefix+'weight11.memh')
        self.write_bias(self.layer11[0].bias.cpu().detach().numpy(),fn_prefix+'bias11.memh')
        self.write_activation(self.out11.cpu().detach().numpy(),fn_prefix+'activation11.memh')
        print('weight12',self.weight12.shape,self.weight12.dtype, 'bias12', self.layer12[0].bias.cpu().detach().numpy().shape,self.layer12[0].bias.cpu().detach().numpy().dtype,'activation',self.out12.shape,self.out12.dtype)
        self.write_weight(self.weight12,fn_prefix+'weight12.memh')
        self.write_bias(self.layer12[0].bias.cpu().detach().numpy(),fn_prefix+'bias12.memh')
        self.write_activation(self.out12.cpu().detach().numpy(),fn_prefix+'activation12.memh')
        print('weight13',self.weight13.shape,self.weight13.dtype, 'bias13', self.layer13[0].bias.cpu().detach().numpy().shape,self.layer13[0].bias.cpu().detach().numpy().dtype,'activation',self.out13.shape,self.out13.dtype)
        self.write_weight(self.weight13,fn_prefix+'weight13.memh')
        self.write_bias(self.layer13[0].bias.cpu().detach().numpy(),fn_prefix+'bias13.memh')
        self.write_activation(self.out13.cpu().detach().numpy(),fn_prefix+'activation13.memh')
        print('weight14',self.weight14.shape,self.weight14.dtype, 'bias14', self.layer14[0].bias.cpu().detach().numpy().shape,self.layer14[0].bias.cpu().detach().numpy().dtype,'activation',self.out14.shape,self.out14.dtype)
        self.write_weight(self.weight14,fn_prefix+'weight14.memh')
        self.write_bias(self.layer14[0].bias.cpu().detach().numpy(),fn_prefix+'bias14.memh')
        self.write_activation(self.out14.cpu().detach().numpy(),fn_prefix+'activation14.memh')
        print('weight15',self.weight15.shape,self.weight15.dtype, 'bias15', self.layer15[0].bias.cpu().detach().numpy().shape,self.layer15[0].bias.cpu().detach().numpy().dtype,'activation',self.out15.shape,self.out15.dtype)
        self.write_weight(self.weight15,fn_prefix+'weight15.memh')
        self.write_bias(self.layer15[0].bias.cpu().detach().numpy(),fn_prefix+'bias15.memh')
        self.write_activation(self.out15.cpu().detach().numpy(),fn_prefix+'activation15.memh')
        print('weight16',self.weight16.shape,self.weight16.dtype, 'bias16', self.layer16[0].bias.cpu().detach().numpy().shape,self.layer16[0].bias.cpu().detach().numpy().dtype,'activation',self.out16.shape,self.out16.dtype)
        self.write_weight(self.weight16,fn_prefix+'weight16.memh')
        self.write_bias(self.layer16[0].bias.cpu().detach().numpy(),fn_prefix+'bias16.memh')
        self.write_activation(self.out16.cpu().detach().numpy(),fn_prefix+'activation16.memh')
        print('weight17',self.weight17.shape,self.weight17.dtype, 'bias17', self.layer17[0].bias.cpu().detach().numpy().shape,self.layer17[0].bias.cpu().detach().numpy().dtype,'activation',self.out17.shape,self.out17.dtype)
        self.write_weight(self.weight17,fn_prefix+'weight17.memh')
        self.write_bias(self.layer17[0].bias.cpu().detach().numpy(),fn_prefix+'bias17.memh')
        self.write_activation(self.out17.cpu().detach().numpy(),fn_prefix+'activation17.memh')
        print('weight18',self.weight18.shape,self.weight18.dtype, 'bias18', self.layer18[0].bias.cpu().detach().numpy().shape,self.layer18[0].bias.cpu().detach().numpy().dtype,'activation',self.out18.shape,self.out18.dtype)
        self.write_weight(self.weight18,fn_prefix+'weight18.memh')
        self.write_bias(self.layer18[0].bias.cpu().detach().numpy(),fn_prefix+'bias18.memh')
        self.write_activation(self.out18.cpu().detach().numpy(),fn_prefix+'activation18.memh')
        print('weight19',self.weight19.shape,self.weight19.dtype, 'bias19', self.layer19[0].bias.cpu().detach().numpy().shape,self.layer19[0].bias.cpu().detach().numpy().dtype,'activation',self.out19.shape,self.out19.dtype)
        self.write_weight(self.weight19,fn_prefix+'weight19.memh')
        self.write_bias(self.layer19[0].bias.cpu().detach().numpy(),fn_prefix+'bias19.memh')
        self.write_activation(self.out19.cpu().detach().numpy(),fn_prefix+'activation19.memh')
        print('weight20',self.weight20.shape,self.weight20.dtype, 'bias20', self.layer20[0].bias.cpu().detach().numpy().shape,self.layer20[0].bias.cpu().detach().numpy().dtype,'activation',self.out20.shape,self.out20.dtype)
        self.write_weight(self.weight20,fn_prefix+'weight20.memh')
        self.write_bias(self.layer20[0].bias.cpu().detach().numpy(),fn_prefix+'bias20.memh')
        self.write_activation(self.out20.cpu().detach().numpy(),fn_prefix+'activation20.memh')
        print('weight21',self.weight21.shape,self.weight21.dtype, 'bias21', self.layer21[0].bias.cpu().detach().numpy().shape,self.layer21[0].bias.cpu().detach().numpy().dtype,'activation',self.out21.shape,self.out21.dtype)
        self.write_weight(self.weight21,fn_prefix+'weight21.memh')
        self.write_bias(self.layer21[0].bias.cpu().detach().numpy(),fn_prefix+'bias21.memh')
        self.write_activation(self.out21.cpu().detach().numpy(),fn_prefix+'activation21.memh')

        print('weightf4',self.weightf4.shape,self.weightf4.dtype, 'biasf4', self.layerf4.bias.cpu().detach().numpy().shape,self.layerf4.bias.cpu().detach().numpy().dtype,'activation',self.outf4.shape,self.outf4.dtype)
        self.write_weight(self.weightf4,fn_prefix+'weightf4.memh')
        self.write_bias(self.layerf4.bias.cpu().detach().numpy(),fn_prefix+'biasf4.memh')
        self.write_activation(self.outf4.cpu().detach().numpy(),fn_prefix+'activationf4.memh')
        self.write_weight(self.weightf4,fn_prefix+'weight22.memh') # alias
        self.write_bias(self.layerf4.bias.cpu().detach().numpy(),fn_prefix+'bias22.memh')
        self.write_activation(self.outf4.cpu().detach().numpy(),fn_prefix+'activation22.memh')

    def forward(self, x):
        self.out1 = self.layer1(x)
        self.out2 = self.layer2(self.out1)
        self.out3 = self.layer3(self.out2)
        self.out4 = self.layer4(self.out3)
        self.out5 = self.layer5(self.out4)
        self.out6 = self.layer6(self.out5)
        self.out7 = self.layer7(self.out6)
        self.out8 = self.layer8(self.out7)
        self.out9 = self.layer9(self.out8)
        self.out10 = self.layer10(self.out9)
        self.out11 = self.layer11(self.out10)
        self.out12 = self.layer12(self.out11)
        self.out13 = self.layer13(self.out12)
        self.out14 = self.layer14(self.out13)
        self.out15 = self.layer15(self.out14)
        self.out16 = self.layer16(self.out15)
        self.out17 = self.layer17(self.out16)
        self.out18 = self.layer18(self.out17)
        self.out19 = self.layer19(self.out18)
        self.out20 = self.layer20(self.out19)
        self.out21 = self.layer21(self.out20)
        self.outf4 = self.layerf4(self.out21)
        return self.outf4

