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

import torch
import torch.nn as nn
from torch.nn import functional as F
from huggingface_hub import PyTorchModelHubMixin
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import numpy as np
import re
import ast

class CNN_ENCODER(nn.Module): # project token embedding [C] to feature map [H,W,C]
    def __init__(self, n_hidden, n_embd, n_enc, n_dec, context, vocab, alt):
        super().__init__()
        self.alt = alt
        if 'repl' in alt:
            layers = []
            layers.append(nn.Conv2d(n_embd, n_hidden, kernel_size=1, stride=1, padding=0))
            layers.append(nn.Upsample(scale_factor=context, mode='nearest'))
            self.layers = nn.ModuleList(layers)
    def forward(self, x):
        if 'repl' in self.alt:
            for layer in self.layers:
                x = layer(x)
        return x

class CNN_DECODER(nn.Module): # project feature map [H,W,C] to token logits [V]
    def __init__(self, n_hidden, n_embd, n_enc, n_dec, context, vocab, alt):
        super().__init__()
        self.alt = alt
        if 'tree' in alt:
            layers = []
            layers.append(nn.Conv2d(n_hidden, n_dec, kernel_size=3, stride=1, padding=1))
            layers.append(nn.ReLU())
            d = np.ceil(np.log2(context)).astype(int)
            for i in range(d):
                layers.append(nn.Conv2d(n_dec, n_dec, kernel_size=3, stride=2, padding=1))
                layers.append(nn.ReLU())
            layers.append(nn.Conv2d(n_dec, n_embd, kernel_size=1, stride=1, padding=0))
            self.layers = nn.ModuleList(layers)
        elif 'pool' in alt:
            layers = []
            layers.append(nn.Conv2d(n_hidden, n_embd, kernel_size=1, stride=1, padding=0))
            layers.append(nn.AvgPool2d(context))
            self.layers = nn.ModuleList(layers)
    def forward(self, x):
        if 'tree' in self.alt:
            for layer in self.layers:
                x = layer(x)
        elif 'pool' in self.alt:
            for layer in self.layers:
                x = layer(x)
        return x

