<template>
  <div class="container">
    <div class="box">
      <div class="control-pannel">
        <div class="title-text">
          Concatenate and Linear Projection
        </div>
        <el-tooltip content="Quit from Concatenation View." placement="top" effect="dark">
          <el-button type="primary" :icon="CloseBold" plain circle @click="onExit()" />
        </el-tooltip>
      </div>
      <div>
        <svg ref="concaAndLinear"></svg>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";
import { getVisualizationSizeConstraint, getGridData, getDataRange } from '../utils/detailview-utils'
import { shallowRef } from "vue"
import { CloseBold } from '@element-plus/icons-vue'
export default {
  name: "ConcatenateView",
  props: {
    encoder: {
      type: Object,
      default: function () { return {}; },
    },
    decoder: {
      type: Object,
      default: function () { return {}; },
    },
    curIter: {
      type: Number,
      default: 1,
    },
    attentionParams: {
      type: Object,
      default: function () { return {}; },
    },
    detailViewNodeType: {
      type: String,
      default: '',
    },
    detailViewNodeId: {
      type: String,
      default: '',
    },

  },
  emits: ["exit", 'getParams'],
  data() {
    return {
      CloseBold: shallowRef(CloseBold),
      highlights: [],
      order: 0,
      openHighlights: true,
    };
  },
  created() {
  },
  beforeUpdate() {

  },
  mounted() {
    this.onGetParams()
    this.drawConcaAndLinear()
  },
  methods: {
    onExit() {
      console.log("exit from the current detailview.");
      this.$emit('exit');
    },
    onGetParams() {
      let nodeSlice = this.detailViewNodeId.split('-')
      let type = nodeSlice[0]
      let attentionType = nodeSlice[1]
      var self = this
      if (type == 'encoder') {
        self.$emit('getParams', type + '-' + nodeSlice[4] + '-full-self-attention')
      } else if (type == 'decoder') {
        if (attentionType == 'masked self') {
          self.$emit('getParams', type + '-' + nodeSlice[4] + '-masked-self-attention')
        } else {
          self.$emit('getParams', type + '-' + nodeSlice[4] + '-full-cross-attention')
        }
      }
    },
    drawConcaAndLinear() {
      d3.select(this.$refs.concaAndLinear).selectAll('*').remove();
      let svg = d3.select(this.$refs.concaAndLinear)
        .attr('id', "concaAndLinear-Svg")
        .attr("width", "100%")
        .attr('height', "500px")
        .attr('transform', `translate(1,10)`)

      let type = this.detailViewNodeId.split('-')[0];
      let blockNum = this.detailViewNodeId.split('-')[4];
      let attentionType = this.detailViewNodeId.split('-')[1] == 'cross' ? 'cross-attention' : 'self-attention'
      let outputWeights = this.attentionParams[1][0]
      let outputBias = this.attentionParams[1][1]
      var self = this
      let headData;
      if (type == 'encoder') {
        headData = self.encoder.self_attn[blockNum]
      } else {
        if (attentionType == 'cross-attention') {
          headData = self.decoder.cross_attn[blockNum]
        } else {
          headData = self.decoder.self_attn[blockNum]
        }
      }

      let groupX = 30;
      let groupY = 50;
      let xSizeOfWeightGrid = 128 * 3;
      let ySizeOfWeightGrid = 128 * 3;
      let xSizeOfConcatenationGrid = 100;
      let ySizeOfConcatenationGrid = 128 * 3;
      let xSizeOfBiasGrid = 20;
      let ySizeOfBiasGrid = 128 * 3;
      let xSizeOfOutputGrid = 100;
      let ySizeOfOutputGrid = 128 * 3;
      let interval = 100;
      let maximumCellSize = 30;
      let colorScale = d3.interpolateRdBu;
      let paramsColorScale = d3.interpolateBrBG;
      let operatorRadius = 10;

      let groupWeight = svg.append('g').attr('class', 'weight-group')
        .attr('transform', `translate(${groupX},${groupY})`);
      let groupConcatenation = svg.append('g').attr('class', 'concatenation-group')
        .attr('transform', `translate(${groupX + (xSizeOfWeightGrid + interval)},${groupY})`);
      let groupBias = svg.append('g').attr('class', 'bias-group')
        .attr('transform', `translate(${groupX + xSizeOfWeightGrid + xSizeOfConcatenationGrid + 2 * interval},${groupY})`);
      let groupOutput = svg.append('g').attr('class', 'output-group')
        .attr('transform', `translate(${groupX + xSizeOfWeightGrid + xSizeOfConcatenationGrid + xSizeOfBiasGrid + 3 * interval},${groupY})`);

      let weightData = outputWeights
      let weightDataRange = getDataRange(outputWeights)
      let concatenationData = transpose(headData.concatenation) // 需要转置
      let concatenationDataRange = getDataRange(concatenationData)
      let biasData = outputBias.map(d => [d]); // 需要转置
      let biasDataRange = getDataRange(biasData)
      let outputData = transpose(headData.output) // 需要转置
      let outputDataRange = getDataRange(outputData)

      drawMatirx.call(this, groupWeight, 'weights', weightData, xSizeOfWeightGrid, ySizeOfWeightGrid, maximumCellSize, weightDataRange,
        paramsColorScale, `Projection Weight (${weightData.length},${weightData[0].length})`, '*');
      drawMatirx.call(this, groupConcatenation, 'conca', concatenationData, xSizeOfConcatenationGrid, ySizeOfConcatenationGrid, maximumCellSize, concatenationDataRange,
        colorScale, `Concatenation (${concatenationData.length},${concatenationData[0].length})`, '+');
      drawMatirx.call(this, groupBias, 'bias', biasData, xSizeOfBiasGrid, ySizeOfBiasGrid, maximumCellSize, biasDataRange,
        paramsColorScale, `Projection Bias (${biasData.length},${biasData[0].length})`, '=');
      drawMatirx.call(this, groupOutput, 'output', outputData, xSizeOfOutputGrid, ySizeOfOutputGrid, maximumCellSize, outputDataRange,
        colorScale, `Output (${outputData.length},${outputData[0].length})`, null);

      function transpose(data) {
        let rows = data.length;
        let cols = data[0].length;
        let transposedData = [];
        for (let c = 0; c < cols; c++) {
          let column = [];
          for (let r = 0; r < rows; r++) {
            column.push(data[r][c]);
          }
          transposedData.push(column);
        }
        return transposedData;
      }

      function drawMatirx(group, type, data, sizeX, sizeY, maximumCellSize, dataRange, colorMapper, text, symbol) {
        let constraintGridCellWidth = getVisualizationSizeConstraint(data[0].length, 'x', sizeX, sizeY, maximumCellSize);
        let constraintGridCellHeight = getVisualizationSizeConstraint(data.length, 'y', sizeX, sizeY, maximumCellSize);

        let gridData = getGridData(data, constraintGridCellWidth, constraintGridCellHeight);
        if (type == 'conca') {
          for (let i = 0; i < 8; i++) {
            let concaGroup=group.append('g').attr('id', 'gridGroup-' + i)
            let gridGroup = concaGroup.append("g").attr("class", "grid")
            let gridRow = gridGroup.selectAll(".row")  // 绘制每一行
              .data(gridData.slice(i * 64, (i + 1) * 64 + 1)).enter().append('g').attr('class', 'row')
            gridRow
              .selectAll(".square")
              .data(d => d).enter().append('rect')
              .attr('class', 'square')
              .attr("x", d => d.x).attr("y", d => d.y)
              .attr("width", d => d.width).attr("height", d => d.height)
              .attr('opacity', 0.9)
              .style('fill', d => {
                let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
                return colorMapper(normlizedVal);
              })
              concaGroup.on('mouseover', (event,d) => {
                console.log(d)
                let linePath = d3.line();
                let squareHighLight =  concaGroup.append('g')
                  .attr('id', 'square-g')
                  .attr('transform', `translate(${0},${48 * i})`)
                let lines = [
                  [[0, 0], [xSizeOfConcatenationGrid, 0]],
                  [[0, 0], [0, 48]],
                  [[0, 48], [xSizeOfConcatenationGrid, 48]],
                  [[xSizeOfConcatenationGrid, 0], [xSizeOfConcatenationGrid, 48]]
                ]
                for (let j = 0; j < lines.length; j++) {
                  squareHighLight.append('path')
                    .attr('d', linePath(lines[j]))
                    .attr('stroke', 'black')
                    .attr('stroke-width', 2)
                }
                squareHighLight.append('text')
                  .attr('class', 'label')
                  .attr('transform', `translate(${xSizeOfConcatenationGrid / 2},${24})`)
                  .text('head #' + (i + 1))
            })
              .on('mouseout', () => {
                  d3.select('#square-g').remove()
              })
          }
        } else {
          let gridGroup = group.append("g").attr("class", "grid")//.attr("transform",`translate(${headNum * ( sizeX + betweenInterval ) },${0})`);
          let gridRow = gridGroup.selectAll(".row")  // 绘制每一行
            .data(gridData).enter().append('g').attr('class', 'row');
          gridRow
            .selectAll(".square")
            .data(d => d).enter().append('rect')
            .attr('class', 'square')
            .attr("x", d => d.x).attr("y", d => d.y)
            .attr("width", d => d.width).attr("height", d => d.height)
            .attr('opacity', 0.9)
            .style('fill', d => {
              let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
              return colorMapper(normlizedVal);
            })
        }



        let totalGridWidth = constraintGridCellWidth * data[0].length;
        let totalGridHeight = constraintGridCellHeight * data.length;

        let gridText = group.append('text').attr("text-anchor", "middle");
        gridText
          .attr('transform', `translate(${totalGridWidth / 2},${-15})`)
          .attr('class', 'label')
          .text(text);

        if (symbol != null) {
          if (symbol == '*') {
            let symbolGroup = group.append('g')
              .attr('id', 'crossmultiply-g')
              .attr('transform', `translate(${totalGridWidth + interval / 2},${totalGridHeight / 2})`)
            symbolGroup.append('circle')
              .attr('class', 'operator')
              .attr('r', operatorRadius)
            symbolGroup.append('text')
              .attr('y', 5.5)
              .attr('font-weight', 'bold')
              .attr('text-anchor', 'middle')
              .attr('dominant-baseline', 'middle')
              .attr('fill', 'rgb(175, 175, 175)')
              .attr('font-size', '23px')
              .text('*')
          } else {
            let symbolGroup = group.append('g')
              .attr('id', 'equation-g')
              .attr('transform', `translate(${totalGridWidth + interval / 2},${totalGridHeight / 2})`)
            symbolGroup.append('circle')
              .attr('class', 'operator')
              .attr('r', operatorRadius)
            symbolGroup.append('text')
              .attr('class', 'operatorText')
              .text(symbol)
          }
        }
      }



    }

  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  border-radius: .5rem;
  background-color: white;
  width: 100%;
  height: 100%;
}

.box {
  padding: 5px 15px 10px 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  /* align-items: center; */
  align-items: stretch;
  width: 100%;
  height: 100%;
}

.control-pannel {
  display: flex;
  position: relative;
  flex-direction: row;
  /* justify-content: center; */
  justify-content: space-between;
  align-items: center;
}

.title-text {
  font-size: 1.1em;
  margin: auto auto;
  display: inline-block;
  vertical-align: middle;
  text-align: center;
  font-weight: bold;
  color: #4a4a4a;
}

.buttons {
  cursor: pointer;
  margin-left: 5px;
  margin-right: 5px;
  margin-top: 5px;
  margin-bottom: 5px;
}

.control-button {
  color: gray;
  /* font-size: 15px; */
  opacity: 0.8;
  cursor: pointer;
  margin-bottom: 2.5px;
}

.control-button:not(:first-child) {
  margin-left: 5px;
}

.label {
  font-size: 14px;
  text-anchor: middle;
  dominant-baseline: middle;
  fill: #4a4a4a;
}

.operator {
  fill: rgb(235, 235, 235);
  stroke: rgb(175, 175, 175);
  stroke-width: 1
}

.operatorText {
  font-size: 12px;
  font-weight: bold;
  text-anchor: middle;
  dominant-baseline: middle;
  fill: rgb(175, 175, 175);
}
</style>