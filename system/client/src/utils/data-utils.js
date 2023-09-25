// 获取访问 data 的 index
export const nodeId2Indices = function (nodeId, curIter) {
  switch (nodeId) {
    // encoder
    case 'encoder-input':
      return [0, 'input'];
    case 'encoder-tokenize':
      return [0, 'tokenize'];
    case 'encoder-embedding':
      return [0, 'embedding'];
    case 'encoder-PE':
      return [0, 'PE'];
    case 'encoder-1-full-self-attention':
      return [0, 'self_attn', 0];
    case 'encoder-1-1-LN':
      return [0, 'LN', 0, 0];
    case 'encoder-1-FF':
      return [0, 'feed_forward', 0];
    case 'encoder-1-2-LN':
      return [0, 'LN', 0, 1];
    case 'encoder-2-full-self-attention':
      return [0, 'self_attn', 1];
    case 'encoder-2-1-LN':
      return [0, 'LN', 1, 0];
    case 'encoder-2-FF':
      return [0, 'feed_forward', 1];
    case 'encoder-2-2-LN':
      return [0, 'LN', 1, 1];
    // decoder
    case 'decoder-input':
      return [curIter, 'input'];
    case 'decoder-tokenize':
      return [curIter, 'tokenize'];
    case 'decoder-embedding':
      return [curIter, 'embedding'];
    case 'decoder-PE':
      return [curIter, 'PE'];
    case 'decoder-1-masked-self-attention':
      return [curIter, 'self_attn', 0];
    case 'decoder-1-1-LN':
      return [curIter, 'LN', 0, 0];
    case 'decoder-1-full-cross-attention':
      return [curIter, 'cross_attn', 0];
    case 'decoder-1-2-LN':
      return [curIter, 'LN', 0, 1];
    case 'decoder-1-FF':
      return [curIter, 'feed_forward', 0];
    case 'decoder-1-3-LN':
      return [curIter, 'LN', 0, 2];
    case 'decoder-2-masked-self-attention':
      return [curIter, 'self_attn', 1];
    case 'decoder-2-1-LN':
      return [curIter, 'LN', 1, 0];
    case 'decoder-2-full-cross-attention':
      return [curIter, 'cross_attn', 1];
    case 'decoder-2-2-LN':
      return [curIter, 'LN', 1, 1];
    case 'decoder-2-FF':
      return [curIter, 'feed_forward', 1];
    case 'decoder-2-3-LN':
      return [curIter, 'LN', 1, 2];
    case 'generator-linear&softmax':
      return [curIter, 'linear_softmax']
    default:  // 剩下的是 add - 直接转到 LayerNorm 的 indices 上  
      // let ids = nodeId.split('-');
      // let prompt = 'Wrong Node Id';
      // console.assert(ids.length == 4, prompt);
      // console.assert(['encoder','decoder'].indexOf(ids[0])>=0, prompt);
      // console.assert(ids[3] == 'add', prompt);
      // ids[3] = 'LN';
      // return nodeId2Indices(ids.join('-'), curIter);
      return [];
  }
}

// 获取访问 params 的 index
export const nodeId2ParamIndices = function (nodeId) {
  let nodeType=nodeId.split('-')[0]
  if(nodeType=='encoder'){
    if(nodeId=='encoder-embedding'){return ['encoder', 0];}
    else if(nodeId=='encoder-PE'){return ['encoder', 1];}
    else{
      for(let i=0;i<6;i++){
        if(nodeId=='encoder-'+(i+1)+'-1-LN'){return ['encoder', 2+4*i];}
        else if(nodeId=='encoder-'+(i+1)+'-full-self-attention'){return ['encoder', 3+4*i];}
        else if(nodeId=='encoder-'+(i+1)+'-2-LN'){return ['encoder', 4+4*i];}
        else if(nodeId=='encoder-'+(i+1)+'-FF'){return ['encoder', 5+4*i];}
      }
    }
  }else if(nodeType=='decoder'){
    if(nodeId=='decoder-embedding'){return ['decoder', 0];}
    else if(nodeId=='decoder-PE'){return ['decoder', 1];}
    else{
      for(let i=0;i<6;i++){
        if(nodeId=='decoder-'+(i+1)+'-1-LN'){return ['decoder', 2+6*i];}
        else if(nodeId=='decoder-'+(i+1)+'-masked-self-attention'){return ['decoder', 3+6*i];}
        else if(nodeId=='decoder-'+(i+1)+'-2-LN'){return ['decoder', 4+6*i];}
        else if(nodeId=='decoder-'+(i+1)+'-full-cross-attention'){return ['decoder', 5+6*i];}
        else if(nodeId=='decoder-'+(i+1)+'-3-LN'){return ['decoder', 6+6*i];}
        else if(nodeId=='decoder-'+(i+1)+'-FF'){return ['decoder', 7+6*i];}
      }
    }
  }else if(nodeType=='generator'){
    if(nodeId=='generator-linear'){return ['generator', 0];}
  }else{return [];}
  // switch (nodeId) {
    // // encoder
    // case 'encoder-embedding':
    //   return ['encoder', 0];
    // case 'encoder-PE':
    //   return ['encoder', 1];
    // case 'encoder-1-full-self-attention':
    //   return ['encoder', 2];
    // case 'encoder-1-1-LN':
    //   return ['encoder', 3];
    // case 'encoder-1-FF':
    //   return ['encoder', 4];
    // case 'encoder-1-2-LN':
    //   return ['encoder', 5];
    // case 'encoder-2-full-self-attention':
    //   return ['encoder', 6];
    // case 'encoder-2-1-LN':
    //   return ['encoder', 7];
    // case 'encoder-2-FF':
    //   return ['encoder', 8];
    // case 'encoder-2-2-LN':
    //   return ['encoder', 9];
    // decoder
    // case 'decoder-embedding':
    //   return ['decoder', 0];
    // case 'decoder-PE':
    //   return ['decoder', 1];
    // case 'decoder-1-masked-self-attention':
    //   return ['decoder', 2];
    // case 'decoder-1-1-LN':
    //   return ['decoder', 3];
    // case 'decoder-1-full-cross-attention':
    //   return ['decoder', 4];
    // case 'decoder-1-2-LN':
    //   return ['decoder', 5];
    // case 'decoder-1-FF':
    //   return ['decoder', 6];
    // case 'decoder-1-3-LN':
    //   return ['decoder', 7];
    // case 'decoder-2-masked-self-attention':
    //   return ['decoder', 8];
    // case 'decoder-2-1-LN':
    //   return ['decoder', 9];
    // case 'decoder-2-full-cross-attention':
    //   return ['decoder', 10];
    // case 'decoder-2-2-LN':
    //   return ['decoder', 11];
    // case 'decoder-2-FF':
    //   return ['decoder', 12];
    // case 'decoder-2-3-LN':
    //   return ['decoder', 13];
    // case 'linear':
    //   return ['generator', 0];
    // default:
    //   return [];
  // }
}

export function parseIndices(nodeIndices, data) {
  for (let idx of nodeIndices) {
    data = data[idx]
  }
  return data;
}
