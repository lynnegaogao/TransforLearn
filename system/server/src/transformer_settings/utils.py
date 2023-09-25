import os
import sentencepiece as spm

import math
import numpy as np
import pandas as pd
import torch 
import torch.nn.functional as F

from src.transformer_settings.models import make_model
from src.transformer_settings.config import src_vocab_size, tgt_vocab_size, n_layers, d_model, d_ff, n_heads, d_k, dropout, model_path


class Counter:
    def __init__(self,count=0):
        self.count = count
    def increase(self):
        self.count += 1
    def decrea(self):
        self.count -= 1
    def __eq__(self,other):
        c = other.__class__
        assert c == int
        return self.count == other
    def __ne__(self,other):
        c = other.__class__
        assert c == int 
        return self.count != other
    def __gt__(self,other):
        c = other.__class__
        assert c == int
        return self.count > other
    def __ge__(self,other):
        c = other.__class__
        assert c == int
        return self.count >= other
    def __lt__(self,other):
        c = other.__class__
        assert c == int
        return self.count < other
    def __le__(self,other):
        c = other.__class__
        assert c == int
        return self.count <= other
    def __str__(self):
        return str(self.count)
    __repr__ = __str__

def initModel():
    # initialize the model
    # model = Model()
    print("initializing the model...")
    transformer = make_model(src_vocab_size,tgt_vocab_size,
                            N = n_layers, d_model = d_model, 
                            d_ff = d_ff, h = n_heads,
                            dropout = dropout)
    print(next(transformer.parameters()).device)
    path = os.path.abspath(os.path.dirname(__file__)) # ./ = /home/newdisk/ziqin.luo/projects/explainable-transformer/system/server/src/transformer
    # path_change = os.path.join(path,'models/change_with_NoamOpt_no_LabelSmoothing_model.pth')
    # path1 = os.path.join(path,'models/with_NoamOpt_no_LabelSmoothing_model.pth')
    # content = torch.load(path1)
    path = os.path.join(path,model_path[2:])
    # print(f"Path: {path}")
    # dfList=[]
    # for k in list(torch.load(path).keys()):
    #     dfList.append([k,torch.load(path)[k].detach().cpu().numpy()])
    # df=pd.DataFrame(dfList,columns = ['keys','params'])
    # df.to_json('params.json',orient = 'records')
    # np.savetxt('params.csv',paramsList)
    print("loading the model weights...")
    transformer.load_state_dict(torch.load(path))

    return transformer

def chinese_tokenizer_load():
    print("load Chinese sentence-piece models...")
    sp_chn = spm.SentencePieceProcessor()
    path = os.path.abspath(os.path.dirname(__file__)) # ./ = /home/newdisk/ziqin.luo/projects/explainable-transformer/system/server/src/transformer
    path = os.path.join(path,"sp_models/chn.model")
    sp_chn.Load(path)
    return sp_chn

def english_tokenizer_load():
    print("load English sentence-piece models...")
    sp_eng = spm.SentencePieceProcessor()
    path = os.path.abspath(os.path.dirname(__file__)) # ./ = /home/newdisk/ziqin.luo/projects/explainable-transformer/system/server/src/transformer
    path = os.path.join(path,"sp_models/eng.model")
    sp_eng.Load(path)
    return sp_eng

# 提取 各个 module 中的参数
def extractParamsInEmbedding(module):
    paramsInFunc = []
    for param in module.parameters():
        paramsInFunc.append(param.tolist())
    return paramsInFunc
    # return []

def extractParamsInPE(module):
    return [torch.squeeze(module.pe,0).tolist()]
    # return []

def extractParamsInLN(module):
    return [module.a_2.tolist(),module.b_2.tolist()]

def extractParamsInAttention(module, headNum, d_low):
    paramsInFunc = []
    count = 0
    # 因为 attention 层里面有四个"大"参数
    # 分别是: x->query(WQ), x->key(WK), x->value(WV), 多头输出的组合->最终的输出(WO)
    for param in module.parameters():
        # 这里相当于 weight 和 bias 两两一组, 组成一个长度为 2 的list
        if count%2==0:
            paramsInFunc.append([])
        paramsInFunc[-1].append(param)
        count += 1
    # 此时 paramsInFunc = [[Weight_Q, Bias_Q], [Weight_K, Bias_K], [Weight_V, Bias_V], [Weight_O, Bias_O]]
    # 我们需要将每个"大"的参数拆成每个头的"小"参数,然后按照head来组织这些参数
    Wo,bo = paramsInFunc[-1]
    paramsNewOrganized = [[],[Wo.tolist(),bo.tolist()]] # 将参数从 Tensor 转换为 List
    for _ in range(headNum):
        paramsNewOrganized[0].append([])
    for combination in paramsInFunc[:-1]:   # paramsInFunc[:-1] 为去除掉 WO 后的切片
        W,b = combination
        for h in range(headNum):
            # append [Weigth, Bias] two-variable tuple
            # 这些参数处理输入x时应该用 W*x+b
            paramsNewOrganized[0][h].append([W[(h*d_low):((h+1)*d_low)].tolist(),b[(h*d_low):((h+1)*d_low)].tolist()])  # 将参数从 Tensor 转换为 List 
    return paramsNewOrganized

