<template>
  <div class="container">
    <svg id="crossHeadSvg"></svg>
  </div>
</template>

<script>
import * as d3 from "d3";
import { getVisualizationSizeConstraint, getDataRange, getGridData } from '../utils/detailview-utils'
// import {getDataRange} from '../utils/detailview-utils'
// import {config} from '../utils/config'
export default {
  name: "AttentionHeadCrossAnimator",
  components: {
    // EmbeddingAnimator,
  },
  props: {
    nodeData: {
      type: Object,
      default: function () { return {}; },
    },
    highlights: {
      type: Array,
      default: function () { return []; },
    },
    curOrder: {
      type: Number,
      default: 0,
    },
    openHighlights: {
      type: Boolean,
      default: true,
    },

  },
  emits: ["exit", "changeOrderAndHilights"],
  data() {
    return {
      oldNodeData: {},
      oldHighlights: [],
      oldOrder: 0,
      // curTokenIndex:0,
      // tokenNums:1,
      // curEquationIndex:0,
      // curOutputColumnIndex:0,
    };
  },
  created() {
    // console.log('this.nodeData in AttentionHeadView.vue:', this.nodeData);
    // this.tokenNums = this.tokens.length;
    // this.curTokenIndex = 0;
    // console.log('this.tokens:',this.tokens);
    // console.log('this.embeddings:',this.embeddings);
    // console.log('this.pe:',this.pe);
    // console.log('this.output:',this.output);
  },
  beforeUpdate() {
    if (this.oldNodeData != this.nodeData) {
      this.oldNodeData = this.nodeData;
      this.init();
    }
    this.redraw();
  },
  mounted() {
    this.init();
    this.redraw();
  },
  methods: {
    onExit() {
      console.log("exit from the current detailview.");
      this.$emit('exit');
    },
    init() {
      this.oldNodeData = this.nodeData;
      this.qInputDataRange = getDataRange(this.nodeData.qInput);
      this.kvInputDataRange = getDataRange(this.nodeData.kvInput);

      this.queryDataRange = getDataRange(this.nodeData.Q);
      this.keyDataRange = getDataRange(this.nodeData.K);
      this.valueDataRange = getDataRange(this.nodeData.V);
      // this.qkvTotalDataRange = {
      //   max: Math.max(queryDataRange.max, keyDataRange.max, valueDataRange.max);
      //   max: Math.min(queryDataRange.min, keyDataRange.min, valueDataRange.min);
      // };

      this.queryWeightDataRange = getDataRange(this.nodeData.Wq);
      this.queryBiasDataRange = getDataRange([this.nodeData.bq]);
      this.keyWeightDataRange = getDataRange(this.nodeData.Wk);
      this.keyBiasDataRange = getDataRange([this.nodeData.bk]);
      this.valueWeightDataRange = getDataRange(this.nodeData.Wv);
      this.valueBiasDataRange = getDataRange([this.nodeData.bv]);
    },
    drawWeights() {
      let svg = d3.select(this.$el).select('#crossHeadSvg');
      // let inputDataRange = this.inputDataRange;
      // let colorScale = d3.interpolateRdBu;
      let paramsColorScale = d3.interpolateBrBG;
      // let fontSize = 20;
      let fontSize = 25;

      // let weightGridGroupX = 10;
      let weightGridGroupX = 40;
      // let weightGridGroupY = 30;
      let weightGridGroupY = 60;
      let weightXSizeOfEachGrid = 260;
      // let weightYSizeOfEachGrid = 80;
      let weightYSizeOfEachGrid = 160;
      // let weightInterval = 30;
      let weightInterval = 60;
      // let maximumCellSize = 20;
      let maximumCellSize = 40;

      let WqWkWvGroup = svg.append('g').attr('class', 'weights-QKV-group')
        .attr('transform', `translate(${weightGridGroupX},${weightGridGroupY})`);

      drawWeight.call(this, WqWkWvGroup, weightInterval, 0, weightXSizeOfEachGrid, weightYSizeOfEachGrid, maximumCellSize)
      drawWeight.call(this, WqWkWvGroup, weightInterval, 1, weightXSizeOfEachGrid, weightYSizeOfEachGrid, maximumCellSize)
      drawWeight.call(this, WqWkWvGroup, weightInterval, 2, weightXSizeOfEachGrid, weightYSizeOfEachGrid, maximumCellSize)

      function drawWeight(group, betweenInterval, order, sizeX, sizeY, maximumCellSize) {
        // 绘制 Weight Q
        let weightData;
        let dataRange;
        let text;
        if (order == 0) {
          weightData = this.nodeData.Wq;
          dataRange = this.queryWeightDataRange;
          text = `Query Weight (${weightData.length},${weightData[0].length}) `;
        } else if (order == 1) {
          weightData = this.nodeData.Wk;
          dataRange = this.keyWeightDataRange;
          text = `Key Weight (${weightData.length},${weightData[0].length}) `
        } else if (order == 2) {
          weightData = this.nodeData.Wv;
          dataRange = this.valueWeightDataRange;
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
            if (this.openHighlights && order == this.curOrder && d.row == this.highlights[0]) return '#5B05A6'
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
          .attr('transform', `translate(${0 + weightTotalGridWidth / 2},${order * (sizeY + betweenInterval) - betweenInterval / 2})`)
          .attr('class', 'title-text')
          .attr('dy', '.3em')
          .style('font-weight', 'bold')
          .style('font-size', fontSize / 1.6)
          .text(text);
        let multiplySymbolGridText = group.append('text').attr("text-anchor", "middle");
        multiplySymbolGridText
          .attr('transform', `translate(${0 + weightTotalGridWidth + 15},${order * (sizeY + betweenInterval) + sizeY / 2})`)
          .attr('class', 'title-text')
          .attr('dy', '.3em')
          .style('font-weight', 'bold')
          .style('font-size', fontSize)
          .text('x');
      }
    },
    drawInput() {
      let svg = d3.select(this.$el).select('#crossHeadSvg');
      // let svgWidth = +(svg.attr('width'));

      // let qInputDataRange = this.qInputDataRange;
      // let kvInputDataRange = this.kvInputDataRange;
      let colorScale = d3.interpolateRdBu;
      // let paramsColorScale = d3.interpolateBrBG;
      let fontSize = 20;
      // let fontSize = 25;
      let maximumCellSize = 30;
      let yInerval = 60;

      let qInputGridGroupX = 330;
      let qInputGridGroupY = 60;
      let qInputXSizeOfGrid = 100;
      let qInputYSizeOfGrid = 160;

      let kvInputGridGroupX = qInputGridGroupX;
      let kvInputGridGroupY = qInputGridGroupY + qInputYSizeOfGrid + yInerval;
      let kvInputXSizeOfGrid = 100;
      let kvInputYSizeOfGrid = 2 * qInputYSizeOfGrid + yInerval;

      let qInputGridGroup = svg.append("g").attr("class", "grid").attr("transform", `translate(${qInputGridGroupX},${qInputGridGroupY})`);
      let kvInputGridGroup = svg.append("g").attr("class", "grid").attr("transform", `translate(${kvInputGridGroupX},${kvInputGridGroupY})`);

      let qInputData = transpose(this.nodeData.qInput);
      let kvInputData = transpose(this.nodeData.kvInput);
      // console.log('qInputData:',qInputData);
      // console.log('kvInputData:',kvInputData);
      let qText = `Input (${qInputData.length},${qInputData[0].length})`;
      let kvText = `Output (${kvInputData.length},${kvInputData[0].length})`;

      drawInput.call(this, qInputGridGroup, 'Q', qInputData, qInputXSizeOfGrid, qInputYSizeOfGrid, this.qInputDataRange, colorScale, maximumCellSize, qText);
      drawInput.call(this, kvInputGridGroup, 'KV', kvInputData, kvInputXSizeOfGrid, kvInputYSizeOfGrid, this.kvInputDataRange, colorScale, maximumCellSize, kvText);

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
        // console.log('width:',constraintGridCellWidth);
        // console.log('height:',constraintGridCellHeight);
        // 对 input 进行转置 得到 inputData, 以进行矩阵乘法
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
              if (this.openHighlights && d.col == this.highlights[1] && this.curOrder == 0) return '#5B05A6';
            } else if (type == 'KV') {
              if (this.openHighlights && d.col == this.highlights[1] && this.curOrder > 0) return '#5B05A6'
            } else return null;
          })
          // .style('stroke',d=>d.row==this.curTokenIndex?'black':null)
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorMap(normlizedVal);
          });
        let totalGridWidth = constraintGridCellWidth * cols;
        // let inputTotalGridHeight = inputConstraintGridCellHeigh * cols;
        let gridText = group.append('text').attr("text-anchor", "middle");
        gridText
          .attr('transform', `translate(${totalGridWidth / 2},${-20})`)
          .attr('class', 'title-text')
          .attr('dy', '.3em')
          .style('font-weight', 'bold')
          .style('font-size', fontSize / 1.5)
          .text(text);
      }
    },
    drawBiasesAndOuputs() {
      // width 1000, height 300;
      let svg = d3.select(this.$el).select('#crossHeadSvg');

      let colorScale = d3.interpolateRdBu;
      let paramsColorScale = d3.interpolateBrBG;
      // let fontSize = 20;
      let fontSize = 25;

      // let groupX = 450;
      let groupX = 480;
      // let groupY = 30;
      let groupY = 60;
      let biasXSizeOfEachGrid = 25;
      // let biasYSizeOfEachGrid = 80;
      let biasYSizeOfEachGrid = 160;
      // let biasInterval = 30;
      let biasInterval = 60;
      // let maximumCellSize = 20;
      let maximumCellSize = 30;
      let outputXSizeOfEachGrid = 80;
      // let outputYSizeOfEachGrid = 80;
      let outputYSizeOfEachGrid = 160;

      let group = svg.append('g').attr('class', 'biases-output-QKV-group')
        .attr('transform', `translate(${groupX},${groupY})`);

      drawBiasAndOutput.call(this, group, biasInterval, 0, biasXSizeOfEachGrid, biasYSizeOfEachGrid, outputXSizeOfEachGrid, outputYSizeOfEachGrid, maximumCellSize);
      drawBiasAndOutput.call(this, group, biasInterval, 1, biasXSizeOfEachGrid, biasYSizeOfEachGrid, outputXSizeOfEachGrid, outputYSizeOfEachGrid, maximumCellSize);
      drawBiasAndOutput.call(this, group, biasInterval, 2, biasXSizeOfEachGrid, biasYSizeOfEachGrid, outputXSizeOfEachGrid, outputYSizeOfEachGrid, maximumCellSize);

      function drawBiasAndOutput(group, betweenInterval, order, sizeX, sizeY, outputSizeX, outputSizeY, maximumCellSize) {
        let biasData = [];
        let dataRange;
        let text;
        let outputData;
        let outputDataRange;
        let outputText;
        if (order == 0) {
          biasData = this.nodeData.bq.map(d => [d]);
          dataRange = this.queryBiasDataRange;
          text = `Query Bias (${biasData.length}) `;
          outputData = this.nodeData.Q;
          outputDataRange = this.queryDataRange;
          outputText = `Query (${outputData[0].length},${outputData.length}) `;
        } else if (order == 1) {
          biasData = this.nodeData.bk.map(d => [d]);
          dataRange = this.keyBiasDataRange;
          text = `Key Bias (${biasData.length}) `;
          outputData = this.nodeData.K;
          outputDataRange = this.keyDataRange;
          outputText = `Key (${outputData[0].length},${outputData.length}) `;
        } else if (order == 2) {
          biasData = this.nodeData.bv.map(d => [d]);
          dataRange = this.valueBiasDataRange;
          text = `Value Bias (${biasData.length}) `;
          outputData = this.nodeData.V;
          // outputDataRange = this.valueDataRange;
          outputDataRange = this.nodeData.attentionOuputTotalDataRange;
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
          .style('stroke-width', 2.5)
          .style('stroke', d => {
            if (this.openHighlights && order == this.curOrder && d.row == this.highlights[0]) return '#5B05A6'
            else return null;
          })
          // .style('stroke',d=>d.row==this.curTokenIndex?'black':null)
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return paramsColorScale(normlizedVal);
          });
        let biasTotalGridWidth = biasConstraintGridCellWidth * biasData[0].length;
        // let inputTotalGridHeight = inputConstraintGridCellHeigh * cols;
        let biasGridText = group.append('text').attr("text-anchor", "middle");
        biasGridText
          .attr('transform', `translate(${0 + biasTotalGridWidth / 2},${order * (sizeY + betweenInterval) - betweenInterval / 2})`)
          .attr('class', 'title-text')
          .attr('dy', '.3em')
          .style('font-weight', 'bold')
          .style('font-size', fontSize / 1.8)
          .text(text);
        let plusSymbolGridText = group.append('text').attr("text-anchor", "middle");
        plusSymbolGridText
          .attr('transform', `translate(${-25},${order * (sizeY + betweenInterval) + sizeY / 2})`)
          .attr('class', 'title-text')
          .attr('dy', '.3em')
          .style('font-weight', 'bold')
          .style('font-size', fontSize)
          .text('+');
        let equalSymbolGridText = group.append('text').attr("text-anchor", "middle");
        equalSymbolGridText
          .attr('transform', `translate(${biasTotalGridWidth + 25},${order * (sizeY + betweenInterval) + sizeY / 2})`)
          .attr('class', 'title-text')
          .attr('dy', '.3em')
          .style('font-weight', 'bold')
          .style('font-size', fontSize)
          .text('=');

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
        let outputGridGroup = group.append("g").attr("class", "grid").attr("transform", `translate(${biasTotalGridWidth + 50},${order * (outputSizeY + betweenInterval)})`);
        // console.log('outputSizeX:',outputSizeX);
        // console.log('outputConstraintGridCellWidth:',outputConstraintGridCellWidth);
        // console.log('outputConstraintGridCellHeigh:',outputConstraintGridCellHeigh);
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
            if (this.openHighlights && order == this.curOrder && d.row == this.highlights[0] && d.col == this.highlights[1]) return '#5B05A6'
            else return null;
          })
          // .style('stroke',d=>d.row==this.curTokenIndex?'black':null)
          .style('fill', d => {
            let normlizedVal = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
            return colorScale(normlizedVal);
          });
        let outputTotalGridWidth = outputConstraintGridCellWidth * outputData.length;
        let outputGridText = group.append('text')
        .attr('id',order+'-output-label')
        .attr("text-anchor", "middle");
        outputGridText
          .attr('transform', `translate(${biasTotalGridWidth + 50 + outputTotalGridWidth / 2},${order * (outputSizeY + betweenInterval) - betweenInterval / 2})`)
          .attr('class', 'title-text')
          .attr('dy', '.3em')
          .style('font-weight', 'bold')
          .style('font-size', fontSize / 1.8)
          .text(outputText);

          let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
          let instructiveArrowWidth = 30
          let instructiveArrowHeight = 30
          let clickIcon = require("../../src/assets/click.svg")
          let clickIconWidth = 13
          let clickIconHeight = 13
          let instructiveArrowOffsetX = biasTotalGridWidth + 100 + outputTotalGridWidth / 2
          let instructiveArrowOffsetY = order * (outputSizeY + betweenInterval) - betweenInterval / 2
          let instructiveText = group.append('g')
            .attr('id',order+'-label')
            .attr('transform', `translate(${instructiveArrowOffsetX},${instructiveArrowOffsetY})`)
            console.log(instructiveText)
          instructiveText.append('svg:image')
            .attr('xlink:href', instructiveArrow)
            .attr("width", instructiveArrowWidth)
            .attr("height", instructiveArrowHeight)
          instructiveText.append('svg:image')
            .attr('transform', `translate(${25},${-10})`)
            .attr('xlink:href', clickIcon)
            .attr("width", clickIconWidth)
            .attr("height", clickIconHeight)
          instructiveText.append('text')
            .text('Click')
            .attr("font-size", '10px')
            .attr("font-weight", 'bold')
            .attr("font-style", 'italic')
            .attr("fill", '#4a4a4a')
            .attr("x", 40)
            .attr("y", 0)
          instructiveText.append('text')
            .text('to learn')
            .attr("font-size", '10px')
            .attr("fill", '#4a4a4a')
            .attr("x", 70)
            .attr("y", 0)
          instructiveText.append('text')
            .text('how to get embeddings!')
            .attr("font-size", '10px')
            .attr("fill", '#4a4a4a')
            .attr("x", 35)
            .attr("y", 13)
        
      }
    },
    redraw() {
      d3.select(this.$el).selectAll('#crossHeadSvg > *').remove();
      d3.select(this.$el).select('#crossHeadSvg').attr('width', 700).attr('height', 720);
      // let svg = d3.select(this.$el).select('#embeddingSvg').attr('width',1550);
      // let svgWidth = +(svg.attr('width'));
      this.drawWeights();
      this.drawInput();
      this.drawBiasesAndOuputs();

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
  font-size: 1.2em;
  /* font-weight: 500; */
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
</style>