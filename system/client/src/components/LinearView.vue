<template>
  <svg id="linearSvg" width="960" height="100%">
  </svg>
</template>

<script>
import * as d3 from "d3";
import {getVisualizationSizeConstraint, getGridData, getDataRange} from '../utils/detailview-utils'
import {getLegendGradient} from '../utils/draw-utils'
import {config} from '../utils/config'

const edgeStrokeWidth = config.edgeStrokeWidth;
const edgeOpacity = config.edgeOpacity;
const edgeInitColor = config.edgeInitColor;
const edgeHoverColor = config.edgeHoverColor;
const plusSymbolRadius = config.plusSymbolRadius;
const intermediateColor = config.intermediateColor;
const kernelRectLength = config.kernelRectLength;
const nodeLength = config.nodeLength;


export default {
  name:"LinearView",
  components:{
    // LayernormAnimator,
  },
  props:{
    input: {
      type: Array,
      default: function(){return [];},
    },
    output: {
      type: Array,
      default: function(){return [];},
    },
    bias: {
      type: Array,
      default: function(){return [];},
    },
    logSoftmax: {
      type: Array,
      default: function(){return [];}
    },
    predict: {
      type: Object,
      default: function(){return {};}
    },
  },
  emits:["exit"],
  data(){
    return {
      inputGridData:[],
      inputDataRange:{},
      outputGridData:[],
      outputDataRange:{},

      oldInput:[],
    }
  },
  mounted(){
    this.redraw();
  },
  beforeUpdate(){
    if(this.oldInput != this.input){
      this.redraw();
    }
  },
  methods:{
    onExit(){
      console.log("exit from the current view.");
      this.$emit('exit');
    },
    redraw(){
      console.log("Enter LinearView.vue");
      let svg = d3.select("#linearSvg");
      svg.selectAll('*').remove();

      this.oldInput = this.input;

      let svgWidth = +(svg.attr('width'));
      let colorScale = d3.interpolateRdBu;

      // 绘制 input rects
      let constraintGridCellWidth = getVisualizationSizeConstraint(this.input.length,'x', svgWidth*0.6, 200, 30);
      let constraintGridCellHeigh = getVisualizationSizeConstraint(1,'y', svgWidth*0.6, 200, 30);
      let totalRectWidth = constraintGridCellWidth * this.input.length;
      let textConstraintDivisor = 0.15;
      let inputRowTransY = 30;
      
      this.inputGridData = getGridData([this.input], constraintGridCellWidth, constraintGridCellHeigh);
      this.inputDataRange = getDataRange([this.input])

      let constraintOutputGridCellWidth = getVisualizationSizeConstraint(this.output.length,'x', svgWidth*0.9, 200, 30);
      let constraintOutputGridCellHeigh = getVisualizationSizeConstraint(1,'y', svgWidth*0.85, 200, 30);
      let totalOutputRectWidth = constraintOutputGridCellWidth * this.output.length;
      // let textConstraintDivisor = 0.15;
      let outputRowTransY = 200;

      this.outputGridData = getGridData([this.output], constraintOutputGridCellWidth, constraintOutputGridCellHeigh);
      this.outputDataRange = getDataRange([this.output])

      console.log('this.bias:',this.bias);
      console.log('this.inputGridData:',this.inputGridData);
      // console.log('this.inputDataRange:',this.inputDataRange);

      // 绘制 inputLegend
      getLegendGradient(svg,colorScale,'inputGradient',this.inputDataRange.min,this.inputDataRange.max)
      getLegendGradient(svg,colorScale,'outputGradient',this.outputDataRange.min,this.outputDataRange.max)
      let gridLength = 40;
      let legendHeight = 5;
      let inputLegendScale = d3.scaleLinear()
      .range([0, 4 * gridLength])
      .domain([this.inputDataRange.min, this.inputDataRange.max]);
      let inputLegendAxis = d3.axisBottom()
      .scale(inputLegendScale)
      .tickFormat(d3.format('.2f'))
      .tickValues([this.inputDataRange.min, this.inputDataRange.min+(this.inputDataRange.max-this.inputDataRange.min)/2 ,this.inputDataRange.max]);
      let inputLegend = svg.append('g')
        .attr('transform', `translate(${svgWidth-totalRectWidth}, ${inputRowTransY/6})`);
      inputLegend.append('g')
        // .attr('transform', `translate(${-2*gridLength}, ${inputLegendHeight+2})`)
        .attr('transform', `translate(${0}, ${legendHeight+2})`)
        .call(inputLegendAxis)
      inputLegend.append('rect')
        // .attr('x',-2*gridLength).attr('y',1.25*gridLength)
        // .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('transform', `translate(${0}, ${0})`)
        .attr('width', 4 * gridLength).attr('height', legendHeight)
        .style('fill', 'url(#inputGradient)');
      
      // 绘制 outputLegend
      // let outputLegendScale = d3.scaleLinear()
      // .range([0, 4 * gridLength])
      // .domain([this.outputDataRange.min, this.outputDataRange.max]);
      // let outputLegendAxis = d3.axisBottom()
      // .scale(outputLegendScale)
      // .tickFormat(d3.format('.2f'))
      // .tickValues([this.outputDataRange.min, this.outputDataRange.max]);
      // let outputLegend = svg.append('g')
      //   .attr('transform', `translate(${svgWidth-totalRectWidth}, ${outputRowTransY + constraintOutputGridCellHeigh*1.2})`);
      // outputLegend.append('g')
      //   // .attr('transform', `translate(${-2*gridLength}, ${inputLegendHeight+2})`)
      //   .attr('transform', `translate(${0}, ${legendHeight+2})`)
      //   .call(outputLegendAxis)
      // outputLegend.append('rect')
      //   // .attr('x',-2*gridLength).attr('y',1.25*gridLength)
      //   // .attr('transform', `translate(${-2*gridLength}, ${0})`)
      //   .attr('transform', `translate(${0}, ${0})`)
      //   .attr('width', 4 * gridLength).attr('height', legendHeight)
      //   .style('fill', 'url(#outputGradient)');

      // 绘制 input row
      let rowInput = svg.selectAll(".rowInput") // 绘制一行
        .data(this.inputGridData)
        .enter().append("g")
        .attr("class","row")
        .attr('transform',`translate(${(svgWidth-totalRectWidth)/2},${inputRowTransY})`);
      // let columnInput = rowInput.selectAll(".square") // 绘制每一列
      rowInput.selectAll(".square") // 绘制每一列
        .data(function(d){return d;})
        .enter().append("rect")
        .attr("class","square")
        .attr("x",d=>d.x)
        .attr("y",d=>d.y)
        .attr("width",d=>d.width)
        .attr("height",d=>d.height)
        .attr("opacity",0.8)
        .style("fill",(d)=>{
          let normalizedValue = (d.text-this.inputDataRange.min)/(this.inputDataRange.max-this.inputDataRange.min);
          return colorScale(normalizedValue);
        });
      // 绘制 output row
      let rowOutput = svg.selectAll(".rowOutput") // 绘制一行
        .data(this.outputGridData)
        .enter().append("g")
        .attr("class","row")
        .attr('transform',`translate(${(svgWidth-totalOutputRectWidth)/2},${outputRowTransY})`);
      // let columnOutput = rowOutput.selectAll(".square") // 绘制每一列
      rowOutput.selectAll(".square") // 绘制每一列
        .data(function(d){return d;})
        .enter().append("rect")
        .attr("class","square")
        .attr("x",d=>d.x)
        .attr("y",d=>d.y)
        .attr("width",d=>d.width)
        .attr("height",d=>d.height)
        .attr("opacity",0.8)
        .style("fill",(d)=>{
          let normalizedValue = (d.text-this.outputDataRange.min)/(this.outputDataRange.max-this.outputDataRange.min);
          return colorScale(normalizedValue);
        });
      // console.log('rowInput:',rowInput);
      // console.log('rowOutput:',columnInput);
      // console.log('rowInput:',rowInput);
      // console.log('columnOutput:',columnOutput);
      // console.log('transform of rowInput:',rowInput.attr("transform"));

      // {x:(svgWidth-totalOutputRectWidth)/2 + this.outputGridData[0][this.predict.token].x + this.outputGridData[0][this.predict.token].width/2, 
      // y:outputRowTransY},
      // draw the plus operation symbol
      // let symbolX = (svgWidth-totalOutputRectWidth)/2 + this.outputGridData[0][this.predict.token].x + this.outputGridData[0][this.predict.token].width/2 - plusSymbolRadius/2;
      let symbolX = (svgWidth-totalOutputRectWidth)/2 + this.outputGridData[0][this.predict.token].x + this.outputGridData[0][this.predict.token].width/2;
      // let symbolY = outputRowTransY - plusSymbolRadius/2;
      let symbolY = outputRowTransY - plusSymbolRadius*2;
      let symbolRectHeight = 1;
      let symbolGroup = svg.append('g').attr('class','plus-symbol').attr('transform',`translate(${symbolX},${symbolY})`);

      symbolGroup.append('rect')
        .attr('x', -plusSymbolRadius) 
        .attr('y', -plusSymbolRadius) // 这两步相当于把最外层的矩形的中心设置成锚点
        .attr('width', plusSymbolRadius * 2)
        .attr('height', plusSymbolRadius * 2)
        .attr('rx', 3)  // 使得矩形的边角变圆
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

      let symbolCircle = symbolGroup.append('circle')
        .attr('cx', -nodeLength / 2 - 0.5 * kernelRectLength)
        .attr('cy', 0)
        .attr('r', kernelRectLength * 1.5)
        .style('stroke', intermediateColor)
        .style('cursor', 'crosshair')
        .style('fill','#DDDDDD');

      // Link from bias to the plus symbol
      symbolGroup.append('path')
        // .attr('d', linkGen({
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
        // symbolY: symbolY + ,
        symbolY: outputRowTransY + constraintOutputGridCellHeigh + plusSymbolRadius*4 ,
        width:60,
        height:plusSymbolRadius * 2,
      }
      let softmaxSymbol = svg.append('g').attr('class','softmax-symbol').attr('transform',`translate(${softmaxArg.symbolX},${softmaxArg.symbolY})`);

      softmaxSymbol.append('rect')
        .attr('x', -softmaxArg.width/2) 
        .attr('y', -softmaxArg.height/2) // 这两步相当于把最外层的矩形的中心设置成锚点
        .attr('width', softmaxArg.width)
        .attr('height', softmaxArg.height)
        .attr('rx', 3)  // 使得矩形的边角变圆
        .attr('ry', 3)
        .style('fill', '#FAFAFA')
        .style('stroke', intermediateColor);

      softmaxSymbol.append('text')
        .attr('x', 0)
        .attr('y', 0)
        .style("text-anchor", "middle")
        .style('dominant-baseline', 'middle')
        .style('font-size', '12px')
        .style('opacity', 0.8)
        .text('softmax');

      // draw prediction rect
      let predictSymbolOffsetY = plusSymbolRadius * 5;
      let predictSymbolX = softmaxArg.symbolX;
      let predictSymbolY = softmaxArg.symbolY + predictSymbolOffsetY;
      let predictSymbolWidth = 60;
      let predictSymbolHeight = 20;
      let predictSymbol = svg.append('g').attr('class','predict-symbol').attr('transform',`translate(${predictSymbolX},${predictSymbolY})`);
      // let predictRect = predictSymbol.append('rect')
      predictSymbol.append('rect')
        .attr('x', -predictSymbolWidth/2) 
        .attr('y', -predictSymbolHeight/2) // 这两步相当于把最外层的矩形的中心设置成锚点
        .attr('width', predictSymbolWidth)
        .attr('height', predictSymbolHeight)
        .attr('rx', 3)  // 使得矩形的边角变圆
        .attr('ry', 3)
        .style('fill', '#FAFAFA')
        .style('cursor', 'crosshair')
        .style('stroke', intermediateColor);
      predictSymbol.append('text')
        .attr('x', 0)
        .attr('y', 0)
        .style("text-anchor", "middle")
        .style('dominant-baseline', 'middle')
        .style('font-size', '12px')
        .style('opacity', 0.8)
        .text('predict');


      // 绘制必要的 线条
      let linkGen = d3.linkVertical().x(d => d.x).y(d => d.y);
      let linkData = [{
        source:{x: symbolX, y: symbolY + plusSymbolRadius},
        target:{x: symbolX, y: outputRowTransY},
        type:'symbol-link',
      },
      {
        source:{x: symbolX, y: outputRowTransY + constraintGridCellHeigh},
        target:{x: symbolX, y: softmaxArg.symbolY - softmaxArg.height/2},
        type:'symbol-link',
      },
      {
        source:{x: symbolX, y: softmaxArg.symbolY + softmaxArg.height/2},
        target:{x: symbolX, y: softmaxArg.symbolY + predictSymbolOffsetY - predictSymbolHeight/2},
        type:'symbol-link',
      }];
      // let n = this.outputGridData[0].length;
      this.inputGridData[0].forEach(d=>{
        let source = {
          x: d.x + d.width/2 + (svgWidth-totalRectWidth)/2,
          y: d.y + inputRowTransY +  d.height,
        }
        linkData.push({
          source:{x: source.x, y: source.y},
          target:{x: (svgWidth-totalOutputRectWidth)/2 + this.outputGridData[0][this.predict.token].x + this.outputGridData[0][this.predict.token].width/2, 
                  y: symbolY - plusSymbolRadius },
          type:'max',
        })
      });
      let edgeGroup = svg.append("g").attr("class","edge-group");
      edgeGroup.selectAll("path.edge")
        .data(linkData)
        .enter().append('path')
        .attr("class",`edge`)
        .attr("d",d=>linkGen({source:d.source, target:d.target}))
        .style('fill','none')
        .style('stroke-width', edgeStrokeWidth) 
        .style('opacity', edgeOpacity)  
        .style('stroke', d=>{
          if(d.type == "max" || d.type == "symbol-link") return edgeHoverColor;
          else return edgeInitColor;
        });  



      // 添加文本
      let biasText = svg.append("text").attr('class','text');
      biasText.attr("dx", "-.2em")
        .attr("dy", ".2em")
        .style("text-anchor", "end")
        .style("font-size", Math.floor(Math.min(constraintGridCellHeigh,constraintGridCellWidth)/(2.4*textConstraintDivisor)+"px"))
        .attr('transform',`translate(${symbolX-nodeLength/2-0.5*kernelRectLength-kernelRectLength*1.5},${symbolY})`)
        .style('display','none')
        .text(`Bias: ${this.bias[this.predict.token]}`);
      symbolCircle.on('mouseover',()=>{
        // biasText.style('display','');
      });
      symbolCircle.on('mouseleave',()=>{
        // biasText.style('display','none');
      });

      svg.append("text").attr('class','text')
        .attr("dx", "-.3em")
        .attr("dy", "1em")
        .style("text-anchor", "end")
        // .style("dominant-baseline", "middle")
        .style("font-size", Math.floor(Math.min(constraintGridCellHeigh,constraintGridCellWidth)/textConstraintDivisor)+"px")
        .attr('transform',`translate(${(svgWidth-totalRectWidth)/2},${inputRowTransY})`)
        .text(`Input (${this.input.length})`);

      svg.append("text").attr('class','text')
        .attr("dx", "-.35em")
        .attr("dy", "1.5em")
        .style("text-anchor", "end")
        // .style("dominant-baseline", "middle")
        // .style("font-size", Math.floor(constraintOutputGridCellHeigh/textConstraintDivisor)+"px")
        .style("font-size", Math.floor(Math.min(constraintGridCellHeigh,constraintGridCellWidth)/(1.15*textConstraintDivisor))+"px")
        .attr('transform',`translate(${(svgWidth-totalOutputRectWidth)/2},${outputRowTransY})`)
        // .text(`Output (${this.output.length})`);
        .selectAll('.tspan')
        .data([`Output`,  `(${this.output.length})`])
        .enter().append('tspan')
        .attr('x',0)
        .attr('dy','1.2em')
        .text(d=>d);
        

      let predictText = svg.append("text").attr('class','text');
      predictText.attr("dx", "-.2em")
        .attr("dy", ".2em")
        .style("text-anchor", "middle")
        .style("font-size", Math.floor(Math.min(constraintGridCellHeigh,constraintGridCellWidth)/(2.4*textConstraintDivisor)+"px"))
        .attr('transform',`translate(${predictSymbolX},${predictSymbolY + predictSymbolHeight})`)
        // .style('display','none')
        .selectAll('.tspan')
        .data([`Token: ${this.predict.token}`, `Word: ${this.predict.word}`, `Score: ${Math.round(Math.exp(this.logSoftmax[this.predict.token])*10000)/10000}`])
        .enter().append('tspan')
        .attr('x',0)
        .attr('dy','1.5em')
        .text(d=>d);
      // predictRect.on('mouseover',()=>{
      //   predictText.style('display','');
      // });
      // predictRect.on('mouseleave',()=>{
      //   predictText.style('display','none');
      // });
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.container {
  display: flex;
  flex-direction:row;
  justify-content: space-between;
  align-items: center;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  border-radius: .5rem;
  background-color: white;
}

.box {
  padding: 5px 15px 10px 15px;
  display: flex;
  flex-direction:row;
  justify-content: space-between;
  align-items: center;
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
  display:flex;
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

#left-column{
  width:60%
}

#right-column{
  width:40%
}
</style>