<template>
  <div class="container">
    <div class="box">
      <div class="control-pannel">
        <div class="title-text">
          Generate Query, Key and Value in each head from Input(s)
        </div>
        <el-tooltip content="Quit from Attention Head View." placement="top" effect="dark">
          <el-button type="primary" :icon="CloseBold" plain circle @click="onExit()" />
        </el-tooltip>
      </div>
      <div id="attention-head-svg">
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";
import { getDataRange, getGridData, getVisualizationSizeConstraint } from '../utils/detailview-utils'
import { shallowRef } from "vue"
import { CloseBold, Switch } from '@element-plus/icons-vue'
export default {
  name: "AttentionHeadView",
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
    curOrder: {
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
    attentionParams: {
      type: Object,
      default: function () { return {}; },
    },
    highlights: {
      type: Array,
      default: function () { return []; },
    },

  },
  emits: ["exit", 'getParams', 'changeOrderAndHilights'],
  data() {
    return {
      CloseBold: shallowRef(CloseBold),
      Switch: shallowRef(Switch),
      openHighlights: true,
    };
  },
  watch: {
    detailViewNodeId(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        this.onGetParams()
      })
    },
    curIter(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        this.drawAttentionHead()
      })
    },
    attentionParams(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        this.drawAttentionHead()
      })
    },
    highlights(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        this.drawAttentionHead()
      })
    },
  },
  mounted() {
    this.onGetParams();
    this.drawAttentionHead();
  },
  methods: {
    onExit() {
      console.log("exit from the current detailview.");
      this.$emit('exit');
    },
    onHighlights() {
      // let content = document.getElementById('highlightsBtn').innerHTML;
      // if(content=='Close Highlights'){
      if (this.openHighlights) {
        document.getElementById('highlightsBtn').innerHTML = 'Open  Highlights';
        this.openHighlights = false;
      } else {
        document.getElementById('highlightsBtn').innerHTML = 'Close Highlights';
        this.openHighlights = true;
      }
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
    drawAttentionHead() {
      let type = this.detailViewNodeId.split('-')[0];
      let blockNum = this.detailViewNodeId.split('-')[4];
      let headNum = this.detailViewNodeId.split('-')[6];
      let headParams = this.attentionParams[0][headNum];
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

      d3.select('#attention-head-svg').selectAll('*').remove()
      let svg = d3.select('#attention-head-svg')
        .append('svg')
        .attr('id', "attentionHeadSvg")
        .attr("width", "100%")
        .attr('height', "700px")
        .attr('transform', `translate(80,0)`)

      this.drawWeight(svg, headParams)
      this.drawInput(svg, headData, attentionType)
      this.drawBiasesAndOuputs(svg, headParams, headData, headNum)
    },

    drawWeight(svg, headParams) {
      let paramsColorScale = d3.interpolateBrBG;
      let weightGridGroupX = 40;
      let weightGridGroupY = 60;
      let weightXSizeOfEachGrid = 260;
      let weightYSizeOfEachGrid = 160;
      let weightInterval = 60;
      let maximumCellSize = 40;
      let operatorRadius = 10;

      let WqWkWvGroup = svg.append('g').attr('class', 'weights-QKV-group')
        .attr('transform', `translate(${weightGridGroupX},${weightGridGroupY})`);

      drawWeight.call(this, WqWkWvGroup, weightInterval, 0, weightXSizeOfEachGrid, weightYSizeOfEachGrid, maximumCellSize)
      drawWeight.call(this, WqWkWvGroup, weightInterval, 1, weightXSizeOfEachGrid, weightYSizeOfEachGrid, maximumCellSize)
      drawWeight.call(this, WqWkWvGroup, weightInterval, 2, weightXSizeOfEachGrid, weightYSizeOfEachGrid, maximumCellSize)

      function drawWeight(group, betweenInterval, order, sizeX, sizeY, maximumCellSize) {
        // 绘制 Weight Q
        let weightData = headParams[order][0];
        let dataRange = getDataRange(weightData);
        let text;
        if (order == 0) {
          text = `Query Weight (${weightData.length},${weightData[0].length}) `;
        } else if (order == 1) {
          text = `Key Weight (${weightData.length},${weightData[0].length}) `
        } else if (order == 2) {
          text = `Value Weight (${weightData.length},${weightData[0].length}) `
        } else {
          return null;
        }
        let weightConstraintGridCellWidth = getVisualizationSizeConstraint(weightData[0].length, 'x', sizeX, sizeY, maximumCellSize);
        let weightConstraintGridCellHeigh = getVisualizationSizeConstraint(weightData.length, 'y', sizeX, sizeY, maximumCellSize);
        // 对 input 进行转置 得到 inputData, 以进行矩阵乘法
        let weightGridData = getGridData(weightData, weightConstraintGridCellWidth, weightConstraintGridCellHeigh);
        let weightGridGroup = group.append("g").attr("class", "grid").attr("transform", `translate(${0},${order * (sizeY + betweenInterval)})`);
        let weightGridRow = weightGridGroup.selectAll(".row")  // 绘制每一行
          .data(weightGridData).enter().append('g').attr('class', 'row');
        weightGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke-width', 0.4)
          .style('stroke', d => {
            if (order == this.curOrder && d.row == this.highlights[0]) return 'black'
            else return null;
          })
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return paramsColorScale(normlizedVal);
          });
        let weightTotalGridWidth = weightConstraintGridCellWidth * weightData[0].length;
        // let inputTotalGridHeight = inputConstraintGridCellHeigh * cols;
        let weightGridText = group.append('text').attr("text-anchor", "middle");
        weightGridText
          .attr('transform', `translate(${0 + weightTotalGridWidth / 2},${order * (sizeY + betweenInterval) - betweenInterval / 3})`)
          .attr('class', 'label')
          .text(text);
        let crossMultiply = group.append('g')
          .attr('id', 'crossmultiply-g')
          .attr('transform', `translate(${0 + weightTotalGridWidth + 30},${order * (sizeY + betweenInterval) + sizeY / 2})`)
        crossMultiply.append('circle')
          .attr('class', 'operator')
          .attr('r', operatorRadius)
        crossMultiply.append('text')
          .attr('y', 5.5)
          .attr('font-weight', 'bold')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', 'rgb(175, 175, 175)')
          .attr('font-size', '23px')
          .text('*')

      }
    },

    drawInput(svg, headData, attentionType) {
      let colorScale = d3.interpolateRdBu;
      let maximumCellSize = 30;
      let yInerval = 60;
      if (attentionType == 'cross-attention') {
        let qInputGridGroupX = 360;
        let qInputGridGroupY = 60;
        let qInputXSizeOfGrid = 100;
        let qInputYSizeOfGrid = 160;

        let kvInputGridGroupX = qInputGridGroupX;
        let kvInputGridGroupY = qInputGridGroupY + qInputYSizeOfGrid + yInerval;
        let kvInputXSizeOfGrid = 100;
        let kvInputYSizeOfGrid = 2 * qInputYSizeOfGrid + yInerval;

        let qInputGridGroup = svg.append("g").attr("class", "grid").attr("transform", `translate(${qInputGridGroupX},${qInputGridGroupY})`);
        let kvInputGridGroup = svg.append("g").attr("class", "grid").attr("transform", `translate(${kvInputGridGroupX},${kvInputGridGroupY})`);

        let qInputData = transpose(headData.input[0]);
        let kvInputData = transpose(headData.input[1]);
        let qInputDataRange = getDataRange(qInputData);
        let kvInputDataRange = getDataRange(kvInputData);

        let qText = `Input (${qInputData.length},${qInputData[0].length})`;
        let kvText = `Input (${kvInputData.length},${kvInputData[0].length}) from encoder`;

        drawInput.call(this, qInputGridGroup, 'Q', qInputData, qInputXSizeOfGrid, qInputYSizeOfGrid, qInputDataRange, colorScale, maximumCellSize, qText);
        drawInput.call(this, kvInputGridGroup, 'KV', kvInputData, kvInputXSizeOfGrid, kvInputYSizeOfGrid, kvInputDataRange, colorScale, maximumCellSize, kvText);
      } else {
        let InputGridGroupX = 360;
        let InputGridGroupY = 60;
        let InputXSizeOfGrid = 120;
        let InputYSizeOfGrid = 600;

        let InputGridGroup = svg.append("g").attr("class", "grid").attr("transform", `translate(${InputGridGroupX},${InputGridGroupY})`);

        let InputData = transpose(headData.input[0]);
        let InputDataRange = getDataRange(InputData)
        let inputText = `Input (${InputData.length},${InputData[0].length})`;

        drawInput.call(this, InputGridGroup, 'QKV', InputData, InputXSizeOfGrid, InputYSizeOfGrid, InputDataRange, colorScale, maximumCellSize, inputText);
      }

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

      function drawInput(group, type, data, sizeX, sizeY, dataRange, colorMap, maximumCellSize, text) {
        let rows = data.length;
        let cols = data[0].length;
        let constraintGridCellWidth = getVisualizationSizeConstraint(cols, 'x', sizeX, sizeY, maximumCellSize);
        let constraintGridCellHeight = getVisualizationSizeConstraint(rows, 'y', sizeX, sizeY, maximumCellSize);
        let gridData = getGridData(data, constraintGridCellWidth, constraintGridCellHeight);
        let gridRow = group.selectAll(".row")  // 绘制每一行
          .data(gridData).enter().append('g').attr('class', 'row');
        gridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke-width', 0.4)
          .style('stroke', d => {
            if (type == 'Q') {
              if (d.col == this.highlights[1] && this.curOrder == 0) return 'black';
            } else if (type == 'KV') {
              if (d.col == this.highlights[1] && this.curOrder > 0) return 'black'
            } else if (type == 'QKV') {
              if (d.col == this.highlights[1]) return 'black'
            } else return null;
          })
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorMap(normlizedVal);
          });
        let totalGridWidth = constraintGridCellWidth * cols;
        // let inputTotalGridHeight = inputConstraintGridCellHeigh * cols;
        let gridText = group.append('text').attr("text-anchor", "middle");
        gridText
          .attr('transform', `translate(${totalGridWidth / 2},${-20})`)
          .attr('class', 'label')
          .text(text);
      }

    },

    drawBiasesAndOuputs(svg, headParams, headData, headNum) {
      let colorScale = d3.interpolateRdBu;
      let paramsColorScale = d3.interpolateBrBG;
      let operatorRadius = 10;
      let groupX = 550;
      let groupY = 60;
      let biasXSizeOfEachGrid = 25;
      let biasYSizeOfEachGrid = 160;
      let biasInterval = 60;
      let maximumCellSize = 30;
      let outputXSizeOfEachGrid = 80;
      let outputYSizeOfEachGrid = 160;

      let group = svg.append('g').attr('class', 'biases-output-QKV-group')
        .attr('transform', `translate(${groupX},${groupY})`);

      drawBiasAndOutput.call(this, group, biasInterval, 0, biasXSizeOfEachGrid, biasYSizeOfEachGrid, outputXSizeOfEachGrid, outputYSizeOfEachGrid, maximumCellSize);
      drawBiasAndOutput.call(this, group, biasInterval, 1, biasXSizeOfEachGrid, biasYSizeOfEachGrid, outputXSizeOfEachGrid, outputYSizeOfEachGrid, maximumCellSize);
      drawBiasAndOutput.call(this, group, biasInterval, 2, biasXSizeOfEachGrid, biasYSizeOfEachGrid, outputXSizeOfEachGrid, outputYSizeOfEachGrid, maximumCellSize);

      function drawBiasAndOutput(group, betweenInterval, order, sizeX, sizeY, outputSizeX, outputSizeY, maximumCellSize) {
        let biasData = headParams[order][1].map(d => [d]);
        let dataRange = getDataRange(biasData);
        let text;
        let outputData = headData.mat_QKV[headNum][order];
        let outputDataRange = getDataRange(outputData);
        let outputText;
        if (order == 0) {
          text = `Query Bias (${biasData.length}) `;
          outputText = `Query (${outputData[0].length},${outputData.length}) `;
        } else if (order == 1) {
          text = `Key Bias (${biasData.length}) `;
          outputText = `Key (${outputData[0].length},${outputData.length}) `;
        } else if (order == 2) {
          text = `Value Bias (${biasData.length}) `;
          outputText = `Value (${outputData[0].length},${outputData.length}) `;
        } else {
          return null;
        }
        let biasConstraintGridCellWidth = getVisualizationSizeConstraint(biasData[0].length, 'x', sizeX, sizeY, maximumCellSize);
        let biasConstraintGridCellHeigh = getVisualizationSizeConstraint(biasData.length, 'y', sizeX, sizeY, maximumCellSize);
        let biasGridData = getGridData(biasData, biasConstraintGridCellWidth, biasConstraintGridCellHeigh);
        let biasGridGroup = group.append("g").attr("class", "grid").attr("transform", `translate(${0},${order * (sizeY + betweenInterval)})`);
        let biasGridRow = biasGridGroup.selectAll(".row")  // 绘制每一行
          .data(biasGridData).enter().append('g').attr('class', 'row');
        biasGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke-width', 5)
          .style('stroke', d => {
            if (order == this.curOrder && d.row == this.highlights[0]) {
              return 'black'
            }
            else return null;
          })
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return paramsColorScale(normlizedVal);
          });
        let biasTotalGridWidth = biasConstraintGridCellWidth * biasData[0].length;
        let biasGridText = group.append('text').attr("text-anchor", "middle");
        biasGridText
          .attr('transform', `translate(${0 + biasTotalGridWidth / 2},${order * (sizeY + betweenInterval) - betweenInterval / 2})`)
          .attr('class', 'label')
          .text(text);

        let plus = group.append('g')
          .attr('id', 'plus-g')
          .attr('transform', `translate(${-30},${order * (sizeY + betweenInterval) + sizeY / 2})`)
        plus.append('circle')
          .attr('class', 'operator')
          .attr('r', operatorRadius)
        plus.append('text')
          .attr('class', 'operatorText')
          .text('+')

        let equation = group.append('g')
          .attr('id', 'equation-g')
          .attr('transform', `translate(${biasTotalGridWidth + 30},${order * (sizeY + betweenInterval) + sizeY / 2})`)
        equation.append('circle')
          .attr('class', 'operator')
          .attr('r', operatorRadius)
        equation.append('text')
          .attr('class', 'operatorText')
          .text('=')


        // 绘制 head 内的 output
        let outputConstraintGridCellWidth = getVisualizationSizeConstraint(outputData.length, 'x', outputSizeX, outputSizeY, maximumCellSize);
        let outputConstraintGridCellHeigh = getVisualizationSizeConstraint(outputData[0].length, 'y', outputSizeX, outputSizeY, maximumCellSize);
        // 对 outputData 进行转置
        let outputDataTranspose = [];
        for (let c = 0; c < outputData[0].length; c++) {
          let column = [];
          for (let r = 0; r < outputData.length; r++) {
            column.push(outputData[r][c]);
          }
          outputDataTranspose.push(column);
        }
        let outputGridData = getGridData(outputDataTranspose, outputConstraintGridCellWidth, outputConstraintGridCellHeigh);
        let outputGridGroup = group.append("g").attr("class", "grid").attr("transform", `translate(${biasTotalGridWidth + 60},${order * (outputSizeY + betweenInterval)})`);
        let outputGridRow = outputGridGroup.selectAll(".row")  // 绘制每一行
          .data(outputGridData).enter().append('g').attr('class', 'row');
        outputGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .on('click', (event, d) => {
            this.$emit('changeOrderAndHilights', { order: order, highlights: [d.row, d.col] });
          })
          .style('stroke-width', 2.5)
          .style('stroke', d => {
            if (order == this.curOrder && d.row == this.highlights[0] && d.col == this.highlights[1]) return 'black'
            else return null;
          })
          .style('fill', d => {
            let normlizedVal = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
            return colorScale(normlizedVal);
          });
        let outputTotalGridWidth = outputConstraintGridCellWidth * outputData.length;
        let outputGridText = group.append('text').attr("text-anchor", "middle");
        outputGridText
          .attr('transform', `translate(${biasTotalGridWidth + 60 + outputTotalGridWidth / 2},${order * (outputSizeY + betweenInterval) - betweenInterval / 2})`)
          .attr('class', 'label')
          .text(outputText);
        
          let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
          let instructiveArrowWidth = 30
          let instructiveArrowHeight = 30
          let clickIcon = require("../../src/assets/click.svg")
          let clickIconWidth = 13
          let clickIconHeight = 13
          let instructiveArrowOffsetX = biasTotalGridWidth + 80 + outputTotalGridWidth / 2
          let instructiveArrowOffsetY = order * (outputSizeY + betweenInterval) - betweenInterval / 2
          let labeText=''
          if(order==0){
            labeText=['Query - Used to compute','the similarity between','the input and the context.']
          }else if(order==1){
            labeText=['Key - Provides the reference','for comparison with the query','to determine the importance.']
          }else{
            labeText=['Value - Holds the information','to be weighted and combined','based on the attention','mechanism.']
          }
          let instructiveText = group.append('g')
            .attr('id',order+'-label')
            .attr('transform', `translate(${instructiveArrowOffsetX},${instructiveArrowOffsetY})`)
            console.log(instructiveText)
          instructiveText.append('svg:image')
            .attr('xlink:href', instructiveArrow)
            .attr("width", instructiveArrowWidth)
            .attr("height", instructiveArrowHeight)
          instructiveText.append('svg:image')
            .attr('transform', `translate(${30},${0})`)
            .attr('xlink:href', clickIcon)
            .attr("width", clickIconWidth)
            .attr("height", clickIconHeight)
            instructiveText.append('text')
            .selectAll('.tspan')
            .data(labeText)
            .enter().append('tspan')
            .attr("x", 45)
            .attr("dy", '1.3em')
            .attr('font-size', '11px')
            .attr('fill', '#4a4a4a')
            .text(d => d)
      }
    },


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
  align-items: center;
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