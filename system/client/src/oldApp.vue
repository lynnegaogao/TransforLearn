<template>
<div>
  <div id="translateGroup">
    <a-row :gutter="[2, 2]">
      <a-col :span="8">
        <div class="top_container">
          <div className="chartHeader">Input View</div>
          <cpnInput
            :disableControl = 'disableControl' 
            @cleanComponentView = 'closeIsShowComponentview()'
            @translate="onTranslate"/>
          
        </div>
      </a-col>
      <a-col :span="16">
        <div class="top_container">
          <div className="chartHeader">Translation View</div>
          <cpnTranslation 
            :currentTranslation = 'currentTranslation'
            :fullTranslation = 'fullTranslation'
            :currentPrediction = 'curIterPred'
            :disableControl = 'disableControl'
            @last = 'onLast()'
            @next = 'onNext()'/>
        </div>
      </a-col>
    </a-row>

    <a-row :gutter="[2, 2]">
      <a-col :span="24">
          <div id="mid_container">
            <div className="chartHeader">Architecture View</div>
            <cpnArchitecture
              :componentNodeId="selectedNodeComponentView.id"
              :detailNodeId="selectedNode.id"
              :encoder='data[0]'
              :decoder='data[curIter]'
              :curIter = 'curIter'
              :disableControl = 'disableControl'
              @nodeSelected='onNodeSelectedInArchitecture'></cpnArchitecture>
          </div>
        </a-col>
    </a-row>

    <a-row :gutter="[2, 2]">
      <a-col :span="24">
        <div class="container">
          <div id="bottom_container">
            <div id="pieces" v-if="data.length>0" >
              <div>Encoder Pieces: {{encoderPieces}}</div>
              <div>Decoder Pieces: {{data[curIter].tokenize.pieces}}</div>
            </div>
            <div id="componentDiv" v-if="data.length>0 && isShowComponentview">
              <EmbeddingView v-if="compoentViewType==='embedding'"
                @cleanComponentView = 'closeIsShowComponentview()'
                :tokens = "selectedNodeComponentView.nodeData.tokens"
                :embeddings = "selectedNodeComponentView.nodeData.embeddings"
                :output = "selectedNodeComponentView.nodeData.output"
                :pe = "selectedNodeComponentView.nodeData.pe"
              />
              <SelfAttentionView v-else-if="compoentViewType==='self_attention'"
                @cleanComponentView = 'closeIsShowComponentview()'
                @openHeadDetailView='onOpenHeadDetailView'
                @openAttentionDetailView='onOpenAttentionDetailView'
                @openConcaAndLinearDetailView='onOpenConcaAndLinearDetailView'
                :nodeData = "selectedNodeComponentView.nodeData"
                :nodeParams = "selectedNodeComponentView.nodeParams"
              />
              <CrossAttentionView v-else-if="compoentViewType==='cross_attention'"
                @cleanComponentView = 'closeIsShowComponentview()'
                @openHeadDetailView='onOpenHeadDetailView'
                @openAttentionDetailView='onOpenAttentionDetailView'
                @openConcaAndLinearDetailView='onOpenConcaAndLinearDetailView'
                :nodeData = "selectedNodeComponentView.nodeData"
                :nodeParams = "selectedNodeComponentView.nodeParams"
              />
              <FeedForwardView v-else-if="compoentViewType==='feed_forward'"
                @cleanComponentView = 'closeIsShowComponentview()'
                :input = "selectedNodeComponentView.nodeData.input"
                :output = "selectedNodeComponentView.nodeData.output"
                :activation = "selectedNodeComponentView.nodeData.activation"
                :intermediate = "selectedNodeComponentView.nodeData.intermediate"
              />
              <LinearSoftmaxView v-else-if="compoentViewType==='linear_softmax'"
                @cleanComponentView = 'closeIsShowComponentview()'
                :input="data[curIter].linear.input"
                :output="data[curIter].linear.output"
                :bias="[[0]]"
                :logSoftmax="data[curIter].softmax"
                :cumulativeProb="cumulativeProb"
                :predict="data[curIter].predict"
              />
            </div>
          </div>
        </div>
      </a-col>
    </a-row>
  </div>

  <div id='detailview' >
    <!-- 渲染 detail view 的条件是 人为地通过事件开启渲染并且此时还要有数据-->
    <div id='detailview-container' v-if="data.length>0 && isShowDetailview">
      <TokenizeView v-if="selectedNode.type==='tokenize'"
        @exit="quitDetailView"
        :id="selectedNode.id"
        :text="selectedNode.nodeData.input"
        :pieces="selectedNode.nodeData.pieces"
        :tokens="selectedNode.nodeData.output"
      />
      <LayernormView v-else-if="selectedNode.type==='LN'"
        @exit="quitDetailView"
        :input="selectedNode.nodeData.input"
        :output="selectedNode.nodeData.output"
        :mean="selectedNode.nodeData.mean"
        :std="selectedNode.nodeData.std"
        :alpha="selectedNode.nodeParams.alpha"
        :beta="selectedNode.nodeParams.beta"
      />
      <AttentionHeadView v-else-if="selectedNode.type==='self_attn' || selectedNode.type==='cross_attn'"
        @exit="quitDetailView"
        :nodeType="selectedNode.type"
        :nodeData="selectedNode.nodeData"
      />
      <AttentionView v-else-if="selectedNode.type==='attention'"
        @exit="quitDetailView"
        :nodeType="selectedNode.type"
        :nodeData="selectedNode.nodeData"
      />
      <ConcatenateView v-else-if="selectedNode.type==='concatenate'"
        @exit="quitDetailView"
        :nodeData="selectedNode.nodeData"
      />
    </div>
  </div>
