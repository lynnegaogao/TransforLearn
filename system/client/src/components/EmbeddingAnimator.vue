<template>
  <div class="container">
    <svg id="embeddingSvg" height="100%"></svg>
  </div>
</template>

<script>
import * as d3 from "d3";
import { getDataRange, getGapGridData, getGridData, getVisualizationSizeConstraint } from '../utils/detailview-utils'
// import {getLegendGradient} from '../utils/draw-utils'
// import {config} from '../utils/config'
export default {
  name: "EmbeddingAnimator",
  props: {
    highlightsIndex: {
      type: Number,
      default: 0,
    },
    curOutputColumnIndex: {
      type: Number,
      default: -1,
    },
    curTokenIndex: {
      type: Number,
      default: 0,
    },
    tokens: {
      type: Array,
      default: function () { return [2, 3]; },
    },
    embeddings: {
      type: Array,
      default: function () { return []; },
    },
    coefficient: {
      type: Number,
      default: 0,
    },
    pe: {
      type: Array,
      default: function () { return []; }
    },
    output: {
      type: Array,
      default: function () { return []; },
    },
  },
  emits: ['cleanComponentView', 'changeHilightsIndex'],
  data() {
    return {
      vocabSize: 32000,
    };
  },
  beforeUpdate() {
    if (this.oldHighlightsIndex != this.highlightsIndex) {
      this.oldHighlightsIndex = this.highlightsIndex;
      this.legalHighlightsIndex = this.highlightsIndex;
    }
    if (this.highlightsIndex >= this.output.length * this.output[0].length) { // this.highlightsIndex 超出范围了
      this.oldHighlightsIndex = 0;
      this.legalHighlightsIndex = 0;
    }
    this.redraw();
  },
  mounted() {
    this.init();
    this.redraw();
  },
  methods: {
    onClean() {
      this.$emit('cleanComponentView');
    },
    init() {
      // this.peDataRange = getDataRange(this.pe);
      this.embeddingsDataRange = getDataRange(this.embeddings);
    },
    redrawLines() {
      // 移除之前所绘制的内容
      d3.select(this.$el).selectAll('#embeddingSvg > *').remove();
    },
    redraw() {
      // console.log("tokens",this.tokens)
      // console.log("embeddings",this.embeddings)
      // console.log("coefficient",this.coefficient)
      let fontSize = 15
      let tokensLength = this.tokens.length
      let tokenGap = 30
      let tokenWidth = 60
      let tokenHeight = 30
      let processGap = 50
      let nodeWidth = 100
      let textHeight = 40
      let height = (tokenGap + tokenHeight) * (tokensLength + 1)
      let windowHeight = 600 >= height ? 600 : height
      let embeddingsDataRange = this.embeddingsDataRange;
      let tokensTranslateY = [];
      let nodeColor = ["#D8D8D8", "#D8D8D8", "#F5EFE6"]
      let colorScale = d3.interpolateRdBu;
      let edgeOpacity = 0.5;
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);

      let svg = d3.select('#embeddingSvg')
        .attr('width', '100%')
        .attr('height', windowHeight)
        .attr('transform', `translate(-30,-30)`);

      // tokenize
      let tokenize = svg.append('g')
        .attr('id', 'tokenize-node')
        .style('opacity', edgeOpacity)
        .attr('transform', `translate(${processGap},${windowHeight / 2})`);
      tokenize.append('rect')
        .attr('class', 'node')
        .attr('width', nodeWidth)
        .attr('height', textHeight)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr('fill', "#EADCA6");
      tokenize.append('text')
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .attr("x", nodeWidth / 2)
        .attr("y", textHeight / 2)
        .attr("font-size", fontSize + 'px')
        .text('tokenize');


      // word tokens
      let tokensGridGroupX = nodeWidth + processGap * 2
      let tokensGridGroupY = 0
      let tokensRect = svg.append('g')
        .attr('id', 'word-tokens')
        .attr('transform', `translate(${tokensGridGroupX},${tokensGridGroupY})`);
      tokensRect.append('text')
        .attr('class', 'label')
        .attr("x", tokenWidth / 2)
        .attr("y", windowHeight / 2 + textHeight / 2 + (tokensLength - 1 - Math.round(tokensLength / 2)) * (tokenGap + tokenHeight) + 70)
        .text("Word Tokens");
      for (let i = 0; i < tokensLength; i++) {
        tokensTranslateY.push(windowHeight / 2 + textHeight / 2 + (i - Math.round(tokensLength / 2)) * (tokenGap + tokenHeight))
        let unitToken = tokensRect.append('g')
          .attr("id", "token-" + (i + 1))
          .attr('transform', `translate(0,${tokensTranslateY[i]})`);
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
      

      }

      // 绘制 embedding matrix
      let embeddingMatrixConstraintGridCellWidth = 300;
      let embeddingMatrixConstraintGridCellHeight = 400;
      let embeddingMatrixGridGroupX = tokensGridGroupX + processGap + tokenWidth;
      let embeddingMatrixGridGroupY = (windowHeight - embeddingMatrixConstraintGridCellHeight) / 2;
      let embeddingMatrixGridData = getGridData([[0]], embeddingMatrixConstraintGridCellWidth, embeddingMatrixConstraintGridCellHeight);
      let embeddingMatrixGridGroup = svg.append("g").attr("class", "grid").attr("transform", `translate(${embeddingMatrixGridGroupX},${embeddingMatrixGridGroupY})`);
      let embeddingMatrixGridRow = embeddingMatrixGridGroup.selectAll(".row")  // 绘制每一行
        .data(embeddingMatrixGridData).enter().append('g').attr('class', 'row');
      embeddingMatrixGridRow
        .selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('fill', '#ECE7E7');

      let embeddingMatrixTotalGridWidth = embeddingMatrixConstraintGridCellWidth;
      let embeddingMatrixGridText = svg.append('text').attr("text-anchor", "middle");
      embeddingMatrixGridText
        .attr('transform', `translate(${embeddingMatrixGridGroupX + embeddingMatrixTotalGridWidth / 2},${embeddingMatrixGridGroupY + embeddingMatrixConstraintGridCellHeight + 20})`)
        .attr('class', 'label')
        .style('text-anchor', 'middle')
        .selectAll('.tspan')
        .data([`Embedding Matrix`, `(${this.vocabSize},${this.embeddings[0].length})`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);

      // 绘制 embeddings
      let xSize = 325;
      let ySize = 250;
      let embeddingsGridGroupX = embeddingMatrixGridGroupX + embeddingMatrixTotalGridWidth + processGap;
      let embeddingsGridGroupY = (windowHeight - (ySize + tokenGap * this.embeddings.length)) / 2 * 1.2;
      let embeddingsConstraintGridCellWidth = getVisualizationSizeConstraint(this.embeddings[0].length, 'x', xSize, ySize, 40);
      let embeddingsConstraintGridCellHeight = getVisualizationSizeConstraint(this.embeddings.length, 'y', xSize, ySize, 40);
      let embeddingsGridData = getGapGridData(this.embeddings, embeddingsConstraintGridCellWidth, embeddingsConstraintGridCellHeight, tokenGap);
      let embeddingsGridGroup = svg.append("g").attr("class", "grid").attr("transform", `translate(${embeddingsGridGroupX},${embeddingsGridGroupY})`);
      let embeddingsGridRow = embeddingsGridGroup.selectAll(".row")  // 绘制每一行
        .data(embeddingsGridData).enter().append('g').attr('class', 'row');
      embeddingsGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * embeddingsGridData[0].length + d.col == this.legalHighlightsIndex ? 'black' : null)
        .on('mouseover', (event, d) => {
          this.$emit('changeHilightsIndex', d.row * embeddingsGridData[0].length + d.col)// this.$emit('changeEquationIndex',newEquationIndex)
        })
        .style('fill', d => {
          let normlizedVal = (d.text - embeddingsDataRange.min) / (embeddingsDataRange.max - embeddingsDataRange.min);
          return colorScale(normlizedVal);
        });
      let embeddingsTotalGridWidth = embeddingsConstraintGridCellWidth * this.embeddings[0].length;
      let embeddingsTotalGridHeight = (embeddingsConstraintGridCellHeight + tokenGap) * this.embeddings.length;
      let embeddingsGridText = svg.append('text').attr("text-anchor", "middle");
      embeddingsGridText
        .attr('transform', `translate(${embeddingsGridGroupX + embeddingsTotalGridWidth / 2},${embeddingsGridGroupY + embeddingsTotalGridHeight})`)
        .attr('class', 'label')
        .text(`embeddings (${this.embeddings.length},${this.embeddings[0].length})`);

      let peGridGroupX =embeddingsGridGroupX + embeddingsTotalGridWidth + processGap
      let peGridGroupY =windowHeight / 2
      let pe = svg.append('g')
        .attr('id', 'pe-node')
        .style('opacity', edgeOpacity)
        .attr('transform', `translate(${peGridGroupX },${peGridGroupY})`);
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

      let linkData = []
      for (let i = 0; i < this.tokens.length; i++) {
        let tokenLinkData= {
          source: {
            x: processGap+nodeWidth,
            y: windowHeight / 2+textHeight/2,
          },
          target: {
            x: tokensGridGroupX,
            y: tokensGridGroupY + tokensTranslateY[i]+tokenHeight / 2,
          },
          class: 'token-link',
          id:(i+1)
        }
        let tokenMatrixLinkData= {
          source: {
            x: tokensGridGroupX + tokenWidth,
            y: tokensGridGroupY + tokensTranslateY[i]+tokenHeight / 2,
          },
          target: {
            x: embeddingMatrixGridGroupX + embeddingMatrixGridData[0][0].x,
            y: embeddingMatrixGridGroupY + embeddingMatrixGridData[0][0].y + (this.tokens[i] / this.vocabSize) * embeddingMatrixGridData[0][0].height,
          },
          class: 'token-matrix-link',
          id:(i+1)
        }
        let matrixEmbeddingLinkData= {
          source: {
            x: embeddingMatrixGridGroupX + embeddingMatrixGridData[0][0].x+ embeddingMatrixGridData[0][0].width,
            y: embeddingMatrixGridGroupY + embeddingMatrixGridData[0][0].y + (this.tokens[i] / this.vocabSize) * embeddingMatrixGridData[0][0].height,
          },
          target: {
            x: embeddingsGridGroupX + embeddingsGridData[i][0].x,
            y: embeddingsGridGroupY + embeddingsGridData[i][0].y + embeddingsGridData[i][0].height/2,
          },
          class: 'matrix-embedding-link',
          id:(i+1)
        }
        let peLinkData= {
          source: {
            x: embeddingsGridGroupX + embeddingsGridData[i][0].x+xSize,
            y: embeddingsGridGroupY + embeddingsGridData[i][0].y + embeddingsGridData[i][0].height/2,
          },
          target: {
            x: peGridGroupX,
            y: peGridGroupY+textHeight/2,
          },
          class: 'pe-link',
          id:(i+1)
        }
        linkData.push(tokenLinkData)
        linkData.push(tokenMatrixLinkData)
        linkData.push(matrixEmbeddingLinkData)
        linkData.push(peLinkData)
      }
      let edgeGroup = svg.append("g").attr("class", "edge-group");
      edgeGroup.selectAll("path.edge").data(linkData).enter().append('path')
        .attr('id', d => d.id != undefined ? d.id : null)
        .attr('class', d => d.class != undefined ? d.class : null)
        .attr('d', d => linkGen({ source: d.source, target: d.target }))
        .style('fill', 'none')
        .style('stroke-width', '2px')
        .style('opacity', edgeOpacity)
        .style('stroke', 'rgb(175, 175, 175)');

    },
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

.node {
  stroke: rgb(175, 175, 175);
  stroke-width: 2;
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
  color: #4a4a4a;
}
</style>