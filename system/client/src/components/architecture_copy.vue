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
import G6 from '@antv/g6';
import { Graph, Node,X6 } from '@antv/x6';
import '@antv/x6-vue-shape';
import { Layout } from '@antv/layout';

//从Node继承一些属性，定义新的Group类
export class Group extends Node {
  collapsed = false;
  expandSize;
  postprocess() {
    this.toggleCollapse(false)
  }
  isCollapsed() {
    return this.collapsed
  }
  toggleCollapse(collapsed) {
    const target = collapsed == null ? !this.collapsed : collapsed
    if (target) {
      this.attr('buttonSign', { d: 'M 1 5 9 5 M 5 1 5 9' })
      this.expandSize = this.getSize()
      this.resize(100, 32)
    } else {
      this.attr('buttonSign', { d: 'M 2 5 8 5' })
      if (this.expandSize) {
        this.resize(this.expandSize.width, this.expandSize.height)
      }
    }
    this.collapsed = target
  }
}

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
      architectureData: {
        nodes: [],  // {id,label,type,style}
        edges: [],  // {source,target,type,id}
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
  },
  mounted() {
    // this.initArchitecture();
    // this.initGraph();
    // this.demoGraph();
    this.demo();

  },
  methods: {
    initGraph() {
      console.log("initalize Graph Demo ...");
      console.log(G6.Global.version);
      // 设置数据
      // 引入 G6 的数据源为 JSON 格式的对象。该对象中需要有节点（nodes）和边（edges）字段，分别用数组表示
      const initData = {
        nodes: [
          {
            id: 'encoder-input',
            label: 'Input',
            x: 200,
            y: 300
          },
          {
            id: 'decoder-input',
            label: 'Input',
          },
          {
            id: 'encoder-input-text',
            label: 'Input Text',
            comboId: 'encoder-tokenize',
          },
          {
            id: 'encoder-input-pieces',
            label: 'Input Pieces',
            comboId: 'encoder-tokenize',
          },
          {
            id: 'encoder-input-tokens',
            label: 'Input Tokens',
            comboId: 'encoder-tokenize',
          },
          {
            id: 'decoder-linear',
            label: 'Linear',
          },
          {
            id: 'decoder-softmax',
            label: 'Softmax',
          },
          {
            id: 'decoder-output',
            label: 'Output',
          },

        ],
        // 边集
        edges: [
          {
            source: 'encoder-input',
            target: 'encoder-input-text',
          },
          {
            source: 'encoder-input-text',
            target: 'encoder-input-pieces',
          },
          {
            source: 'encoder-input-pieces',
            target: 'encoder-input-tokens',
          },
          //   {
          //     source: 'encoder',
          //     target: 'decoder',
          //   },
          //   {
          //     source: 'decoder',
          //     target: 'decoder-tokenizing',
          //   },
          //   {
          //     source: 'decoder-tokenizing',
          //     target: 'decoder-embedding',
          //   },
          //   {
          //     source: 'decoder-embedding',
          //     target: 'decoder',
          //   },
          //   {
          //     source: 'decoder',
          //     target: 'decoder-linear',
          //   },
          //   {
          //     source: 'decoder-linear',
          //     target: 'decoder-softmax',
          //   },
          //   {
          //     source: 'decoder-softmax',
          //     target: 'decoder-output',
          //   },

          // ],
          // combo: [
          //   {
          //     id: 'encoder-tokenizing',
          //     label: 'Tokenize',
          //   },
          //   {
          //     id: 'encoder-embedding',
          //     label: 'Embedding',
          //   },
          //   {
          //     id: 'encoder-PE',
          //     label: 'Position Encoding',
          //   },
          //   {
          //     id: 'encoder',
          //     label: 'Encoder',
          //   },
          //   {
          //     id: 'decoder-tokenizing',
          //     label: 'Tokenize',
          //   },
          //   {
          //     id: 'decoder-embedding',
          //     label: 'Embedding',
          //   },
          //   {
          //     id: 'decoder',
          //     label: 'Decoder',
          //   },

        ],
      };

      const graph = new G6.Graph({
        container: 'container', // 指定挂载容器
        width: 1600,   // 图的宽度  
        height: 500,  // 图的高度
        defaultNode: {
          type: 'rect',
          size: [100, 50],
          color: '#5B8FF9',
          style: {
            fill: '#9EC9FF',
            lineWidth: 3,
          },
          labelCfg: {
            style: {
              fill: '#fff',
              fontSize: 3,
            },
          },
        },
        defaultEdge: {
          style: {
            stroke: '#black',
          },
        },
        defaultCombo: {
          style: {
            fill: '#steelblue',
            stroke: '#eaff8f',
            lineWidth: 5,
          },
        },
      });

      graph.data(initData); // 加载数据
      graph.render();   // 渲染
    },

    demoGraph() {
      const data = {
        // 节点
        nodes: [
          {
            id: 'node1', // String，可选，节点的唯一标识
            x: 40,       // Number，必选，节点位置的 x 值
            y: 40,       // Number，必选，节点位置的 y 值
            width: 80,   // Number，可选，节点大小的 width 值
            height: 40,  // Number，可选，节点大小的 height 值
            label: 'hello', // String，节点标签
          },
          {
            id: 'node2', // String，节点的唯一标识
            x: 60,      // Number，必选，节点位置的 x 值
            y: 180,      // Number，必选，节点位置的 y 值
            width: 80,   // Number，可选，节点大小的 width 值
            height: 40,  // Number，可选，节点大小的 height 值
            label: 'world', // String，节点标签
          },
        ],
        // 边
        edges: [
          {
            source: 'node1', // String，必须，起始节点 id
            target: 'node2', // String，必须，目标节点 id
          },
        ],
      };

      const graph = new Graph({
        container: document.getElementById('container'),
        width: 1600,
        height: 560,
      });
      graph.fromJSON(data);

      const parentnode = graph.addNode({
        x: 160,
        y: 50,
        width: 180,
        height: 140,
        label: 'parent',
      });
      const childnode = graph.addNode({
        x: 170,
        y: 60,
        width: 80,
        height: 40,
        label: 'child',
      });
      parentnode.addChild(childnode);
      const node1 = graph.getCellById("node1");
      console.log("node:", node1);
      graph.addEdge({
        shape: 'edge',
        source: node1,
        target: parentnode,
      });
    },

    demo() {
      Group.config({
        markup: [
          {
            tagName: 'rect',
            selector: 'body',
          },
          {
            tagName: 'text',
            selector: 'label',
          },
          {
            tagName: 'g',
            selector: 'buttonGroup',
            children: [
              {
                tagName: 'rect',
                selector: 'button',
                attrs: {
                  'pointer-events': 'visiblePainted',
                },
              },
              {
                tagName: 'path',
                selector: 'buttonSign',
                attrs: {
                  fill: 'none',
                  'pointer-events': 'none',
                },
              },
            ],
          },
        ],
        attrs: {
          body: {
            refWidth: '100%',
            refHeight: '100%',
            strokeWidth: 1,
            fill: '#ffffff',
            stroke: 'none',
          },
          buttonGroup: {
            refX: 8,
            refY: 8,
          },
          button: {
            height: 14,
            width: 16,
            rx: 2,
            ry: 2,
            fill: '#f5f5f5',
            stroke: '#ccc',
            cursor: 'pointer',
            event: 'node:collapse',
          },
          buttonSign: {
            refX: 3,
            refY: 2,
            stroke: '#808080',
          },
          label: {
            fontSize: 14,
            fill: '#fff',
            refX: 32,
            refY: 10,
          },
        },
      })

      // const graph = new Graph({
      //   container: document.getElementById('container'),
      //   width: 1600,
      //   height: 560,
      // })

      // function createGroup(id, x, y, width, height, fill,  label) {
      //   const group = new Group({
      //     id, x, y, width, height,
      //     attrs: {
      //       body: {
      //         fill,
      //         rx: 10,
      //         ry: 10
      //       },
      //       label: {
      //         text: label,
      //         fill: '#000',
      //         fontSize: 15,
      //       },
      //     },
      //   })
      //   graph.addNode(group)
      //   return group
      // }

      // function createNode(id, x, y, width, height, fill, label) {
      //   return graph.addNode({
      //     id, x, y, width, height,
      //     attrs: {
      //       body: {
      //         fill: fill,
      //         stroke: 'none',
      //         rx: 20,
      //         ry: 20
      //       },
      //       label: {
      //         text: label,
      //         fill: '#000',
      //         fontSize: 15,
      //       },
      //     },
      //   })
      // }

      // function createEdge(id, source, target, vertices) {
      //   return graph.addEdge({
      //     id, source, target, vertices, label: id, attrs: {
      //       label: {
      //         fontSize: 12,
      //       },
      //     },
      //   })
      // }

      // //Encoder部分
      // const enX=50,enY=30,enGap=60;
      // createNode('en-input', enX, enY, 60, 40, '#F5E271', "Input")
      // createGroup('en-tokenize', enX, enY+enGap, 100, 40, "#F5E271", "Tokenize")
      // createGroup('en-embedding', enX, enY+enGap*2, 60, 40, "#F5E271", "Embedding")
      // createGroup('en-PE', enX, enY+enGap*3, 60, 40, "#F5E271", "Position\nEncoding")
      // createGroup('en-encoder', enX, enY+enGap*4, 60, 40, "#F5E271", "Encoder")

      // //Decoder部分
      // createNode('de-input', 400, 100, 60, 40, '#F5E271', "Input")
      // createGroup('de-tokenize',400,140,60,40,"#F5E271","Tokenize")
      // createGroup('de-embedding',400,180,60,40,"#F5E271","Embedding")
      // createGroup('de-PE',400,220,60,40,"#F5E271","Position\nEncoding")
      // createGroup('de-decoder', 400, 260, 60, 40, "#F5E271", "Decoder")

      // //Generator部分
      // createGroup('ge-linear', 400, 300, 60, 40, "#F5E271", "Linear")
      // createGroup('ge-softmax',400,340,60,40,"#F5E271","Softmax")
      // createNode('ge-output',400,380,60,40,"#F5E271","Output")

      // //创建边
      // createEdge('', 'en-input', 'en-tokenize')
      // createEdge('', 'en-tokenize', 'en-embedding')
      // createEdge('', 'en-embedding', 'en-PE')
      // createEdge('','en-PE','en-encoder')
      // createEdge('','en-encoder','de-decoder')
      // createEdge('','de-input','de-tokenize')
      // createEdge('', 'de-tokenize', 'de-embedding')
      // createEdge('', 'de-embedding', 'de-PE')
      // createEdge('','de-PE','de-decoder')
      // createEdge('','de-decoder','ge-linear')
      // createEdge('','ge-linear','ge-softmax')
      // createEdge('','ge-softmax','ge-output')

      // tokenize部分
      // const inputText=createNode('en-inputText',)

      // #region 注册基础图形
      Graph.registerNode(
        'class',
        {
          inherit: 'rect',
          markup: [
            {
              tagName: 'rect',
              selector: 'body',
            },
            {
              tagName: 'rect',
              selector: 'name-rect',
            },
            {
              tagName: 'rect',
              selector: 'attrs-rect',
            },
            {
              tagName: 'rect',
              selector: 'methods-rect',
            },
            {
              tagName: 'text',
              selector: 'name-text',
            },
            {
              tagName: 'text',
              selector: 'attrs-text',
            },
            {
              tagName: 'text',
              selector: 'methods-text',
            },
          ],
          attrs: {
            rect: {
              width: 160,
            },
            body: {
              stroke: '#fff',
            },
            'name-rect': {
              fill: '#5f95ff',
              stroke: '#fff',
              strokeWidth: 0.5,
            },
            'attrs-rect': {
              fill: '#eff4ff',
              stroke: '#fff',
              strokeWidth: 0.5,
            },
            'methods-rect': {
              fill: '#eff4ff',
              stroke: '#fff',
              strokeWidth: 0.5,
            },
            'name-text': {
              ref: 'name-rect',
              refY: 0.5,
              refX: 0.5,
              textAnchor: 'middle',
              fontWeight: 'bold',
              fill: '#fff',
              fontSize: 12,
            },
            'attrs-text': {
              ref: 'attrs-rect',
              refY: 0.5,
              refX: 0.5,
              textAnchor: 'middle',
              fill: 'black',
              fontSize: 10,
            },
            'methods-text': {
              ref: 'methods-rect',
              refY: 0.5,
              refX: 0.5,
              textAnchor: 'middle',
              fill: 'black',
              fontSize: 10,
            },
          },
          propHooks(meta) {
            const { name, budget, number, ...others } = meta
            if (!(name && budget && number)) {
              return meta
            }
            const rects = [
              { type: 'name', text: name },
              { type: 'attrs', text: budget },
              { type: 'methods', text: number },
            ]
            let offsetY = 0
            rects.forEach((rect) => {
              const height = rect.text.length * 12 + 16
              X6.ObjectExt.setByPath(
                others,
                `attrs/${rect.type}-text/text`,
                rect.text.join('\n'),
              )
              X6.ObjectExt.setByPath(others, `attrs/${rect.type}-rect/height`, height)
              X6.ObjectExt.setByPath(
                others,
                `attrs/${rect.type}-rect/transform`,
                'translate(0,' + offsetY + ')',
              )
              offsetY += height
            })
            others.size = { width: 160, height: offsetY }
            return others
          },
        },
        true,
      )
      // 继承
      Graph.registerEdge(
        'extends',
        {
          inherit: 'edge',
          attrs: {
            line: {
              strokeWidth: 1,
              stroke: "#7c68fc", // 指定 path 元素的填充色
            },
          },
        },
        true,
      )
      const graph = new Graph({
        container: document.getElementById('container'),
        width: 800,
        height: 700,
        background: {
          color: '#fff', // 设置画布背景颜色
        },
        grid: {
          size: 10,      // 网格大小 10px
          visible: true, // 渲染网格背景
        },
      })
      const data = [
        {
          "id": "1",
          "shape": "class",
          "name": [
            "工程1"
          ],
          "budget": [
            "预算"
          ],
          "number": [
            "100亿"
          ],

          "position": {
            "x": 300,
            "y": 40
          }
        },
        {
          "id": "2",
          "shape": "class",
          "name": [
            "子工程1-1"
          ],
          "budget": [
            "预算"
          ],
          "number": [
            "80亿"
          ],
          // "position": {
          //   "x": 200,
          //   "y": 200
          // }
        },
        {
          "id": "3",
          "shape": "extends",
          "source": "1",
          "target": "2"
        },
        {
          "id": "4",
          "shape": "class",
          "name": [
            "子工程1-2"
          ],
          "budget": [
            "预算"
          ],
          "number": [
            "20亿"
          ],
          // "position": {
          //   "x": 400,
          //   "y": 200
          // }
        },
        {
          "id": "5",
          "shape": "extends",
          "source": "1",
          "target": "4"
        },
        {
          "id": "6",
          "shape": "class",
          "name": [
            "子工程1-2-1"
          ],
          "budget": [
            "预算"
          ],
          "number": [
            "10亿"
          ],
          // "position": {
          //   "x": 400,
          //   "y": 350
          // }
        },
        {
          "id": "7",
          "shape": "extends",
          "source": "4",
          "target": "6"
        },
        {
          "id": "8",
          "shape": "class",
          "name": [
            "子工程1-2-1"
          ],
          "budget": [
            "预算"
          ],
          "number": [
            "10亿"
          ],
          // "position": {
          //   "x": 400,
          //   "y": 350
          // }
        },
        {
          "id": "9",
          "shape": "extends",
          "source": "1",
          "target": "8"
        },
        {
          "id": "10",
          "shape": "class",
          "name": [
            "子工程1-2-1"
          ],
          "budget": [
            "预算"
          ],
          "number": [
            "10亿"
          ],
          // "position": {
          //   "x": 400,
          //   "y": 350
          // }
        },
        {
          "id": "11",
          "shape": "extends",
          "source": "8",
          "target": "10"
        },
        {
          "id": "12",
          "shape": "class",
          "name": [
            "子工程1-2-1"
          ],
          "budget": [
            "预算"
          ],
          "number": [
            "10亿"
          ],
          // "position": {
          //   "x": 400,
          //   "y": 350
          // }
        },
        {
          "id": "13",
          "shape": "extends",
          "source": "8",
          "target": "12"
        }
      ]
      let nodes = []
      let edges = []
      let obj = {}
      data.forEach(v => {
        if (v.shape === "class") {
          nodes.push(v)
        }
        if (v.shape === "extends") {
          edges.push(v)
        }
      })
      obj.nodes = nodes
      obj.edges = edges
      const gridLayout = new Layout.DagreLayout({
        type: 'dagre',
        rankdir: 'TB',
        align: 'DL',
        ranksep: 50,
        nodesep: 50,
        controlPoints: true,
      })
      const newModel = gridLayout.layout(obj)
      graph.fromJSON(newModel)


      graph.on('node:collapse', ({ node }) => {
        node.toggleCollapse()
        const collapsed = node.isCollapsed()
        const collapse = (parent) => {
          const cells = parent.getChildren()
          if (cells) {
            cells.forEach((cell) => {
              if (collapsed) {
                cell.hide()
              } else {
                cell.show()
              }

              if (cell instanceof Group) {
                if (!cell.isCollapsed()) {
                  collapse(cell)
                }
              }
            })
          }
        }

        collapse(node)
      })
    },
  }
}
</script>

<style>

</style>