</div> 



</template>

<script>
import cpnInput from "./components/input"
import cpnTranslation from "./components/translation"
import cpnArchitecture from "./components/architecture"

import TokenizeView from "./components/TokenizeView"
import LayernormView from "./components/LayernormView"
import LinearSoftmaxView from "./components/LinearSoftmaxView"
import FeedForwardView from "./components/FeedForwardView"
import EmbeddingView from "./components/EmbeddingView"
import SelfAttentionView from "./components/SelfAttentionView"
import CrossAttentionView from "./components/CrossAttentionView"
import AttentionHeadView from "./components/AttentionHeadView"
import AttentionView from "./components/AttentionView"
import ConcatenateView from "./components/ConcatenateView"

// 后续还会有一些 attention 内部的 detailview

import DataService from "./utils/data-service"; // 这里将 后端服务器 抽象为一个对象 DataService, 前端与后端的交互就通过 DataService 完成
import {nodeId2Indices, parseIndices, nodeId2ParamIndices} from "./utils/data-utils"
import { ElLoading } from 'element-plus'
export default {
  name: 'App',
  components: {
    cpnInput,
    cpnTranslation,
    cpnArchitecture,
    TokenizeView,
    LayernormView,
    LinearSoftmaxView,
    FeedForwardView,
    EmbeddingView,
    SelfAttentionView,
    CrossAttentionView,
    AttentionHeadView,
    ConcatenateView,
    AttentionView,
  },
  data() {
    return {
      // data for HTTP requests in DataService
      get: null,
      getData: null,
      loadParam: {'data': 'load'},
      loadData: null,

      // data for event handling in EventService
      dataName: null,
      dataValue: null,
      
      // 我们所使用的一些变量
      // sentence begin
      BOS: 'BOS',
      // sentence end
      EOS: 'EOS',

      // 标记后台翻译工作是否完成
      inTranslating: false,

      // candidates input texts
      inputTextArray: ["Why are you so happy?","I'm glad you come to see me.",],
      
      // index of input text in input text inputTextArray
      curInputIndex:0,

      // input text
      // inputText: this.inputTextArray[this.curIndex],
      inputText: '',

      // intermediate data generated from the translation
      data: [],
      params:{},
      // parameters of the Transformer model
      // params: null,
      cumulativeProb:1,

      // translations
      fullTranslation: '',
      currentTranslation: '',

      // current iteration index
      totalIterations:0,
      curIter:1,
      curIterPred:'',

      // detail view conditions
      isShowDetailview:false,
      selectedNode:{},
      disableControl:false,
      selectedNodeComponentView:{},

      // overlay
      mask:null,
      zIndexOverlay:"10",
      // zIndexDetailview:"20",

      // component view settings
      isShowComponentview:false,
      compoentViewType:"",
    }
  },
  // 学习一下 Vue 里的 mounted 的作用；
  // 里面不同的方法对应着不同的前端访问后端的方式
  mounted () {
    // HTTP GET request
    // DataService.get(data => {
    //   this.get = data;
    // });

    // DataService.getData(data => {
    //   this.getData = data;
    // });

    // HTTP POST request
    // DataService.post(this.loadParam, (data) => {
    //   this.loadData = data;
    // });
  },
  methods: {
    onTranslate(text){
      console.log("App.vue - input text: "+text );
      this.inputText = text;
      const loading = ElLoading.service({
        lock: true,
        text: 'Translating',
        background: 'rgba(0, 0, 0, 0.7)',
      })
      // DataService.translate_input_text({text},onTranslateCallback)
      DataService.translate_input_text({text},(backendData)=>{
        console.log('backendData:', backendData);
        this.fullTranslation = backendData.translation;
        this.data = backendData.data;
        this.totalIterations = this.data.length-1;
        this.curIter = 1;
        this.currentTranslation = this.data[this.curIter].input;
        this.curIterPred = this.data[this.curIter].predict.word;
        // 记录当前轮次的所有 pieces
        this.encoderPieces = this.data[0].tokenize.pieces;
        this.decoderPieces = this.data[this.curIter].tokenize.pieces;
        // console.log('this.encoderPieces: ',this.encoderPieces);
        // console.log('this.decoderPieces: ',this.decoderPieces);
        loading.close();
      });
    },
    onLast(){
      console.log('this.curIter: ',this.curIter);
      console.log('this.curIter > 1 ?', this.curIter>1);
      if(this.curIter > 1){
        this.curIter -= 1;
        this.currentTranslation = this.data[this.curIter].input;
        this.curIterPred = this.data[this.curIter].predict.word;
        this.decoderPieces = this.data[this.curIter].tokenize.pieces;
        // 改变各个图元绑定的 data (if needed)
        // 改变 cumulative score
        this.cumulativeProb = 1;
        for(let i=1; i<=this.curIter; i++){
          this.cumulativeProb *= Math.exp((this.data[i].softmax)[this.data[i].predict.token]);
        }
        // 改变 选择的 selectedNodeComponentView
        console.log(this.selectedNodeComponentView);
        if(this.selectedNodeComponentView.id!=undefined){
          // const indices = nodeId2Indices(this.selectedNodeComponentView.id,this.curIter);
          // // const nodeData = parseIndices(indices,this.data);
          // this.selectedNodeComponentView.nodeData = parseIndices(indices,this.data);
          if(this.selectedNodeComponentView.type=="embedding" || this.selectedNodeComponentView.type=="PE"){
            const coderType = this.selectedNodeComponentView.id.split('-')[0];
            const embeddingId = coderType+'-embedding';
            const peId = coderType+'-PE';
            const embeddingNodeData = parseIndices(nodeId2Indices(embeddingId,this.curIter),this.data);
            const peNodeData = parseIndices(nodeId2Indices(peId,this.curIter),this.data);
            const sentence_len = coderType=='decoder'?this.curIter:embeddingNodeData.input.length;
            DataService.getParams({
                paramIndex: nodeId2ParamIndices(peId),
                sentence_len,
              },(backendParams)=>{
                this.selectedNodeComponentView = {
                  'id':this.selectedNodeComponentView.id,
                  'type':this.selectedNodeComponentView.type,
                  'nodeData':{
                    tokens: embeddingNodeData.input,
                    embeddings: embeddingNodeData.output,
                    coefficient: embeddingNodeData.coefficient,
                    output: peNodeData.output,
                    pe:backendParams.param,
                  }
                };
            });
          } else {
            const indices = nodeId2Indices(this.selectedNodeComponentView.id,this.curIter);
            // const nodeData = parseIndices(indices,this.data);
            this.selectedNodeComponentView.nodeData = parseIndices(indices,this.data);
          }
        }
      } else {
        // alert("当前已是首轮预测迭代")
        console.log("当前已是首轮预测迭代");
      }
    },
    onNext(){
      console.log('this.curIter: ',this.curIter);
      console.log(`this.curIter < ${this.totalIterations}: `, this.curIter<this.totalIterations);

      if(this.curIter < this.totalIterations){
        this.curIter += 1;
        this.currentTranslation = this.data[this.curIter].input;
        this.curIterPred = this.curIter < this.totalIterations ? this.data[this.curIter].predict.word : this.EOS;
        this.decoderPieces = this.data[this.curIter].tokenize.pieces;
        // 改变各个图元绑定的 data (if needed)
        // 改变 cumulative score
        this.cumulativeProb = 1;
        for(let i=1; i<=this.curIter; i++){
          this.cumulativeProb *= Math.exp((this.data[i].softmax)[this.data[i].predict.token]);
        }
        // 改变 选择的 selectedNodeComponentView
        console.log(this.selectedNodeComponentView);
        if(this.selectedNodeComponentView.id!=undefined){
          if(this.selectedNodeComponentView.type=="embedding" || this.selectedNodeComponentView.type=="PE"){
            const coderType = this.selectedNodeComponentView.id.split('-')[0];
            const embeddingId = coderType+'-embedding';
            const peId = coderType+'-PE';
            const embeddingNodeData = parseIndices(nodeId2Indices(embeddingId,this.curIter),this.data);
            const peNodeData = parseIndices(nodeId2Indices(peId,this.curIter),this.data);
            const sentence_len = coderType=='decoder'?this.curIter:embeddingNodeData.input.length;
            DataService.getParams({
                paramIndex: nodeId2ParamIndices(peId),
                sentence_len,
              },(backendParams)=>{
                this.selectedNodeComponentView = {
                  'id':this.selectedNodeComponentView.id,
                  'type':this.selectedNodeComponentView.type,
                  'nodeData':{
                    tokens: embeddingNodeData.input,
                    embeddings: embeddingNodeData.output,
                    coefficient: embeddingNodeData.coefficient,
                    output: peNodeData.output,
                    pe:backendParams.param,
                  }
                };
            });
          } else {
            const indices = nodeId2Indices(this.selectedNodeComponentView.id,this.curIter);
            // const nodeData = parseIndices(indices,this.data);
            this.selectedNodeComponentView.nodeData = parseIndices(indices,this.data);
          }
        } else {
          console.log("当前已是末轮预测迭代");
        }
      }
    },
    onNodeSelectedInArchitecture(node) {
      if(this.data.length === 0 ) { // 数据还未加载完毕
        console.log('data are not received yet');
      } else {  // 数据已加载完毕
        const nodeId = node.getModel().id;
        // encoder-2-full-self-attention
        // console.log(nodeId) 
        const indices = nodeId2Indices(nodeId,this.curIter);
        // [0,'self_attn',1]
        // console.log(indices)
        if(indices.length == 0){  // 点击了目前还不支持的结点, 不予以反馈
          return null;
        }
        const nodeType = indices[1];
        if (nodeType=="tokenize" || nodeType=="LN") {
          if (nodeType == "tokenize"){
            const nodeData = parseIndices(indices,this.data);
            const selectedNode = {
              'id':nodeId,
              'type':nodeType,
              'nodeData':nodeData,
            }
            console.log(selectedNode)
            this.enterDetailView(selectedNode);
          } else {
            const nodeData = parseIndices(indices,this.data);
            const paramIndex = nodeId2ParamIndices(nodeId);
            DataService.getParams({paramIndex},(backendParams)=>{
              console.log('backendParams:', backendParams);
              const nodeParams = {
                'alpha':backendParams.param[0],
                'beta':backendParams.param[1],
              }
              const selectedNode = {
                'id':nodeId,
                'type':nodeType,
                'nodeData':nodeData,
                'nodeParams':nodeParams,
              }
              //  等待后端参数请求好之后, 再打开 LayerNorm 视图
              console.log(selectedNode)
              this.enterDetailView(selectedNode);
            });
          }
        } else {
          // 剩下的 type 都需要先进入到 component view
          if ( nodeType=="embedding" || nodeType=="PE") {
            const coderType = nodeId.split('-')[0];
            const embeddingId = coderType+'-embedding';
            const peId = coderType+'-PE';
            const embeddingNodeData = parseIndices(nodeId2Indices(embeddingId,this.curIter),this.data);
            const peNodeData = parseIndices(nodeId2Indices(peId,this.curIter),this.data);
            // const sentence_len = coderType=='decoder'?this.curIter:this.totalIterations;
            const sentence_len = coderType=='decoder'?this.curIter:embeddingNodeData.input.length;
            DataService.getParams({
              paramIndex: nodeId2ParamIndices(peId),
              sentence_len,
            },(backendParams)=>{
              this.selectedNodeComponentView = {
                'id':nodeId,
                'type':nodeType,
                'nodeData':{
                  tokens: embeddingNodeData.input,
                  embeddings: embeddingNodeData.output,
                  coefficient: embeddingNodeData.coefficient,
                  output: peNodeData.output,
                  pe:backendParams.param,
                }
              };
              this.compoentViewType="embedding";
              this.isShowComponentview = true;
              console.log(this.selectedNodeComponentView);
            })
          } else if ( nodeType=="linear" || nodeType=="softmax" ) {
            console.log("Sotmax-part");
            // // 先看看 之前有没有访问过相同的参数
            // if ('linear' in this.params) { // 如果有访问过相同的参数, 则直接从前端获取
            //   this.compoentViewType="linearsoftmax"
            // } else {  // 如果这次是第一次访问相关参数, 那么访问得到参数后先对参数进行保存;
            //   // const paramIndex = nodeId2ParamIndices('linear');
            //   DataService.getParams({paramIndex:nodeId2ParamIndices('linear')},
            //   (backendParams)=>{
            //     console.log('backendParams:', backendParams);
            //     // const bias = backendParams.param;
            //     this.params['linear'] = backendParams.param;
            //     this.compoentViewType="linearsoftmax"
            //   });
            // }
            this.compoentViewType="linear_softmax";
            this.selectedNodeComponentView = {'id':nodeId};
            this.isShowComponentview = true;
            console.log(this.selectedNodeComponentView)
          } else if ( nodeType=="feed_forward") {
            // feed_forward 视图打开时没有向后端申请参数
            console.log("FeedForward-part");
            this.compoentViewType='feed_forward'
            this.isShowComponentview = true;
            const nodeData = parseIndices(indices,this.data);
            const selectedNode = {
              'id':nodeId,
              'type':nodeType,
              'nodeData':nodeData,
            }
            this.selectedNodeComponentView = selectedNode;
            console.log(this.selectedNodeComponentView)
          // } else if ( nodeType=="self_attn") {
          } else if ( nodeType=="self_attn" || nodeType=="cross_attn") {
            console.log("Attention-part");
            // const nodeId = node.getModel().id;
            // const indices = nodeId2Indices(nodeId,this.curIter);
            // const nodeType = indices[1];
            const nodeData = parseIndices(indices,this.data);
            const paramIndex = nodeId2ParamIndices(nodeId);
            DataService.getParams({paramIndex},(backendParams)=>{
              // const param = backendParams.param;
              this.selectedNodeComponentView = {
                'id':nodeId, 
                'type':nodeType,
                'nodeData':nodeData,
                'nodeParams': backendParams.param,
              };
              // this.compoentViewType = "self_attention";
              this.compoentViewType = nodeType=="self_attn" ? "self_attention" : "cross_attention";
              this.isShowComponentview = true;
              console.log(this.selectedNodeComponentView)
            });
          } 
          // else if ( nodeType=="cross_attn") {
          //   console.log("CrossAttention-part");
          // }
        }
      }
    },
    enterDetailView(selectedNode){
      // 根据选中的结点对各个变量进行设置
      this.selectedNode = selectedNode;
      this.isShowDetailview = true;
      this.disableControl = true;
      
      // 确定 detail view 的位置
      const detailview = document.getElementById('detailview');
      const canvas = document.getElementById('container').firstElementChild;
      const width = +(canvas.style.width.slice(0,-2));
      const height = +(canvas.style.height.slice(0,-2));
      const offsetY = document.getElementsByClassName('top_container')[0].clientHeight;
      detailview.style.top = `${ height/16 + offsetY }px`;  // 设定 detailview 在 y 轴上的位置
      detailview.style.left = `${ width/12 }px`;  // 设定 detailview 在 x 轴上的位置
      detailview.style.position = 'absolute'; // 将 detailview 的位置设定为绝对位置(i.e.出现在浏览器的相应的地方)

      // 添加遮盖物
      this.mask = document.createElement('div');
      this.mask.style.width = window.innerWidth + 'px';
      this.mask.style.height = window.innerHeight + 'px';
      this.mask.style.background = '#fff';
      this.mask.style.opacity = '.7';
      this.mask.style.position = 'fixed';
      this.mask.style.top = '0';
      this.mask.style.left = '0';
      this.mask.style.zIndex = this.zIndexOverlay;
      this.mask.onclick = (event)=>{
        event = event || window.event;
        if(event || event.stopPropagation()){
          event.stopPropagation();
        } else {
          event.cancelBubble = true;
        }
        this.quitDetailView();
      }
      document.getElementById('translateGroup').appendChild(this.mask);
    },

    quitDetailView(){
      // 设置各项变量
      this.selectedNode = {};
      this.isShowDetailview = false;
      this.disableControl = false;
      // 移除覆盖物
      document.getElementById('translateGroup').removeChild(this.mask);
    },
    closeIsShowComponentview(){
      this.isShowComponentview = false;
      this.compoentViewType = '';
      this.selectedNodeComponentView = {};
    },
    onOpenHeadDetailView(nodeData){
      // const nodeType = this.selectedNodeComponentView.type;
      const selectedNode = {
        'id':this.selectedNodeComponentView.id,
        'type':this.selectedNodeComponentView.type,
        'nodeData':nodeData,
      }
      console.log('Enter OpenHeadDetailView - selectedNode:',selectedNode);
      this.enterDetailView(selectedNode);
    },
    onOpenAttentionDetailView(nodeData){
      const selectedNode = {
        'id':this.selectedNodeComponentView.id,
        'type':'attention',
        'nodeData':nodeData,
      }
      console.log('Enter OpenAttentionDetailView - selectedNode:',selectedNode);
      this.enterDetailView(selectedNode);
    },
    onOpenConcaAndLinearDetailView(nodeData){
      // const nodeType = this.selectedNodeComponentView.type;
      const selectedNode = {
        'id':this.selectedNodeComponentView.id,
        'type':'concatenate',
        'nodeData':nodeData,
      }
      console.log('Enter OpenConcaAndLinearDetailView - selectedNode:',selectedNode);
      this.enterDetailView(selectedNode);
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  width: 1600px;
  /* height: 1370px; */
  height: 1200px;
  margin: 2px;
  border: 1px solid lightblue;
}

#pieces {
  display: flex;
  flex-direction:row;
  justify-content: space-between;
  align-items: center;
  /* 
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  border-radius: .5rem;
  background-color: white;
  width:100%;
  height:100%;
  */
}

.top_container{
  box-sizing: border-box;
  height: 120px;
  width: 100%;
  margin-bottom: 2px;
  border: 2px ;
  border-color:#ddd;
}

#mid_container{
  box-sizing: border-box;
  /* height: 750px;*/
  height: 580px;
  width: 100%;
  border: 1px solid darkblue;
}

#bottom_container{
  box-sizing: border-box;
  height: 490px;
  width: 100%;
  border: 1px solid darkblue;
}

#componentDiv{
  width: 100%;
  height: 100%;
}

#detailview{
  z-index:100;
}
.chartHeader {
    width: 100%;
    /* height: 8%; */
    height: 2.8vh;
    background-color: #ddd;
    text-align: left;
    text-indent: 4px;
    line-height: 2;
    /* line-height: 2; */
    font-weight: bold;
    font-size: 16px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
  }
</style>
