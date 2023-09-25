import src.transformer_settings.utils as utils

import numpy as np
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.autograd import Variable

from src.transformer_settings.models import DEVICE,subsequent_mask
from src.transformer_settings.config import max_len, model_path, n_layers


def registerHooks(model,data,params,iterOrder):
    # ** Encoder Hooks **
    model.src_embed[0].register_forward_hook(
        utils.getEmbeddingHook('encoder',data,params,iterOrder))
    
    model.src_embed[1].register_forward_hook(
        utils.getPositionalEncodingHook('encoder',data,params,iterOrder))

    for i in range(n_layers):
        model.encoder.layers[i].self_attn.register_forward_hook(
            utils.getSelfAttentionHook('encoder',data,params,iterOrder,blockOrder=(i+1)))

        model.encoder.layers[i].sublayer[0].norm.register_forward_hook(
            utils.getLayerNormHook('encoder',data,params,iterOrder,blockOrder=(i+1),sublayerOrder=1))

        model.encoder.layers[i].feed_forward.register_forward_hook(
            utils.getFeedForwardHook('encoder',data,params,iterOrder,blockOrder=(i+1)))

        model.encoder.layers[i].sublayer[1].norm.register_forward_hook(
            utils.getLayerNormHook('encoder',data,params,iterOrder,blockOrder=(i+1),sublayerOrder=2))

    # ** Decoder Hooks **
    model.tgt_embed[0].register_forward_hook(
        utils.getEmbeddingHook('decoder',data,params,iterOrder))

    model.tgt_embed[1].register_forward_hook(
        utils.getPositionalEncodingHook('decoder',data,params,iterOrder))

    for i in range(n_layers):
        model.decoder.layers[i].self_attn.register_forward_hook(
            utils.getSelfAttentionHook('decoder',data,params,iterOrder,blockOrder=(i+1)))

        model.decoder.layers[i].sublayer[0].norm.register_forward_hook(
            utils.getLayerNormHook('decoder',data,params,iterOrder,blockOrder=(i+1),sublayerOrder=1))

        model.decoder.layers[i].src_attn.register_forward_hook(
            utils.getCrossAttentionHook(data,params,iterOrder,blockOrder=(i+1)))

        model.decoder.layers[i].sublayer[1].norm.register_forward_hook(
            utils.getLayerNormHook('decoder',data,params,iterOrder,blockOrder=(i+1),sublayerOrder=2))

        model.decoder.layers[i].feed_forward.register_forward_hook(
            utils.getFeedForwardHook('decoder',data,params,iterOrder,blockOrder=(i+1)))

        model.decoder.layers[i].sublayer[2].norm.register_forward_hook(
            utils.getLayerNormHook('decoder',data,params,iterOrder,blockOrder=(i+1),sublayerOrder=3))

    # ** Generator Hook **
    model.generator.proj.register_forward_hook(
        utils.getProjectionHook(data,params,iterOrder))

# def generate_data(sentences,model,sp_eng,sp_chn):
def generate_data(sentence,model,sp_eng,sp_chn):
    # 这里默认 输入 sentence 只包含一个句子/文本, 也即 len(sentences) == 1
    # sentence = sentences[0] 

    # 存储和 encoder 相关的所有数据
    encoder = dict()

    # 存储数据的所有数据的总data
    data = [encoder] 

    # 存储模型的所有必需的参数
    params = {'encoder':[],'decoder':[],'generator':[]}
    
    # 计数器 - 统计当前迭代的轮次/次数
    iterOrder = utils.Counter(-1)

    # 将 model 中所有需要数据的 Moduel 都注册 hook
    registerHooks(model=model, data=data, params=params,iterOrder=iterOrder)

    # encoder-input
    encoder["input"] = sentence 
    # encoder-tokenize
    PAD = sp_eng.pad_id()  # 0
    start_symbol = BOS = sp_eng.bos_id()  # 2
    end_symbol = EOS = sp_eng.eos_id()  # 3
    sentence_tokens = [[BOS] + sp_eng.EncodeAsIds(sentence) + [EOS]]
    encoder["tokenize"] = {
        'input':sentence,
        'pieces':["<BOS>"] + sp_eng.EncodeAsPieces(sentence) + ["<EOS>"],
        'output':sentence_tokens[0],
    }
    src = pad_sequence([torch.LongTensor(np.array(l_)) for l_ in sentence_tokens],
                                batch_first = True, padding_value = PAD).to(DEVICE)
    src_mask = (src != 0).unsqueeze(-2)
    
    with torch.no_grad():
        model.eval()
        # 接下来的部分改写自 batch_greedy_decode(...)
        # encoder inference
        batch_size, src_seq_len = src.size()    # src.shape = [B,T]
        results = [[] for _ in range(batch_size)]   # 每个list里面存储着最后目标句子翻译结果的 vocab index 的表示
        stop_flag = [False for _ in range(batch_size)]  # stop_flag.shape = [B], 每个元素为 boolean;
        count = 0

        # 调用 Transformer 的 .encode 方法, 得到 Encoder 的输出;
        # memory.shape = [B, T, d_model]
        memory = model.encode(src, src_mask)

        # 随着下面for循环的进行, tgt 会逐渐变长, 其每一行表示了一个英文句子的中文 vocab index 表示;
        # tgt.shape = [B, current_time]; current_time表示当前时间步, 
        # 也意味着本次 iteration 会基于当前 current_time 个翻译/预测结果, 以及 Encoder的输出 memory 对每个句子预测下一个时间步的 vocab index 是什么
        tgt = torch.Tensor(batch_size, 1).fill_(start_symbol).type_as(src.data)

        # 这个 for 循环的每一个 iteration 都代表基于 encoder 的输出 和 decoder 在当前时间步的预测 来 预测下一个时间步的 index
        for s in range(max_len):
        # for s in range(2):
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
            # 这里把所有batch里面最后一个时间步的 decode output 输入到 generator 里面产生预测结果
            prob = model.generator(out[:, -1, :])

            # pred.shape = [B]; 没有 keepdim, 也即对最后一个维度求argmax, 返回概率值最大的index
            pred = torch.argmax(prob, dim=-1)

            # 保留每一轮迭代中的预测结果
            # 因为 tutorial 里面 B=1, 所以只取 pred 第一个元素即可
            data[-1]['predict'] = {'token':pred[0].tolist(),'word':sp_chn.decode_ids(pred.tolist())}

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

    # 为 decoder 中的 input node 添加数据
    for idx in range(1,len(data)):
        tokens = data[idx]['embedding']['input']
        # 文本分词结果
        data[idx]['tokenize'] = utils.parse_tokens(tokens=tokens,sp_model=sp_chn)
        data[idx]['input'] = data[idx]['tokenize']['input']
    # results 内保留了每个句子的最终输出结果
    # 因为 tutorial 里面输入只有一句话, 所以 len(results)==1
    return sp_chn.decode_ids(results[0]), data, params

if __name__ == "__main__":
    
    import os
    os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
    path = os.path.abspath(os.path.dirname(__file__)) # ./ = /home/newdisk/ziqin.luo/projects/explainable-transformer/system/server/src/transformer
    path = os.path.join(path,model_path)
    print(f"Path: {path}")
    
    # initialize model
    transformer = utils.initModel(path)
    sp_eng = utils.english_tokenizer_load()
    sp_chn = utils.chinese_tokenizer_load()

    generate_data(sentences=["Why are you so happy ?"], model=transformer,
                    sp_eng=sp_eng,sp_chn=sp_chn)
