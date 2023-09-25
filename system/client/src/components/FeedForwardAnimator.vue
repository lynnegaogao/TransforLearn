<template>
<div class="container">
  <svg id="feedforwardSvg" height="100%"></svg>
</div>
</template>

<script>
import * as d3 from "d3";
import {getVisualizationSizeConstraint, getDataRange, getGridData} from '../utils/detailview-utils'
import {getLegendGradient} from '../utils/draw-utils'
import {config} from '../utils/config'
export default {
  name:"FeedForwardAnimator",
  props:{
    curEquationIndex: {
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
    input: {
      type: Array,
      default: function(){return [];},
    },
    output: {
      type: Array,
      default: function(){return [];},
    },
    intermediate: {
      type: Array,
      default: function(){return [];},
    },
    activation: {
      type: Array,
      default: function(){return [];}
    },
  },
  emits:['cleanComponentView','changeEquationIndex','changeOutputColumnIndex'],
  data(){
    return {
      oldTokenIndex:0,
      oldInput:[],
      inputDataRange:{},
      intermediateDataRange:{},
      activationDataRange:{},
      outputDataRange:{},
      
      oldEquationIndex:0,
      // curEquationIndex:[0],

      oldOutputColumnIndex:0,
      // curOutputColumnIndex:[-1],

      intermediateColumnGridRow:{},
      activationColumnGridRow:{},
      outputGridRow:{},

      symbolYInter:100,
      symbolYOutput:100,


    };
  },
  beforeUpdate(){
    console.log('FeedForwardAnimator beforeUpdate');
    if(this.oldInput != this.input) {
      this.oldInput = this.input;
      this.oldTokenIndex = this.curTokenIndex;
      // this.oldEquationIndex = 0;
      // this.curEquationIndex = 0;
      // this.oldOutputColumnIndex = -1;
      // this.curOutputColumnIndex = -1;

      this.init();
      this.redraw();
    } else if (this.oldTokenIndex != this.curTokenIndex) {
       this.oldTokenIndex = this.curTokenIndex;
       this.redraw();
    } else if (this.oldEquationIndex != this.curOutputColumnIndex || this.oldOutputColumnIndex != this.curOutputColumnIndex) {
      this.oldEquationIndex = this.curEquationIndex;
      this.oldOutputColumnIndex = this.curOutputColumnIndex;
      // this.curOutputColumnIndex = -1;
      this.redraw();
    }
  },
  mounted(){
    this.init();
    this.redraw();
  },
  methods:{
    onClean(){
      this.$emit('cleanComponentView');
    },
    init(){
      this.inputDataRange = getDataRange(this.input);
      this.intermediateDataRange = getDataRange(this.intermediate);
      this.activationDataRange = getDataRange(this.activation);
      this.outputDataRange = getDataRange(this.output);
    },
    redraw(){
      // 初始化一些常量
      this.oldInput = this.input;
      this.oldTokenIndex = this.curTokenIndex;

      // 移除之前所绘制的内容
      d3.select(this.$el).selectAll('#feedforwardSvg > *').remove();

      // 获取画板
      let svg = d3.select(this.$el).select('#feedforwardSvg').attr('width',1550);
      let svgWidth = +(svg.attr('width'));
      // 提前定义一些变量
      const textConstraintDivisor = 1.3;
      // let paramsColorScale = d3.interpolateBrBG;
      let colorScale = d3.interpolateRdBu;
      let fontSize = 20;
      let inputDataRange = this.inputDataRange;
      let intermediateDataRange = this.intermediateDataRange;
      let activationDataRange = this.activationDataRange;
      let equationDataRange = { 
        max:Math.max(intermediateDataRange.max,activationDataRange.max),
        min:Math.min(intermediateDataRange.min,activationDataRange.min)
      }
      let outputDataRange = this.outputDataRange;

      // 

      // 绘制 input 
      let inputGridGroupX = 0.02*svgWidth;
      let inputGridGroupY = 50;
      let inputConstraintGridCellWidth = getVisualizationSizeConstraint(this.input[0].length,'x',400,330,40);
      let inputConstraintGridCellHeight = getVisualizationSizeConstraint(this.input.length,'y',400,330,40);
      let inputGridData = getGridData(this.input, inputConstraintGridCellWidth, inputConstraintGridCellHeight);
      let inputGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${inputGridGroupX},${inputGridGroupY})`);
      let inputGridRow = inputGridGroup.selectAll(".row")  // 绘制每一行
          .data(inputGridData).enter().append('g').attr('class','row');
      inputGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          // .attr('opacity',0.9)
          .attr('opacity',d=>{
            if(d.row!=this.curTokenIndex) return 0.25;
            else return 0.9;
          })
          .style('fill',d=>{
            let normlizedVal = (d.text-inputDataRange.min)/(inputDataRange.max-inputDataRange.min);
            return colorScale(normlizedVal);
          });
      let inputTotalGridWidth = inputConstraintGridCellWidth*this.input[0].length;
      let inputTotalGridHeight = inputConstraintGridCellHeight*this.input.length;
      let inputGridText = svg.append('text').attr("text-anchor","middle");
      inputGridText
        .attr('transform',`translate(${ inputGridGroupX + inputTotalGridWidth/2 },${inputGridGroupY/2})`)
        .attr('class','title-text')
        .attr('dy','.3em')
        .style('font-weight','bold')
        .style('font-size',fontSize)
        .text(`Input (${this.input.length},${this.input[0].length})`);
      
      getLegendGradient(svg,colorScale,'inputGradient',inputDataRange.min,inputDataRange.max)
      let gridLength = 40;
      let legendHeight = 5;
      let inputLegendScale = d3.scaleLinear()
      .range([0, 4 * gridLength])
      .domain([inputDataRange.min,inputDataRange.max]);
      let inputLegendAxis = d3.axisBottom()
      .scale(inputLegendScale)
      .tickFormat(d3.format('.2f'))
      .tickValues([inputDataRange.min, inputDataRange.min+(inputDataRange.max-inputDataRange.min)/2, inputDataRange.max]);
      let inputLegend = svg.append('g')
        .attr('transform', `translate(${inputGridGroupX+inputTotalGridWidth/2}, ${inputGridGroupY+inputTotalGridHeight+15})`);
      inputLegend.append('g')
        // .attr('transform', `translate(${-2*gridLength}, ${inputLegendHeight+2})`)
        .attr('transform', `translate(${-2*gridLength}, ${legendHeight+2})`)
        .call(inputLegendAxis)
      inputLegend.append('rect')
        // .attr('x',-2*gridLength).attr('y',1.25*gridLength)
        // .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('width', 4 * gridLength).attr('height', legendHeight)
        .style('fill', 'url(#inputGradient)');

      
      // 绘制 input column
      let inputColumnGridGroupX = inputGridGroupX + inputTotalGridWidth + 0.035*svgWidth;
      let inputColumnGridGroupY = inputGridGroupY;
      let inputColumnConstraintGridCellWidth = getVisualizationSizeConstraint(1,'x',400,360,30);
      let inputColumnConstraintGridCellHeight = getVisualizationSizeConstraint(this.input[0].length,'y',400,360,30);
      let inputColumnData = this.input[this.curTokenIndex].map(d=>[d]); // 把行向量转化为列向量
      // let inputColumDataRange = getDataRange(inputColumnData);
      let inputColumnGridData = getGridData(inputColumnData, inputColumnConstraintGridCellWidth, inputColumnConstraintGridCellHeight);
      let inputColumnGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${inputColumnGridGroupX},${inputColumnGridGroupY})`);
      let inputColumnGridRow = inputColumnGridGroup.selectAll(".row")  // 绘制每一行
          .data(inputColumnGridData).enter().append('g').attr('class','row');
      inputColumnGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          .attr('opacity',0.9)
          .style('fill',d=>{
            let normlizedVal = (d.text-inputDataRange.min)/(inputDataRange.max-inputDataRange.min);
            return colorScale(normlizedVal);
          });
      // 绘制 input column 的文本
      let inputColumnTotalGridWidth = inputColumnConstraintGridCellWidth;
      // let inputTotalGridHeight = inputConstraintGridCellHeight*this.input.length;
      let inputColumnGridText = svg.append('text').attr("text-anchor","middle");
      inputColumnGridText
        .attr('transform',`translate(${ inputColumnGridGroupX + inputColumnTotalGridWidth/2 },${0})`)
        .attr('class','title-text')
        .attr('dy','.3em')
        .style('font-weight','bold')
        .style('font-size',fontSize/1.5)
        // .text(`Input Embedding (${inputColumnData.length})`);
        .selectAll('.tspan')
        .data([`Input Embed`, `(${inputColumnData.length})`])
        .enter().append('tspan')
        .attr('x',0)
        .attr('dy','1.5em')
        .text(d=>d);

      // 绘制 intermediate column
      let intermediateColumnGridGroupX = inputColumnGridGroupX + inputColumnTotalGridWidth + 0.065*svgWidth;
      let intermediateColumnGridGroupY = inputColumnGridGroupY;
      let intermediateColumnConstraintGridCellWidth = getVisualizationSizeConstraint(1,'x',400,360,30);
      // console.log('this.intermediate:',this.intermediate);
      let intermediateColumnConstraintGridCellHeight = getVisualizationSizeConstraint(this.intermediate[0].length,'y',400,360,30);
      let intermediateColumnData = this.intermediate[this.curTokenIndex].map(d=>[d]); // 把行向量转化为列向量
      let intermediateColumnGridData = getGridData(intermediateColumnData, intermediateColumnConstraintGridCellWidth, intermediateColumnConstraintGridCellHeight);
      let intermediateColumnGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${intermediateColumnGridGroupX},${intermediateColumnGridGroupY})`);
      let intermediateColumnGridRow = intermediateColumnGridGroup.selectAll(".row")  // 绘制每一行
          .data(intermediateColumnGridData).enter().append('g').attr('class','row');
      this.intermediateColumnGridRow = intermediateColumnGridRow;
      intermediateColumnGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          .attr('opacity',0.9)
          .on('mouseover',(event,d)=>{
            // console.log('mouseover');
            // this.curEquationIndex = d.row;
            this.$emit('changeEquationIndex', d.row)// this.$emit('changeEquationIndex',newEquationIndex)
          })
          .style('stroke',(d)=>{
            if(d.row==this.curEquationIndex) return 'black';
            return null;
          })
          .style('fill',d=>{
            let normlizedVal = (d.text-equationDataRange.min)/(equationDataRange.max-equationDataRange.min);
            return colorScale(normlizedVal);
          });
      // 绘制 intermediate column 的文本
      let intermediateColumnTotalGridWidth = intermediateColumnConstraintGridCellWidth;
      let intermediateColumnTotalGridHeight = intermediateColumnConstraintGridCellHeight * intermediateColumnGridData.length;
      let intermediateColumnGridText = svg.append('text').attr("text-anchor","middle");
      intermediateColumnGridText
          .attr('transform',`translate(${ intermediateColumnGridGroupX + intermediateColumnTotalGridWidth/2 },${0})`)
          .attr('class','title-text')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/1.5)
          // .text(`Input Embedding (${inputColumnData.length})`);
          .selectAll('.tspan')
          .data([`Inter Embed`, `(${intermediateColumnGridData.length})`])
          .enter().append('tspan')
          .attr('x',0)
          .attr('dy','1.5em')
          .text(d=>d);

      // 绘制 activation column
      let activationColumnGridGroupX = intermediateColumnGridGroupX + intermediateColumnTotalGridWidth + 0.15*svgWidth;
      let activationColumnGridGroupY = intermediateColumnGridGroupY;
      let activationColumnConstraintGridCellWidth = getVisualizationSizeConstraint(1,'x',400,360,30);
      let activationColumnConstraintGridCellHeight = getVisualizationSizeConstraint(this.activation[0].length,'y',400,360,30);
      let activationColumnData = this.activation[this.curTokenIndex].map(d=>[d]); // 把行向量转化为列向量
      let activationColumnGridData = getGridData(activationColumnData, activationColumnConstraintGridCellWidth, activationColumnConstraintGridCellHeight);
      let activationColumnGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${activationColumnGridGroupX},${activationColumnGridGroupY})`);
      let activationColumnGridRow = activationColumnGridGroup.selectAll(".row")  // 绘制每一行
          .data(activationColumnGridData).enter().append('g').attr('class','row');
      this.activationColumnGridRow = activationColumnGridRow;
      activationColumnGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          .attr('opacity',0.9)
          .on('mouseover',(event,d)=>{this.$emit('changeEquationIndex', d.row)})
          .style('stroke',(d)=>{
            if(d.row==this.curEquationIndex) return 'black';
            return null;
          })
          .style('fill',d=>{
            let normlizedVal = (d.text-equationDataRange.min)/(equationDataRange.max-equationDataRange.min);
            return colorScale(normlizedVal);
          });
      // 绘制 activation column 的文本
      let activationColumnTotalGridWidth = activationColumnConstraintGridCellWidth;
      let activationColumnGridText = svg.append('text').attr("text-anchor","middle");
      activationColumnGridText
          .attr('transform',`translate(${ activationColumnGridGroupX + activationColumnTotalGridWidth/2 },${0})`)
          .attr('class','title-text')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/1.5)
          // .text(`Input Embedding (${inputColumnData.length})`);
          .selectAll('.tspan')
          .data([`Activ Embed`, `(${activationColumnGridData.length})`])
          .enter().append('tspan')
          .attr('x',0)
          .attr('dy','1.5em')
          .text(d=>d);

      // 绘制 output column
      let outputColumnGridGroupX = activationColumnGridGroupX + activationColumnTotalGridWidth + 0.065*svgWidth;
      let outputColumnGridGroupY = activationColumnGridGroupY;
      let outputColumnConstraintGridCellWidth = getVisualizationSizeConstraint(1,'x',400,360,30);
      let outputColumnConstraintGridCellHeight = getVisualizationSizeConstraint(this.output[0].length,'y',400,360,30);
      let outputColumnData = this.output[this.curTokenIndex].map(d=>[d]); // 把行向量转化为列向量
      // let inputColumDataRange = getDataRange(inputColumnData);
      let outputColumnGridData = getGridData(outputColumnData, outputColumnConstraintGridCellWidth, outputColumnConstraintGridCellHeight);
      let outputColumnGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${outputColumnGridGroupX},${outputColumnGridGroupY})`);
      let outputColumnGridRow = outputColumnGridGroup.selectAll(".row")  // 绘制每一行
          .data(outputColumnGridData).enter().append('g').attr('class','row');
      outputColumnGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          .attr('opacity',0.9)
          .on('mouseover',(event,d)=>{this.$emit('changeOutputColumnIndex',d.row);})
          .style('stroke',(d)=>{
            if(d.row==this.curOutputColumnIndex) return 'black';
            return null;
          })
          .style('fill',d=>{
            let normlizedVal = (d.text-outputDataRange.min)/(outputDataRange.max-outputDataRange.min);
            return colorScale(normlizedVal);
          });
      // 绘制 output column 的文本
      let outputColumnTotalGridWidth = outputColumnConstraintGridCellWidth;
      // let outputTotalGridHeight = outputConstraintGridCellHeight*this.output.length;
      let outputColumnGridText = svg.append('text').attr("text-anchor","middle");
      outputColumnGridText
        .attr('transform',`translate(${ outputColumnGridGroupX + outputColumnTotalGridWidth/2 },${0})`)
        .attr('class','title-text')
        .attr('dy','.3em')
        .style('font-weight','bold')
        .style('font-size',fontSize/1.5)
        // .text(`Input Embedding (${inputColumnData.length})`);
        .selectAll('.tspan')
        .data([`Output Embed`, `(${outputColumnData.length})`])
        .enter().append('tspan')
        .attr('x',0)
        .attr('dy','1.5em')
        .text(d=>d);

      // 绘制 output 
      let outputGridGroupX = outputColumnGridGroupX + outputColumnTotalGridWidth + 0.035*svgWidth;
      let outputGridGroupY = outputColumnGridGroupY;
      let outputConstraintGridCellWidth = getVisualizationSizeConstraint(this.output[0].length,'x',400,330,40);
      let outputConstraintGridCellHeight = getVisualizationSizeConstraint(this.output.length,'y',400,330,40);
      let outputGridData = getGridData(this.output, outputConstraintGridCellWidth, outputConstraintGridCellHeight);
      let outputGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${outputGridGroupX},${outputGridGroupY})`);
      let outputGridRow = outputGridGroup.selectAll(".row")  // 绘制每一行
          .data(outputGridData).enter().append('g').attr('class','row');
      this.outputGridRow = outputGridRow;
      outputGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          // .attr('opacity',0.9)
          .attr('opacity',d=>{
            if(d.row!=this.curTokenIndex) return 0.25;
            else return 0.9;
          })
          .style('fill',d=>{
            let normlizedVal = (d.text-outputDataRange.min)/(outputDataRange.max-outputDataRange.min);
            return colorScale(normlizedVal);
          });
      let outputTotalGridWidth = outputConstraintGridCellWidth * this.output[0].length;
      let outputTotalGridHeight = inputConstraintGridCellHeight*this.input.length;
      let outputGridText = svg.append('text').attr("text-anchor","middle");
      outputGridText
        .attr('transform',`translate(${ outputGridGroupX + outputTotalGridWidth/2 },${outputGridGroupY/2})`)
        .attr('class','title-text')
        .attr('dy','.3em')
        .style('font-weight','bold')
        .style('font-size',fontSize)
        .text(`Output (${this.output.length},${this.output[0].length})`);

      getLegendGradient(svg,colorScale,'outputGradient',outputDataRange.min,outputDataRange.max)
      let outputLegendScale = d3.scaleLinear()
      .range([0, 4 * gridLength])
      .domain([outputDataRange.min,outputDataRange.max]);
      let outputLegendAxis = d3.axisBottom()
      .scale(outputLegendScale)
      .tickFormat(d3.format('.2f'))
      .tickValues([outputDataRange.min, outputDataRange.min+(outputDataRange.max-outputDataRange.min)/2, outputDataRange.max]);
      let outputLegend = svg.append('g')
        .attr('transform', `translate(${outputGridGroupX + outputTotalGridWidth/2}, ${outputGridGroupY+outputTotalGridHeight+15})`);
      outputLegend.append('g')
        // .attr('transform', `translate(${-2*gridLength}, ${inputLegendHeight+2})`)
        .attr('transform', `translate(${-2*gridLength}, ${legendHeight+2})`)
        .call(outputLegendAxis)
      outputLegend.append('rect')
        // .attr('x',-2*gridLength).attr('y',1.25*gridLength)
        // .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('width', 4 * gridLength).attr('height', legendHeight)
        .style('fill', 'url(#outputGradient)');

      // 接下来绘制公式
      
      let equationX = intermediateColumnGridGroupX + intermediateColumnTotalGridWidth + 0.01*svgWidth;
      let equationY = intermediateColumnGridGroupY + intermediateColumnTotalGridHeight/2;
      let equationGridLength = 40;
      let equationInterGridX = 0.025*svgWidth;
      let equationCommaX = equationInterGridX + equationGridLength*1.15;
      let equationZeroGridX = equationCommaX + equationGridLength/4; 
      let equationRightBracketX = equationZeroGridX + equationGridLength*1.18;
      let equationActivGridX = equationRightBracketX + equationGridLength/2;
      let equationGroup = svg.append('g').attr('class','equation').attr('transform',`translate(${equationX},${equationY})`)
      
      equationGroup.append('text').attr('class','equation-text')
        .style('font-weight','bold').style('font-size',fontSize/1.5)
        .text('Max ( ');
      let zeroGirdRow = equationGroup.append('g').attr('class','equation-group').attr('transform',`translate(${equationZeroGridX},${-equationGridLength/1.5})`)
        .selectAll('.row').data(getGridData([[0]],equationGridLength,equationGridLength)).enter().append('g').attr('class','row');
      zeroGirdRow
          .selectAll('.square').data(d=>d).enter().append('rect').attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y).attr("width",d=>d.width).attr("height",d=>d.height).attr('opacity',0.8)
          .style('stroke','black')
          .style("fill",(d)=>{
            let normalizedValue = (d.text-equationDataRange.min)/(equationDataRange.max-equationDataRange.min);
            return colorScale(normalizedValue);
          });
      zeroGirdRow
          .selectAll('.text').data(d=>d).enter().append('text').attr('class','text')
          .attr("x", d=>d.x+d.width/2).attr("y", d=>d.y+d.height/2)
          .style("text-anchor","middle").style("dominant-baseline","middle")
          .style('font-size',fontSize/textConstraintDivisor)
          .style('fill',d=>{
            let normalizedValue = (d.text-equationDataRange.min)/(equationDataRange.max-equationDataRange.min);
            if(normalizedValue < 0.2 || normalizedValue > 0.8){
              return 'white';
            } else {
              return 'black';
            }
          }).text(d=>d.text.toString());
      
      equationGroup.append('text').attr('class','equation-text').attr('transform',`translate(${equationCommaX},${0})`)
        .style('font-weight','bold').style('font-size',fontSize/1.5)
        .text(' , ');

      let interGridRow = equationGroup.append('g').attr('class','equation-group').attr('transform',`translate(${equationInterGridX},${-equationGridLength/1.5})`)
        .selectAll('.row').data(getGridData([[ this.intermediate[this.curTokenIndex][this.curEquationIndex] ]],equationGridLength,equationGridLength))
          .enter().append('g').attr('class','row');
      interGridRow
        .selectAll('.square').data(d=>d).enter().append('rect').attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y).attr("width",d=>d.width).attr("height",d=>d.height).attr('opacity',0.8)
          .style('stroke','black')
          .style("fill",(d)=>{
            let normalizedValue = (d.text-equationDataRange.min)/(equationDataRange.max-equationDataRange.min);
            return colorScale(normalizedValue);
          }).text(d=>d.text);
      interGridRow
        .selectAll('.text').data(d=>d).enter().append('text').attr('class','text')
          .attr("x", d=>d.x+d.width/2).attr("y", d=>d.y+d.height/2)
          .style("text-anchor","middle").style("dominant-baseline","middle")
          .style('font-weight','bold').style('font-size',fontSize/textConstraintDivisor)
          .style('fill',d=>{
            let normalizedValue = (d.text-equationDataRange.min)/(equationDataRange.max-equationDataRange.min);
            if(normalizedValue < 0.2 || normalizedValue > 0.8){
              return 'white';
            } else {
              return 'black';
            }
          }).text(d=>Math.round(d.text*100)/100);

      equationGroup.append('text').attr('class','equation-text').attr('transform',`translate(${equationRightBracketX},${0})`)
        .style('font-weight','bold').style('font-size',fontSize/1.5)
        .text(' ) = ');
        
      let activGirdRow =equationGroup.append('g').attr('class','equation-group').attr('transform',`translate(${equationActivGridX},${-equationGridLength/1.5})`)
        .selectAll('.row').data(getGridData([[ this.activation[this.curTokenIndex][this.curEquationIndex] ]],equationGridLength,equationGridLength))
          .enter().append('g').attr('class','row');
      activGirdRow
        .selectAll('.square').data(d=>d).enter().append('rect').attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y).attr("width",d=>d.width).attr("height",d=>d.height).attr('opacity',0.8)
          .style('stroke','black')
          .style("fill",(d)=>{
            let normalizedValue = (d.text-equationDataRange.min)/(equationDataRange.max-equationDataRange.min);
            return colorScale(normalizedValue);
          }).text(d=>d.text);
      activGirdRow
        .selectAll('.text').data(d=>d).enter().append('text').attr('class','text')
          .attr("x", d=>d.x+d.width/2).attr("y", d=>d.y+d.height/2)
          .style("text-anchor","middle").style("dominant-baseline","middle")
          .style('font-weight','bold').style('font-size',fontSize/textConstraintDivisor)
          .style('fill',d=>{
            let normalizedValue = (d.text-equationDataRange.min)/(equationDataRange.max-equationDataRange.min);
            if(normalizedValue < 0.2 || normalizedValue > 0.8){
              return 'white';
            } else {
              return 'black';
            }
          }).text(d=>Math.round(d.text*100)/100);
      
      // 接下来准备绘制 plus symbols + links
      // 初始准备
      const edgeStrokeWidth = config.edgeStrokeWidth;
      const edgeOpacity = config.edgeOpacity;
      const edgeInitColor = config.edgeInitColor;
      const edgeHoverColor = config.edgeHoverColor;
      const plusSymbolRadius = config.plusSymbolRadius;
      const intermediateColor = config.intermediateColor;
      const kernelRectLength = config.kernelRectLength;
      const nodeLength = config.nodeLength;

      // 绘制 plus symbol - intermediate column
      let symbolXInter = intermediateColumnGridGroupX - plusSymbolRadius*2.5;
      let symbolYInter = intermediateColumnGridGroupY + intermediateColumnGridData[this.curEquationIndex][0].y + intermediateColumnGridData[this.curEquationIndex][0].height/2;
      let symbolRectHeight = 1;
      let symbolInterGroup = svg.append('g').attr('class','plus-symbol').attr('transform',`translate(${symbolXInter},${symbolYInter})`);
      symbolInterGroup.append('rect')
        .attr('x', -plusSymbolRadius).attr('y', -plusSymbolRadius)
        .attr('width', plusSymbolRadius*2).attr('height', plusSymbolRadius*2)
        .attr('rx', 3).attr('ry',3)
        .style('fill','none').style('stroke',intermediateColor);
      symbolInterGroup.append('rect')
        .attr('x', -(plusSymbolRadius - 3)).attr('y', -symbolRectHeight / 2)
        .attr('width', 2 * (plusSymbolRadius - 3)).attr('height', symbolRectHeight)
        .style('fill',intermediateColor);
      symbolInterGroup.append('rect')
        .attr('x', -symbolRectHeight / 2).attr('y', -(plusSymbolRadius - 3))
        .attr('width', symbolRectHeight).attr('height', 2 * (plusSymbolRadius - 3))
        .style('fill',intermediateColor);
      // let symbolInterCircle = symbolInterGroup.append('circle')
      symbolInterGroup.append('circle')
        .attr('cx', 0).attr('cy', -nodeLength / 2 - 0.5 * kernelRectLength)
        .attr('r', kernelRectLength * 1.5)
        .style('stroke', intermediateColor)
        .style('cursor', 'crosshair')
        .style('fill','#DDDDDD');
      symbolInterGroup.append('path')
        .attr('d', (d3.linkHorizontal().x(d => d.x).y(d => d.y))({
          source: { x: 0, y: 0 },
          target: { x: 0, y: -nodeLength / 2 - 0.5 * kernelRectLength }
        }))
        .attr('id', 'bias-plus')
        .attr('stroke-width', 1.2)
        .attr('stroke', '#E5E5E5')
        .lower();

      // 绘制 plus symbol - output column
      let symbolXOutput = outputColumnGridGroupX - plusSymbolRadius*2.5;
      let symbolYOutput = outputColumnGridGroupY + outputColumnGridData[this.curOutputColumnIndex][0].y + outputColumnGridData[this.curOutputColumnIndex][0].height/2;
      let symbolOutputGroup = svg.append('g').attr('class','plus-symbol').attr('transform',`translate(${symbolXOutput},${symbolYOutput})`);
      symbolOutputGroup.append('rect')
        .attr('x', -plusSymbolRadius).attr('y', -plusSymbolRadius)
        .attr('width', plusSymbolRadius*2).attr('height', plusSymbolRadius*2)
        .attr('rx', 3).attr('ry',3)
        .style('fill','none').style('stroke',intermediateColor);
      symbolOutputGroup.append('rect')
        .attr('x', -(plusSymbolRadius - 3)).attr('y', -symbolRectHeight / 2)
        .attr('width', 2 * (plusSymbolRadius - 3)).attr('height', symbolRectHeight)
        .style('fill',intermediateColor);
      symbolOutputGroup.append('rect')
        .attr('x', -symbolRectHeight / 2).attr('y', -(plusSymbolRadius - 3))
        .attr('width', symbolRectHeight).attr('height', 2 * (plusSymbolRadius - 3))
        .style('fill',intermediateColor);
      // let symbolOutputCircle = symbolInterGroup.append('circle')
      symbolOutputGroup.append('circle')
        .attr('cx', 0).attr('cy', -nodeLength / 2 - 0.5 * kernelRectLength)
        .attr('r', kernelRectLength * 1.5)
        .style('stroke', intermediateColor)
        .style('cursor', 'crosshair')
        .style('fill','#DDDDDD');
      symbolOutputGroup.append('path')
        .attr('d', (d3.linkHorizontal().x(d => d.x).y(d => d.y))({
          source: { x: 0, y: 0 },
          target: { x: 0, y: -nodeLength / 2 - 0.5 * kernelRectLength }
        }))
        .attr('id', 'bias-plus')
        .attr('stroke-width', 1.2)
        .attr('stroke', '#E5E5E5')
        .lower();

      // 绘制图上的 links
      let linkGen = d3.linkHorizontal().x(d=>d.x).y(d=>d.y);
      let linkData = [{
        source:{x: symbolXInter + plusSymbolRadius , y:symbolYInter},
        target:{x: intermediateColumnGridGroupX , y:symbolYInter},
        type:'symbol-link'
      },{
        source:{x: symbolXOutput + plusSymbolRadius , y:symbolYOutput},
        target:{x: outputColumnGridGroupX , y:symbolYOutput},
        type:'symbol-link'
      }]
      let inGrid = inputGridData[this.curTokenIndex][inputGridData[0].length-1]
      inputColumnGridData.forEach(d=>{
        linkData.push({
          source:{
            x: inputColumnGridGroupX + d[0].x + d[0].width,
            y: inputColumnGridGroupY + d[0].y + d[0].height/2,
          },
          target:{
            x: symbolXInter - plusSymbolRadius + 1,
            y: symbolYInter,
          },
          type:'interaction-link'
        });
        linkData.push({
          target:{
            x: inputColumnGridGroupX + d[0].x,
            y: inputColumnGridGroupY + d[0].y + d[0].height/2,
          },
          source:{
            x: inputGridGroupX + inGrid.x + inGrid.width,
            y: inputGridGroupY + inGrid.y + inGrid.height/2,
          },
          type:'token-link'
        });
      });
      activationColumnGridData.forEach(d=>{
        let source = {
          x: activationColumnGridGroupX + d[0].x + d[0].width,
          y: activationColumnGridGroupY + d[0].y + d[0].height/2,
        };
        let target = {
          x: symbolXOutput - plusSymbolRadius + 1,
          y: symbolYOutput,
        };
        linkData.push({
          source,
          target,
          type:'interaction-link'
        });
      });
      let outGrid = outputGridData[this.curTokenIndex][0]
      outputColumnGridData.forEach(d=>{
        linkData.push({
          source:{
            x: outputColumnGridGroupX + d[0].x +d[0].width,
            y: outputColumnGridGroupY + d[0].y + d[0].height/2,
          },
          target:{
            x: outputGridGroupX + outGrid.x,
            y: outputGridGroupY + outGrid.y + outGrid.height/2,
          },
          type:'token-link'
        });
      });
      let edgeGroup = svg.append("g").attr("class","edge-group");
      edgeGroup.selectAll("path.edge").data(linkData).enter().append('path')
        .attr('class','edge').attr('d',d=>linkGen({source:d.source, target:d.target}))
        .style('fill','none').style('stroke-width',edgeStrokeWidth).style('opacity',edgeOpacity)
        .style('stroke',d=>{
          if(d.type == "symbol-link") return edgeHoverColor;
          else return edgeInitColor;
        });
       
    },
  }
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
  width:100%;
  height:100%;
}

.box {
  padding: 5px 15px 10px 15px;
  display: flex;
  flex-direction:column;
  justify-content: space-between;
  /* align-items: center; */
  align-items: stretch;
  width:100%;
  height:100%;
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