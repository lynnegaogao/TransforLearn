<template>
  <div class="container">
    <div class="title-text">
      Tokenize - From Text to Tokens
    </div>
    <div class="container" id="svgContainer">
      <svg id="tokenizeSvg">
      </svg>
    </div>

  </div>
</template>

<script>
import * as d3 from "d3";
import { shallowRef } from "vue"
import { CloseBold } from '@element-plus/icons-vue'
// import {getDataRange} from '../utils/detailview-utils'
export default {
  name: "TokenizeView",
  props: {
    // node: {
    //   type: Object,
    //   default: function(){return {}},
    // },
    id: {
      type: String,
      default: "",
    },
    text: {
      type: String,
      default: "",
    },
    pieces: {
      type: Array,
      default: function () { return []; },
    },
    tokens: {
      type: Array,
      default: function () { return []; },
    },
  },
  // emits:["exit"],
  data() {
    return {
      CloseBold: shallowRef(CloseBold),
    };
  },
  mounted() {
    this.redraw();
  },
  methods: {
    redraw() {
      // 移除原来已绘制的所有图元, 并在后续根据新的数据重新绘制
      d3.select("#svgContainer").selectAll('#tokenizeSvg > *').remove();
      // console.log("id",this.id)
      // console.log("text",this.text)
      // console.log("pieces",this.pieces.toString())
      // console.log("tokens",Math.max.apply(Math,this.tokens))
      let type = this.id.split("-")[0];
      let fontSize = 15
      let unitLength = type == "encoder" ? 10 : 25
      let textHeight = 40
      let pieceWidth = 80
      let tokenWidth = 60
      let tokenHeight = 30
      let pieceHeight = 30
      let nodeWidth = 100
      let tokenGap = 15
      let processGap = 70
      let textLength = this.text.length
      let tokensLength = this.pieces.length
      let height = (tokenGap + tokenHeight) * (tokensLength + 1)
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);
      let edgeOpacity = 0.5;
      let nodeColor=["#D8D8D8","#D8D8D8","#F5EFE6"]

      let svg = d3.select('#tokenizeSvg')
        .attr('width', '100%')
        .attr('height', height + 50)
        .attr('transform', `translate(-30,0)`);

      // input text
      let textRect = svg.append('g')
        .attr('id', type + '-input-text')
        .attr('transform', `translate(${processGap},${height / 2})`);
      textRect.append('rect')
        .attr('class', 'node')
        .attr('width', textLength * unitLength)
        .attr('height', textHeight)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr('fill', nodeColor[0]);
      textRect.append('text')
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .attr("x", (textLength * unitLength) / 2)
        .attr("y", textHeight / 2)
        .attr("font-size", fontSize + 'px')
        .text(this.text);
      textRect.append('text')
        .attr('class', 'label')
        .attr("x", (textLength * unitLength) / 2)
        .attr("y", textHeight + tokenGap)
        .text("Input Text");

      // word segmentations
      let piecesRect = svg.append('g')
        .attr('id', type + '-word-segmentations')
        .attr('transform', `translate(${(textLength * unitLength) + processGap * 2},0)`);
      piecesRect.append('text')
        .attr('class', 'label')
        .attr("x", pieceWidth / 2)
        .attr("y", height - 10)
        .text("Word Segmentations");
      for (let i = 0; i < tokensLength; i++) {
        // console.log(i - Math.round(tokensLength/2))
        let translateY = height / 2 + textHeight / 2 + (i - Math.round(tokensLength / 2)) * (tokenGap + tokenHeight)
        let unitPiece = piecesRect.append('g')
          .attr("id", "piece-" + (i + 1))
          .attr('transform', `translate(0,${translateY})`);
        unitPiece.append('rect').attr('class', 'node')
          .attr('width', pieceWidth)
          .attr('height', pieceHeight)
          .attr("rx", 5)
          .attr("ry", 5)
          .attr('fill', nodeColor[1]);
        unitPiece.append('text')
          .style("text-anchor", "middle")
          .style("dominant-baseline", "middle")
          .attr("x", pieceWidth / 2)
          .attr("y", pieceHeight / 2)
          .attr("font-size", fontSize + 'px')
          .text(this.pieces[i]);
        let linkDataElement = [{
          source: {
            x: -processGap,
            y: (Math.round(tokensLength / 2) - i) * (tokenGap + tokenHeight),
          },
          target: {
            x: 0,
            y: pieceHeight / 2,
          },
        }]
        unitPiece.append('path')
          .attr('class', 'edge')
          .data(linkDataElement)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)');
      }

      // word tokens
      let tokensRect = svg.append('g')
        .attr('id', type + '-word-tokens')
        .attr('transform', `translate(${(textLength * unitLength) + pieceWidth + processGap * 3},0)`);
      tokensRect.append('text')
        .attr('class', 'label')
        .attr("x", tokenWidth / 2)
        .attr("y", height - 10)
        .text("Word Tokens");
      for (let i = 0; i < tokensLength; i++) {
        let translateY = height / 2 + textHeight / 2 + (i - Math.round(tokensLength / 2)) * (tokenGap + tokenHeight)
        let unitToken = tokensRect.append('g')
          .attr("id", "token-" + (i + 1))
          .attr('transform', `translate(0,${translateY})`);
        unitToken.append('rect').attr('class', 'node')
          .attr('width', tokenWidth)
          .attr('height', tokenHeight)
          .attr("rx", 5)
          .attr("ry", 5)
          .attr('fill', nodeColor[2]);

        unitToken.append('text')
          .style("text-anchor", "middle")
          .style("dominant-baseline", "middle")
          .attr("x", tokenWidth / 2)
          .attr("y", tokenHeight / 2)
          .attr("font-size", fontSize + 'px')
          .text(this.tokens[i]);
        let linkDataElement1 = [{
          source: {
            x: -processGap,
            y: tokenHeight / 2,
          },
          target: {
            x: 0,
            y: tokenHeight / 2,
          },
        },]
        let linkDataElement2 = [{
          source: {
            x: tokenWidth,
            y: tokenHeight / 2,
          },
          target: {
            x: tokenWidth+processGap,
            y: (Math.round(tokensLength / 2) - i) * (tokenGap + tokenHeight),
          },
        },]
        unitToken.append('path')
          .attr('class', 'edge')
          .data(linkDataElement1)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)');
          unitToken.append('path')
          .attr('class', 'edge')
          .data(linkDataElement2)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)');
      }

      let embedding = svg.append('g')
        .attr('id', 'embedding-node')
        .style('opacity', edgeOpacity)
        .attr('transform', `translate(${(textLength * unitLength) + pieceWidth + tokenWidth + processGap * 4},${height / 2})`);
      embedding.append('rect')
        .attr('class', 'node')
        .attr('width', nodeWidth)
        .attr('height', textHeight)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr('fill', "#EADCA6");
      embedding.append('text')
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .attr("x", nodeWidth / 2)
        .attr("y", textHeight / 2)
        .attr("font-size", fontSize + 'px')
        .text('embedding');
        let linkDataElement = [{
          source: {
            x: nodeWidth,
            y: textHeight / 2,
          },
          target: {
            x: nodeWidth+processGap,
            y: textHeight / 2,
          },
        }]
        embedding.append('path')
          .attr('class', 'edge')
          .data(linkDataElement)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)');

      let pe = svg.append('g')
        .attr('id', 'pe-node')
        .style('opacity', edgeOpacity)
        .attr('transform', `translate(${(textLength * unitLength) + pieceWidth + tokenWidth + nodeWidth + processGap * 5},${height / 2})`);
      pe.append('rect')
        .attr('class', 'node')
        .attr('width', nodeWidth)
        .attr('height', textHeight)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr('fill', "#EADCA6");
      pe.append('text')
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .attr("x", nodeWidth / 2)
        .attr("y", textHeight / 2)
        .attr("font-size", fontSize + 'px')
        .text('PE');
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
.container {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: .5rem;
  background-color: rgb(240, 239, 239);
  ;
}

.title-text {
  font-size: 1.2em;
  font-weight: bold;
  color: #4a4a4a;
}

.label {
  font-size: 14px;
  text-anchor: middle;
  dominant-baseline: middle;
  fill: #4a4a4a;
}

.node {
  stroke: rgb(175, 175, 175);
  stroke-width: 2;

}
</style>