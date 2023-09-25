import src.transformer_settings.config as config
import numpy as np
# from data_loader import subsequent_mask

import math
import copy
from torch.autograd import Variable

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence

DEVICE = config.device

def subsequent_mask(size):
    """Mask out subsequent positions."""
    # 设定subsequent_mask矩阵的shape
    attn_shape = (1, size, size)

    # 生成一个右上角(不含主对角线)为全1，左下角(含主对角线)为全0的subsequent_mask矩阵
    subsequent_mask = np.triu(np.ones(attn_shape), k=1).astype('uint8')

    # 返回一个右上角(不含主对角线)为全False，左下角(含主对角线)为全True的subsequent_mask矩阵
    return torch.from_numpy(subsequent_mask) == 0

# 计算输入 x 和 目标 target 之间的 KL散度损失, 且使用了 label smoothing
# 不需要深入理解
class LabelSmoothing(nn.Module):
    """Implement label smoothing."""

    def __init__(self, size, padding_idx, smoothing=0.0):
        super(LabelSmoothing, self).__init__()
        self.criterion = nn.KLDivLoss(size_average=False)   # 没有对loss进行reduce
        self.padding_idx = padding_idx
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.size = size
        self.true_dist = None

    def forward(self, x, target):
        assert x.size(1) == self.size
        true_dist = x.data.clone()
        true_dist.fill_(self.smoothing / (self.size - 2)) # 将 true_dist 全部填充为 self.smoothing / (self.size - 2) - 为后续计算 label smoothing 中的 ε/(K-2)
        true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence) # 将 true_dist 中那些正确的类别填充为 1-smoothing
        true_dist[:, self.padding_idx] = 0
        mask = torch.nonzero(target.data == self.padding_idx)
        if mask.dim() > 0:
            true_dist.index_fill_(0, mask.squeeze(), 0.0)
        self.true_dist = true_dist
        return self.criterion(x, Variable(true_dist, requires_grad=False))


# Embedding层, 作用于文本输入进入到 attention 之前
# 输入是 a list of indices, 输出是 the corresponding word embeddings
# 得到的输出的形状是 [T,d_model], T是输入序列的长度
class Embeddings(nn.Module):
    def __init__(self, d_model, vocab):
        super(Embeddings, self).__init__()

        # Embedding层
        self.lut = nn.Embedding(vocab, d_model)
        # self.lut.weight 可以看到 embedding层的参数形式, 它本质上是一个矩阵, 矩阵有 vocab 行 和 d_model 列;
        # 矩阵的每一行表示一个 vocabulary 里的一个 word 所对应的 embedding, 
        # embedding 层的输入是每个分词在vocab中对应的 indices, 而这个indices会用于索引取对应参数矩阵的行数, e.g. embedding(2) 会取 self.lut.weight 的第二个行向量;
        # 而 列数 d_model 表示 每个 分词 所对应的 embedding vector 的维度
        # embedding层的学习本质上就是对于利用 loss 函数得到 gradient, 然后用来更新参数矩阵;

        # Embedding维数
        self.d_model = d_model

    def forward(self, x):
        # 返回x对应的embedding矩阵（需要乘以math.sqrt(d_model)）
        return self.lut(x) * math.sqrt(self.d_model)

