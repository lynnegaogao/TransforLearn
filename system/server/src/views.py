# views.py 内引用自定义模板需要表明完整的路径(从 src 开始)

import json
import os
import time
from flask_cors import CORS

from src import app
# from src.models import Model # ,make_model
from src.transformer_settings.models import translate # , make_model
from src.transformer_settings.config import device_id_str
from src.transformer_settings.data_generate import generate_data
# from src.transformer_settings.config import src_vocab_size, tgt_vocab_size, n_layers, d_model, d_ff, n_heads, dropout
import src.transformer_settings.utils as utils

from flask import request
import simplejson

CORS(app, supports_credentials=True)

def json_dumps(data):
    # 返回 string 对象, 也即这里把 data 给 JSON 序列化 —— 将一个 Python对象转换为 JSON
    # 参考: https://www.jb51.net/article/212376.htm
    return simplejson.dumps(data, ensure_ascii=False, ignore_nan=True)
# 定义了前端访问后端的接口, 每个接口对应一个路径, 前端会发送请求到相应的路径上, 后端接收到请求后会执行相应的功能

# 当前端只索要数据时,访问方式是get; 当前端还向后端输入数据时, 访问方式为 POST
# 要获取从前端传入的参数 - 使用 request 对象
os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
os.environ['CUDA_VISIBLE_DEVICES'] = device_id_str
transformer = utils.initModel()
sp_eng = utils.english_tokenizer_load()
sp_chn = utils.chinese_tokenizer_load()

# 记录相关数据
inputText = None
translation = None
data = None
params = {}



@app.route('/get')
def get():
    return 'hello world!'


# @app.route('/get_data')
# def get_data():
#     return json_dumps(model.get_data())


@app.route('/post', methods=['POST'])
def post():
    post_data = request.data.decode()
    if post_data != "":
        post_data = simplejson.loads(post_data)
    return json_dumps(post_data)



@app.route('/translate_input_text', methods=['POST'])
def translate_input_text():
    print("******* enter /translate_input_text *******")
    
    # print(request)
    # print("**** enter the translate_input_text() **** ")
    # print(f"request.data.decode(): {request.data.decode()}")
    # print(f"type(request.data.decode()): {type(request.data.decode())}")
    # print(f"request.data.decode()['text']: {request.data.decode()['text']}")
    data_request = json.loads(request.data.decode())    # 将字符串转化为 python 字典
    print(f"data: {data_request}")
    inputText = data_request.get("text","")
    print(f"English Text: {inputText}")

    # translation = translate([text],transformer,sp_eng,sp_chn)
    start = time.time()
    translation, data, parameters = generate_data(sentence=inputText, model=transformer, 
                sp_eng=sp_eng, sp_chn=sp_chn)
    print(f'Translation done. Time consuming : ${time.time()-start}')
    start = time.time()
    res = json_dumps({
        'translation': translation,
        'data': data,
        # 'params': params,
    })
    print('response.translation:',translation)
    print('response.data.length:',len(data))
    print(f'JsonDump done. Time consuming : ${time.time()-start}')
    print('parameters:',parameters.keys())
    utils.set_params(params=params,newParams=parameters)
    return res

@app.route('/getParams', methods=['POST'])
def getParams():
    print("******* enter /getParams *******")
    data_request = json.loads(request.data.decode())    # 将字符串转化为 python 字典
    print(f"data: {data_request}")
    paramIndex = data_request.get("paramIndex","")
    print(f"paramIndex: {paramIndex}")
    param = utils.parse_paramsIndex(params=params, paramsIndex=paramIndex)
    if(len(paramIndex) > 1 and paramIndex[1]==1): # 表示请求的参数的 PE
        sentence_len = data_request.get("sentence_len","")
        res = param[0][:sentence_len]
        print('len(res):',len(res))
        print('len(res[0]):',len(res[0]))
        # print('res:',res)
        return json_dumps({
            'param':res
        })
    # print(f"param: {param}")
    print(f"param.__class__: {param.__class__}")
    # if(paramIndex[0]=="linear"):
    if(len(paramIndex) > 1 and paramIndex[0]=="generator"):
        return json_dumps({
            'param':param[1]
        })
    res =  json_dumps({
        'param':param
    })
    return res