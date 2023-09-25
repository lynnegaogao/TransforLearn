<template>
  <svg ref="matMul1Svg"></svg>
</template>

<script>
import * as d3 from "d3";
import { getVisualizationSizeConstraint, getDataRange, getGridData } from '../utils/detailview-utils'
// import {config} from '../utils/config'
export default {
  name: "AttentionCalScoreAnimator",
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
        this.drawMatMul()
      })
    }
  },
  beforeUpdate() {

  },
  mounted() {
    this.drawMatMul()
  },
  methods: {
    drawMatMul() {
      d3.select(this.$refs.matMul1Svg).selectAll('*').remove();
      let svg = d3.select(this.$refs.matMul1Svg)
        .attr('id', "matMul-1-Svg")
        .attr("width", "100%")
        .attr('height', "450px")
        .attr('transform', `translate(40,10)`)

      // title
      let titleOffsetX = 100
      let titleOffsetY = 50
      svg.append('text')
        .attr('transform', `translate(${titleOffsetX},${titleOffsetY})`)
        .attr('class', 'label')
        .style('font-weight', 'bold')
        .text('Step.1 Matrix Multiply');

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

      let colorScale = d3.interpolateRdBu;
      let interval = 65;
      let operatorRadius = 10;
      let maximumCellSize = 20;

      let qGroupX = 20;
      let qGroupY = 130;
      let xSizeOfQGrid = 350;
      let ySizeOfQGrid = 200;
      let qData = headData.mat_QKV[headNum][0];
      let qDataRange = getDataRange(qData);
      let qText = `Q (${qData.length},${qData[0].length})`;
      let qSymbol = '*';


      let xSizeOfKGrid = ySizeOfQGrid;
      let ySizeOfKGrid = xSizeOfQGrid;
      let kGroupX = qGroupX + xSizeOfQGrid + interval;
      let kGroupY = qGroupY - (ySizeOfKGrid - ySizeOfQGrid) / 2;
      let kData = transpose(headData.mat_QKV[headNum][1]);
      let kDataRange = getDataRange(headData.mat_QKV[headNum][1]);
      let kText = `K^T (${kData.length},${kData[0].length})`;
      let kSymbol = '=';

      let resGroupX = kGroupX + xSizeOfKGrid + interval;
      let resGroupY = qGroupY;
      let xSizeOfResGrid = ySizeOfQGrid;
      let ySizeOfResGrid = ySizeOfQGrid;
      let resData = headData['Q*KT'][headNum];
      let resDataRange = getDataRange(resData);
      let resText = `Q*K^T (${resData.length},${resData[0].length})`;
      let resSymbol = null;

      let qGroup = svg.append('g').attr('class', 'query-group')
        .attr('transform', `translate(${qGroupX},${qGroupY})`);
      let kGroup = svg.append('g').attr('class', 'key-group')
        .attr('transform', `translate(${kGroupX},${kGroupY})`);
      let resGroup = svg.append('g').attr('class', 'multiplied-group')
        .attr('transform', `translate(${resGroupX},${resGroupY})`);

      drawMatrix(qGroup, 'Q', qData, xSizeOfQGrid, ySizeOfQGrid, interval, maximumCellSize, qDataRange, colorScale, qText, qSymbol);
      drawMatrix(kGroup, 'K', kData, xSizeOfKGrid, ySizeOfKGrid, interval, maximumCellSize, kDataRange, colorScale, kText, kSymbol);
      drawMatrix(resGroup, 'RES', resData, xSizeOfResGrid, ySizeOfResGrid, interval, maximumCellSize, resDataRange, colorScale, resText, resSymbol);

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

      function drawMatrix(group, type, data, sizeX, sizeY, xInetrval, maximumCellSize, dataRange, colorMapper, text, symbol) {
        let constraintGridCellWidth = getVisualizationSizeConstraint(data[0].length, 'x', sizeX, sizeY, maximumCellSize);
        let constraintGridCellHeight = getVisualizationSizeConstraint(data.length, 'y', sizeX, sizeY, maximumCellSize);

        let gridData = getGridData(data, constraintGridCellWidth, constraintGridCellHeight);
        let gridGroup = group.append("g").attr("class", "grid")
        let gridRow = gridGroup.selectAll(".row")  // 绘制每一行
          .data(gridData).enter().append('g').attr('class', 'row').attr('id', (d, i) => `${type}-row-${i}`);
        gridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr('id', d => `${type}-row-${d.row}-col-${d.col}`)
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .on('click', (event, d) => {
            if (type == "RES") {
              if (self.highLightArray[0] != d.row || self.highLightArray[1] != d.col) self.$emit('changeHighLightArray', [d.row, d.col]);
              else self.$emit('changeHighLightArray', [-1, -1]);
            }
          })
          .style('stroke', d => {
            if (type == "Q") {
              if (self.highLightArray[0] == d.row) return 'black';
              else return null;
            } else if (type == "K") {
              if (self.highLightArray[1] == d.col) return 'black';
              else return null;
            } else {
              if (self.highLightArray[0] == d.row && self.highLightArray[1] == d.col) return 'black';
              else return null;
            }
          })
          .style('stroke-width', 1.2)
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorMapper(normlizedVal);
          });



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
            .attr('transform', `translate(${totalGridWidth + xInetrval / 2 + 20},${totalGridHeight / 2 - 20})`)
          symbolGroup.append('circle')
            .attr('class', 'operator')
            .attr('r', operatorRadius)
          symbolGroup.append('text')
            .attr('class', 'operatorText')
            .text(symbol)
        } else if (symbol == '*') {
          let symbolGroup = group.append('g')
            .attr('id', 'crossmultiply-g')
            .attr('transform', `translate(${totalGridWidth + xInetrval / 2},${totalGridHeight / 2})`)
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

        // for(let i=0;i<5;i++){
        //   d3.select(`row-${i}`).selectAll(".square").style('stroke','black')
        //   d3.selectAll(".row").selectAll(".square").style('stroke','')
        // }
        let i = 0;
        let j = 0;
        let range=type=='Q'?data.length:data[0].length
        let dimension=type=='Q'?data[0].length:data.length
        const interval = setInterval(() => {
          if (i >= range) {
              clearInterval(interval); // 当达到指定次数后清除定时器
              return;
            }
          if (type == 'Q') {
            if(i>0){
              d3.select(`#${type}-row-${i-1}`).selectAll(".square").style('stroke', '');
            }
            // else if(i==range){
            //   d3.select(`#${type}-row-${0}`).selectAll(".square").style('stroke', '');
            // }
            d3.select(`#${type}-row-${i}`).selectAll(".square").style('stroke', 'black');
          }
          if (type == 'K') {
            // d3.selectAll(".row").selectAll(".square").style('stroke', '');
            for (let k = 0; k < dimension; k++) {
              if(j>0){
                d3.select(`#${type}-row-${k}-col-${j-1}`).style('stroke', '');
              }else if(j==0){
                d3.select(`#${type}-row-${k}-col-${range-1}`).style('stroke', '');
              }
              d3.select(`#${type}-row-${k}-col-${j}`).style('stroke', 'black');
              // console.log(d3.selectAll(".row").select(`#${type}-row-${k}-col-${j}`).selectAll(".square"))
            }

          }
          if (type == 'RES') {
            if(j>0){
                d3.select(`#${type}-row-${i}-col-${j-1}`).style('stroke', '');
              }else if(i>0&&j==0){
                d3.select(`#${type}-row-${i-1}-col-${range-1}`).style('stroke', '');
              }
            d3.select(`#${type}-row-${i}-col-${j}`).style('stroke', 'black');
            // console.log(d3.select(`#${type}-row-${i}-col-${j}`))
          }
          j++
          if (j == range) { i++; j = 0 }
        }, 800); // 设置每2秒执行一次（2000毫秒）
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

#matMul1Svg {
  width: 100%;
  height: 100%;
  background-color: white;
}
</style>