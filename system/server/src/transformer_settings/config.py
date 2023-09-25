import torch
import os

# # Normal Transformer
d_model = 512   # 每个 word 的 embedding 的维度
n_heads = 8     # head的个数
n_layers = 6    # transformer block 的个数
# d_k * n_heads = d_model
d_k = 64        # 经过降维映射后的 key 的维度; 
d_v = 64        # 经过降维映射后的 value 的维度;
d_ff = 2048     # 全连接层中隐层的大小
# use normal Transformer
model_path = './models/with_NoamOpt_no_LabelSmoothing_model.pth'


# # Small Transformer
# d_model = 256   # 每个 word 的 embedding 的维度
# n_heads = 4     # head的个数
# n_layers = 2    # transformer block 的个数
# # d_k * n_heads = d_model
# d_k = 64        # 经过降维映射后的 key 的维度; 
# d_v = 64        # 经过降维映射后的 value 的维度;
# d_ff = 1024     # 全连接层中隐层的大小
# # use small Transformer
# model_path = './models/small_with_NoamOpt_no_LabelSmoothing_model.pth'

# Small Transformer with New Architecture
# d_model = 256   # 每个 word 的 embedding 的维度
# n_heads = 4     # head的个数
# n_layers = 2    # transformer block 的个数
# # d_k * n_heads = d_model
# d_k = 64        # 经过降维映射后的 key 的维度; 
# d_v = 64        # 经过降维映射后的 value 的维度;
# d_ff = 1024     # 全连接层中隐层的大小
# # use small Transformer
# model_path = './models/NewArc_small_with_NoamOpt_no_LabelSmoothing_model.pth'

# other configurations
dropout = 0.1   # dropout 概率
padding_idx = 0 # 填充 token 对应在词汇表中的 index
bos_idx = 2     # 句子起始 token 对应在词汇表中的 index
eos_idx = 3     # 句子结束 token 对应在词汇表中的 index
src_vocab_size = 32000  # 源语言 (EN) 词汇表大小
tgt_vocab_size = 32000  # 目标语言 (CN) 词汇表大小
batch_size = 32 # 小批量大小
epoch_num = 35  # 总共训练的 epoch 数
early_stop = 5  # 早停
lr = 3e-4       # 学习率

# greed decode的最大句子长度
max_len = 60
# beam size for bleu
beam_size = 3
# Label Smoothing
use_smoothing = False
# NoamOpt — 动态调整学习率
use_noamopt = True

# Normal Transformer
data_dir = './data'
train_data_path = './data/json/train.json'
# dev_data_path = './data/json/dev.json'
dev_data_path = './data/json/newDev.json'
test_data_path = './data/json/test.json'
# model_path = './experiment/model.pth'


# gpu_id and device id is the relative id
# thus, if you wanna use os.environ['CUDA_VISIBLE_DEVICES'] = '2, 3'
# you should set CUDA_VISIBLE_DEVICES = 2 as main -> gpu_id = '0', device_id = [0, 1]
gpu_id = '0'
# gpu_id = '3'    # 这里告诉系统我们使用第0个gpu 也即是 0号 gpu (来进行 inference);
# device_id = [0, 1, 2, 3]    # 这里列出了用来加速 training 的所有 gpu 编号;
device_id_str = '3'    # 这里列出了用来加速 training 的所有 gpu 编号;
# device_id_str = '2, 3'    # 这里列出了用来加速 training 的所有 gpu 编号;

# torch.cuda.device_count() #返回可用 gpu 数量
# torch.cuda.get_device_name(0)
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
device =torch.device('cuda:0' if torch.cuda.is_available() else 'cpu' )
# set device
# if gpu_id != '':
#     device = torch.device(f"cuda:{gpu_id}")
# else:
#     device = torch.device('cpu')