def extractParamsInFeedForward(module):
    paramsInFunc = []
    count = 0
    for param in module.parameters():
        # 这里相当于 weight 和 bias 两两一组, 组成一个长度为 2 的list
        if count%2==0:
            paramsInFunc.append([])
        paramsInFunc[-1].append(param)
        count += 1
    # paramsInFunc[0][0].size(): torch.Size([1024,256])
    # paramsInFunc[0][1].size(): torch.Size([1024])
    # paramsInFunc[1][0].size(): torch.Size([256,1024])
    # paramsInFunc[1][1].size(): torch.Size([256])
    return paramsInFunc

def extractParamsInProjection(module):
    # Projection 就是一个 Linear
    paramsInFunc = []
    for param in module.parameters():
        paramsInFunc.append(param.tolist())
    # paramsInFunc[0].size(): torch.Size([256,32000])
    # paramsInFunc[1].size(): torch.Size([32000])
    return paramsInFunc
    # return []

# 提取 各个 module 中的数据
def calLinear(x,params):
    '''
    x: 输入 input (形状 [B,T,d_model])
    params: 线性层所包含的参数 ( weight + bias )
    '''
    W,b = params
    # Linear(x) 等价于 W*x+b 
    # Linear(x).size() == [B, T, d_new]
    # x.unsqueeze(-1).size == [B, T, d_model, 1] -> 相当于使得 x 变成多个列向量
    return torch.squeeze(torch.matmul(W,x.unsqueeze(-1)),-1) + b

def extractDataInEmbeddng(x,y,d_model):
    # x.size() = torch.Size([B,T]) = torch.Size([1,T])
    # y.size() = torch.Size([B,T,d_model]) = torch.Size([1,T,d_model])
    return {
        'input':torch.squeeze(x,0).tolist(),
        'coefficient':math.sqrt(d_model), # y = x * coefficient = x * math.sqrt(d_model)
        # 'output':torch.squeeze(y,0).tolist(),
        'output':y.tolist(),
    }

def extractDataInPE(x,y):
    # y = x + Variable(self.pe[:, :x.size(1)], requires_grad=False)
    return {
        'input':torch.squeeze(x,0).tolist(),
        # 'output':torch.squeeze(y,0).tolist(),
        'output':y.tolist(),
    }

