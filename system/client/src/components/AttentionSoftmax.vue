<template>
  <svg ref="attentionSoftmaxSvg"></svg>
</template>

<script>
import * as d3 from "d3";
import { getVisualizationSizeConstraint, getDataRange, getGridData } from '../utils/detailview-utils'
// import {getVisualizationSizeConstraint, getGridData} from '../utils/detailview-utils'
// import {getDataRange} from '../utils/detailview-utils'
// import {config} from '../utils/config'
export default {
  name: "AttentionScaleOut",
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
        this.drawSotmax()
      })
    }
  },
  beforeUpdate() {
  },
  mounted() {
    this.drawSotmax()
  },
  methods: {
    drawSotmax() {
      // 移除之前所绘制的内容
      d3.select(this.$refs.attentionSoftmaxSvg).selectAll('*').remove();
      let svg = d3.select(this.$refs.attentionSoftmaxSvg)
        .attr('id', "softmax-Svg")
        .attr("width", "100%")
        .attr('height', "450px")
        .attr('transform', `translate(30,10)`)

      // title
      let titleOffsetX = 100
      let titleOffsetY = 50
      svg.append('text')
        .attr('transform', `translate(${titleOffsetX},${titleOffsetY})`)
        .attr('class', 'label')
        .style('font-weight', 'bold')
        .text('Step.3 Softmax');

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
      let afterMask = headData['after_mask'][headNum];
      let afterExp = [];
      let expSum = [];
      afterMask.forEach(arr => {
        let expArr = arr.map(d => Math.exp(d));
        afterExp.push(expArr);
        expSum.push(expArr.reduce((x, y) => x + y));
      });

      let fontSize = 10;
      let interval = 65;
      let maximumCellSize = 20;
      let operatorRadius = 10
      let colorScale = d3.interpolateRdBu;

      let scoreGroupX = 10;
      let scoreGroupY = 130;
      let xSizeOfScoreGrid = 200;
      let ySizeOfScoreGrid = 200;
      let scoreData = headData['after_mask'][headNum];
      let scoreDataRange = getDataRange(headData['Q*KT'][headNum]);
      let scoreText = `Masked(Q*K^T/coef) (${scoreData.length},${scoreData[0].length})`;
      let scoreSymbol = null;

      let dividedScoreGroupX = scoreGroupX + xSizeOfScoreGrid + 2.5 * interval;
      let dividedScoreGroupY = scoreGroupY;
      let xSizeOfDividedScoreGrid = 200;
      let ySizeOfDividedScoreGrid = 200;
      let dividedScoreData = afterExp;
      let singleGridWidth = Math.min(xSizeOfDividedScoreGrid / dividedScoreData[0].length, maximumCellSize)
      let xRealSize = singleGridWidth * dividedScoreData[0].length;
      let dividedScoreDataRange = getDataRange(dividedScoreData);
      let dividedScoreText = `Exp(Masked) (${dividedScoreData.length},${dividedScoreData[0].length})`;
      let dividedScoreSymbol = null;

      let sumData = expSum.map(d => [d]);
      let sumText = [`Sum(Exp)`, `(${sumData.length},${sumData[0].length})`]
      let sumSymbol = null;

      let maskedScoreGroupX = dividedScoreGroupX + xSizeOfScoreGrid + 2.5 * interval;
      let maskedScoreGroupY = dividedScoreGroupY;
      let xSizeOfMaskedScoreGrid = 200;
      let ySizeOfMaskedScoreGrid = 200;
      let maskedScoreData = headData['after_softmax'][headNum]
      let maskedScoreText = `Masked(Q*K^T/coef) (${maskedScoreData.length},${maskedScoreData[0].length})`;
      let maskedScoreSymbol = null;


      let scoreGroup = svg.append('g').attr('class', 'score-group')
        .attr('transform', `translate(${scoreGroupX},${scoreGroupY})`);
      let dividedScoreGroup = svg.append('g').attr('class', 'dividedScore-group')
        .attr('transform', `translate(${dividedScoreGroupX - maximumCellSize},${dividedScoreGroupY})`);
      let sumGroup = svg.append('g').attr('class', 'sum-group')
        .attr('transform', `translate(${dividedScoreGroupX - maximumCellSize * 0.4 + xRealSize},${dividedScoreGroupY})`);
      let maskedScoreGroup = svg.append('g').attr('class', 'MaskedScore-group')
        .attr('transform', `translate(${maskedScoreGroupX},${maskedScoreGroupY})`);

      drawMatrix(scoreGroup, 'score', scoreData, xSizeOfScoreGrid, ySizeOfScoreGrid, interval, maximumCellSize, scoreDataRange, colorScale, scoreText, scoreSymbol);
      drawMatrix(dividedScoreGroup, 'divide', dividedScoreData, xSizeOfDividedScoreGrid, ySizeOfDividedScoreGrid, interval, maximumCellSize, dividedScoreDataRange, colorScale, dividedScoreText, dividedScoreSymbol);
      drawMatrix(sumGroup, 'sum', sumData, maximumCellSize, ySizeOfDividedScoreGrid, interval, maximumCellSize, dividedScoreDataRange, colorScale, sumText, sumSymbol);
      drawMatrix(maskedScoreGroup, 'masked', maskedScoreData, xSizeOfMaskedScoreGrid, ySizeOfMaskedScoreGrid, interval, maximumCellSize, { max: 1, min: 0 }, colorScale, maskedScoreText, maskedScoreSymbol);

      // draw Equation of divide
      let divideGroupX = scoreGroupX + xSizeOfScoreGrid + interval * 0.58;
      let divideGroupY = scoreGroupY + ySizeOfScoreGrid / 2;
      let divideGroup = svg.append('g').attr('class', 'divide-group')
        .attr('transform', `translate(${divideGroupX},${divideGroupY})`);
      let expOffsetX = -45;
      let expOffsetY = -25;
      divideGroup.append('text')
        .attr('class', 'label')
        .style("font-size", 20)
        .style('text-anchor', 'middle')
        .attr('transform', `translate(${expOffsetX},${expOffsetY})`)
        .text(`exp(`);
      divideGroup.append('text')
        .attr('class', 'label')
        .style("font-size", 20)
        .style('text-anchor', 'middle')
        .attr('transform', `translate(${expOffsetX + 70},${expOffsetY})`)
        .text(`)`);
      let equalGroup = divideGroup.append('g')
        .attr('id', 'equation-g')
        .attr('transform', `translate(${expOffsetX + 85},${expOffsetY})`)
      equalGroup.append('circle')
        .attr('class', 'operator')
        .attr('r', operatorRadius)
      equalGroup.append('text')
        .attr('class', 'operatorText')
        .text('=')

      let singleCellSize = 35
      let divideNumeratorGridData = getGridData([[scoreData[this.highLightArray[0]][this.highLightArray[1]]]], singleCellSize, singleCellSize)
      let divideRow = divideGroup.selectAll(".rowNum")  // 绘制每一行
        .data(divideNumeratorGridData).enter().append('g').attr('class', 'rowNum')
        .attr('transform', `translate(${expOffsetX + 25},${expOffsetY - singleCellSize / 2})`);
      divideRow
        .selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', 'black')
        .style('stroke-width', 1.2)
        .style('fill', d => {
          let normlizedVal = (d.text - scoreDataRange.min) / (scoreDataRange.max - scoreDataRange.min);
          return colorScale(normlizedVal);
        });
      divideRow
        .selectAll(".text")
        .data(d => d)
        .enter().append("text")
        .attr("class", "text")
        .style("font-size", 9)
        .attr("x", d => d.x + d.width / 2)
        .attr("y", d => d.y + d.height / 2)
        .style("fill", d => {  // 为颜色设置填充色
          let normlizedVal = (d.text - scoreDataRange.min) / (scoreDataRange.max - scoreDataRange.min);
          if (normlizedVal < 0.2 || normlizedVal > 0.8) {
            return 'white';
          } else {
            return 'black';
          }
        })
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .text(d => {
          if (d.text < -1e5) return '-Inf';
          else return d.text;
        })

      let resGridData = getGridData([[dividedScoreData[this.highLightArray[0]][this.highLightArray[1]]]], singleCellSize, singleCellSize)
      let resGridRow = divideGroup.selectAll(".rowRes")  // 绘制每一行
        .data(resGridData).enter().append('g').attr('class', 'rowRes')
        .attr('transform', `translate(${expOffsetX + 100},${expOffsetY - singleCellSize / 2})`);
      resGridRow
        .selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', 'black')
        .style('stroke-width', 1.2)
        .style('fill', d => {
          let normlizedVal = (d.text - dividedScoreDataRange.min) / (dividedScoreDataRange.max - dividedScoreDataRange.min);
          return colorScale(normlizedVal);
        });
      resGridRow
        .selectAll(".text")
        .data(d => d)
        .enter().append("text")
        .attr("class", "text")
        .style("font-size", 10)
        .attr("x", d => d.x + d.width / 2)
        .attr("y", d => d.y + d.height / 2)
        .style("fill", d => {  // 为颜色设置填充色
          // let normlizedVal = (d.text-this.dataRange.min)/(this.dataRange.max-this.dataRange.min);
          let normlizedVal = (d.text - dividedScoreDataRange.min) / (dividedScoreDataRange.max - dividedScoreDataRange.min);
          if (normlizedVal < 0.2 || normlizedVal > 0.8) {
            return 'white';
          } else {
            return 'black';
          }
        })
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .text(d => d.text)


      // draw Mask Equation
      let maskEqGroupX = dividedScoreGroupX + xSizeOfDividedScoreGrid + interval * 0.65;
      let maskEqGroupY = dividedScoreGroupY + ySizeOfDividedScoreGrid / 2;
      let maskEqGroup = svg.append('g').attr('class', 'mask-op-group')
        .attr('transform', `translate(${maskEqGroupX},${maskEqGroupY})`);
 
      let maskGridData = getGridData([[expSum[this.highLightArray[0]]]], singleCellSize, singleCellSize)
      let maskedResGridData = getGridData([[maskedScoreData[this.highLightArray[0]][this.highLightArray[1]]]], singleCellSize, singleCellSize)
      let resGridDataOffsetX = -30
      let resGridDataOffsetY = -80
      let maskGridDataOffsetX = resGridDataOffsetX
      let maskGridDataOffsetY = resGridDataOffsetY + singleCellSize + 20
      let maskedResGridDataOffsetX = maskGridDataOffsetX + singleCellSize + 50
      let maskedResGridDataOffsetY = resGridDataOffsetY + singleCellSize / 2 + 10
      maskEqGroup.append('text')
        .attr('class', 'label')
        .attr('transform', `translate(${interval * 0.7 * 0.5},${30})`)
        .text('Calculate Softmax Score.');

      let lineWidth = 55;
      let lineStrokeWidth = 2;
      maskEqGroup.append('line').attr('class', 'separation-line')
        .attr('x1', resGridDataOffsetX - 10).attr('y1', resGridDataOffsetY + singleCellSize + 10).attr('x2', resGridDataOffsetX - 10 + lineWidth).attr('y2', resGridDataOffsetY + singleCellSize + 10)
        .style('stroke-width', lineStrokeWidth).style('stroke', 'gray');

      let equal = maskEqGroup.append('g')
        .attr('id', 'equation-g')
        .attr('transform', `translate(${maskGridDataOffsetX + singleCellSize + 30},${resGridDataOffsetY + singleCellSize + 10})`)
      equal.append('circle')
        .attr('class', 'operator')
        .attr('r', operatorRadius)
      equal.append('text')
        .attr('class', 'operatorText')
        .text('=')

      drawSingleGrid(maskEqGroup, resGridData, dividedScoreDataRange, 'rowRes', resGridDataOffsetX, resGridDataOffsetY)
      drawSingleGrid( maskEqGroup, maskGridData, dividedScoreDataRange, 'rowMask', maskGridDataOffsetX, maskGridDataOffsetY)
      drawSingleGrid(maskEqGroup, maskedResGridData, { max: 1, min: 0 }, 'rowMaskedRes', maskedResGridDataOffsetX, maskedResGridDataOffsetY)

      function drawSingleGrid(group, gridData, dataRange, className, transX, transY) {
        let row = group.selectAll(`.${className}`)  // 绘制每一行
          .data(gridData).enter().append('g').attr('class', className)
          .attr('transform', `translate(${transX},${transY})`);
        row
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', 'black')
          .style('stroke-width', 1.2)
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorScale(normlizedVal);
          });
        row
          .selectAll(".text")
          .data(d => d)
          .enter().append("text")
          .attr("class", "text")
          .style("font-size", 9)
          .attr("x", d => d.x + d.width / 2)
          .attr("y", d => d.y + d.height / 2)
          .style("fill", d => {  // 为颜色设置填充色
            // let normlizedVal = (d.text-this.dataRange.min)/(this.dataRange.max-this.dataRange.min);
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            if (normlizedVal < 0.2 || normlizedVal > 0.8) {
              return 'white';
            } else {
              return 'black';
            }
          })
          .style("text-anchor", "middle")
          .style("dominant-baseline", "middle")
          .text(d => {
            if (d.text < -1e5) return '-Inf';
            else return d.text;
          });
      }

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
          .on('click', (event, d) => {
            if (type != 'sum') self.$emit('changeHighLightArray', [d.row, d.col]);
          })
          .style('stroke-width', 1.2)
          .style('stroke', d => {
              if (type == 'sum' && self.highLightArray[0] == d.row) return 'black';
              if (self.highLightArray[0] == d.row && self.highLightArray[1] == d.col) return 'black';
              else return null;
            })
          .style('stroke-width', 1.2)
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            if (normlizedVal < 0) normlizedVal = 0;
            else if (normlizedVal > 1) normlizedVal = 1;
            return colorMapper(normlizedVal);
          });


        let totalGridWidth = constraintGridCellWidth * data[0].length;
        let totalGridHeight = constraintGridCellHeight * data.length;
        let gridText = group.append('text').attr("text-anchor", "middle");
        if (type == 'sum') {
          gridText
          .attr('transform', `translate(${totalGridWidth / 2},${-50})`)
          .style('text-anchor', 'middle')
          .style('font-size', '14px')
          .attr("fill", '#4a4a4a')
          .selectAll('.tspan')
          .data(text)
          .enter().append('tspan')
          .attr('x', 0)
          .attr('dy', '1.5em')
          .text(d => d);
        } else {
          gridText
            .attr('transform', `translate(${totalGridWidth / 2},${-20})`)
            .attr('class', 'label')
            .text(text);
        }



        if (symbol != null) {
          let symbolText = group.append('text').attr("text-anchor", "middle");
          symbolText
            .attr('transform', `translate(${totalGridWidth + xInetrval / 2},${totalGridHeight / 2})`)
            .attr('class', 'title-text')
            .attr('dy', symbol == "*" ? '.55em' : '.3em')
            .style('font-weight', 'bold')
            .style('font-size', symbol == "*" ? fontSize * 1.6 : fontSize)
            .text(symbol);
        }
      }

    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
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