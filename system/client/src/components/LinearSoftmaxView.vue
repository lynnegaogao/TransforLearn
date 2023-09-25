<template>
  <div class="container">
    <div class="box">
      <div class="control-pannel">
        <div class="title-text">
          Linear Projection and Softmax
        </div>
        <el-tooltip content="Quit from Linear & Softmax View." placement="top" effect="dark">
          <el-button type="primary" :icon="CloseBold" plain circle @click="onExit()" />
        </el-tooltip>
      </div>
      <div class="container">
        <svg ref="generatorSvg"> </svg>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";
import { getVisualizationSizeConstraint, getGridData, getDataRange } from '../utils/detailview-utils'
import { config } from '../utils/config'
import { shallowRef } from "vue"
import { CloseBold } from '@element-plus/icons-vue'
export default {
  name: "LinearSoftmaxView",
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
    generatorParams: {
      type: Object,
      default: function () { return {}; },
    }
  },
  emits: ["exit", 'getParams'],
  data() {
    return {
      CloseBold: shallowRef(CloseBold),
    };
  },
  watch: {
    curIter(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        this.drawGenerator()
      })
    },
    generatorParams(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        this.drawGenerator()
      })
    },
  },
  mounted() {
    this.onGetParams();
    this.drawGenerator();
  },
  methods: {
    onExit() {
      console.log("exit from the current detailview.");
      this.$emit('exit');
    },
    onGetParams() {
      this.$emit('getParams', 'generator-linear')
    },
    drawGenerator() {
      d3.select(this.$refs.generatorSvg).selectAll('*').remove();
      let svg = d3.select(this.$refs.generatorSvg)
        .attr('id', "generator-Svg")
        .attr("width", "100%")
        .attr('height', "500px")
        .attr('transform', `translate(1,10)`)
      var self = this
      let colorScale = d3.interpolateRdBu;
      const edgeStrokeWidth = config.edgeStrokeWidth;
      const edgeOpacity = config.edgeOpacity;
      const edgeInitColor = config.edgeInitColor;
      const edgeHoverColor = config.edgeHoverColor;
      const plusSymbolRadius = config.plusSymbolRadius;
      const intermediateColor = config.intermediateColor;
      const kernelRectLength = config.kernelRectLength;
      const nodeLength = config.nodeLength;
      // let svgWidth = +(svg.attr('width'));
      // 绘制 input
      let inputData = this.decoder.linear.input
      let xSizeOfInputGrid = 350
      let ySizeOfInputGrid = 200
      let constraintGridCellWidth = getVisualizationSizeConstraint(inputData.length, 'x', xSizeOfInputGrid, ySizeOfInputGrid, 30);
      let constraintGridCellHeigh = getVisualizationSizeConstraint(1, 'y', xSizeOfInputGrid, ySizeOfInputGrid, 30);
      // let totalRectWidth = constraintGridCellWidth * inputData.length;
      // let textConstraintDivisor = 0.15;
      let inputRowTransX = 300
      let inputRowTransY = 30;

      let inputGridData = getGridData([inputData], constraintGridCellWidth, constraintGridCellHeigh);
      let inputDataRange = getDataRange([inputData])

      let outputData = this.decoder.linear.output
      let xSizeOfOutputGrid = 800
      let ySizeOfOutputGrid = 200
      let constraintOutputGridCellWidth = getVisualizationSizeConstraint(outputData.length, 'x', xSizeOfOutputGrid, ySizeOfOutputGrid, 30);
      let constraintOutputGridCellHeigh = getVisualizationSizeConstraint(1, 'y', xSizeOfOutputGrid, ySizeOfOutputGrid, 30);
      // let totalOutputRectWidth = constraintOutputGridCellWidth * outputData.length;
      // let textConstraintDivisor = 0.15;
      let outputRowTransX = 100;
      let outputRowTransY = 200;

      let outputGridData = getGridData([outputData], constraintOutputGridCellWidth, constraintOutputGridCellHeigh);
      let outputDataRange = getDataRange([outputData])


      // 绘制 input row
      let rowInput = svg.selectAll(".rowInput") // 绘制一行
        .data(inputGridData)
        .enter().append("g")
        .attr("class", "row")
        .attr('transform', `translate(${inputRowTransX},${inputRowTransY})`);

      rowInput.selectAll(".square")
        .data(function (d) { return d; })
        .enter().append("rect")
        .attr("class", "square")
        .attr("x", d => d.x)
        .attr("y", d => d.y)
        .attr("width", d => d.width)
        .attr("height", d => d.height)
        .attr("opacity", 0.8)
        .style("fill", (d) => {
          let normalizedValue = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
          return colorScale(normalizedValue);
        });
      // 绘制 output row
      let rowOutput = svg.selectAll(".rowOutput")
        .data(outputGridData)
        .enter().append("g")
        .attr("class", "row")
        .attr('transform', `translate(${outputRowTransX},${outputRowTransY})`);

      rowOutput.selectAll(".square")
        .data(function (d) { return d; })
        .enter().append("rect")
        .attr("class", "square")
        .attr("x", d => d.x)
        .attr("y", d => d.y)
        .attr("width", d => d.width)
        .attr("height", d => d.height)
        .attr("opacity", 0.8)
        .style("fill", (d) => {
          let normalizedValue = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
          return colorScale(normalizedValue);
        });

      let prediction = this.decoder.predict
      let symbolX = outputRowTransX + outputGridData[0][prediction.token].x + outputGridData[0][prediction.token].width / 2;
      let symbolY = outputRowTransY - plusSymbolRadius * 2;
      let symbolRectHeight = 1;
      let symbolGroup = svg.append('g').attr('class', 'plus-symbol').attr('transform', `translate(${symbolX},${symbolY})`);

      symbolGroup.append('rect')
        .attr('x', -plusSymbolRadius)
        .attr('y', -plusSymbolRadius)
        .attr('width', plusSymbolRadius * 2)
        .attr('height', plusSymbolRadius * 2)
        .attr('rx', 3)
        .attr('ry', 3)
        .style('fill', 'none')
        .style('stroke', intermediateColor);
      symbolGroup.append('rect')
        .attr('x', -(plusSymbolRadius - 3))
        .attr('y', -symbolRectHeight / 2)
        .attr('width', 2 * (plusSymbolRadius - 3))
        .attr('height', symbolRectHeight)
        .style('fill', intermediateColor);
      symbolGroup.append('rect')
        .attr('x', -symbolRectHeight / 2)
        .attr('y', -(plusSymbolRadius - 3))
        .attr('width', symbolRectHeight)
        .attr('height', 2 * (plusSymbolRadius - 3))
        .style('fill', intermediateColor);

      symbolGroup.append('circle')
        .attr('cx', -nodeLength / 2 - 0.5 * kernelRectLength)
        .attr('cy', 0)
        .attr('r', kernelRectLength * 1.5)
        .style('stroke', intermediateColor)
        .style('cursor', 'crosshair')
        .style('fill', '#DDDDDD');

      // Link from bias to the plus symbol
      symbolGroup.append('path')
        .attr('d', (d3.linkHorizontal().x(d => d.x).y(d => d.y))({
          source: { x: 0, y: 0 },
          target: { x: -nodeLength / 2 - 0.5 * kernelRectLength, y: 0 }
        }))
        .attr('id', 'bias-plus')
        .attr('stroke-width', 1.2)
        .attr('stroke', '#E5E5E5')
        .lower();


      // draw softmax box
      let softmaxArg = {
        symbolX: symbolX,
        symbolY: outputRowTransY + constraintOutputGridCellHeigh + plusSymbolRadius * 5,
        width: 80,
        height: 30,
      }
      let softmaxSymbol = svg.append('g').attr('class', 'softmax-symbol').attr('transform', `translate(${softmaxArg.symbolX},${softmaxArg.symbolY})`);
      let mouseClickCounter=0
      softmaxSymbol.append('rect')
        .attr('x', -softmaxArg.width / 2)
        .attr('y', -softmaxArg.height / 2)
        .attr('width', softmaxArg.width)
        .attr('height', softmaxArg.height)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr('fill', 'rgb(235,235,235)')
        .attr('stroke', 'rgb(175,175,175)')
        .attr('stroke-width', 2)
      softmaxSymbol.append('text')
        .attr("class", "label")
        .text('softmax');
      softmaxSymbol.style('cursor', 'hand')
        .on('click', (event) => {
          if(mouseClickCounter==0){
            mouseClickCounter=1
            self.drawFormula(tooltipGroup, event)
          }else{
            mouseClickCounter=0
            d3.select('#detailed-softmax').remove()
          }
        })

      // draw prediction rect
      let predictSymbolOffsetY = plusSymbolRadius * 6;
      let predictSymbolX = softmaxArg.symbolX;
      let predictSymbolY = softmaxArg.symbolY + predictSymbolOffsetY;
      let predictSymbolWidth = 80;
      let predictSymbolHeight = 30;
      let predictSymbol = svg.append('g').attr('class', 'predict-symbol').attr('transform', `translate(${predictSymbolX},${predictSymbolY})`);
      // let predictRect = predictSymbol.append('rect')
      predictSymbol.append('rect')
        .attr('x', -predictSymbolWidth / 2)
        .attr('y', -predictSymbolHeight / 2) // 这两步相当于把最外层的矩形的中心设置成锚点
        .attr('width', predictSymbolWidth)
        .attr('height', predictSymbolHeight)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr('fill', 'rgb(235,235,235)')
        .attr('stroke', 'rgb(175,175,175)')
        .attr('stroke-width', 2)

      predictSymbol.append('text')
        .attr("class", "label")
        .text('predict')

      // 绘制必要的 线条
      let linkGen = d3.linkVertical().x(d => d.x).y(d => d.y);
      let linkData = [{
        source: { x: symbolX, y: symbolY + plusSymbolRadius },
        target: { x: symbolX, y: outputRowTransY },
        type: 'symbol-link',
      },
      {
        source: { x: symbolX, y: outputRowTransY + constraintGridCellHeigh },
        target: { x: symbolX, y: softmaxArg.symbolY - softmaxArg.height / 2 },
        type: 'symbol-link',
      },
      {
        source: { x: symbolX, y: softmaxArg.symbolY + softmaxArg.height / 2 },
        target: { x: symbolX, y: softmaxArg.symbolY + predictSymbolOffsetY - predictSymbolHeight / 2 },
        type: 'symbol-link',
      }];
      inputGridData[0].forEach(d => {
        let source = {
          x: d.x + d.width / 2 + inputRowTransX,
          y: d.y + inputRowTransY + d.height,
        }
        linkData.push({
          source: { x: source.x, y: source.y },
          target: {
            x: outputRowTransX + outputGridData[0][prediction.token].x + outputGridData[0][prediction.token].width / 2,
            y: symbolY - plusSymbolRadius
          },
          type: 'max',
        })
      });
      let edgeGroup = svg.append("g").attr("class", "edge-group");
      edgeGroup.selectAll("path.edge")
        .data(linkData)
        .enter().append('path')
        .attr("class", `edge`)
        .attr("d", d => linkGen({ source: d.source, target: d.target }))
        .style('fill', 'none')
        .style('stroke-width', edgeStrokeWidth)
        .style('opacity', edgeOpacity)
        .style('stroke', d => {
          if (d.type == "max" || d.type == "symbol-link") return edgeHoverColor;
          else return edgeInitColor;
        });

      // 添加文本
      svg.append("text")
        .attr('class', 'label')
        .attr('transform', `translate(${inputRowTransX - 50},${inputRowTransY + 15})`)
        .text(`Input (1,${inputData.length})`);

      svg.append("text")
        .attr('class', 'label')
        .attr('transform', `translate(${outputRowTransX - 50},${outputRowTransY - 10})`)
        .selectAll('.tspan')
        .data([`Output`, `(1,${outputData.length})`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.2em')
        .text(d => d);


      let predictText = svg.append("text").attr('class', 'label');
      predictText
        .attr('transform', `translate(${predictSymbolX},${predictSymbolY + predictSymbolHeight})`)
        .selectAll('.tspan')
        .data([`Token: ${prediction.token}`, `Word: ${prediction.word}`, `Score: ${Math.round(Math.exp(this.decoder.softmax[prediction.token]) * 10000) / 10000}`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);

      let tooltipGroup = svg.append("g")
        .attr('id', 'softmax-tooltip')
    },

    drawFormula(svg, event) {
      let offsetX = event.screenX < 900 ? event.screenX - 400 : event.screenX - 850
      let offsetY = event.screenY - 300
      let rectWidth = 360
      let rectHeight = 160
      let backgroundOpacity = 0.5

      let softmaxTooltipPart = svg.append('g')
        .attr('id', 'detailed-softmax')
        .attr('transform', `translate(${offsetX},${offsetY})`)
      softmaxTooltipPart.append('rect')
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("width", rectWidth)
        .attr("height", rectHeight)
        .attr("fill", "rgb(235, 235, 235)")
        .attr('stroke', 'rgb(175, 175, 175)')
        .attr('stroke-width', 1)
        .style('opacity', backgroundOpacity)
      softmaxTooltipPart.append('text')
        .attr('class', 'label')
        .attr('transform', `translate(${rectWidth / 2},${20})`)
        .text('Softmax score for ' + this.decoder.predict.word)

      let denominatorGroupX = 10,
        denominatorGroupY = 100;

      // Denominator
      let denominatorGroup = softmaxTooltipPart.append('g')
        .attr('class', 'denominator')
        .attr('transform', `translate(${denominatorGroupX}, ${denominatorGroupY})`);

      let colorScale = d3.interpolateRdBu;
      let outputDataRange = getDataRange([this.decoder.linear.output]);
      let fontSize = 12;
      let curX = 5;
      let deltaX = 8;
      let unitY = 30;
      let offsetX_right = 2;
      let offsetX_left = 2;
      let numOfRows = 4;
      let n = this.decoder.linear.output.length;
      let logits = [this.decoder.linear.output[0], this.decoder.linear.output[1], "...",
      this.decoder.linear.output[this.decoder.predict.token], "...",
      this.decoder.linear.output[n - 2], this.decoder.linear.output[n - 1],];
      // Add the left (
      denominatorGroup.append('text')
        .attr('x', 0)
        .attr('y', 0)
        .style('fill', 'gray')
        .style('font-size', 1.25 * fontSize)
        .text('(');
      logits.forEach((d, i) => {
        if (i / numOfRows >= 1 && i % numOfRows === 0) curX = 8;
        let curText = denominatorGroup.append('text')
        if (d == "...") {
          curText.attr('x', curX)
            .attr('y', Math.floor(i / numOfRows) * unitY)
            .style('cursor', 'crosshair')
            .style('pointer-events', 'all')
            .style('font-size', fontSize)
            .text(` ... `);
        } else {
          curText.attr('x', curX)
            .attr('y', Math.floor(i / numOfRows) * unitY)
            .style('cursor', 'crosshair')
            .style('pointer-events', 'all')
            .style('font-size', fontSize)
            .text(`exp(`);

          curText.append('tspan')
            .attr('class', `formula-term-${i} formula-term`)
            // .attr('dx', '1')
            .attr('dx', offsetX_right)
            .style('fill', colorScale((d - outputDataRange.min) / (outputDataRange.max - outputDataRange.min)))
            .style('fill-opacity', 1)
            .style('font-size', fontSize)
            .text(Math.round(d * 100) / 100);

          curText.append('tspan')
            // .attr('dx', '1')
            .attr('dx', offsetX_right)
            .style('font-size', fontSize)
            .text(')');
        }

        let curBBox = curText.node().getBBox();
        curX += curBBox.width + 4;

        if (i !== logits.length - 1) {
          denominatorGroup.append('text')
            .attr('x', curX)
            .attr('y', Math.floor(i / numOfRows) * unitY)
            .style('font-size', fontSize)
            .text('+');
          curX += deltaX;
        } else {
          denominatorGroup.append('text')
            .attr('x', curX - offsetX_left)
            .attr('y', Math.floor(i / numOfRows) * unitY)
            .style('font-size', 1.25 * fontSize)
            .style('fill', 'gray')
            .text(')');
        }
      });
      // Calculate the dynamic denominator group width
      let denominatorGroupBBox = denominatorGroup.node().getBBox();
      let lineOffsetX = 3;
      let ypos = 75;
      let lineStrokeWidth = 2;
      // Draw the fraction line
      softmaxTooltipPart.append('line')
        .attr('class', 'separation-line')
        .attr('x1', lineOffsetX)
        .attr('x2', denominatorGroupBBox.width + lineOffsetX+10)
        .attr('y1', ypos)
        .attr('y2', ypos)
        .style('stroke-width', lineStrokeWidth)
        .style('stroke', 'gray');

      let numeratorX = 0,
        numeratorY = 60;
      // Draw the numerator
      let numeratorGroup = softmaxTooltipPart.append('g')
        .attr('class', 'numerator-group')
        .attr('transform', `translate(${numeratorX}, ${numeratorY})`);

      let numeratorText = numeratorGroup.append('text')
        .attr('x', denominatorGroupBBox.x + denominatorGroupBBox.width / 2)
        .attr('y', 0)
        .style('pointer-events', 'all')
        .style('cursor', 'crosshair')
        .style('text-anchor', 'middle')
        .style('font-size', fontSize)
        .text('exp(');

      numeratorText.append('tspan')
        .attr('dx', offsetX_right)
        .style('fill', colorScale((this.decoder.linear.output[this.decoder.predict.token] - outputDataRange.min) / (outputDataRange.max - outputDataRange.min)))
        .style('font-size', fontSize)
        .text(Math.round(this.decoder.linear.output[this.decoder.predict.token] * 100) / 100);

      numeratorText.append('tspan')
        .attr('dx', offsetX_right)
        .style('font-size', fontSize)
        .text(')');

      let formulaLeftGroupX = 280,
        formulaLeftGroupY =ypos,
        softmaxTextX = 20;
      // Draw the left part of the formula
      let formulaLeftGroup = softmaxTooltipPart.append('g')
        .attr('class', 'formula-left')
        .attr('transform', `translate(${formulaLeftGroupX}, ${formulaLeftGroupY})`);

      // let softmaxText = formulaLeftGroup.append('text')
      formulaLeftGroup.append('text')
        .attr('x', softmaxTextX)
        .attr('dominant-baseline', 'middle')
        .style('font-weight', 'bold')
        .style('font-size', fontSize * 1.25)
        .text(Math.round(Math.exp(this.decoder.softmax[this.decoder.predict.token]) * 10000) / 10000);
      // .text(Math.exp(this.decoder.softmax[this.decoder.predict.token]));

      // let softmaxTextBBox = softmaxText.node().getBBox();
      formulaLeftGroup.append('text')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0)
        .attr('y', 0)
        .style('fill', 'gray')
        .style('font-weight', 'bold')
        .style('font-size', fontSize)
        .text('=');
    },
  },
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