# PositionalEncoding - 对位置进行编码;
# Embedding 可以得到一个 embedding vector 序列, 形状为 [T,d_model]; 现在需要加 位置信息 加入到这个序列中, 随后才传递给 attention 层;
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        # 初始化一个size为 max_len(设定的最大长度)×embedding维度 的全零矩阵
        # 来存放所有小于这个长度位置对应的 positional embedding
        pe = torch.zeros(max_len, d_model, device=DEVICE)   # pe.shape = [max_len,d_model]
        # 生成一个位置下标的tensor矩阵(每一行都是一个位置下标)
        """
        形式如：
        tensor([[0.],
                [1.],
                [2.],
                [3.],
                [4.],
                ...])
        """
        position = torch.arange(0., max_len, device=DEVICE).unsqueeze(1)
        # 这里幂运算太多，我们使用exp和log来转换实现公式中pos下面要除以的分母（由于是分母，要注意带负号）
        div_term = torch.exp(torch.arange(0., d_model, 2, device=DEVICE) * -(math.log(10000.0) / d_model))

        # 根据公式，计算各个位置在各embedding维度上的位置纹理值，存放到pe矩阵中
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        # 加1个维度，使得pe维度变为：1×max_len×embedding维度
        # (方便后续与一个batch的句子所有词的embedding批量相加)
        pe = pe.unsqueeze(0)    # pe.shape = [batch_size,max_len,d_model] = [1,max_len,d_model]
        # 将pe矩阵以持久的buffer状态存下(不会作为要训练的参数)
        # nn.Module.register_buffer() 通常用于注册一个不被视为模型参数的buffer, 可以进行持久化
        self.register_buffer('pe', pe)

    def forward(self, x):
        # 将一个batch的句子所有词的embedding与已构建好的positional embeding相加
        # (这里按照该批次数据的最大句子长度来取对应需要的那些positional embedding值)
        # 输入的 x 的形状为 [batch_size, T, d_model]
        # 这里的 x.size(1) 就是 T, 也即是这一个batch里所有的序列中，最长的那个序列的长度
        x = x + Variable(self.pe[:, :x.size(1)], requires_grad=False)
        return self.dropout(x)


# attention func 用于根据输入的 query, key 和 value 来决定输出
# 因为 attention 是在 MultiHeadedAttention 里面调用的, 所以这里的 mask 的形状还有一个轴以表示 head
# mask.shape = [B, 1, 1, T]/[B, 1, T, T]
def attention(query, key, value, mask=None, dropout=None):
    # query.shape = key.shape = value.shape = [B, h, T, d_k], 其中 h*d_k == d_model

    # 将query矩阵的最后一个维度值作为d_k
    d_k = query.size(-1)

    # 将key的最后两个维度互换(转置)，才能与query矩阵相乘，乘完了还要除以d_k开根号
    # key.transpose(-2, -1).shape = [B, h, d_k, T]
    # scores = Q * K^\top / sqrt(d_k) ; scores.shape = [B, h, T, d_k] * [B, h, d_k, T] = [B, h, T, T]
    # 虽然这里 query 和 key 都有 4 个轴, shape = [B, h, T, d_k] 但是可以直接使用 torch.matmul
    # 因为 torch.matmul 自动作用于最后两个轴
    scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k)
    # scores.shape = [B, h, T, T]

    # 这里的 mask 的作用是屏蔽一个句子里面的某些部分，使得被屏蔽部分的 attention 权重为 0;
    # 如果存在要进行mask的内容，则将那些为0的部分替换成一个很大的负数
    if mask is not None:
        # mask == 0 表明将那些为 PAD 的部分的 attention 权重置为 0 
        scores = scores.masked_fill(mask == 0, -1e9)

    # 将mask后的attention矩阵按照最后一个维度进行softmax
    p_attn = F.softmax(scores, dim=-1)

    # 如果dropout参数设置为非空，则进行dropout操作
    if dropout is not None:
        p_attn = dropout(p_attn)
    
    # torch.matmul(p_attn, value).shape = [B, h, n_q, n_k] * [B, h, n_k, d_v] = [B, h, n_q, d_v]
    # 对应到 Transformer的情形中, n_q = n_k = T, d_v=d_k 所以 shape = [B, h, T, d_k]
    # 也即每个 query 都对应一个 output;
    # 最后返回注意力矩阵跟value的乘积，以及注意力矩阵
    return torch.matmul(p_attn, value), p_attn


