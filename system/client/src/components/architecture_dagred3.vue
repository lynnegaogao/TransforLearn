<template>
  <div id="architectureDiv" style="height: 100%; width: 100%">
  </div>
</template>

<script>
import * as d3 from "d3";
import * as dagreD3 from "dagre-d3";


export default {
  name: "cpnArchitecture",
  props: {
    // loadData: Object,
  },
  // emits: ['selected'], // 子组件发射事件, 父组件接收事件并完成相应数据交互
  emits: [], // 子组件发射事件, 父组件接收事件并完成相应数据交互
  data() {
    return {
      // svg: null,
      architecture: null,
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
  },
  mounted() {
    // this.initTest();
    // this.initDemo();
    this.initArchitecture();
    // this.initArc2();
  },
  methods: {

    initArc2() {
      // 设置画布大小 - 四周留间距
      console.log("initialize architecture...");
      let architectureVieWidth = 1600, architectureViewHeight = 700;
      let margin = { top: 10, right: 30, bottom: 30, left: 40 },
        width = architectureVieWidth - margin.right - margin.left,
        height = architectureViewHeight - margin.top - margin.bottom;

      // 创建 SVG 元素并添加到 对应的 html 元素中
      let svg = d3.select("#architectureDiv")
        .append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom);
      svg;

      // 创建 small-transoformer 所需要的所有结点的信息
      this.architecture = {
        encoder: [
          this.createInputNode(true),
          this.createTokenizeNode(true),
          this.createEmbeddingNode(true),
          this.createPositionalEncodingNode(true),
          this.createEncoderLayer(1), // 一个数组
          this.createEncoderLayer(2), // 一个数组
        ],
        decoder: [
          this.createInputNode(false),
          this.createTokenizeNode(false),
          this.createEmbeddingNode(false),
          this.createPositionalEncodingNode(false),
          this.createDecoderLayer(1),
          this.createDecoderLayer(2),
        ],
        generator: [
          this.createLinearNode(),
          this.createSoftmaxNode(),
        ]
      }

      // 创建流程图
      let g = new dagreD3.graphlib.Graph({
        directed: true,
        compound: true,
        multigraph: false
      })
        .setGraph({
          ranker: "network-simplex",
          rankdir: 'BT',// 将流程图的排列方式设置为垂直排列
          aligh: "UL",
          // nodesep: 10,
          // edgesep: 10,
          // ranksep: 20
        })
        .setDefaultEdgeLabel(function () { return {}; });
      this.graph = g;

      // 创建流程图中所需要的结点
      this.createGraphNodes();

      // 构建流程图中结点的位置;  — rank constraint

      //  创建流程图中所有需要可能需要的边
      // this.createGraphEdges();

      // Create the renderer
      let render = new dagreD3.render();
      this.render = render;

      // Set up an SVG group so that we can translate the final graph.
      let svgGroup = svg.append("g");
      svgGroup;
      // Run the renderer. This is what draws the final graph.
      render(d3.select("svg g"), this.graph);

      // Center the graph
      let xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
      svgGroup.attr("transform", "translate(" + xCenterOffset + ", 30)");
      svg.attr("height", g.graph().height + 40);

      // svg.select("#encoder-input").attr("transform",`translate(${10},${10})`);

    },

    initArchitecture() {
      // 设置画布大小 - 四周留间距
      console.log("initialize architecture...");
      let architectureVieWidth = 1600, architectureViewHeight = 700;
      let margin = { top: 10, right: 30, bottom: 30, left: 40 },
        width = architectureVieWidth - margin.right - margin.left,
        height = architectureViewHeight - margin.top - margin.bottom;

      // 创建 SVG 元素并添加到 对应的 html 元素中
      let svg = d3.select("#architectureDiv")
        .append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom);

      // 创建 small-transoformer 所需要的所有结点
      this.architecture = {
        encoder: [
          this.createInputNode(true),
          this.createTokenizeNode(true),
          this.createEmbeddingNode(true),
          this.createPositionalEncodingNode(true),
          this.createEncoderLayerNode(1),
          this.createEncoderLayerNode(2),
          this.createEncoderLayerNode(3),
          this.createEncoderLayerNode(4),
          this.createEncoderLayerNode(5),
          this.createEncoderLayerNode(6),
        ],
        decoder: [
          this.createInputNode(false),
          this.createTokenizeNode(false),
          this.createEmbeddingNode(false),
          this.createPositionalEncodingNode(false),
          this.createDecoderLayerNode(1),
          this.createDecoderLayerNode(2),
          this.createDecoderLayerNode(3),
          this.createDecoderLayerNode(4),
          this.createDecoderLayerNode(5),
          this.createDecoderLayerNode(6),
        ],
        generator: [
          this.createLinearNode(),
          this.createSoftmaxNode(),
          this.createOutputNode(),
        ]
      }
      // this.createEncoderLayer(1).forEach(node=>{
      //   this.architecture.encoder.push(node);
      // });
      // this.createEncoderLayer(2).forEach(node=>{
      //   this.architecture.encoder.push(node);
      // });
      // this.createDecoderLayer(1).forEach(node=>{
      //   this.architecture.decoder.push(node);
      // });
      // this.createDecoderLayer(2).forEach(node=>{
      //   this.architecture.decoder.push(node);
      // });

      // 创建流程图
      let g = new dagreD3.graphlib.Graph({
        directed: true,
        compound: true,
        multigraph: false
      })
        .setGraph({
          // ranker: "network-simplex",
          rankdir: 'BT',// 将流程图的排列方式设置为水平排列
          aligh: "BT",
          nodesep: 15,
          edgesep: 10,
          ranksep: 20
        }) // 将流程图的排列方式设置为水平排列
        .setDefaultEdgeLabel(function () { return {}; });
      this.graph = g;

      // 向流程图中加入 Node 和 Edge
      // 加入输入文本结点
      this.addNodesIntoGraph();

      // 向流程图中加入 Edge
      this.addEdgesIntoGraph();

      // 为各个结点分组
      this.addClustesIntoGraph(6);

      //设置结点为圆角矩形
      g.nodes().forEach(function (v) {
        var node = g.node(v);
        node.rx = node.ry = 5;
      });

      // this.graph.setParent("decoder-input","root");

      // Create the renderer
      let render = new dagreD3.render();

      // Set up an SVG group so that we can translate the final graph.
      let svgGroup = svg.append("g");

      // Run the renderer. This is what draws the final graph.
      render(d3.select("svg g"), g);

      // Center the graph
      let xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
      svgGroup.attr("transform", "translate(" + xCenterOffset + ", 0)");
      svg.attr("height", g.graph().height + 40);

      let encoder6Rect = document.getElementById("encoder-6").getBoundingClientRect()
      let decoder6Rect = document.getElementById("decoder-6").getBoundingClientRect()
      let decoder5Rect = document.getElementById("decoder-5").getBoundingClientRect()
      let decoder4Rect = document.getElementById("decoder-4").getBoundingClientRect()
      let decoder3Rect = document.getElementById("decoder-3").getBoundingClientRect()
      let decoder2Rect = document.getElementById("decoder-2").getBoundingClientRect()
      let decoder1Rect = document.getElementById("decoder-1").getBoundingClientRect()

      let pareRect = document.getElementById("architectureDiv").getBoundingClientRect()

      let lines = [[
        [encoder6Rect.x - pareRect.x + encoder6Rect.width, encoder6Rect.y - pareRect.y + encoder6Rect.height * 0.5],
        [decoder6Rect.x - pareRect.x, decoder6Rect.y - pareRect.y + decoder6Rect.height * 0.5],
      ], [
        [encoder6Rect.x - pareRect.x + encoder6Rect.width, encoder6Rect.y - pareRect.y + encoder6Rect.height * 0.5],
        [decoder5Rect.x - pareRect.x, decoder5Rect.y - pareRect.y + decoder5Rect.height * 0.5],
      ], [
        [encoder6Rect.x - pareRect.x + encoder6Rect.width, encoder6Rect.y - pareRect.y + encoder6Rect.height * 0.5],
        [decoder4Rect.x - pareRect.x, decoder4Rect.y - pareRect.y + decoder4Rect.height * 0.5],
      ], [
        [encoder6Rect.x - pareRect.x + encoder6Rect.width, encoder6Rect.y - pareRect.y + encoder6Rect.height * 0.5],
        [decoder3Rect.x - pareRect.x, decoder3Rect.y - pareRect.y + decoder3Rect.height * 0.5],
      ], [
        [encoder6Rect.x - pareRect.x + encoder6Rect.width, encoder6Rect.y - pareRect.y + encoder6Rect.height * 0.5],
        [decoder2Rect.x - pareRect.x, decoder2Rect.y - pareRect.y + decoder2Rect.height * 0.5],
      ], [
        [encoder6Rect.x - pareRect.x + encoder6Rect.width, encoder6Rect.y - pareRect.y + encoder6Rect.height * 0.5],
        [decoder1Rect.x - pareRect.x, decoder1Rect.y - pareRect.y + decoder1Rect.height * 0.5],
      ]]

      let linePath = d3.line();
      for (let i = 0; i < lines.length; i++) {
        svg
          .append('path')
          .attr('d', linePath(lines[i]))
          .attr('stroke', '#a6a6a6')
          .attr("marker-end", "url(#triangle)");
      }



    },

    createInputNode(isEncoder = true) {
      return {
        id: isEncoder == true ? "encoder-input" : "decoder-input",
        // label: isEncoder == true ? "Encoder Embedding" : "Decoder Embedding",
        label: "Input",
        class: "input",
      }
    },

    createTokenizeNode(isEncoder = true) {
      return {
        id: isEncoder == true ? "encoder-tokenize" : "decoder-tokenize",
        // label: isEncoder == true ? "Encoder Embedding" : "Decoder Embedding",
        label: "Tokenize",
        class: "tokenize",
      }
    },

    createEmbeddingNode(isEncoder = true) {
      return {
        id: isEncoder == true ? "encoder-embedding" : "decoder-embedding",
        // label: isEncoder == true ? "Encoder Embedding" : "Decoder Embedding",
        label: "Embedding",
        class: "embedding"
      }
    },

    createPositionalEncodingNode(isEncoder = true) {
      return {
        id: isEncoder == true ? "encoder-PE" : "decoder-PE",
        // label: isEncoder == true ? "Encoder Positional Encoding" : "Decoder Positional Encoding",
        label: "Positional\nEncoding",
        class: "PE",
        style: "fill:#CBEEA8 "
      }
    },

    createAttentionNode(layerOrder, isEncoder = true, isSelf = true, isMasked = false) {
      let coder = isEncoder ? "encoder-" : "decoder-";
      let mask = isMasked ? "masked-" : "full-", maskLabel = isMasked ? "Masked " : "Full ";
      let mechanism = isSelf ? "self-" : "cross-", mechanismLabel = isSelf ? "Self-" : "Cross-";
      return {
        id: coder + layerOrder + "-" + mask + mechanism + "attention",
        label: maskLabel + mechanismLabel + "Attention",
        class: "attention",
        layerOrder: layerOrder
      }
    },

    createAddNode(layerOrder, innerOrder, isEncoder = true) {
      let coder = isEncoder ? "encoder-" : "decoder-";
      return {
        id: coder + layerOrder + "-" + innerOrder + "-add",
        label: "Add",
        class: "add",
        layerOrder: layerOrder,
        innerOrder: innerOrder
      }
    },

    createLayerNormNode(layerOrder, innerOrder, isEncoder = true) {
      let coder = isEncoder ? "encoder-" : "decoder-";
      return {
        id: coder + layerOrder + "-" + innerOrder + "-LN",
        label: "Layer Norm",
        class: "LN",
        layerOrder: layerOrder,
        innerOrder: innerOrder
      }
    },

    createFeedForwardNode(layerOrder, isEncoder = true) {
      let coder = isEncoder ? "encoder-" : "decoder-";
      return {
        id: coder + layerOrder + "-FF",
        label: "Feed Forward",
        class: "FF",
        layerOrder: layerOrder
      }
    },

    createLinearNode() {
      return {
        id: "linear",
        label: "Linear",
        class: "linear",
        style: "fill:#CEB1DF  "
      }
    },

    createSoftmaxNode() {
      return {
        id: "softmax",
        label: "Softmax",
        class: "softmax",
        style: "fill:#E8C391  "
      }
    },

    createOutputNode() {
      return {
        id: "output",
        label: "Output",
        class: "output"
      }
    },

    createEncoderLayerNode(layerOrder) {
      return {
        id: "encoder-" + layerOrder,
        label: "Encoder #" + layerOrder,
        class: "encoder",
        style: 'fill: #F9E79F'
      }
    },

    createDecoderLayerNode(layerOrder) {
      return {
        id: "decoder-" + layerOrder,
        label: "Decoder #" + layerOrder,
        class: "decoder",
        style: 'fill: #AED6F1'
      }
    },

    createEncoderLayer(layerOrder) {
      return [
        this.createAttentionNode(layerOrder, true, true, false),
        this.createAddNode(layerOrder, 1, true),
        this.createLayerNormNode(layerOrder, 1, true),
        this.createFeedForwardNode(layerOrder, true),
        this.createAddNode(layerOrder, 2, true),
        this.createLayerNormNode(layerOrder, 2, true),
      ]
    },


    createDecoderLayer(layerOrder) {
      return [
        this.createAttentionNode(layerOrder, false, true, true),
        this.createAddNode(layerOrder, 1, false),
        this.createLayerNormNode(layerOrder, 1, false),
        this.createAttentionNode(layerOrder, false, false, false),
        this.createAddNode(layerOrder, 2, false),
        this.createLayerNormNode(layerOrder, 2, false),
        this.createFeedForwardNode(layerOrder, false),
        this.createAddNode(layerOrder, 3, false),
        this.createLayerNormNode(layerOrder, 3, false),
      ]
    },

    createGraphNodes() {
      // focus == 0
      let counter = 0;
      let rank = 0;
      this.architecture.encoder.forEach(item => {
        rank += 1;
        if (item instanceof Array) {
          counter += 1;
          let props = {
            id: "encoder-block-" + counter,
            label: "Encoder Block",
            class: "transformer-block",
            rank: rank
          }
          this.graph.setNode(props.id, props);
        } else {
          item.rank = rank;
          this.graph.setNode(item.id, item);
        }
      });
      counter = 0;
      rank = 0
      this.architecture.decoder.forEach(item => {
        rank += 1;
        if (item instanceof Array) {
          counter = counter + 1;
          let props = {
            id: "decoder-block-" + counter,
            label: "Decoder Block",
            class: "transformer-block",
            rank: rank
          }
          this.graph.setNode(props.id, props);
        } else {
          item.rank = rank;
          this.graph.setNode(item.id, item);
        }
      });
      this.architecture.generator.forEach(item => {
        rank += 1;
        item.rank = rank;
        this.graph.setNode(item.id, item);
      });
    },

    createGraphEdges() {
      // focus == 0
      let counter = 0;
      let id_source = "encoder-input";
      this.architecture.encoder.forEach(item => {
        if (item instanceof Array) {
          counter += 1;
          let id = "encoder-block-" + counter
          this.graph.setEdge(id_source, id);
          id_source = id;
        } else {
          if (item.id != "encoder-input") {
            this.graph.setEdge(id_source, item.id);
            id_source = item.id;
          }
        }
      });
      let id_source_encoder_output = id_source;
      id_source = "decoder-input";
      counter = 0;
      this.architecture.decoder.forEach(item => {
        if (item instanceof Array) {
          counter += 1;
          let id = "decoder-block-" + counter
          this.graph.setEdge(id_source, id);
          this.graph.setEdge(id_source_encoder_output, id);
          id_source = id;
        } else {
          if (item.id != "decoder-input") {
            this.graph.setEdge(id_source, item.id);
            id_source = item.id;
          }
        }
      });
      this.architecture.generator.forEach(item => {
        this.graph.setEdge(id_source, item.id);
        id_source = item.id;
      });
    },

    changeGraphEdges(focus) { // 根据 focus 来动态地改变视图;
      focus;
    },

    addNodesIntoGraph() {
      this.architecture.encoder.forEach(item => {
        // item.width = 15;
        // item.height = 10;
        this.graph.setNode(item.id, item);
      });
      this.architecture.decoder.forEach(item => {
        // item.width = 15;
        // item.height = 10;
        this.graph.setNode(item.id, item);
      });
      this.architecture.generator.forEach(item => {
        // item.width = 15;
        // item.height = 10;
        this.graph.setNode(item.id, item);
      });
    },

    addEdgesIntoGraph() {
      let id_source = "encoder-input"
      // let id_source_residual_connection = null;
      this.architecture.encoder.forEach(item => {
        if (item.id != "encoder-input") {
          if (item.id == "encoder-PE") {
            this.graph.setEdge("encoder-tokenize", item.id);
            id_source = "encoder-embedding";
          } else {
            this.graph.setEdge(id_source, item.id);
            id_source = item.id;
          }
          // if (item.class == "PE" || item.class == "LN") {
          //   id_source_residual_connection = item.id;
          // } else if (item.class == "add") {
          //   console.log([id_source_residual_connection,item.id]);
          //   this.graph.setEdge(id_source_residual_connection, item.id);
          // }
        }
      });
      // if (id_source == "encoder-6") {
      //   this.graph.setEdge(id_source, "decoder-1");
      //   this.graph.setEdge(id_source, "decoder-2");
      //   this.graph.setEdge(id_source, "decoder-3");
      //   this.graph.setEdge(id_source, "decoder-4");
      //   this.graph.setEdge(id_source, "decoder-5");
      //   this.graph.setEdge(id_source, "decoder-6");
      // }
      // id_encoder_output = "encoder-2-2-LN"
      // let id_encoder_output = id_source;
      // id_source_residual_connection = null;
      id_source = "decoder-input";
      this.architecture.decoder.forEach(item => {
        if (item.id != "decoder-input") {
          if (item.id == "decoder-PE") {
            this.graph.setEdge("decoder-tokenize", item.id);
            id_source = "decoder-embedding";
          } else {
            this.graph.setEdge(id_source, item.id);
            id_source = item.id;
          }
          // if (item.id.match("cross") != null) { // cross-attention
          //   console.log([id_encoder_output,item.id]);
          //   this.graph.setEdge(id_encoder_output, item.id);
          // } else if (item.class == "PE" || item.class == "LN") { // beginning of residual connection
          //   id_source_residual_connection = item.id;
          // } else if (item.class == "add") { // end of residual connection
          //   console.log([id_source_residual_connection,item.id]);
          //   this.graph.setEdge(id_source_residual_connection, item.id);
          // }
        }
      });
      // id_source = "decoder-2-3-LN"
      this.architecture.generator.forEach(item => {
        this.graph.setEdge(id_source, item.id);
        id_source = item.id;
      });
    },

    addClustesIntoGraph(layerOrder) {
      console.log("addClustesIntoGraph...");
      this.graph.setNode("encoderLayer", {
        id: "encoderLayer",
        label: "Encoder Layer",
        clusterLabelPos: "top",
        style: 'fill: #FCF3CF'
      });
      this.graph.setNode("decoderLayer", {
        id: "decoderLayer",
        label: "Decoder Layer",
        clusterLabelPos: "top",
        style: 'fill: #D6EAF8'
      });
      for (let i = 1; i <= layerOrder; i++) {
        this.graph.setParent("encoder-" + i, "encoderLayer");
        this.graph.setParent("decoder-" + i, "decoderLayer");
      }
    },
  }

}

</script>

<style>
#translateText {
  width: 50%;
  margin-right: 3px;
}

.clusters rect {
  fill: #00ffd0;
  stroke: #999;
  stroke-width: 1.5px;
}

text {
  font-weight: 300;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serf;
  font-size: 14px;
}

.node rect {
  stroke: #a6a6a6;
  fill: #fff;
  stroke-width: 1.5px;
}

.edgePath path {
  stroke: #a6a6a6;
  stroke-width: 1.5px;
}
</style>