class CNN_PROJECTOR(nn.Module): # project feature map [H,W,C] to [H,W,C]
    def __init__(self, n_hidden, n_embd, n_enc, n_dec, context, vocab, alt, proj_depth=4, proj_kernel=3):
        super().__init__()
        self.alt = alt
        pad = proj_kernel // 2
        if 'proj' in alt:
            layers = []
            in_ch = 2 * n_hidden  # concatenated context + token encoding
            for i in range(proj_depth):
                layers.append(nn.Conv2d(in_ch, n_hidden, kernel_size=proj_kernel, stride=1, padding=pad))
                layers.append(nn.ReLU())
                in_ch = n_hidden
            self.layers = nn.ModuleList(layers)
        elif 'res' in alt:
            layers = []
            for i in range(int(context*np.sqrt(2))):
                layers.append(nn.Sequential(nn.Conv2d(n_hidden, n_hidden, kernel_size=proj_kernel, stride=1, padding=pad), nn.ReLU()))
            self.last = nn.Conv2d(n_hidden, n_hidden, kernel_size=1, stride=1, padding=0)
            self.layers = nn.ModuleList(layers)
        elif 'deep' in alt:
            layers = []
            for i in range(context*2):
                layers.append(nn.Sequential(nn.Conv2d(n_hidden, n_hidden, kernel_size=proj_kernel, stride=1, padding=pad), nn.ReLU()))
            self.last = nn.Conv2d(n_hidden, n_hidden, kernel_size=1, stride=1, padding=0)
            self.layers = nn.ModuleList(layers)
        elif 'xtra' in alt:
            layers = []
            for i in range(context*2):
                layers.append(nn.Sequential(nn.Conv2d(n_hidden, n_hidden, kernel_size=proj_kernel, stride=1, padding=pad), nn.ReLU()))
            self.last = nn.Conv2d(n_hidden, n_hidden, kernel_size=1, stride=1, padding=0)
            self.layers = nn.ModuleList(layers)
        elif 'wide' in alt:
            layers = []
            in_ch = 2 * n_hidden  # concatenated context + token encoding
            for i in range(proj_depth):
                layers.append(nn.Sequential(nn.Conv2d(in_ch, n_hidden, kernel_size=proj_kernel, stride=1, padding=pad), nn.ReLU()))
                in_ch = n_hidden
            self.layers = nn.ModuleList(layers)
        elif 'fixed' in alt:
            layers = []
            for i in range(context):
                layers.append(nn.Conv2d(n_hidden, n_hidden, kernel_size=proj_kernel, stride=1, padding=pad))
                layers.append(nn.ReLU())
            layers.append(nn.Conv2d(n_hidden, n_hidden, kernel_size=1, stride=1, padding=0)) # linear output
            self.layers = nn.ModuleList(layers)
    def forward(self, x):
        if 'proj' in self.alt:
            for layer in self.layers:
                x = layer(x)
        elif 'res' in self.alt or 'deep' in self.alt:
            for layer in self.layers:
                x = 0.5*x + layer(x)
            x = self.last(x)
        elif 'xtra' in self.alt:
            #x0 = x.clone()
            for layer in self.layers:
                x = 0.5*x + layer(x)
                #x = 0.5*x0 + 0.5*x + layer(x)
                #x = x0 + layer(x)
                #x = 0.5*x + layer(x)
                #x = 0.5*x0 + 0.5*x + layer(x)
            x = self.last(x)
            #del x0
        elif 'wide' in self.alt:
            x = self.layers[0](x)        # first layer: 2*n_hidden -> n_hidden, no residual
            for layer in self.layers[1:]:
                x = 0.5*x + layer(x)    # remaining layers: n_hidden -> n_hidden
        elif 'fixed' in self.alt:
            for layer in self.layers:
                x = layer(x)
        return x

class ByteLevelTokenizer:
    """
    A minimal byte-level tokenizer with only encode() and decode() methods.
    It directly maps input characters to their byte values (0-255) and vice versa.
    """
    def __init__(self):
        # The vocabulary size is fixed to 256 (all possible byte values)
        self.vocab_size = 256
        # We don't need explicit stoi/itos dictionaries as we use built-in methods

    def encode(self, text, add_special_tokens=False) -> list[int]:
        """
        Encodes a string into a list of integer byte values (0-255).

        This assumes standard UTF-8 encoding.
        """
        #print('text', type(text), len(text), text)
        if add_special_tokens==True:
            try:
                text = ast.literal_eval("b'" + text + "'")
            except:
                text = text.encode('utf-8')
        else:
            text = text.encode('utf-8')
        #print('text', type(text), len(text), text)
        return list(text)

    def decode(self, tokens: list[int]) -> str:
        """
        Decodes a list of integer byte values (0-255) back into a string.
        """
        ## Convert the list of integers back into a 'bytes' object,
        ## then decode those bytes into a string.
        return str(chr(tokens[0]))