# attention sub-layer — Transformer块中的注意力子层
class MultiHeadedAttention(nn.Module):
    def __init__(self, h, d_model, dropout=0.1):
        super(MultiHeadedAttention, self).__init__()
        # 保证可以整除
        assert d_model % h == 0
        # 得到一个head的attention表示维度
        self.d_k = d_model // h
        # head数量 - 原始版本的 Transformer 是 8 个 head
        self.h = h
        # 定义4个全连接函数，供后续作为WQ，WK，WV矩阵和最后h个多头注意力矩阵concat之后进行变换的矩阵
        # self.linear = [WQ, WK, WV, WO], 这些矩阵(也即全连接层)作用于输入x上, 从而得到 query, key 和 values, 以及最后合并各个头的输出
        # 需要注意的是, 这里 WQ, WK, WV 是把论文中的每一个头的 W_i^Q, W_i^K, W_i^V 合起来形成一个大的全连接层 WQ, WK, WV
        self.linears = clones(nn.Linear(d_model, d_model), 4)   
        self.attn = None    # 存放注意力得分矩阵
        # 定义一个 dropout 正则化层
        self.dropout = nn.Dropout(p=dropout)

    def forward(self, query, key, value, mask=None):
        if mask is not None:
            # 因为这里 attention 分了多个 head, 所以增加一个轴表示将这个 mask 分配到不同的head上 
            # mask.shape: [B, 1, T]/[B, T, T] -> [B, 1, 1, T]/[B, 1, T, T], 第二个轴表示对应着 num of head
            mask = mask.unsqueeze(1)

        # query的第一个维度值为batch size
        # query.shape = [B, T(i.e. n_q), d_model]
        nbatches = query.size(0)

        # 将embedding层乘以WQ，WK，WV矩阵(均为全连接)
        # 并将结果拆成h块，然后将第二个和第三个维度值互换(具体过程见上述解析)
        # 注意,在 Encoder中 query, key, value 都是输入 x, 下面这一步是通过 WQ, WK, WV 将输入 x 映射为 q, k, v
        # 在下一步之前, query.shape = key.shape = value.shape = x.shape = [B, T, d_model]
        query, key, value = [l(x).view(nbatches, -1, self.h, self.d_k).transpose(1, 2)
                             for l, x in zip(self.linears, (query, key, value))]
                             # 这里的 zip 打包结果是 [(WQ, query), (WK, key), (Wv, value)]
                             # self.linears 有 4个元素, 而(query, key, value)只有3个元素, 所以打包结果只覆盖了self.linears的前三个元素
        # 这里输入前维度为 [B, T, d_model];
        # 因为 linear层的输入维度等于输出维度, l(x).shape = [B, T, d_model]
        # 又因为我们还要得到每一个 head 的 query, key, value; 又因为 有 d_model == h*d_k 所以 l(x).view(nbatches, -1, self.h, self.d_k).shape = [B, T, h, d_k]
        # 进一步分析可以知道经过转置后: l(x).view(nbatches, -1, self.h, self.d_k).transpose(1, 2).shape = [B, h, T, d_k]

        # 调用上述定义的attention函数计算得到h个注意力矩阵跟value的乘积，以及注意力矩阵
        # 这里的 query, key, value 均是在低维空间中的 query, key, value; .Size() = [B, h, T, d_k]
        x, self.attn = attention(query, key, value, mask=mask, dropout=self.dropout)

        # 将h个多头注意力矩阵concat起来（注意要先把h变回到第三维的位置）
        # 经过下面的操作后, x.shape -> [B, T, h, d_k] -> [B, T, h*d_k] = [B, T, d_model]
        x = x.transpose(1, 2).contiguous().view(nbatches, -1, self.h * self.d_k)

        # 使用self.linears中构造的最后一个全连接函数来存放变换后的矩阵进行返回
        # self.linears[-1] 对应着矩阵 WO, 将 concatenate 后的结果进行变换, 得到 sublayer 的输出 
        return self.linears[-1](x)


# 输入的形状为 x.shape = [B, T, d_model]
class LayerNorm(nn.Module):
    def __init__(self, features, eps=1e-6): # 这里的 features 实际上也即是对应这 d_model
        super(LayerNorm, self).__init__()
        # 初始化α为全1, 而β为全0
        self.a_2 = nn.Parameter(torch.ones(features))   # α - 学习新分布的标准差
        self.b_2 = nn.Parameter(torch.zeros(features))  # β - 学习新分布的均值
        # 平滑项
        self.eps = eps

    def forward(self, x):   
        # 这里的 LayerNorm 的实现方式是对于每个 batch 内每个 sequence 内的每个 embedding vector 的内部元素做平均;
        # 而非是对于每个 batch 内的 sequence的所有元素做平均;

        # 按最后一个维度计算均值和方差 
        mean = x.mean(-1, keepdim=True) # mean.shape = [B, T, 1]
        std = x.std(-1, keepdim=True)   # std.shape = [B, T, 1]

        # 返回Layer Norm的结果
        return self.a_2 * (x - mean) / torch.sqrt(std ** 2 + self.eps) + self.b_2


