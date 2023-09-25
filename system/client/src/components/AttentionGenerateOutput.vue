<template>
  <svg ref="attentionOuputSvg" ></svg>
</template>

<script>
import * as d3 from "d3";
import { getVisualizationSizeConstraint, getDataRange, getGridData } from '../utils/detailview-utils'
// import { getVisualizationSizeConstraint, getDataRange } from '../utils/detailview-utils'
// import {getDataRange} from '../utils/detailview-utils'
// import {config} from '../utils/config'
export default {
  name: "AttentionGenerateOutput",
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
    detailViewNodeType: {
      type: String,
      default: '',
    },
    detailViewNodeId: {
      type: String,
      default: '',
    },
    highLightArray: {
      type: Array,
      default: function () { return []; },
    },
  },
  emits: ['changeHighLightArray'],
  data() {
    return {
    };
  },
  watch: {
    highLightArray(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        this.drawMatMul2();
      })
    }
  },
  beforeUpdate() {
  },
  mounted() {
    this.drawMatMul2();
  },
  methods: {
    drawMatMul2() {
      // 移除之前所绘制的内容
      d3.select(this.$refs.attentionOuputSvg).selectAll('*').remove();
      let svg = d3.select(this.$refs.attentionOuputSvg)
        .attr('id', "scale-Svg")
        .attr("width", "100%")
        .attr('height', "450px")
        .attr('transform', `translate(1,10)`)
      // title
      let titleOffsetX = 140
      let titleOffsetY = 50
      svg.append('text')
        .attr('transform', `translate(${titleOffsetX},${titleOffsetY})`)
        .attr('class', 'label')
        .style('font-weight', 'bold')
        .text('Step.4 Matrix Multiply');

      let type = this.detailViewNodeId.split('-')[0];
      let blockNum = this.detailViewNodeId.split('-')[4];
      let headNum = this.detailViewNodeId.split('-')[6];
      let attentionType = this.detailViewNodeId.split('-')[1] == 'cross' ? 'cross-attention' : 'self-attention'
      let headData;
      var self = this
      if (type == 'encoder') {
        headData = self.encoder.self_attn[blockNum]
      } else {
        if (attentionType == 'cross-attention') {
          headData = self.decoder.cross_attn[blockNum]
        } else {
          headData = self.decoder.self_attn[blockNum]
        }
      }

      let operatorRadius = 10;
      let interval = 30;
      let maximumCellSize = 20;
      let colorScale = d3.interpolateRdBu;

      let softmaxGroupX = 5;
      let softmaxGroupY = 130;
      let xSizeOfSoftmaxGrid = 200;
      let ySizeOfSoftmaxGrid = 200;
      let softmaxData = headData['after_softmax'][headNum];
      let singleGridWidth = Math.max(xSizeOfSoftmaxGrid / softmaxData[0].length, maximumCellSize)
      let xRealSize = singleGridWidth * softmaxData[0].length;
      let softmaxDataRange = { max: 1, min: 0 };
      let softmaxText = `Normalized Score (${softmaxData.length},${softmaxData[0].length})`;
      let softmaxSymbol = '*';

      let vGroupX = softmaxGroupX + xRealSize+30 ;
      let vGroupY = softmaxGroupY;
      let xSizeOfVGrid = 350;
      let ySizeOfVGrid = 200;
      let vData = headData.mat_QKV[headNum][2];
      let vDataRange = getDataRange(vData);
      let vText = `V (${vData.length},${vData[0].length})`;
      let vSymbol = '=';

      let outputGroupX = vGroupX + xSizeOfVGrid + interval;
      let outputGroupY = vGroupY;
      let xSizeOfOutputGrid = xSizeOfVGrid;
      let ySizeOfOutputGrid = ySizeOfVGrid;
      let outputData = headData['attention_output'][headNum];
      let outputDataRange = getDataRange(outputData);
      let outputText = `output (${outputData.length},${outputData[0].length})`;
      let outputSymbol = null;

      let softmaxGroup = svg.append('g').attr('class', 'softmax-weight-group')
        .attr('transform', `translate(${softmaxGroupX},${softmaxGroupY})`);
      let vGroup = svg.append('g').attr('class', 'value-group')
        .attr('transform', `translate(${vGroupX - 20},${vGroupY})`);
      let outputGroup = svg.append('g').attr('class', 'output-group')
        .attr('transform', `translate(${outputGroupX},${outputGroupY})`);
      drawMatrix(softmaxGroup, 'softmax', softmaxData, xSizeOfSoftmaxGrid, ySizeOfSoftmaxGrid, interval, maximumCellSize, softmaxDataRange, colorScale, softmaxText, softmaxSymbol);
      drawMatrix(vGroup, 'V', vData, xSizeOfVGrid, ySizeOfVGrid, interval, maximumCellSize, vDataRange, colorScale, vText, vSymbol);
      drawMatrix(outputGroup, 'output', outputData, xSizeOfOutputGrid, ySizeOfOutputGrid, interval, maximumCellSize, outputDataRange, colorScale, outputText, outputSymbol);
      // function drawMatirx(group, data, sizeX, sizeY, maximumCellSize, dataRange, colorMapper, text, symbol){
      function drawMatrix(group, type, data, sizeX, sizeY, xInetrval, maximumCellSize, dataRange, colorMapper, text, symbol) {
        let constraintGridCellWidth = getVisualizationSizeConstraint(data[0].length, 'x', sizeX, sizeY, maximumCellSize);
        let constraintGridCellHeight = getVisualizationSizeConstraint(data.length, 'y', sizeX, sizeY, maximumCellSize);

        let gridData = getGridData(data, constraintGridCellWidth, constraintGridCellHeight);
        let gridGroup = group.append("g").attr("class", "grid")
        let gridRow = gridGroup.selectAll(".row")  // 绘制每一行
          .data(gridData).enter().append('g').attr('class', 'row');
          gridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .attr('stroke', function(d) {
            if (type == "softmax") {
              if (self.highLightArray[0] == d.row) return 'black';
              else return null;
            } else if (type == "V") {
              if (self.highLightArray[1] == d.col) return 'black';
              else return null;
            } else {
              if (self.highLightArray[0] == d.row && self.highLightArray[1] == d.col) {
                return 'black';
              }
              else return null;
            }
          })
          .style('stroke-width', 1.2)
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorMapper(normlizedVal);
          })
          .on('click', (event, d) => {
            if (type == "output") {
              if (self.highLightArray[0] != d.row || self.highLightArray[1] != d.col) {
                self.$emit('changeHighLightArray', [d.row, d.col]);
              }
              else self.$emit('changeHighLightArray', [-1, -1]);
            }
          })


        let totalGridWidth = constraintGridCellWidth * data[0].length;
        let totalGridHeight = constraintGridCellHeight * data.length;

        let gridText = group.append('text').attr("text-anchor", "middle");
        gridText
          .attr('transform', `translate(${totalGridWidth / 2},${-20})`)
          .attr('class', 'label')
          .text(text);

        if (symbol == '=') {
          let symbolGroup = group.append('g')
            .attr('id', 'equation-g')
            .attr('transform', `translate(${totalGridWidth + xInetrval / 2 + 10},${totalGridHeight / 2})`)
          symbolGroup.append('circle')
            .attr('class', 'operator')
            .attr('r', operatorRadius)
          symbolGroup.append('text')
            .attr('class', 'operatorText')
            .text(symbol)
        } else if (symbol == '*') {
          let symbolGroup = group.append('g')
            .attr('id', 'crossmultiply-g')
            .attr('transform', `translate(${totalGridWidth + xInetrval / 2 + 10},${totalGridHeight / 2})`)
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
        }
      }
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
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