class CharacterOneHotEmbedding(nn.Module):
    """
    A PyTorch Module that functions as a character-level one-hot functional
    "embedding" layer.

    It converts input tokens (integers in the range 0..255) into one-hot
    vectors of length 256. This is a drop-in replacement for nn.Embedding
    where you require one-hot encoding instead of learned embeddings.
    """
    def __init__(self, num_embeddings=256, embedding_dim=256):
        """
        Initializes the layer.

        Args are kept consistent with nn.Embedding signature for drop-in
        compatibility, but num_embeddings and embedding_dim are fixed at 256
        for ASCII character support.
        """
        super(CharacterOneHotEmbedding, self).__init__()
        if num_embeddings != 256 or embedding_dim != 256:
            raise ValueError(
                "For character one-hot encoding, both num_embeddings and "
                f"embedding_dim must be 256. Got {num_embeddings}, {embedding_dim}."
            )
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim

    def forward(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """
        Processes the input tensor (batch_size, seq_len) into
        one-hot vectors (batch_size, seq_len, 256).

        Args:
            input_tensor: A LongTensor of shape (*, seq_len)
                          containing integer indices (0-255).

        Returns:
            A FloatTensor of shape (*, seq_len, 256) with one-hot vectors.
        """
        # Ensure the input indices are within the valid range
        if input_tensor.max() >= self.num_embeddings or input_tensor.min() < 0:
             raise IndexError("Character indices are out of the 0-255 range.")

        # Use F.one_hot to perform the encoding
        # The input tensor must be of type Long/Int
        #print('input_tensor', input_tensor, type(input_tensor), dir(input_tensor))
        one_hot = F.one_hot(input_tensor.long(), num_classes=self.num_embeddings)

        # Convert the resulting tensor from Long (default for one_hot) to Float
        # so it can be used in subsequent neural network layers (e.g., Linear, Conv)
        return one_hot.float()

class CNN_LM(nn.Module, PyTorchModelHubMixin):
    def __init__(self, n_hidden, n_embd, n_enc, n_dec, context, vocab, alt, proj_depth=4, proj_kernel=3):
        super().__init__()
        self.alt = alt
        self.n_hidden = n_hidden
        self.n_embd = n_embd
        self.n_enc = n_enc
        self.n_dec = n_dec
        self.vocab = vocab
        self.context = context

        self.ctx = torch.zeros([1,self.n_hidden,self.context,self.context])
        self.projector = CNN_PROJECTOR(n_hidden, n_embd, n_enc, n_dec, context, vocab, alt, proj_depth=proj_depth, proj_kernel=proj_kernel)
        if 'dbl' in self.alt:
            self.projector2 = CNN_PROJECTOR(n_hidden, n_embd, n_enc, n_dec, context, vocab, alt, proj_depth=proj_depth, proj_kernel=proj_kernel)
        self.encoder = CNN_ENCODER(n_hidden, n_embd, n_enc, n_dec, context, vocab, alt)
        self.decoder = CNN_DECODER(n_hidden, n_embd, n_enc, n_dec, context, vocab, alt)

        if n_embd==768:
            self.tok_model = AutoModelForCausalLM.from_pretrained('roneneldan/TinyStories-33M')
            self.tokenizer = AutoTokenizer.from_pretrained('EleutherAI/gpt-neo-125M')
            self.embed = self.tok_model.transformer.wte         # 50257->256
            self.lmhead = self.tok_model.lm_head    # 256->50257
        elif n_embd==256 and 'char' in alt:
            self.tokenizer = ByteLevelTokenizer()
            self.embed  = CharacterOneHotEmbedding()
            self.lmhead  = nn.Identity()
        elif n_embd==256:
            self.tok_model = AutoModelForCausalLM.from_pretrained('roneneldan/TinyStories-8M')
            self.tokenizer = AutoTokenizer.from_pretrained('roneneldan/TinyStories-8M')
            self.embed = self.tok_model.transformer.wte         # 50257->256
            self.lmhead = self.tok_model.lm_head    # 256->50257

    def reset(self):
        device = next(self.parameters()).device
        self.ctx = torch.zeros([1, self.n_hidden, self.context, self.context], device=device)
        
    def forward(self, idx, targets=None): # idx and targets are both (B,T) tensor of integers
        tok = self.embed(idx)
        tok = tok.unsqueeze(-1)
        tok = tok.unsqueeze(-1)
        enc = self.encoder(tok)
        use_concat = 'proj' in self.alt or 'wide' in self.alt
        if 'dbl' in self.alt:
            res1 = torch.cat([self.ctx.expand_as(enc), enc], dim=1) if use_concat else torch.add(self.ctx, enc)
            proj = self.projector(res1)
            res2 = torch.cat([proj, enc], dim=1) if use_concat else torch.add(proj, enc)
            proj = self.projector2(res2)
            self.ctx = proj.clone().detach()
        else:
            res = torch.cat([self.ctx.expand_as(enc), enc], dim=1) if use_concat else torch.add(enc, self.ctx)
            proj = self.projector(res)
            self.ctx = proj.clone().detach()

        dec = self.decoder(proj)
        dec = torch.squeeze(dec, dim=(-2, -1))
        logits = self.lmhead(dec)

        if targets is None:
            loss = None
        else:
            loss = F.cross_entropy(logits, targets)
        
        return logits,loss

    def sanitize_for_terminal(self, s: str) -> str:
        """
        Removes non-printable control characters (C0 and C1 sets)
        that might cause issues in a terminal, but keeps regular
        printable characters, including UTF-8 emojis.
        """

        # Define the ranges for C0 and C1 control codes
        # C0: 0x00 to 0x1F (includes NUL, BEL, BS, ESC, etc.)
        # C1: 0x80 to 0x9F (less common, but good practice to remove)

        control_chars = (
            chr(i) for i in range(0x00, 0x20)
        )
        # Note: Newline (\n), carriage return (\r), and tab (\t)
        # are often desired in terminal output, so they are explicitly
        # excluded from the removal set if you want to keep formatting.
        # To remove them, simply include them in the control_chars list.

        # Example to exclude \n, \r, \t:
        chars_to_remove = set(control_chars) - {'\n', '\r', '\t'}

        # Build a translation table mapping unwanted characters to None (which removes them)
        # This approach is generally better than using string.printable as string.printable
        # only includes ASCII characters and would filter out all emojis and non-ASCII text.
        trans_table = {ord(c): None for c in chars_to_remove}

        # For a more comprehensive removal of *all* characters not considered "printable"
        # by the unicode standard, you could use a slightly different approach, but
        # the above targets the specific characters known to disrupt terminals.

        # Use translate to remove the characters
        return s.translate(trans_table)

# --- Example Usage ---
# String with control characters (like null byte \x00, escape \x1b, bell \x07)
# and a UTF-8 emoji
#malicious_string = "Hello\x00 World\x1b[31m! \a Look, an emoji: 😊"
# \x1b[31m is an ANSI color code, often treated as control sequence

# Sanitize the string
#clean_string = sanitize_for_terminal(malicious_string)

#print(f"Original: {repr(malicious_string)}")
#print(f"Cleaned:  {repr(clean_string)}")

# If you also want to specifically handle ANSI escape codes, which are a common
# cause of terminal issues, a dedicated library might be better, or a regex:
    def remove_ansi_escape(self, s):
        # Regex for common ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', s)

    def generate(self, prompt, ntokens=20):
        vis=[]
        tok=[]
        self.eval()
        device = next(self.parameters()).device
        self.reset()

        tok_prompt = self.tokenizer.encode(prompt, add_special_tokens=True)
        #print('tok_prompt', tok_prompt)
        if len(tok_prompt) > 0:
            for idx in tok_prompt:
                logits,_ = self.forward(torch.tensor([idx]).to(device))
        else:
            print('ERROR: zero length prompt')

        for i in range(ntokens):
            probs = F.softmax(logits, dim=-1)
            if torch.isnan(probs).any() or torch.isinf(probs).any() or (probs < 0).any():
                tok.append('X')
                continue
            probs = probs[0]
            idx = torch.multinomial(probs,num_samples=1)
            t = self.tokenizer.decode(idx)
            #t = self.sanitize_for_terminal(t)
            #t = self.remove_ansi_escape(t)
            t = "".join(char for char in t if char.isprintable() or char=='\n' or char=='\t' or char=='\r')
            if idx[0].item()==2:
                tok.append('<START>')
            elif idx[0].item()==3:
                tok.append('<END>')
            else:
                tok.append(t)
            logits,_ = self.forward(idx)
            f = self.ctx.cpu().numpy()
            f = f[0]
            f = np.std(f, axis=0)
            vis.append(f)
        
        return tok, np.array(vis)