# 这个 SublayerConnection 就等价于实现了 残差连接(residual connection) 的功能
class SublayerConnection(nn.Module):
    """
    SublayerConnection的作用就是把Multi-Head Attention和Feed Forward层连在一起
    只不过每一层输出之后都要先做Layer Norm再残差连接
    sublayer是lambda函数
    """
    def __init__(self, size, dropout):
        super(SublayerConnection, self).__init__()
        self.norm = LayerNorm(size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer):
        # 返回Layer Norm和残差连接后结果
        return x + self.dropout(sublayer(self.norm(x)))
        # return self.norm(x + self.dropout(sublayer(x)))


def clones(module, N):
    """克隆模型块，克隆的模型块参数不共享"""
    return nn.ModuleList([copy.deepcopy(module) for _ in range(N)])

# Feed-Forward 子层网络架构 - 本质上就是一个简单的 MLP
class PositionwiseFeedForward(nn.Module):
    # d_ff 是隐藏层的大小, 默认是 2048
    def __init__(self, d_model, d_ff, dropout=0.1):
        super(PositionwiseFeedForward, self).__init__()
        self.w_1 = nn.Linear(d_model, d_ff)
        self.w_2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.w_2(self.dropout(F.relu(self.w_1(x))))

# Transformer 中的 Encoder 部分
class Encoder(nn.Module):
    # layer = EncoderLayer
    # N = 6
    def __init__(self, layer, N):
        super(Encoder, self).__init__()
        # 复制N个encoder layer - 也即 Transformer 的 encoder 块 
        #  原始 Transformer 中 N=6
        self.layers = clones(layer, N)
        # Layer Norm
        self.norm = LayerNorm(layer.size)   # 用于 Encoder的最后输出的 Layer Norm, 可以先省略掉

    def forward(self, x, mask):
        """
        使用循环连续encode N次(这里为6次)
        这里的Eecoderlayer会接收一个对于输入的attention mask处理
        """
        for layer in self.layers:
            x = layer(x, mask)
        return self.norm(x)
        # return x    # 直接返回 x, Layer Norm 都在 SublayerConnection里面完成了

# Transformer 中 Encoder 内的 Transformer块 (其内部包含了 MultiHeadedAttention , Layer Norm, feed_forward)
class EncoderLayer(nn.Module):
    def __init__(self, size, self_attn, feed_forward, dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn = self_attn  # multi-headed attention sublayer = MultiHeadedAttention
        self.feed_forward = feed_forward    # feed-forward sublayer = PositionwiseFeedForward

        # SublayerConnection的作用就是把multi和ffn连在一起 
        # 只不过每一层输出之后都要先做Layer Norm再残差连接
        # 具体来说就是 SublayerConnection 在功能上等价于 residual connection
        # 因为 encoder 内的 Transformer 块中有两次 残差链接, 所以这里是 2
        self.sublayer = clones(SublayerConnection(size, dropout), 2)
        # d_model
        self.size = size

    def forward(self, x, mask):
        # 将embedding层进行Multi head Attention
        # 很显然, encoder内的 第一个 Transformer 块的输入 x 的形状为 [B, T, d_model]
        x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x, mask))
        # 注意到attn得到的结果x直接作为了下一层的输入
        return self.sublayer[1](x, self.feed_forward)

# Transformer 中的 Decoder 部分
class Decoder(nn.Module):
    def __init__(self, layer, N):
        super(Decoder, self).__init__()
        # 复制N个encoder layer
        self.layers = clones(layer, N)
        # Layer Norm
        self.norm = LayerNorm(layer.size)   # 用于 Decoder的最后输出的 Layer Norm, 可以先省略掉

    def forward(self, x, memory, src_mask, tgt_mask):
        """
        使用循环连续decode N次(这里为6次)
        这里的Decoderlayer会接收一个对于输入的attention mask处理
        和一个对输出的attention mask + subsequent mask处理
        """
        for layer in self.layers:
            x = layer(x, memory, src_mask, tgt_mask)
        return self.norm(x)
        # return x