def extractDataInAttention(module,xQuery,xKey,xValue,mask,finalOutput):

    extractedData = {
        'input': [
            torch.squeeze(xQuery,0).tolist(),
            torch.squeeze(xKey,0).tolist(),
            torch.squeeze(xValue,0).tolist(),
        ],
        # 'output': torch.squeeze(finalOutput,0).tolist(),
        'output': finalOutput.tolist(),
    }

    if mask is not None:
        # 因为这里 attention 分了多个 head, 所以增加一个轴表示将这个 mask 分配到不同的head上 
        mask = mask.unsqueeze(1)   # mask.shape: [B, 1, T]/[B, T, T] -> [B, 1, 1, T]/[B, 1, T, T], 第二个轴表示对应着 num of head
        # 因为在 tutorial 里面 Batch Size只有一个, 所以 B=1
        mask = torch.squeeze(mask,0)    # 去掉 Batch 维度 [1,1,T]/[1,T,T]

    nbatches = xQuery.size(0)

    # 这里的 zip 打包结果是 [(WQ, query), (WK, key), (Wv, value)]
    # module.linears 有 4个元素, 而(query, key, value)只有3个元素, 所以打包结果只覆盖了module.linears的前三个元素
    query, key, value = [l(x).view(nbatches, -1, module.h, module.d_k).transpose(1, 2)
                            for l, x in zip(module.linears, (xQuery, xKey, xValue))]
    # 这里的 query, key, value 即 Q, K, V矩阵; 形状为 [B, h, T, d_low]
    # 在我们的这个 tutorial 里面也即 [1, n_head, T, d_low]
    query = torch.squeeze(query,0)
    key = torch.squeeze(key,0)
    value = torch.squeeze(value,0)
    # 此后 q,k,v 的形状变为 [h, T, d_low]

    # 保存中间变量: 每个 head 内的 Q, K, V 矩阵
    extractedData['mat_QKV'] = []
    for h in range(module.h):
        extractedData['mat_QKV'].append([])
        # append 当前 head 内的 Q, K ,V 矩阵
        extractedData['mat_QKV'][-1].append(query[h].tolist())
        extractedData['mat_QKV'][-1].append(key[h].tolist())
        extractedData['mat_QKV'][-1].append(value[h].tolist())

    # 保存中间变量: 每个 head 内的 Q * K^\top
    extractedData['Q*KT'] = []
    scores = torch.matmul(query, key.transpose(-2,-1))   # [h, T, T]
    for h in range(module.h):
        # append 当前 head 内的 Q * K^\top
        extractedData['Q*KT'].append(scores[h].tolist())
    
    # 保存中间变量: 各个 head 内共享的系数参数 sqrt(d_low)
    extractedData['coefficient'] = math.sqrt(module.d_k)
    extractedData['d_low'] = module.d_k

    # 保存中间变量: 每个 head 内 (Q * K^\top)/sqrt(d_k)
    scores /= math.sqrt(module.d_k)  # [h, T, T]
    extractedData['Q*KT/coefficient'] = []
    for h in range(module.h):
        # append 当前 head 内的 (Q * K^\top)/sqrt(d_k)
        extractedData['Q*KT/coefficient'].append(scores[h].tolist())
    
    if mask is not None:
        # mask == 0 表明将那些为 PAD 的部分的 attention 权重置为 0
        # mask.size() = [h, 1, T]/[h, T, T]
        scores = scores.masked_fill(mask == 0, -1e9)    # [h, T, T]
        
        # 保存中间变量, mask            
        extractedData['mask'] = mask[0].repeat(mask[0].size()[1],1).tolist() if(mask[0].size()[0]==1) else mask[0].tolist()
        extractedData['after_mask'] = []
        for h in range(module.h):
            # append 当前 head 内经过了 mask 的 (Q * K^\top)/sqrt(d_k)
            extractedData['after_mask'].append(scores[h].tolist())
    
    # 保存中间变量: softmax 的结果
    p_attn = F.softmax(scores, dim=-1)  # [h, T, T]
    extractedData['after_softmax'] = []
    for h in range(module.h):
        # append 当前 head 内 softmax 的结果
        extractedData['after_softmax'].append(p_attn[h].tolist())

    # p_attn.size() = [h, T, T]; value.size() = [h, T, d_low]
    # (p_attn * value).size() = output.size() = [h, T, d_low]
    output = torch.matmul(p_attn, value)
    # 保存中间变量: attention 的输出
    extractedData['attention_output'] = []
    for h in range(module.h):
        # append 当前 head 内 attention 的输出
        extractedData['attention_output'].append(output[h].tolist())
    
    # 保存中间变量: 各个 head 的 attention output 的拼接结果
    extractedData['concatenation'] = output.transpose(0,1).contiguous().view(-1, module.h*module.d_k).tolist()
    
    return extractedData

def extractDataInFeedForward(x,y,params):
    '''
    x: Feed Forward Layer 输入
    y: Feed Forward Layer 输出
    params: 用于计算中间变量所需要的参数
    '''
    intermediateVariable = calLinear(x,params)
    return {
        'input': torch.squeeze(x,0).tolist(),    # 消除 Batch size 那一维度
        'intermediate':torch.squeeze(intermediateVariable,0).tolist(),
        'activation':torch.squeeze(F.relu(intermediateVariable),0).tolist(),
        # 'output': torch.squeeze(y,0).tolist(),
        'output': y.tolist(),
    }

def extractDataInLN(x,y):
    # self.a_2 * (x - mean) / torch.sqrt(std ** 2 + self.eps) + self.b_2
    # print('input.shape',x.shape)
    # print('output.shape',y.shape)
    return {
        'input':torch.squeeze(x,0).tolist(),
        'output':y.tolist(),
        # 'output':torch.squeeze(y,0).tolist(),
        'mean':torch.squeeze(x.mean(-1),0).tolist(),
        'std':torch.squeeze(x.std(-1),0).tolist(),
    }

def extractDataInProj(x,y):
    # F.log_softmax(self.proj(x), dim=-1)
    # generator 里面没有使用 ReLU
    return {
        'input': torch.squeeze(x,0).tolist(),
        'output':torch.squeeze(y,0).tolist(),
    }

# iterOrder 是 Counter 类实例

def getEmbeddingHook(type,data,params,iterOrder):
    assert type in ["encoder","decoder"]
    def hook(module,input,output):
        # embedding 的输入和输出都只有一个参数, 直接提取
        iterOrder.increase()
        x,y = input[0], output[0]
        idx = 0 if (type=='encoder') else -1
        if(type=='decoder'):
            data.append(dict()) # 为本轮迭代的 decoder 数据增添存储容器
        data[idx]['embedding'] = extractDataInEmbeddng(x, y, module.d_model)
        if( type == "encoder" or iterOrder <= 1 ):
            params[type].append(extractParamsInEmbedding(module))
    return hook

