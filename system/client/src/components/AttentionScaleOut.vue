<template>
  <svg ref="scaleoutSvg"></svg>
</template>

<script>
import * as d3 from "d3";
import { getVisualizationSizeConstraint, getDataRange, getGridData } from '../utils/detailview-utils'
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
        this.drawScale()
      })
    }
  },
  beforeUpdate() {
  },
  mounted() {
    this.drawScale();
  },
  methods: {
    drawScale() {
      d3.select(this.$refs.scaleoutSvg).selectAll('*').remove();
      let svg = d3.select(this.$refs.scaleoutSvg)
        .attr('id', "scale-Svg")
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
        .text('Step.2 Scale & Mask');

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
      let interval = 65;
      let maximumCellSize = 20;
      let fontSize = 10
      let operatorRadius = 10
      let colorScale = d3.interpolateRdBu;

      let scoreGroupX = 0;
      let scoreGroupY = 130;
      let xSizeOfScoreGrid = 200;
      let ySizeOfScoreGrid = 200;
      let scoreData = headData['Q*KT'][headNum];
      let scoreDataRange = getDataRange(headData['Q*KT'][headNum]);
      let scoreText = `Q*K^T (${scoreData.length},${scoreData[0].length})`;
      let scoreSymbol = null;

      let dividedScoreGroupX = scoreGroupX + xSizeOfScoreGrid + 2.5 * interval;
      let dividedScoreGroupY = scoreGroupY;
      let xSizeOfDividedScoreGrid = 160;
      let ySizeOfDividedScoreGrid = 160;
      let dividedScoreData = headData['Q*KT/coefficient'][headNum];
      // let dividedScoreDataRange = getDataRange(this.QKTdivided);
      let dividedScoreText = `Q*K^T/coefficient (${dividedScoreData.length},${dividedScoreData[0].length})`;
      let dividedScoreSymbol = null;

      let maskedScoreGroupX = dividedScoreGroupX + xSizeOfScoreGrid + 2.5 * interval;
      let maskedScoreGroupY = dividedScoreGroupY;
      let xSizeOfMaskedScoreGrid = 160;
      let ySizeOfMaskedScoreGrid = 160;
      let maskedScoreData = headData['after_mask'][headNum];
      // let dividedScoreDataRange = getDataRange(this.QKTdivided);
      let maskedScoreText = `Masked(Q*K^T/coefficient)(${maskedScoreData.length},${maskedScoreData[0].length})`;
      let maskedScoreSymbol = null;

      let maskGroupX = dividedScoreGroupX + xSizeOfScoreGrid + interval * 0.9;
      let maskGroupY = dividedScoreGroupY;
      let xSizeOfMaskGrid = 80;
      let ySizeOfMaskGrid = 80;
      let maskData = headData.mask;
      // let dividedScoreDataRange = getDataRange(this.QKTdivided);
      let maskText = `Mask Op. (${maskData.length},${maskData[0].length})`;
      let maskSymbol = null;

      let scoreGroup = svg.append('g').attr('class', 'score-group')
        .attr('transform', `translate(${scoreGroupX},${scoreGroupY})`);
      let dividedScoreGroup = svg.append('g').attr('class', 'dividedScore-group')
        .attr('transform', `translate(${dividedScoreGroupX},${dividedScoreGroupY})`);
      let maskedScoreGroup = svg.append('g').attr('class', 'MaskedScore-group')
        .attr('transform', `translate(${maskedScoreGroupX},${maskedScoreGroupY})`);
      let maskGroup = svg.append('g').attr('class', 'MaskedScore-group')
        // .attr('transform',`translate(${maskGroupX-xSizeOfMaskGrid/2},${maskGroupY-ySizeOfMaskGrid/2})`);
        .attr('transform', `translate(${maskGroupX - xSizeOfMaskGrid / 2},${maskGroupY - ySizeOfMaskGrid / 2})`);

      drawMatrix(scoreGroup, 'score', scoreData, xSizeOfScoreGrid, ySizeOfScoreGrid, interval, maximumCellSize, scoreDataRange, colorScale, scoreText, scoreSymbol);
      drawMatrix(dividedScoreGroup, 'divide', dividedScoreData, xSizeOfDividedScoreGrid, ySizeOfDividedScoreGrid, interval, maximumCellSize, scoreDataRange, colorScale, dividedScoreText, dividedScoreSymbol);
      drawMatrix(maskedScoreGroup, 'masked', maskedScoreData, xSizeOfMaskedScoreGrid, ySizeOfMaskedScoreGrid, interval, maximumCellSize, scoreDataRange, colorScale, maskedScoreText, maskedScoreSymbol);
      drawMatrix(maskGroup, 'mask', maskData, xSizeOfMaskGrid, ySizeOfMaskGrid, interval, maximumCellSize, { max: 1, min: 0 }, colorScale, maskText, maskSymbol);

      // draw Equation of divide
      let divideGroupX = scoreGroupX + xSizeOfScoreGrid - 10;
      let divideGroupY = scoreGroupY + ySizeOfScoreGrid / 2 - 20;
      let divideGroup = svg.append('g').attr('class', 'divide-group')
        .attr('transform', `translate(${divideGroupX},${divideGroupY})`);
      let lineWidth = 65;
      let lineStrokeWidth = 2;
      divideGroup.append('line').attr('class', 'separation-line')
        .attr('x1', 0).attr('y1', 1).attr('x2', lineWidth).attr('y2', 1)
        .style('stroke-width', lineStrokeWidth).style('stroke', 'gray');
      divideGroup.append('text').attr('class', 'label')
        .style("font-size", 16).style('text-anchor', 'middle')
        .attr('transform', `translate(${lineWidth / 2},${maximumCellSize * 0.8})`)
        .text(`${headData.coefficient}`);
      let equalGroup = divideGroup.append('g')
        .attr('id', 'equation-g')
        .attr('transform', `translate(${lineWidth + 20},${0})`)
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
        .attr('transform', `translate(${lineWidth / 5},${-40})`);
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
          // let normlizedVal = (d.text-this.dataRange.min)/(this.dataRange.max-this.dataRange.min);
          let normlizedVal = (d.text - scoreDataRange.min) / (scoreDataRange.max - scoreDataRange.min);
          if (normlizedVal < 0.2 || normlizedVal > 0.8) {
            return 'white';
          } else {
            return 'black';
          }
        })
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .text(d => d.text)

      let resGridData = getGridData([[dividedScoreData[this.highLightArray[0]][this.highLightArray[1]]]], singleCellSize, singleCellSize)
      let resGridRow = divideGroup.selectAll(".rowRes")  // 绘制每一行
        .data(resGridData).enter().append('g').attr('class', 'rowRes')
        .attr('transform', `translate(${lineWidth + 40},${-20})`);
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
          let normlizedVal = (d.text - scoreDataRange.min) / (scoreDataRange.max - scoreDataRange.min);
          return colorScale(normlizedVal);
        });
      resGridRow
        .selectAll(".text")
        .data(d => d)
        .enter().append("text")
        .attr("class", "text")
        .style("font-size", 9)
        .attr("x", d => d.x + d.width / 2)
        .attr("y", d => d.y + d.height / 2)
        .style("fill", d => {  // 为颜色设置填充色
          // let normlizedVal = (d.text-this.dataRange.min)/(this.dataRange.max-this.dataRange.min);
          let normlizedVal = (d.text - scoreDataRange.min) / (scoreDataRange.max - scoreDataRange.min);
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
      let maskEqGroupX = dividedScoreGroupX + xSizeOfDividedScoreGrid + 60;
      let maskEqGroupY = dividedScoreGroupY + ySizeOfDividedScoreGrid / 2;
      let maskEqGroup = svg.append('g').attr('class', 'mask-op-group')
        .attr('transform', `translate(${maskEqGroupX},${maskEqGroupY})`);
      let maskGridData = getGridData([[maskData[this.highLightArray[0]][this.highLightArray[1]]]], singleCellSize, singleCellSize)
      let maskedResGridData = getGridData([[maskedScoreData[this.highLightArray[0]][this.highLightArray[1]]]],singleCellSize, singleCellSize)

      maskEqGroup.append('text')
        .attr('class', 'label')
        .attr('transform', `translate(${45},${50})`)
        .text('Mask Operation');

      let resGridDataOffsetX=-45
      let resGridDataOffsetY=-10
      let maskGridDataOffsetX=resGridDataOffsetX+singleCellSize+singleCellSize
      let maskGridDataOffsetY=resGridDataOffsetY
      let maskedResGridDataOffsetX=maskGridDataOffsetX+singleCellSize+singleCellSize
      let maskedResGridDataOffsetY=resGridDataOffsetY
      drawSingleGrid( maskEqGroup, resGridData, scoreDataRange, 'rowRes', resGridDataOffsetX,resGridDataOffsetY)
      drawSingleGrid(maskEqGroup, maskGridData, { max: 1, min: 0 }, 'rowMask', maskGridDataOffsetX, maskGridDataOffsetY)
      drawSingleGrid(maskEqGroup, maskedResGridData, scoreDataRange, 'rowMaskedRes', maskedResGridDataOffsetX,maskedResGridDataOffsetY)
      let multiply = maskEqGroup.append('g')
          .attr('id', 'crossmultiply-g')
          .attr('transform', `translate(${maskGridDataOffsetX-17},${maskedResGridDataOffsetY+singleCellSize/2})`)
          multiply.append('circle')
          .attr('class', 'operator')
          .attr('r', operatorRadius)
          multiply.append('text')
          .attr('y', 5.5)
          .attr('font-weight', 'bold')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', 'rgb(175, 175, 175)')
          .attr('font-size', '23px')
          .text('*')
      let equal = maskEqGroup.append('g')
        .attr('id', 'equation-g')
        .attr('transform', `translate(${maskedResGridDataOffsetX-17},${maskedResGridDataOffsetY+singleCellSize/2})`)
      equal.append('circle')
        .attr('class', 'operator')
        .attr('r', operatorRadius)
      equal.append('text')
        .attr('class', 'operatorText')
        .text('=')
      

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
            if (type != 'mask') self.$emit('changeHighLightArray', [d.row, d.col]);
          })
          .style('stroke-width', 1.2)
          .style('stroke', d => {
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
        gridText
          .attr('transform', `translate(${totalGridWidth / 2},${-20})`)
          .attr('class', 'label')
          .text(text);

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
  display: flex;
  flex-direction: row;
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

/*
#left-column{
  width:60%;
  height:92%;
}

#right-column{
  width:40%;
  height:92%;
}
*/
</style>