# Transformer 中 Dncoder 内的 Transformer块 (其内部包含了 MultiHeadedAttention(masked) , Layer Norm, feed_forward)
class DecoderLayer(nn.Module):
    def __init__(self, size, self_attn, src_attn, feed_forward, dropout):
        super(DecoderLayer, self).__init__()
        self.size = size
        # Self-Attention
        self.self_attn = self_attn
        # 与Encoder传入的Context进行Attention
        self.src_attn = src_attn
        self.feed_forward = feed_forward
        # masked
        self.sublayer = clones(SublayerConnection(size, dropout), 3)

    def forward(self, x, memory, src_mask, tgt_mask):
        # 用m来存放encoder的最终hidden表示结果
        m = memory

        # Self-Attention：注意 self-attention 的 q，k 和 v 均为 decoder hidden
        # 这一层的输入 x 是 Decoder 的输入 (该 x 涉及到 attention mask 以及 sequence mask)
        # tgt_mask.shape = [B, 1, T, T]; 呈下三角状, 其作用是 mask 掉 query 访问当前时间步以后的 key
        x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x, tgt_mask))

        # Context-Attention：注意context-attention的q为decoder hidden，而k和v为encoder hidden
        # 这一层的输入为 x 和 encoder 的 output;
        # src_mask.shape = [B, 1, 1, T]; 其反映了一个batch里面每个sequence的哪些部分是有效index, 哪些部分是 pad index; 
        # 并且针对 PAD 位置的 query
        x = self.sublayer[1](x, lambda x: self.src_attn(x, m, m, src_mask))

        return self.sublayer[2](x, self.feed_forward)


class Transformer(nn.Module):
    def __init__(self, encoder, decoder, src_embed, tgt_embed, generator):
        super(Transformer, self).__init__()
        self.encoder = encoder  # 表示 Transformer 中的整个 Encoder 部分
        self.decoder = decoder  # 表示 Transformer 中的整个 Dncoder 部分
        self.src_embed = src_embed  # 表示 源语言(English) 输入的 embedding layer
        self.tgt_embed = tgt_embed  # 表示 目标语言(Chinese) 输入的 embedding layer
        self.generator = generator

    def encode(self, src, src_mask):
        # src 是源语言的只含有 indices 的表示形式 [B,T]
        # self.src_embed(src) 的结果则是 一个 batch 里源语言已经转变为 embedding vector 的形式 [B, T, d_model]
        return self.encoder(self.src_embed(src), src_mask)

    def decode(self, memory, src_mask, tgt, tgt_mask):
        # self.src_embed(src) 的结果则是 一个 batch 里源语言已经转变为 embedding vector 的形式 [B, T, d_model]
        return self.decoder(self.tgt_embed(tgt), memory, src_mask, tgt_mask)

    # src_mask 只用来识别 encoder 输入的 src 中那些不是 pad 的部分 — shape = [B, 1, T]
    # tgt_mask 既要识别 decoder 输入的 tgt 中那些不是 pad 的部分, 又要识别当前时刻是多少, 从而生成相应的mask — shape = [B, T, T]
    # 详解请看 data_loader.py 中的 class Batch
    def forward(self, src, tgt, src_mask, tgt_mask):
        # encoder的结果作为decoder的memory参数传入，进行decode
        return self.decode(self.encode(src, src_mask), src_mask, tgt, tgt_mask)


# Generator 对应着 原 paper 里的, -> linear -> Softmax -> probs 的部分;
class Generator(nn.Module):
    # vocab: tgt_vocab
    def __init__(self, d_model, vocab):
        super(Generator, self).__init__()
        # decode后的结果，先进入一个全连接层变为词典大小的向量
        self.proj = nn.Linear(d_model, vocab)

    def forward(self, x):
        # 然后再进行log_softmax操作(在softmax结果上再做多一次log运算)
        return F.log_softmax(self.proj(x), dim=-1)