def getPositionalEncodingHook(type,data,params,iterOrder):
    assert type in ["encoder","decoder"]
    def hook(module,input,output):
        # Positional Encoding 的输入和输出都只有一个参数, 直接提取
        x,y = input[0], output[0]
        idx = 0 if(type=='encoder') else -1
        data[idx]["PE"] = extractDataInPE(x,y)
        if( type == "encoder" or iterOrder <= 1 ):
            params[type].append(extractParamsInPE(module))
    return hook

def getLayerNormHook(type,data,params,iterOrder,blockOrder,sublayerOrder):
    assert type in ["encoder","decoder"]
    assert blockOrder in range(1,n_layers+1)
    assert sublayerOrder in [1,2,3]
    def hook(module,input,output):
        # Layer Norm 的输入和输出都只有一个参数, 直接提取
        x,y = input[0],output[0]
        idx = 0 if (type=='encoder') else -1
        if (blockOrder == 1 and sublayerOrder == 1): # 最开始的第一个 LayerNorm, 需要首先添加空的数组以作为容器
            data[idx]["LN"] = []
            for _ in range(n_layers):   # 初始化完成后 data[idx]["LN"] == [[],[]]
                data[idx]["LN"].append([])
        data[idx]["LN"][blockOrder-1].append(extractDataInLN(x,y))
        if( type == "encoder" or iterOrder <= 1 ):
            params[type].append(extractParamsInLN(module))
    return hook

def getSelfAttentionHook(type,data,params,iterOrder,blockOrder):
    assert type in ["encoder","decoder"]
    assert blockOrder in range(1,n_layers+1)
    def hook(module,input,output):
        # len(input)==4; len(output)==1;
        xQuery,xKey,xValue,mask = input
        finalOutput = output[0]
        idx = 0 if (type=='encoder') else -1
        if( blockOrder == 1):
            data[idx]["self_attn"] = []
        data[idx]["self_attn"].append(extractDataInAttention(module,xQuery,xKey,xValue,mask,finalOutput))
        if( type == "encoder" or iterOrder <= 1 ):
            params[type].append(extractParamsInAttention(module,n_heads,d_k))
    return hook

def getCrossAttentionHook(data,params,iterOrder,blockOrder):
    assert blockOrder in range(1,n_layers+1)
    def hook(module,input,output):
        xQuery,xKey,xValue,mask = input
        finalOutput = output[0]
        if( blockOrder == 1):
            data[-1]["cross_attn"] = []
        data[-1]["cross_attn"].append(extractDataInAttention(module,xQuery,xKey,xValue,mask,finalOutput))
        if( iterOrder <= 1 ):
            params['decoder'].append(extractParamsInAttention(module,n_heads,d_k))
    return hook

def getFeedForwardHook(type,data,params,iterOrder,blockOrder):
    assert type in ["encoder","decoder"]
    assert blockOrder in range(1,n_layers+1)
    def hook(module,input,output):
        x,y = input[0],output[0]
        paramsInFunc = extractParamsInFeedForward(module)
        idx = 0 if (type=='encoder') else -1
        if( blockOrder == 1):
            data[idx]["feed_forward"] = []
        data[idx]["feed_forward"].append(extractDataInFeedForward(x,y,paramsInFunc[0]))
        if( type == "encoder" or iterOrder <= 1 ):
            # 此时 paramsInFunc 中的参数还是 tensor, 需要处理成 List
            paramsListInFunc = []
            for W,b in paramsInFunc:
                paramsListInFunc.append([W.tolist(),b.tolist()])
            params[type].append(paramsListInFunc)
    return hook

def getProjectionHook(data,params,iterOrder):
    def hook(module,input,output):
        x,y = input[0],output[0]
        data[-1]["linear"]=extractDataInProj(x,y)
        data[-1]["softmax"] = F.log_softmax(y, dim=-1).tolist()
        if( iterOrder <= 1 ):
            params['generator'].append(extractParamsInProjection(module))
    return hook

def parse_tokens(tokens, sp_model):
    '''
    tokens: a list of tokens
    sp_model: a setencepiece model used to encode and decode tokens
    '''
    text = sp_model.decode_ids(tokens)  # 句子文本
    pieces = sp_model.EncodeAsPieces(text)   # 句子分词
    return {
        'input': text,
        'pieces': ["<BOS>"]+ pieces,
        'output':tokens,
    }

def parse_paramsIndex(params, paramsIndex):
    # print('params:',params)
    # print('paramsIndex:',paramsIndex)
    param = params
    for i in paramsIndex:
        param = param[i]
    return param

def set_params(params,newParams):
    params['encoder'] = newParams.get('encoder',[])
    params['decoder'] = newParams.get('decoder',[])
    params['generator'] = newParams.get('generator',[])
