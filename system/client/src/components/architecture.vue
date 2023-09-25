<template>
    <div id="architectureDiv" style="height: 100%; width: 100%">
      <div id="container">
      </div>
    </div>
</template>

<script>
  /*
  This component use G6 to construct Architecture View for Transformer
  G6 github: https://github.com/antvis/G6
  G6 是一个图可视化引擎。它提供了图的绘制、布局、分析、交互、动画等基础的图可视化能力。旨在让关系变得透明，简单。让用户获得关系数据的 Insight.
   */
  // import * as d3 from "d3";
  import G6 from '@antv/g6'
  // import {ext} from '@antv/matrix-util'

  // import nodeId2Index from '../utils/data-utils'

  export default {
    name: "cpnArchitecture",
    props: {
      encoder: {
        type: Object,
        default: function(){return {};},
      },
      decoder: {
        type: Object,
        default: function(){return {};},
      },   
      componentNodeId: {
        type: String,
        default: "",
      },
      detailNodeId: {
        type: String,
        default: "",
      },
      curIter: {
        type: Number,
        default: 1,
      },
      disableControl: {
        type: Boolean,
        default: false,
      },
    },
    // emits: ['selected'], // 子组件发射事件, 父组件接收事件并完成相应数据交互
    emits: ['nodeSelected'], // 子组件发射事件, 父组件接收事件并完成相应数据交互
    data() {
      return {
        oldComponentNodeId:"",
        oldDetailNodeId:"",

        architecture: null,
        architectureData: {
          nodes: [],  // {id,label,type,style}
          edges: [],  // {source,target,type,id}
          combos: [],
        },
        // edges: [],
        graph: null,
        render: null,
        // focus = 0,1,2,3,4 ;
        // 0 表示没有放大, 1-2表示放大encoder, 3-4表示放大decoder
        focus: 0,
      }
    },
    watch: {
      // loadData: function () {
      //   // When data is changed in parent, render this component
      //   this.renderBarChart();
      // },
      // disableControl:function(){

      // },
    },
    beforeUpdate(){
      if(this.oldComponentNodeId != this.componentNodeId){
        // 更新 node state
        // if (!this.disableControl) {
        const oldNode = this.graph.findById(this.oldComponentNodeId);
        const newNode = this.graph.findById(this.componentNodeId);
        if(oldNode && oldNode.hasState('focused')){
        // if(oldNode && oldNode.hasState('focused') && newNode){
          this.graph.setItemState(oldNode,'focused', false);
          // this.graph.setItemState(newNode,'focused', true);
        } // else if (newNode && !(oldNode && oldNode.hasState('focused'))) {
        //   this.graph.setItemState(newNode,'focused', true);
        // } 
        if(newNode){
          this.graph.setItemState(newNode,'focused', true);
        }
        // }
        // 更新记录
        if(oldNode && this.oldComponentNodeId == this.oldDetailNodeId){
          this.graph.setItemState(oldNode,'focused', true);
        }
        this.oldComponentNodeId = this.componentNodeId;
      } 

      if(this.oldDetailNodeId != this.detailNodeId){
        // 更新 node state
        // if (!this.disableControl) {
        const oldNode = this.graph.findById(this.oldDetailNodeId);
        const newNode = this.graph.findById(this.detailNodeId);
        if(oldNode && oldNode.hasState('focused')){
        // if(oldNode && oldNode.hasState('focused' && newNode)){
          this.graph.setItemState(oldNode,'focused', false);
          // this.graph.setItemState(newNode,'focused', true);
        }
        if(newNode){
          this.graph.setItemState(newNode,'focused', true);
        }
        // }
        // 更新记录
        if(oldNode && this.oldComponentNodeId == this.oldDetailNodeId){
          this.graph.setItemState(oldNode,'focused', true);
        }
        this.oldDetailNodeId = this.detailNodeId;
      }

    },
    mounted() {
      this.initArchitecture();
    },
    methods: {
      initArchitecture(){
        console.log("Intializing the Architecture View ...");

        const graphPlugins = [this.registerCustomizedDataTip()];
        const graph = new G6.Graph({  // 对图的初始化设置
          container: 'container', // 指定挂载容器
          width: 1600,   // 图的宽度  
          // height: 750,  // 图的高度
          height: 560,  // 图的高度
          // 图的交互模式Mode设置
          // 如果要使用自定义的 behavior, 需要在定义图的时候先进行注册
          modes: {
            default:[
              // 'drag-canvas', 
              // 'zoom-canvas', 
              // {
              //   type: 'collapse-expand-combo',
              //   relayout: false,
              // },
              // 'drag-node',
              // 'drag-combo',
            ],
          },
          plugins: graphPlugins,
          // plugins: [],
          // 图的布局设置
          layout: {
            type: 'dagre', // 层次布局
            rankdir: 'LR',
            align: 'UR',
            nodesep: 80,
            ranksep: 20,
            // nodesep: 50,
            // ranksep: 10,
            controlPoints: true,

          },
          // 图中节点的默认设置
          defaultNode: {
            // 访问data的方式为 evt.item.getModel().data - .getModel 可以返回相关的数据
            data: null, // 为结点设置自定义数据, 实现数据绑定
            type: 'rect', // 节点默认形状
            size: [20,120],    // 节点默认大小 
            color: '#5B8FF9', // 节点默认颜色
            // 该节点可选的连接点集合 - 边 连入 节点的相对位置
            anchorPoints: [
              [0, 0.5],
              [0.5, 0],
              [0.5, 1],
              [1, 0.5],
            ],
            style: {
              fill: '#9EC9FF',  // 节点填充色
              // lineWidth: 5,     // 节点描边色
              // cursor: "pointer",
              opacity: 0.7,
            },
            labelCfg: {
              // position: "top",
              position: "bottom",
              style: {    
                fill: '#000',   // 节点上的标签文字颜色
                fontSize: 15,   // 节点上的标签文字大小
                // cursor: "pointer",
              },
            },
          },
          // 图中边的默认设置
          defaultEdge: {
            data: null, // 为边设置自定义数据, 实现数据绑定
            type: "can-running-line", // 自定义的边
            // properties:{
            //   data: "edges' data",
            // },
            style: {
              // stroke: 'grey',  // 边的描边颜色
              stroke: '#100873',  // 边的描边颜色
              opacity: 0.7,   // 边不透明度
              lineWidth: 3,
              endArrow: true,
              // endArrow:  {
              //   path: 'M 0,0 L -2,1 L -2,-1 Z',
              //   d: 1.5,
              // }
              // cursor: "crosshair",
            },
          },
          // 图中 combo 的默认设置
          defaultCombo: {
            type: 'rect',
            size: [100,120],  // combo 的最小 size
            // fixSize: [100,120],
            // fixCollapseSize: [], 
            // collapsed: true,
            style: {
              fill: '#FFBA73',
              stoke: '#eaff8',
              lineWidth: 5,
              // 其他属性
            },
            labelCfg: {
              // position: "bottom",
              position: "top",
              refX: 120,
              refY: 30,
              style:{
                fontSize: 15,
              },
            },
          },
          nodeStateStyles: {  // 这里设置了 Node 处于不同 state 下会有怎样的 style
            'hover': {
              fill: '#d3adf7',
              opacity: 1,
            },
            'focused': {
              // fill: '#3F7D3',
              fill: 'MAROON',
              opacity: 1,
              stroke: 'red',
            }
          },
          edgeStateStyles: {
            running: {
              stroke: '#black',  // 边的描边颜色
              opacity: 1,   // 边不透明度
            },
          },
          fitView: true,    // 设置是否将图适配到画布中
          // fitViewPadding: [25, 25, 25, 25],  // 画布上四周的留白宽度
          // renderer: 'svg',  // 指定渲染方式
          cursor: "default",
          groupByTypes: false,
          animate: true,
        });
        this.graph = graph;
        
        // 监听 this.disableControl 的变化
        // this.$watch(()=>this.disableControl,(newVal)=>{
        //   console.log('now:',this.disableControl);
        //   console.log('newVal:',newVal);
        //   console.log('plugins:',this.graph.plugins);
        //   this.graph.plugins = newVal==true?graphPlugins:[];
        // })

        console.log("Register customized edges into Graph...");
        // 注册自定义 Edge (其中定义了 Edge 的事件和触发事件的回调函数)
        this.registerCustomizedEdge("can-running-line");
        this.registerCustomizedEdge("can-running-polyline");

        // 为每个节点初始化事件
        this.initNodesEvents();

        // 初始化数据
        console.log("Initialize the data...");
        this.initArcitectureData();

        console.log("Load the data...");
        console.log(this.architectureData);
        graph.data(this.architectureData); // 加载数据

        // 在进行渲染前, 初始化 canvas 的相关设置
        // 调整 decoder-2-full-cross-attention Node 位置
        this.initTimeGraphEvent();

        console.log("Rendering...");
        graph.render();   // 渲染

        //  微调部分结点位置
        // console.log("Fine Tuning...");
        // this.fineTuneTheNodePos();
        
      },

      createInputNode(isEncoder=true){
        return {
          id: isEncoder == true ? "encoder-input" : "decoder-input",
          // label: isEncoder == true ? "Encoder Embedding" : "Decoder Embedding",
          label: "Input",
          type:"rect",
          style:{},
          y: isEncoder == true ? 100 : 300,
          layer: 0,
          // _order: isEncoder == true ? 1 : 2,
        }
      },

      createTokenizeNode(isEncoder=true){
        return {
          id: isEncoder == true ? "encoder-tokenize" : "decoder-tokenize",
          // label: isEncoder == true ? "Encoder Embedding" : "Decoder Embedding",
          label: "Tokenize",
          type:"rect",
          style:{},
          // y: isEncoder == true ? 100 : 300,
          layer: 1,
          // _order: isEncoder == true ? 1 : 2,
        }
      },

      createEmbeddingNode(isEncoder=true){
        return {
          id: isEncoder == true ? "encoder-embedding" : "decoder-embedding",
          // label: isEncoder == true ? "Encoder Embedding" : "Decoder Embedding",
          label: "Embedding",
          type:"rect",
          style:{},
          // y: isEncoder == true ? 100 : 300,
          layer: 2,
          // _order: isEncoder == true ? 1 : 2,
        }
      },

      createPositionalEncodingNode(isEncoder=true){
        return {
          id: isEncoder == true ? "encoder-PE" : "decoder-PE",
          // label: isEncoder == true ? "Encoder Positional Encoding" : "Decoder Positional Encoding",
          // label: "Positional Encoding",
          label: "PE",
          type: "rect",
          style: {},
          // y: isEncoder == true ? 100 : 300,
          layer: 3,
          // _order: isEncoder == true ? 1 : 2,
        }
      },

      createAttentionNode(layerOrder, isEncoder=true, isSelf=true, isMasked=false){
        let coder = isEncoder ? "encoder-" : "decoder-";
        let mask = isMasked ? "masked-" : "full-", maskLabel = isMasked ? "Masked " : "Full ";
        let mechanism = isSelf ? "self-" : "cross-", mechanismLabel = isSelf ? "Self-" : "Cross-";
        let cfg =  { 
          id: coder + layerOrder + "-" + mask + mechanism + "attention",
          label: maskLabel + mechanismLabel + "Attention",
          type:"rect",
          style: {},
        }
        return cfg;
      },

      createAddNode(layerOrder, innerOrder, isEncoder=true) {
        let coder = isEncoder ? "encoder-" : "decoder-";
        return {
          id: coder + layerOrder + "-" + innerOrder + "-add",
          label: "Add",
          type: "circle",
          size: 20,
          style: {},
          // layerOrder: layerOrder,
          // innerOrder: innerOrder
        }
      },

      createLayerNormNode(layerOrder, innerOrder,isEncoder=true){
        let coder = isEncoder ? "encoder-" : "decoder-";
        return {
          id: coder + layerOrder + "-" + innerOrder + "-LN",
          label: "Layer Norm",
          type: "rect",
          style: {},
          // layerOrder: layerOrder,
          // innerOrder: innerOrder
        };
      },

      createFeedForwardNode(layerOrder,isEncoder=true){
        let coder = isEncoder ? "encoder-" : "decoder-";
        return {
          id: coder + layerOrder + "-FF",
          label: "Feed Forward",
          type: "rect",
          style: {},
          // layerOrder: layerOrder
        }
      },

      createLinearNode(){
        return {
          id: "linear",
          label: "Linear",
          type: "rect",
          style: {},
        }
      },
      
      createSoftmaxNode(){
        return {
          id: "softmax",
          label: "Softmax",
          type: "rect",
          style: {},
        }
      },

      createEncoderLayer(layerOrder){
        return [
          // this.createAttentionNode(layerOrder=layerOrder, isEncoder=true, isSelf=true, isMasked=false),
          this.createAttentionNode(layerOrder, true, true, false),
          // this.createAddNode(layerOrder=layerOrder, innerOrder=1, isEncoder=true),
          this.createAddNode(layerOrder, 1, true),
          // this.createLayerNormNode(layerOrder=layerOrder, innerOrder=1, isEncoder=true),
          this.createLayerNormNode(layerOrder, 1, true),
          // this.createFeedForwardNode(layerOrder=layerOrder, isEncoder=true),
          this.createFeedForwardNode(layerOrder, true),
          // this.createAddNode(layerOrder=layerOrder, innerOrder=2, isEncoder=true),
          this.createAddNode(layerOrder, 2, true),
          // this.createLayerNormNode(layerOrder=layerOrder, innerOrder=2, isEncoder=true),
          this.createLayerNormNode(layerOrder, 2, true),
        ]
      },

      createDecoderLayer(layerOrder){
        return [
          // this.createAttentionNode(layerOrder=layerOrder, isEncoder=false, isSelf=true, isMasked=true),
          this.createAttentionNode(layerOrder, false, true, true),
          // this.createAddNode(layerOrder=layerOrder, innerOrder=1, isEncoder=false),
          this.createAddNode(layerOrder, 1, false),
          // this.createLayerNormNode(layerOrder=layerOrder, innerOrder=1, isEncoder=false),
          this.createLayerNormNode(layerOrder, 1, false),
          // this.createAttentionNode(layerOrder=layerOrder, isEncoder=false, isSelf=false, isMasked=false),
          this.createAttentionNode(layerOrder, false, false, false),
          // this.createAddNode(layerOrder=layerOrder, innerOrder=2, isEncoder=false),
          this.createAddNode(layerOrder, 2, false),
          // this.createLayerNormNode(layerOrder=layerOrder, innerOrder=2, isEncoder=false),
          this.createLayerNormNode(layerOrder, 2, false),
          // this.createFeedForwardNode(layerOrder=layerOrder, isEncoder=false),
          this.createFeedForwardNode(layerOrder, false),
          // this.createAddNode(layerOrder=layerOrder, innerOrder=3, isEncoder=false),
          this.createAddNode(layerOrder, 3, false),
          // this.createLayerNormNode(layerOrder=layerOrder, innerOrder=3, isEncoder=false),
          this.createLayerNormNode(layerOrder, 3, false),
        ]
      },

      initArcitecture(){
        this.architecture = {
          encoder: [
            this.createInputNode(true),
            this.createTokenizeNode(true),
            this.createEmbeddingNode(true),
            this.createPositionalEncodingNode(true),
            this.createEncoderLayer(1), // 一个数组
            this.createEncoderLayer(2), // 一个数组
            this.createEncoderLayer(3), // 一个数组
            this.createEncoderLayer(4), // 一个数组
            this.createEncoderLayer(5), // 一个数组
            this.createEncoderLayer(6), // 一个数组
          ],
          decoder: [
            this.createInputNode(false),
            this.createTokenizeNode(false),
            this.createEmbeddingNode(false),
            this.createPositionalEncodingNode(false),
            this.createDecoderLayer(1),
            this.createDecoderLayer(2),
            this.createDecoderLayer(3),
            this.createDecoderLayer(4),
            this.createDecoderLayer(5),
            this.createDecoderLayer(6),
          ],
          generator: [
            this.createLinearNode(),
            this.createSoftmaxNode(),
          ]
        }
        this.architecture;
        console.log(this.architecture)
      },

      convertArc2ArcDataNodes(){
        // 添加 Encoder 内部的节点
        let order = 0;
        this.architecture.encoder.forEach(d => {
          if (d instanceof Array) {
            // d 是一个数组
            order += 1
            let orderInBlock = 0;
            d.forEach(node=>{
              // 为当前 Combo 下的所有结点添加 comboId属性, 从而聚类;
              node.comboId = "encoder-block-" + order;
              // 为当前 node 添加 layer 属性, 从而平衡布局
              // let charArr = node.id.split("-");
              // console.log(node);
              // node.layer = parseInt(charArr[1]);
              orderInBlock += 1;
              node.layer = 3 + (order-1)*27 + orderInBlock;
              
              this.architectureData.nodes.push(node);
            });
            // 添加 combo
            this.architectureData.combos.push({
              id: "encoder-block-" + order,
              label: "Encoder Block",
              // style:{},
            });
          } else {
            // d 是一个节点对象
            // console.log(d);
            this.architectureData.nodes.push(d);
          }
        });
        // 添加 Decoder 内部的节点
        order = 0
        this.architecture.decoder.forEach(d => {
          if (d instanceof Array) {
            // d 是一个数组
            order += 1;
            let orderInBlock = 0;
            d.forEach(node=>{
              node.comboId = "decoder-block-" + order;
              // 为当前 node 添加 layer 属性, 从而平衡布局
              orderInBlock += 1;
              node.layer = 3 + (order-1)*27 + orderInBlock;
              this.architectureData.nodes.push(node);
              // 最后一个 layer norm 结点的 layer 数 为 3 + 6 + 6 = 15;
            });
            // 添加 combo
            this.architectureData.combos.push({
              id: "decoder-block-" + order,
              label: "Decoder Block",
              // style:{},
            });
          } else {
            // d 是一个节点对象
            // console.log(d);
            this.architectureData.nodes.push(d);
          }
        });
        // 到 linear node 所对应的 layer
        let currentLayer = 3 + 9*2 + 1
        // 添加 generator 内部的节点
        this.architecture.generator.forEach(d=>{
          d.layer  = currentLayer;
          this.architectureData.nodes.push(d);
          currentLayer += 1;
        });
        // 添加辅助结点使得最后的layout正常排布
        // let auxiliaryNodes = [{id: 'auxiliary-node-10',layer: 10,type:'rect'},
        //     {id: 'auxiliary-node-11',layer: 11,type:'rect'},{id: 'auxiliary-node-12',layer: 12,type:'rect'},];
        // auxiliaryNodes.forEach(node=>{this.architectureData.nodes.push(node);});
      },

      convertArc2ArcDataEdges(){
        // let counter = 0;
        let id_source = "encoder-input";
        let id_residual_connect = null;
        // 添加 Encoder 内部的所有边
        this.architecture.encoder.forEach(d => {
          if (d instanceof Array) {
            // 统计遇到过数组的次数
            // counter += 1;
            // 访问到一组 nodes
            d.forEach(node=>{

              // 将常规边加入到 graph.edges 中
              let edge = {source: id_source, target: node.id, sourceAnchor:3, targetAnchor:0, type:"can-running-line"};
              // let edge = {source: id_source, target: node.id, type:"can-running-line"};
              this.architectureData.edges.push(edge);

              // 检查是否有 residual connection 
              let idx = node.id.split('-').length-1;
              let nodeIdSuffix = node.id.split('-')[idx];
              if (nodeIdSuffix == "add") { // 说明当前遍历的是 add 结点, 存在残差连接边
                // let edgeRes = {source: id_residual_connect, target: node.id, sourceAnchor:[1,0.5], targetAnchor:[0.5,0], type:"can-running-polyline"};
                // let edgeRes = {source: id_residual_connect, target: node.id, sourceAnchor:1, targetAnchor:1, type:"can-running-polyline"};
                let edgeRes = {source: id_residual_connect, target: node.id,  type:"can-running-polyline"};
                this.architectureData.edges.push(edgeRes);
              } else if (nodeIdSuffix == "LN") {  // 更新下一次残差连接的起点
                id_residual_connect = node.id;
              }

              // 更新 id_source
              id_source = node.id;
            });
          } else {
            // 访问到单独的node
            if (d.id != "encoder-input"){
              // 将常规的边加入到 graph.edges 中
              let edge = {source: id_source, target: d.id, type: "can-running-line"}
              this.architectureData.edges.push(edge);

              // 检查 残差连接的起点的更新
              let idx = d.id.split('-').length-1;
              let nodeIdSuffix = d.id.split('-')[idx];
              if (nodeIdSuffix == "PE") {
                id_residual_connect = d.id;
              }

              // 更新 id_source
              id_source = d.id;
            }
          }
        });

        // 添加 Decoer 内部的所有边
        let id_source_encoder_output = id_source;
        id_residual_connect = null;
        id_source = "decoder-input";
        // counter = 0;
        this.architecture.decoder.forEach(d=>{
          if (d instanceof Array){
            // 统计遇到过数组的次数
            // counter += 1;

            // 访问一组 node
            d.forEach(node=>{
              // 将常规边加入到 graph.edges 中
              let edge = {source: id_source, target: node.id, sourceAnchor:3, targetAnchor:0, type:"can-running-line"};
              // let edge = {source: id_source, target: node.id, type:"can-running-line"};
              this.architectureData.edges.push(edge);

              // 检查是否有 residual connection 
              let idx = node.id.split('-').length-1;
              let nodeIdSuffix = node.id.split('-')[idx];
              if (nodeIdSuffix == "add") { // 说明当前遍历的是 add 结点, 存在残差连接边
                // let edgeRes = {source: id_residual_connect, target: node.id, sourceAnchor:1, targetAnchor:1, type:"can-running-polyline"};
                let edgeRes = {source: id_residual_connect, target: node.id, type:"can-running-polyline"};
                this.architectureData.edges.push(edgeRes);
              } else if (nodeIdSuffix == "LN") {  // 更新下一次残差连接的起点
                id_residual_connect = node.id;
              } else if (nodeIdSuffix == "attention" && node.id.split('-')[idx-1] == "cross") {
                // 当前 node 是 cross-attention sublayer, 需要接收从 encoder 过来的连接;
                let edgeCross = {source: id_source_encoder_output, target: node.id, sourceAnchor:3, targetAnchor:1, type:"can-running-polyline"};
                // let edgeCross = {source: id_source_encoder_output, target: node.id, type:"can-running-polyline"};
                this.architectureData.edges.push(edgeCross);
              }

              // 更新 id_source
              id_source = node.id;
            });
          }else{
            // 访问单独的 node
            if (d.id != "decoder-input") {
              // 访问单独的 node
              // 将常规的边加入到 graph.edges 中
              let edge = {source: id_source, target: d.id, sourceAnchor:3, targetAnchor:0, type: "can-running-line"}
              // let edge = {source: id_source, target: d.id, type: "can-running-line"}
              this.architectureData.edges.push(edge);

              // 检查 残差连接的起点的更新
              let idx = d.id.split('-').length-1;
              let nodeIdSuffix = d.id.split('-')[idx];
              if (nodeIdSuffix == "PE") {
                id_residual_connect = d.id;
              }

              // 更新 id_source
              id_source = d.id;
            }
          }
        });

        // 添加 Generator 内部的所有边
        this.architecture.generator.forEach(d => {
          let edge = {source:id_source, target:d.id, sourceAnchor:3, targetAnchor:0, type:"can-running-line"};
          // console.log(edge);
          this.architectureData.edges.push(edge);
          id_source = d.id;
        });
        
        // 添加辅助边 - 
        // let auxiliaryEdges = [{source: 'encoder-1-2-LN',target: 'auxiliary-node-10'},{source: 'auxiliary-node-10',target: 'auxiliary-node-11'},
        //     {source: 'auxiliary-node-11',target: 'auxiliary-node-12'},{source: 'auxiliary-node-12',target: 'encoder-2-full-self-attention'},];
        // console.log(auxiliaryEdges);
        // auxiliaryEdges.forEach(node=>{
        //   this.architectureData.edges.push(node);
        // });
      },

      initArcitectureData(){
        this.initArcitecture();
        this.convertArc2ArcDataNodes();
        this.convertArc2ArcDataEdges();
        // console.log(this.architectureData.nodes);
        // 调整 label 的位置
        // this.architectureData.nodes.forEach(node=>{
        //   let layer = node.layer;
        //   node.labelCfg = {position: layer%2 == 0? "top" : "bottom",};
        // });
      },

      initNodesEvents(){
        this.graph.on("node:mouseenter", (evt) => {
          const node = evt.item;
          if (!this.disableControl) this.graph.setItemState(node,'hover', true);
          // console.log(node.hasState('hover'));
        });
        this.graph.on("node:mouseleave", (evt) => {
          const node = evt.item;
          if (!this.disableControl) this.graph.setItemState(node,'hover', false);
          // console.log(node.hasState('hover'));
        });
        this.graph.on('node:click', (evt) => {
          const node = evt.item;
          console.log(node)
          if (!this.disableControl) {
            this.$emit('nodeSelected',node);
            if(node.hasState('hover')){
              this.graph.setItemState(node,'hover', false);
            }
          }
        });
      },

      initTimeGraphEvent(){
        this.graph.on('afterlayout', evt => {
          // 调整 decoder-2-full-cross-attention 这个 node 在 layout 中的位置;
          console.log("触发了 After Layout 事件.");
          let node = this.graph.findById('decoder-2-full-cross-attention');
          node.updatePosition({x:1310,y:515});
          evt;
          // 更新与 Node 相关联的所有边的位置
          let edges = node.getEdges();
          console.log(edges);
          edges.forEach(edge=>{
            edge.refresh();
          });
          // refreshPositions 是 G6 内置函数
          this.graph.refreshPositions();
        });
      },

      registerCustomizedEdge(edgeName){
        if (edgeName == "can-running-line"){
          const lineDash = [4, 2, 1, 2];
          let options = {
            // 自定义数据
            // properties:{
            //   data: "can-running-line",
            // },

            // 复写 setState 方法 
            setState(name, value, item){
              // item: 需要修改状态的元素
              // name: 状态名
              // value: 修改状态的内容
              const shape = item.get('keyShape');
              // shape;
              // 监听 running 状态
              if (name == 'running') {
                // running 状态为 true 时
                if (value) {
                  let index = 0; // 边 path 图形的动画
                  shape.animate(
                    ()=>{
                      index++;
                      if (index > 9 ){
                        index = 0;
                      }
                      const res = {
                        lineDash,
                        lineDashOffset: -index,
                      };
                      //返回需要修改的参数集, 
                      return res;
                    },
                    {
                      repeat: true, // 动画重复
                      duration: 3000, // 一次动画持续时长
                    },
                  );
                
                } else {
                // running 状态 为 false
                // 结束动画
                shape.stopAnimate();
                // running 为 false 时，要停止动画，同时把 lineDash 清空
                shape.attr("lineDash", null);
                }
              }
            },
            stateStyles: {  // 当对应节点 or 边处于不同状态下时, 所需要呈现的视觉样式
              running: {
                stroke: 'black',  // 边的描边颜色
                opacity: 1,   // 边不透明度
              },
            },
          };
          G6.registerEdge(edgeName,options,"line");
          // 监听 mouseenter 事件
          this.graph.on('edge:mouseenter',(evt) => {
            // 获得当前鼠标操作的目标边
            const edge = evt.item;
            // 将当前边的 running 状态设置为 true
            if (!this.disableControl) this.graph.setItemState(edge, 'running', true);
            // 查看当前状态
            // console.log(evt.item.hasState('running'));  // true
          }); 
          // 监听 mouseleave 事件
          this.graph.on('edge:mouseleave',(evt) => {
            // 获得当前鼠标操作的目标边
            const edge = evt.item;
            // 将当前边的 running 状态设置为 false
            if (!this.disableControl) this.graph.setItemState(edge, 'running', false);
            // console.log(evt.item.hasState('running')); // false
          }); 
          // 监听 mouseclick 事件 - 显示对应数据流
          this.graph.on('edge:click',(evt)=>{
            evt;
            console.log('Edge.getModel():', evt.item.getModel());
            // ...
          });
        } else  if (edgeName == "can-running-polyline"){
          const lineDash = [4, 2, 1, 2];
          let options = {
            // 自定义数据
            // properties:{
            //   data: "can-running-polyline",
            // },

            // 复写 setState 方法 
            setState(name, value, item){
              const shape = item.get('keyShape');
              // 监听 running 状态
              if (name == 'running') {
                // running 状态为 true 时
                if (value) {
                  let index = 0; // 边 path 图形的动画
                  shape.animate(
                    ()=>{
                      index++;
                      if (index > 9 ){
                        index = 0;
                      }
                      const res = {
                        lineDash,
                        lineDashOffset: -index,
                      };
                      //返回需要修改的参数集, 
                      return res;
                    },
                    {
                      repeat: true, // 动画重复
                      duration: 3000, // 一次动画持续时长
                    },
                  );
                } else {
                // running 状态 为 false
                // 结束动画
                shape.stopAnimate();
                // running 为 false 时，要停止动画，同时把 lineDash 清空
                shape.attr("lineDash", null);
                }
              }
            },
            stateStyles: {  // 当对应节点 or 边处于不同状态下时, 所需要呈现的视觉样式
              running: {
                stroke: 'black',  // 边的描边颜色
                opacity: 1,   // 边不透明度
              },
            },
          };
          G6.registerEdge(edgeName,options,"polyline");
          // 监听 mouseenter 事件
          this.graph.on('edge:mouseenter',(evt) => {
            // 获得当前鼠标操作的目标边 
            const edge = evt.item;
            // 将当前边的 running 状态设置为 true
            if (!this.disableControl) this.graph.setItemState(edge, 'running', true);
          }); 
          // 监听 mouseleave 事件
          this.graph.on('edge:mouseleave',(evt) => {
            // 获得当前鼠标操作的目标边
            const edge = evt.item;
            // 将当前边的 running 状态设置为 false
            if (!this.disableControl) this.graph.setItemState(edge, 'running', false);
          }); 
          // 监听 mouseclick 事件 - 显示对应数据流
          this.graph.on('edge:click',(evt)=>{
            const edge = evt.item;
            console.log("edge: ",edge);
            // ...
            console.log('Edge.getModel():', evt.item.getModel());
          });
        }
      },
      // 注册 tooltip 插件
      registerCustomizedDataTip(){
        const that = this;
        const tooltip = new G6.Tooltip({
          offsetX: 10,
          offsetY: 20,
          getContent(evt) {
            const outDiv = document.createElement('div'); //  到时候可以替换为子组件
            outDiv.style.width = 'fit-content';
            outDiv.style.height = 'fit-content';
            const header = document.createElement('h4');
            header.style.textAlign = 'center';
            const inDiv = document.createElement('div');
            inDiv.style.textAlign = 'left';
            outDiv.appendChild(header);
            outDiv.appendChild(inDiv);
            const type = evt.item._cfg.type;
            const model = evt.item.getModel();
            // console.log('Outside encoder:',that.encoder);
            // console.log('Outside decoder:',that.decoder);
            if(type == "edge") {
              // nodeId2Index(model.source,that.curIter);
              const sourceNodeId = model.source;
              const ids = sourceNodeId.split('-');
              let dataInfo = '';
              if(that.encoder.input === undefined){
                dataInfo = 'data are not received yet.';
              } else if (ids[ids.length-1] == 'linear') {
                dataInfo = 'Vec(32000)';
              } else if (ids[ids.length-1] == 'input') {
                // console.log('encoder:',that.encoder);
                // console.log('decoder:',that.decoder);
                dataInfo = ids[0]=='encoder' ? that.encoder.input : that.decoder.input;
              } else if (ids[ids.length-1] == 'tokenize') {
                dataInfo = ids[0]=='encoder' ? that.encoder.tokenize.output : that.decoder.tokenize.output;
                dataInfo = '[' + dataInfo.toString().split(',').join(", ") + ']';
              } else {
                // console.log('encoder:',that.encoder);
                // console.log('decoder:',that.decoder);
                let T = ids[0]=='encoder'? that.encoder.tokenize.output.length : that.decoder.tokenize.output.length;
                let d_model = that.decoder.linear.input.length;
                dataInfo = `Vec(${d_model})-`.repeat(T).split('-');
                dataInfo.splice(dataInfo.length-1,1);
                dataInfo = '[' + dataInfo.join(", ") + ']'; 
              }
              header.innerHTML = `Edge Info`;
              inDiv.innerHTML = `
              <ul>
                <li> Source Module: ${model.source} </li>
                <li> Target Module: ${model.target} </li>
                <li> Data: ${dataInfo}</li>
              </ul>`;
            } else {  // type == 'node'
              let {predecessors,successors} = that.getPredecessorAndSuccessorsOfNode(evt.item)
              header.innerHTML = `Node Info`;
              if (predecessors.length == 0) {
                inDiv.innerHTML = `
                <ul>
                  <li> Module ID: ${model.id} </li>
                  <li> Successor(s): ${successors.join(', ')} </li>
                </ul>`
              } else if (successors.length == 0) {
                inDiv.innerHTML = `
                <ul>
                  <li> Module ID: ${model.id} </li>
                  <li> Predecessor(s): ${predecessors.join(', ')} </li>
                </ul>`
              } else {
                inDiv.innerHTML = `
                <ul>
                  <li> Module ID: ${model.id} </li>
                  <li> Predecessor(s): ${predecessors.join(', ')} </li>
                  <li> Successor(s): ${successors.join(', ')} </li>
                </ul>`
              }             
            }
            // if(that.disableControl) outDiv.style.display = 'none';
            // console.log(outDiv);
            return outDiv
          },
          itemTypes: ['edge','node'],
        });
        return tooltip;
      },

      registerCustomizedMinimap(){
        const minimap = new G6.Minimap({
          size: [50,50],
        });
        return minimap;
      },

      getPredecessorAndSuccessorsOfNode(node){
        const model = node.getModel();
        const edges = node.getEdges();
        let predecessors = [],
            successors = [];
        edges.forEach(edge => {
          let edgeModel = edge.getModel();
          if (edgeModel.source == model.id) { // 表明当前 edge 是 Module 的出边
            successors.push(edgeModel.target);
          } else {
            predecessors.push(edgeModel.source);
          }
        });
        return {predecessors,successors}
      }
    }
  }
</script>

<style>
</style>