# 初始化模型
def make_model(src_vocab, tgt_vocab, N=6, d_model=512, d_ff=2048, h=8, dropout=0.1):
    """
    src_vocab:  源语言的词表大小
    tgt_vocab:  目标语言的词表大小
    N:  transformer块的个数
    d_model:    每个word的embedding的维数
    d_ff:   Feed-Forward 中间隐层的大小
    h:      head的个数
    dropout:    丢弃概率
    """

    c = copy.deepcopy

    # 实例化Attention对象
    # 输入形状: [B, T, d_model];  输出形状: [B, T, d_model]
    attn = MultiHeadedAttention(h, d_model).to(DEVICE)

    # 实例化FeedForward对象
    # 输入形状: [B, T, d_model];  输出形状: [B, T, d_model]
    ff = PositionwiseFeedForward(d_model, d_ff, dropout).to(DEVICE)

    # 实例化PositionalEncoding对象
    # 输入形状: [B, T, d_model];  输出形状: [B, T, d_model]
    position = PositionalEncoding(d_model, dropout).to(DEVICE)

    # 实例化Transformer模型对象
    # model = Transformer(encoder, decoder, src_embed, tgt_embed, generator)
    model = Transformer(
        Encoder(EncoderLayer(d_model, c(attn), c(ff), dropout).to(DEVICE), N).to(DEVICE),   # Encoder
        Decoder(DecoderLayer(d_model, c(attn), c(attn), c(ff), dropout).to(DEVICE), N).to(DEVICE),  # Decoder
        nn.Sequential(Embeddings(d_model, src_vocab).to(DEVICE), c(position)),  # src_embed
        nn.Sequential(Embeddings(d_model, tgt_vocab).to(DEVICE), c(position)),  # tgt_embed
        Generator(d_model, tgt_vocab)).to(DEVICE)   # generator

    # This was important from their code.
    # Initialize parameters with Glorot / fan_avg.
    # 遍历模型的每一部分的参数并进行初始化;
    for p in model.parameters():
        if p.dim() > 1:
            # 这里初始化采用的是nn.init.xavier_uniform
            nn.init.xavier_uniform_(p)
    return model.to(DEVICE)


def batch_greedy_decode(model, src, src_mask, max_len=64, start_symbol=2, end_symbol=3):
    # src.shape = [B, T]
    # src_mask.shape = [B, 1, T]
    batch_size, src_seq_len = src.size()

    # results - a list of lists, 总共有 batch size 个 list
    # 每个list里面存储着最后目标句子翻译结果的 vocab index 的表示
    results = [[] for _ in range(batch_size)] 
    
    # stop_flag.shape = [B], 每个元素为 boolean;
    # 其标志了在当前 batch 内的相同index的句子是否翻译完毕; True表示对应句子已翻译完毕, False 则表示还在翻译;
    stop_flag = [False for _ in range(batch_size)]  
    count = 0

    # 调用 Transformer 的 .encode 方法, 得到 Encoder 的输出;
    # memory.shape = [B, T, d_model]
    memory = model.encode(src, src_mask)

    # tgt 初始化时, 每一句话的 第一个 index 是 <BOS>
    tgt = torch.Tensor(batch_size, 1).fill_(start_symbol).type_as(src.data)
    # 随着下面for循环的进行, tgt 会逐渐变长, 其每一行表示了一个英文句子的中文 vocab index 表示;
    # tgt.shape = [B, current_time]; current_time表示当前时间步, 
    # 也意味着本次 iteration 会基于当前 current_time 个翻译/预测结果, 以及 Encoder的输出 memory 对每个句子预测下一个时间步的 vocab index 是什么

    # 这个 for 循环的每一个 iteration 都代表基于 encoder 的输出 和 decoder 在当前时间步的预测 来 预测下一个时间步的 index
    for s in range(max_len):
        # tgt.size(1) = current_time = t
        # Tensor.expand(batch_size,-1,-1) 表示将 维度从 [1,current_time,current_time] 扩充为 [B,current_time,current_time]
        # tgt_mask.shape = [B, t, t]
        tgt_mask = subsequent_mask(tgt.size(1)).expand(batch_size, -1, -1).type_as(src.data)
        
        # 调用 Transformer.decode 方法, 通过输入 Encoder 的输出和 Decoder 本身的预测来得到下一个时间步的 index 预测;
        # memory 为 encoder 的输出, 用于将其传入 decoder 中的 DecoderLayer 的第二个 sublayer 作为 key和value
        # tgt 作为 decoder 已有的预测, 作为下一个时间步预测的输入, 输入到 masked Multi-Headed Attention
        # memory.shape = [B, T, d_model], src_mask.shape = [B, 1, T], tgt.shape = [B, t], tgt_mask.shape = [B, t, t]
        out = model.decode(memory, src_mask, Variable(tgt), Variable(tgt_mask))
        # out.shape = [B, t, d_model]

        # prob.shape = [B, trg_vocab_size]
        prob = model.generator(out[:, -1, :])

        # pred.shape = [B]; 没有 keepdim, 也即对最后一个维度求argmax, 返回概率值最大的index
        pred = torch.argmax(prob, dim=-1)

        # 把这一轮的预测结果和已有的预测结果 tgt 拼接起来, 得到新的预测;
        tgt = torch.cat((tgt, pred.unsqueeze(1)), dim=1)

        # 把本轮每个句子的预测结果转到cpu上, 并转成 ndarray 格式
        pred = pred.cpu().numpy()
        for i in range(batch_size):
            # print(stop_flag[i])
            if stop_flag[i] is False:
                if pred[i] == end_symbol:
                    count += 1
                    stop_flag[i] = True
                else:
                    results[i].append(pred[i].item())
            if count == batch_size:
                break

    # results 内保留了每个句子的最终输出结果
    return results

# 这里用贪心算法来对模型进行预测;
# inference 是没有 target 的, 需要 Transformer 将自己的预测作为 decoder 的输入
def greedy_decode(model, src, src_mask, max_len=64, start_symbol=2, end_symbol=3):
    """传入一个训练好的模型，对指定数据进行预测"""

    """
    model:  已训练好的模型
    src:    源语言的 vocabulary indices 表示
    src_mask:   标记源语言的有效部分
    max_len:    限制预测的最大长度
    start_symbol:   表示句子开始的 token (<BOS>) 在词汇表中的 index
    end_symbol:   表示句子结束的 token (<EOS>) 在词汇表中的 index
    """

    # 先用encoder进行encode
    memory = model.encode(src, src_mask)

    # 初始化预测内容为1×1的tensor，填入开始符('BOS')的id，并将type设置为输入数据类型(LongTensor)
    ys = torch.ones(1, 1).fill_(start_symbol).type_as(src.data)

    # 遍历输出的长度下标 (预测步骤)
    for i in range(max_len - 1):
        # decode得到隐层表示
        out = model.decode(memory,          # memory 表示
                           src_mask,
                           Variable(ys),
                           Variable(subsequent_mask(ys.size(1)).type_as(src.data)))

        # 将隐藏表示转为对词典各词的log_softmax概率分布表示
        prob = model.generator(out[:, -1])

        # 获取当前位置最大概率的预测词id
        _, next_word = torch.max(prob, dim=1)
        next_word = next_word.data[0]
        if next_word == end_symbol:
            break
        # 将当前位置预测的字符id与之前的预测内容拼接起来
        ys = torch.cat([ys,
                        torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=1)
    return ys

def translate(sentences, model, sp_eng, sp_chn):

    PAD = sp_eng.pad_id()  # 0
    BOS = sp_eng.bos_id()  # 2
    EOS = sp_eng.eos_id()  # 3
    sentences_tokens = [[BOS] + sp_eng.EncodeAsIds(sent) + [EOS] for sent in sentences]

    src = pad_sequence([torch.LongTensor(np.array(l_)) for l_ in sentences_tokens],
                                batch_first = True, padding_value = PAD).to(DEVICE)
    with torch.no_grad():
        model.eval()
        src_mask = (src != 0).unsqueeze(-2)
        decode_result = batch_greedy_decode(model, src, src_mask, max_len=config.max_len)
        translation = [sp_chn.decode_ids(_s) for _s in decode_result]
    for idx,trans in enumerate(translation):
        print(f"第 {idx} 句话的翻译情况:")
        print(f"原句子为: {sentences[idx]}") 
        print(f"翻译结果: {trans}\n")
    return translation