<template>
<div class="container">
  <svg id="crossAttentionSvg" height="100%"></svg>
</div>
</template>

<script>
import * as d3 from "d3";
import {getVisualizationSizeConstraint, getDataRange, getGridData} from '../utils/detailview-utils'
import {getLegendGradient} from '../utils/draw-utils'
import {config} from '../utils/config'
export default {
  name:"CrossAttentionAnimator",
  props:{
    nodeData: {
      type: Object,
      default: function(){return {};},
    },
    nodeParams: {
      type: Array,
      default: function(){return [[],[]];},
    },
  },
  emits:['cleanComponentView','openHeadDetailView','openAttentionDetailView','openConcaAndLinearDetailView'],
  data(){
    return {
      svgLeftWidth:400,
    };
  },
  beforeUpdate(){
    this.init();
    this.redraw();
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
      // input 与 output 的 data range
      this.inputDataRange = getDataRange(this.nodeData.input[0]);
      this.inputFromEncoderDataRange = getDataRange(this.nodeData.input[1]);
      this.outputDataRange = getDataRange(this.nodeData.output);
      // 各个 head 内的 Q, K, V 的 data range
      let lowDimQueryDataRangeArray = [];
      let lowDimKeyDataRangeArray = [];
      let lowDimValueDataRangeArray = [];
      this.nodeData.mat_QKV.forEach(QKV=>{
        lowDimQueryDataRangeArray.push(getDataRange(QKV[0]));
        lowDimKeyDataRangeArray.push(getDataRange(QKV[1]));
        lowDimValueDataRangeArray.push(getDataRange(QKV[2]));
      });
      this.lowDimQueryDataRangeArray = lowDimQueryDataRangeArray;
      this.lowDimKeyDataRangeArray = lowDimKeyDataRangeArray;
      this.lowDimValueDataRangeArray = lowDimValueDataRangeArray;
      
      this.lowDimQueryTotalDataRange = {
        max:-1E5,
        min:1E5,
      };
      lowDimQueryDataRangeArray.forEach(obj=>{
        this.lowDimQueryTotalDataRange.max = Math.max(this.lowDimQueryTotalDataRange.max,obj.max);
        this.lowDimQueryTotalDataRange.min = Math.min(this.lowDimQueryTotalDataRange.min,obj.min);
      });

      this.lowDimKeyTotalDataRange = {
        max:-1E5,
        min:1E5,
      };
      lowDimKeyDataRangeArray.forEach(obj=>{
        this.lowDimKeyTotalDataRange.max = Math.max(this.lowDimKeyTotalDataRange.max,obj.max);
        this.lowDimKeyTotalDataRange.min = Math.min(this.lowDimKeyTotalDataRange.min,obj.min);
      });

      this.lowDimValueTotalDataRange = {
        max:-1E5,
        min:1E5,
      };
      lowDimValueDataRangeArray.forEach(obj=>{
        this.lowDimValueTotalDataRange.max = Math.max(this.lowDimValueTotalDataRange.max,obj.max);
        this.lowDimValueTotalDataRange.min = Math.min(this.lowDimValueTotalDataRange.min,obj.min);
      });
      
      // 计算 attention output 内的 total datarange 
      let attentionOuputDataRangeArray = [];
      this.nodeData.attention_output.forEach(attn_output=>{
        attentionOuputDataRangeArray.push(getDataRange(attn_output));
      });
      this.attentionOuputDataRangeArray = attentionOuputDataRangeArray;
      this.attentionOuputTotalDataRange = {
        max:-1E5,
        min:1E5,
      };
      attentionOuputDataRangeArray.forEach(obj=>{
        this.attentionOuputTotalDataRange.max = Math.max(this.attentionOuputTotalDataRange.max,obj.max);
        this.attentionOuputTotalDataRange.min = Math.min(this.attentionOuputTotalDataRange.min,obj.min);
      });

      this.outputAttentionGridDataArray = [];
    },
    drawSvgLeft(){
      // 绘制 Svg 的左半部分, 主要是为了和 Cross-Attention 区分开来
      let svg = d3.select(this.$el).select('#crossAttentionSvg');
      let svgWidth = this.svgLeftWidth;
      // 提前定义一些变量
      let colorScale = d3.interpolateRdBu;
      let fontSize = 20;
      let inputDataRange = this.inputDataRange;
      let inputFromEncoderDataRange = this.inputFromEncoderDataRange;

      // 绘制 input - as query
      let inputGridGroupX = 0.03*svgWidth;
      let inputGridGroupY = 45;
      let xSizeOfInputFromDecoder = 320;
      let ySizeOfInputFromDecoder = 100;
      let maximumCellSize = 30;
      let inputConstraintGridCellWidth = getVisualizationSizeConstraint(this.nodeData.input[0][0].length,'x',xSizeOfInputFromDecoder,ySizeOfInputFromDecoder,maximumCellSize);
      let inputConstraintGridCellHeight = getVisualizationSizeConstraint(this.nodeData.input[0].length,'y',xSizeOfInputFromDecoder,ySizeOfInputFromDecoder,maximumCellSize);
      let inputData = this.nodeData.input[0];
      let inputGridData = getGridData(inputData, inputConstraintGridCellWidth, inputConstraintGridCellHeight);
      let inputGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${inputGridGroupX},${inputGridGroupY})`);
      let inputGridRow = inputGridGroup.selectAll(".row")  // 绘制每一行
          .data(inputGridData).enter().append('g').attr('class','row');
      inputGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          .attr('opacity',0.9)
          .style('fill',d=>{
            let normlizedVal = (d.text-inputDataRange.min)/(inputDataRange.max-inputDataRange.min);
            return colorScale(normlizedVal);
          });
      let inputTotalGridWidth = inputConstraintGridCellWidth * inputData[0].length;
      let inputTotalGridHeight = inputConstraintGridCellHeight * inputData.length;
      let inputGridText = svg.append('text').attr("text-anchor","middle");
      inputGridText
        .attr('transform',`translate(${ inputGridGroupX + inputTotalGridWidth/2 },${inputGridGroupY/6})`)
        .attr('class','title-text')
        .attr('dy','.3em')
        .style('font-weight','bold')
        .style('font-size',fontSize/1.6)
        // .text(`Input (${inputData.length},${inputData[0].length}) to get Query, Key, Value`);
        .selectAll('.tspan')
        .data([`Input (${inputData.length},${inputData[0].length}) to get Query`,  `From decoder embedding`])
        .enter().append('tspan')
        .attr('x',0)
        .attr('dy','1.2em')
        .text(d=>d);
      getLegendGradient(svg,colorScale,'inputGradient',inputDataRange.min,inputDataRange.max)
      let gridLength = 40;
      let legendHeight = 4;
      let inputLegendScale = d3.scaleLinear()
      .range([0, 4 * gridLength])
      .domain([inputDataRange.min,inputDataRange.max]);
      let inputLegendAxis = d3.axisBottom()
      .scale(inputLegendScale)
      .tickFormat(d3.format('.2f'))
      .tickValues([inputDataRange.min, inputDataRange.min+(inputDataRange.max-inputDataRange.min)/2, inputDataRange.max]);
      let inputLegend = svg.append('g')
        .attr('transform', `translate(${inputGridGroupX+inputTotalGridWidth/2}, ${inputGridGroupY+inputTotalGridHeight+5})`);
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
      

      // 绘制 input - as key and value
      let yInerval = 50;
      let inputFromEncoderGridGroupX = 0.03*svgWidth;
      let inputFromEncoderGridGroupY = inputGridGroupY + ySizeOfInputFromDecoder + yInerval + 10;
      let xSizeOfInputFromEncoder = 320;
      let ySizeOfInputFromEncoder = 200;
      let inputFromEncoderConstraintGridCellWidth = getVisualizationSizeConstraint(this.nodeData.input[1][0].length,'x',xSizeOfInputFromEncoder,ySizeOfInputFromEncoder,maximumCellSize);
      let inputFromEncoderConstraintGridCellHeight = getVisualizationSizeConstraint(this.nodeData.input[1].length,'y',xSizeOfInputFromEncoder,ySizeOfInputFromEncoder,maximumCellSize);
      let inputFromEncoderData = this.nodeData.input[1];
      let inputFromEncoderGridData = getGridData(inputFromEncoderData, inputFromEncoderConstraintGridCellWidth, inputFromEncoderConstraintGridCellHeight);
      let inputFromEncoderGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${inputFromEncoderGridGroupX},${inputFromEncoderGridGroupY})`);
      let inputFromEncoderGridRow = inputFromEncoderGridGroup.selectAll(".row")  // 绘制每一行
          .data(inputFromEncoderGridData).enter().append('g').attr('class','row');
      inputFromEncoderGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          .attr('opacity',0.9)
          .style('fill',d=>{
            let normlizedVal = (d.text-inputFromEncoderDataRange.min)/(inputFromEncoderDataRange.max-inputFromEncoderDataRange.min);
            return colorScale(normlizedVal);
          });
      let inputFromEncoderTotalGridWidth = inputFromEncoderConstraintGridCellWidth * inputFromEncoderData[0].length;
      let inputFromEncoderTotalGridHeight = inputFromEncoderConstraintGridCellHeight * inputFromEncoderData.length;
      let inputFromEncoderGridText = svg.append('text').attr("text-anchor","middle");
      inputFromEncoderGridText
        .attr('transform',`translate(${ inputFromEncoderGridGroupX + inputFromEncoderTotalGridWidth/2 },${inputFromEncoderGridGroupY-yInerval*0.65})`)
        .attr('class','title-text')
        .attr('dy','.3em')
        .style('font-weight','bold')
        .style('font-size',fontSize/1.6)
        // .text(`Input (${inputData.length},${inputData[0].length}) to get Query, Key, Value`);
        .selectAll('.tspan')
        .data([`Input (${inputFromEncoderData.length},${inputFromEncoderData[0].length}) to get Key, Value`,  `From encoder output`])
        .enter().append('tspan')
        .attr('x',0)
        .attr('dy','1.2em')
        .text(d=>d);
      getLegendGradient(svg,colorScale,'inputFromEncoderGradient',inputFromEncoderDataRange.min,inputFromEncoderDataRange.max)
      let inputEncoderLegendScale = d3.scaleLinear()
      .range([0, 4 * gridLength])
      .domain([inputFromEncoderDataRange.min,inputFromEncoderDataRange.max]);
      let inputEncoderLegendAxis = d3.axisBottom()
      .scale(inputEncoderLegendScale)
      .tickFormat(d3.format('.2f'))
      .tickValues([inputFromEncoderDataRange.min, inputFromEncoderDataRange.min+(inputFromEncoderDataRange.max-inputFromEncoderDataRange.min)/2, inputFromEncoderDataRange.max]);
      let inputEncoderLegend = svg.append('g')
        .attr('transform', `translate(${inputFromEncoderGridGroupX+inputFromEncoderTotalGridWidth/2}, ${inputFromEncoderGridGroupY+inputFromEncoderTotalGridHeight+5})`);
      inputEncoderLegend.append('g')
        // .attr('transform', `translate(${-2*gridLength}, ${inputLegendHeight+2})`)
        .attr('transform', `translate(${-2*gridLength}, ${legendHeight+2})`)
        .call(inputEncoderLegendAxis)
      inputEncoderLegend.append('rect')
        // .attr('x',-2*gridLength).attr('y',1.25*gridLength)
        // .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('width', 4 * gridLength).attr('height', legendHeight)
        .style('fill', 'url(#inputFromEncoderGradient)');

    },
    drawSvgRight(){
      // 绘制 Svg 的右半部分, 这部分在 self-attention 和 cross-attention 都是相同的;
      // 初始化一些通用的变量
      // let inputGridGroupX = this.inputGridGroupX;
      // let inputGridGroupY = this.inputGridGroupY;
      // let inputGridData = this.inputGridData;
      // let inputTotalGridWidth = this.inputTotalGridWidth;
      // let inputTotalGridHeight = this.inputTotalGridHeight;

      // let lowDimQueryTotalDataRange = this.lowDimQueryTotalDataRange;
      // let lowDimKeyTotalDataRange = this.lowDimKeyTotalDataRange;
      // let lowDimValueTotalDataRange = this.lowDimValueTotalDataRange;
      let attentionOuputTotalDataRange = this.attentionOuputTotalDataRange;
      let outputDataRange = this.outputDataRange;

      let svg = d3.select(this.$el).select('#crossAttentionSvg');
      let svgWidth = +(svg.attr('width')) - this.svgLeftWidth;
      
      let colorScale = d3.interpolateRdBu;
      let fontSize = 20;
      let HeadsGroupX = this.svgLeftWidth + 0.02 * svgWidth;
      let HeadsGroupY = 40;
      let xSizeOfEachHead = 240; // width 
      let ySizeOfEachHead = 55; // height
      let maximumCellSize = 30;
      let headInterval = 25 // 每个 head 之间的间隔
      let matInterval = 7.5 // 每个 mat 之间的间隔

      let headsQKVgroup = svg.append('g').attr('class','heads-QKV-group').attr('transform',`translate(${HeadsGroupX},${HeadsGroupY})`);

      let QKVTitleText = svg.append('text').attr("text-anchor","middle");
        QKVTitleText
          .attr('transform',`translate(${ HeadsGroupX + xSizeOfEachHead/2 },${HeadsGroupY/5})`)
          .attr('class','title-text')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/1.8)
          .text(`Query,Key,Value in all heads`);
      let shapeQueryText = svg.append('text').attr("text-anchor","middle");
        shapeQueryText
          .attr('transform',`translate(${ HeadsGroupX + xSizeOfEachHead/2 },${HeadsGroupY*0.5})`)
          .attr('class','title-text')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/2.2)
          .text(`Size of Query in each head: (${this.nodeData.mat_QKV[0][0].length},${this.nodeData.mat_QKV[0][0][0].length})`);
      let shapeKVText = svg.append('text').attr("text-anchor","middle");
        shapeKVText
          .attr('transform',`translate(${ HeadsGroupX + xSizeOfEachHead/2 },${HeadsGroupY*0.8})`)
          .attr('class','title-text')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/2.2)
          .text(`Size of Key and Value in each head: (${this.nodeData.mat_QKV[0][1].length},${this.nodeData.mat_QKV[0][1][0].length})`);
      let attentionOutputText = svg.append('text').attr("text-anchor","middle");
        attentionOutputText
          .attr('transform',`translate(${ HeadsGroupX + xSizeOfEachHead*2.15 },${HeadsGroupY*0.5})`)
          .attr('class','title-text')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/1.5)
          .text(`Attenion output in each head: (${this.nodeData.attention_output[0].length},${this.nodeData.attention_output[0][0].length})`);

      // drawHeadsQKV.call(this, HeadsGroupX, HeadsGroupY, xSizeOfEachHead, ySizeOfEachHead, maximumCellSize);
      drawHead.call(this, svg, headsQKVgroup, 0, HeadsGroupX, HeadsGroupY, matInterval, xSizeOfEachHead, ySizeOfEachHead, maximumCellSize);
      drawHead.call(this, svg, headsQKVgroup, 1, HeadsGroupX, HeadsGroupY, matInterval, xSizeOfEachHead, ySizeOfEachHead, maximumCellSize);
      drawHead.call(this, svg, headsQKVgroup, 2, HeadsGroupX, HeadsGroupY, matInterval, xSizeOfEachHead, ySizeOfEachHead, maximumCellSize);
      drawHead.call(this, svg, headsQKVgroup, 3, HeadsGroupX, HeadsGroupY, matInterval, xSizeOfEachHead, ySizeOfEachHead, maximumCellSize);

      let gridLength = 40;
      let legendHeight = 5;
      getLegendGradient(svg,colorScale,'attentionGradient',attentionOuputTotalDataRange.min,attentionOuputTotalDataRange.max)
      let attentionLegendScale = d3.scaleLinear()
      .range([0, 4 * gridLength])
      .domain([attentionOuputTotalDataRange.min,attentionOuputTotalDataRange.max]);
      let attentionLegendAxis = d3.axisBottom()
      .scale(attentionLegendScale)
      .tickFormat(d3.format('.2f'))
      .tickValues([attentionOuputTotalDataRange.min, attentionOuputTotalDataRange.min+(attentionOuputTotalDataRange.max-attentionOuputTotalDataRange.min)/2, attentionOuputTotalDataRange.max]);
      let attentionLegend = svg.append('g')
        .attr('transform', `translate(${this.svgLeftWidth + svgWidth*0.47}, ${402})`);
      attentionLegend.append('g')
        // .attr('transform', `translate(${-2*gridLength}, ${inputLegendHeight+2})`)
        .attr('transform', `translate(${-2*gridLength}, ${legendHeight+2})`)
        .call(attentionLegendAxis)
      attentionLegend.append('rect')
        // .attr('x',-2*gridLength).attr('y',1.25*gridLength)
        // .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('transform', `translate(${-2*gridLength}, ${0})`)
        .attr('width', 4 * gridLength).attr('height', legendHeight)
        .style('fill', 'url(#attentionGradient)');

      // 绘制 concatenate 
      let concatenateSymbolGroupX = this.svgLeftWidth + svgWidth*0.65;
      let concatenateSymbolGroupY = 225;
      let concatenateSymbolWidth = 100;
      let concatenateSymbolHeight = 40;
      let concatenateSymbol = svg.append('g').attr('class','concatennate-symbol').attr('transform',`translate(${concatenateSymbolGroupX},${concatenateSymbolGroupY})`);

      concatenateSymbol.append('rect')
        .attr('x', -concatenateSymbolWidth/2) 
        .attr('y', -concatenateSymbolHeight/2) // 这两步相当于把最外层的矩形的中心设置成锚点
        .attr('width', concatenateSymbolWidth)
        .attr('height', concatenateSymbolHeight)
        .attr('rx', 3)  // 使得矩形的边角变圆
        .attr('ry', 3)
        .style('fill', '#FAFAFA')
        .style('stroke', 'gray')
        .style('cursor', 'pointer')
        .on('click',()=>{
          this.onConcatenateAndLinearClick();
        });

      concatenateSymbol.append('text')
        .attr('x', 0)
        .attr('y', -20)
        .style("text-anchor", "middle")
        .style('dominant-baseline', 'middle')
        .style('font-size', fontSize/1.4)
        .style('opacity', 0.8)
        .style('cursor', 'pointer')
        .on('click',()=>{
          this.onConcatenateAndLinearClick();
        }).selectAll('.tspan')
        .data([`Concatenate`, `& Linear`])
        .enter().append('tspan')
        .attr('x',0)
        .attr('dy','1em')
        .text(d=>d);

      // 绘制最终的 multi-headed output 
      let outputGridGroupX = concatenateSymbolGroupX + concatenateSymbolWidth*0.9;
      let outputGridGroupY = 75;
      let outputData = this.nodeData.output;
      let outputConstraintGridCellWidth = getVisualizationSizeConstraint(outputData[0].length,'x',330,300,40);
      let outputConstraintGridCellHeight = getVisualizationSizeConstraint(outputData.length,'y',330,300,40);
      let outputGridData = getGridData(outputData, outputConstraintGridCellWidth, outputConstraintGridCellHeight);
      let outputGridGroup = svg.append("g").attr("class","grid").attr("transform",`translate(${outputGridGroupX},${outputGridGroupY})`);
      let outputGridRow = outputGridGroup.selectAll(".row")  // 绘制每一行
          .data(outputGridData).enter().append('g').attr('class','row');
      outputGridRow.selectAll(".square")
          .data(d=>d).enter().append('rect')
          .attr('class','square')
          .attr("x",d=>d.x).attr("y",d=>d.y)
          .attr("width",d=>d.width).attr("height",d=>d.height)
          .attr('opacity',0.9)
          .style('fill',d=>{
            let normlizedVal = (d.text-outputDataRange.min)/(outputDataRange.max-outputDataRange.min);
            return colorScale(normlizedVal);
          });
      let outputTotalGridWidth = outputConstraintGridCellWidth * outputData[0].length;
      let outputTotalGridHeight = outputConstraintGridCellHeight * outputData.length;
      let outputGridText = svg.append('text').attr("text-anchor","middle");
      outputGridText
        .attr('transform',`translate(${ outputGridGroupX + outputTotalGridWidth/2 },${0})`)
        .attr('class','title-text')
        .attr('dy','.3em')
        .style('font-weight','bold')
        .style('font-size',fontSize)
        // .text(`Final Output (${outputData.length},${outputData[0].length}) of Multi-Head Attention`);
        .selectAll('.tspan')
        .data([`Final Output (${outputData.length},${outputData[0].length})`, `of Multi-Head Attention`])
        .enter().append('tspan')
        .attr('x',0)
        .attr('dy','1.5em')
        .text(d=>d);

      getLegendGradient(svg,colorScale,'outputGradient',outputDataRange.min,outputDataRange.max)
      let outputLegendScale = d3.scaleLinear()
      .range([0, 4 * gridLength])
      .domain([outputDataRange.min,outputDataRange.max]);
      let outputLegendAxis = d3.axisBottom()
      .scale(outputLegendScale)
      .tickFormat(d3.format('.2f'))
      .tickValues([outputDataRange.min, outputDataRange.min+(outputDataRange.max-outputDataRange.min)/2, outputDataRange.max]);
      let outputLegend = svg.append('g')
        .attr('transform', `translate(${outputGridGroupX+outputTotalGridWidth/2}, ${outputGridGroupY+outputTotalGridHeight+15})`);
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

      // let headInterval = 25 // 每个 head 之间的间隔
      // let matInterval = 7.5 // 每个 mat 之间的间隔
      // 绘制 links
      let attnOutput2concaLinkOffsetX = 83
      let attnOutput2concaLinkStartY = 75;
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);
      let linkData = [{
        source:{x: concatenateSymbolGroupX-attnOutput2concaLinkOffsetX, y: attnOutput2concaLinkStartY,},
        target:{x: concatenateSymbolGroupX-concatenateSymbolWidth/2, y: concatenateSymbolGroupY,},
      },{
        source:{x: concatenateSymbolGroupX-attnOutput2concaLinkOffsetX, y: 10 + attnOutput2concaLinkStartY + 1*(2.5*ySizeOfEachHead/3 + 2*matInterval + headInterval),},
        target:{x: concatenateSymbolGroupX-concatenateSymbolWidth/2, y: concatenateSymbolGroupY,},
      },{
        source:{x: concatenateSymbolGroupX-attnOutput2concaLinkOffsetX, y: 20 + attnOutput2concaLinkStartY + 2*(2.5*ySizeOfEachHead/3 + 2*matInterval + headInterval),},
        target:{x: concatenateSymbolGroupX-concatenateSymbolWidth/2, y: concatenateSymbolGroupY,},
      },{
        source:{x: concatenateSymbolGroupX-attnOutput2concaLinkOffsetX, y: 30 +attnOutput2concaLinkStartY + 3*(2.5*ySizeOfEachHead/3 + 2*matInterval + headInterval),},
        target:{x: concatenateSymbolGroupX-concatenateSymbolWidth/2, y: concatenateSymbolGroupY,},
      },{
        source:{x: concatenateSymbolGroupX+concatenateSymbolWidth/2, y: concatenateSymbolGroupY,},
        target:{x: outputGridGroupX-2, y: outputGridGroupY+outputTotalGridHeight/2,},
      }]
      const edgeHoverColor = config.edgeHoverColor;
      let edgeGroup = svg.append("g").attr("class","edge-group");
      edgeGroup.selectAll("path.edge")
        .data(linkData)
        .enter().append('path')
        .attr("class",`edge`)
        .attr("d",d=>linkGen({source:d.source, target:d.target}))
        .style('fill','none')
        .style('stroke-width', 1.2) 
        .style('opacity', 1)  
        .style('stroke', edgeHoverColor );

      // 定义绘制 QKV 矩阵的函数 ( Q, K, V in 4 heads)
      function drawHead(svg, headsQKVgroup, headNum, HeadsGroupX, HeadsGroupY, yInterval, xSize, ySize, maximumCellSize){
        // 定义 每一个 Matrix 的 Size
        let xSizeOfEachMat = xSize;
        let ySizeOfEachMat = ySize/3;

        // 定义描述性文本的向左偏移量
        let xOffsetDescription = 12.5;
        
        // 第一个 head 内的 QKV 的 group
        let group1 = headsQKVgroup.append('g').attr('class','head').attr('transform',`translate(${0},${headNum*(ySize+2*yInterval+headInterval)})`);
        // 绘制 query 1
        // let query1Data = this.nodeData.mat_QKV[0][0];
        let query1Data = this.nodeData.mat_QKV[headNum][0];
        let query1ConstraintGridCellWidth = getVisualizationSizeConstraint(query1Data[0].length,'x',xSizeOfEachMat,ySizeOfEachMat,maximumCellSize);
        let query1ConstraintGridCellHeight = getVisualizationSizeConstraint(query1Data.length,'y',xSizeOfEachMat,ySizeOfEachMat,maximumCellSize);
        let query1GridData = getGridData(query1Data, query1ConstraintGridCellWidth, query1ConstraintGridCellHeight);
        let query1GridGroup = group1.append("g").attr("class","grid").attr("transform",`translate(${0},${0})`);
        let query1GridRow = query1GridGroup.selectAll(".row")  // 绘制每一行
            .data(query1GridData).enter().append('g').attr('class','row');
        let lowDimQueryDataRange = this.lowDimQueryDataRangeArray[headNum];
        query1GridRow.selectAll(".square")
            .data(d=>d).enter().append('rect')
            .attr('class','square')
            .attr("x",d=>d.x).attr("y",d=>d.y)
            .attr("width",d=>d.width).attr("height",d=>d.height)
            .attr('opacity',0.9)
            .style('fill',d=>{
              // let normlizedVal = (d.text-lowDimQueryTotalDataRange.min)/(lowDimQueryTotalDataRange.max-lowDimQueryTotalDataRange.min);
              let normlizedVal = (d.text-lowDimQueryDataRange.min)/(lowDimQueryDataRange.max-lowDimQueryDataRange.min);
              return colorScale(normlizedVal);
            });
        let query1Text = query1GridGroup.append('text').attr("text-anchor","middle");
        query1Text
          .attr('transform',`translate(${ -xOffsetDescription },${ySizeOfEachMat/2})`)
          .attr('class','description')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/2)
          .text(`Q${headNum+1}`);
        
        // 绘制 key 1
        let key1Data = this.nodeData.mat_QKV[headNum][1];
        let key1ConstraintGridCellWidth = getVisualizationSizeConstraint(key1Data[0].length,'x',xSizeOfEachMat,ySizeOfEachMat,maximumCellSize);
        let key1ConstraintGridCellHeight = getVisualizationSizeConstraint(key1Data.length,'y',xSizeOfEachMat,ySizeOfEachMat,maximumCellSize);
        let key1GridData = getGridData(key1Data, key1ConstraintGridCellWidth, key1ConstraintGridCellHeight);
        let key1GridGroup = group1.append("g").attr("class","grid").attr("transform",`translate(${0},${ySizeOfEachMat + yInterval})`);
        let key1GridRow = key1GridGroup.selectAll(".row")  // 绘制每一行
            .data(key1GridData).enter().append('g').attr('class','row');
        let lowDimKeyDataRange = this.lowDimKeyDataRangeArray[headNum];
        key1GridRow.selectAll(".square")
            .data(d=>d).enter().append('rect')
            .attr('class','square')
            .attr("x",d=>d.x).attr("y",d=>d.y)
            .attr("width",d=>d.width).attr("height",d=>d.height)
            .attr('opacity',0.9)
            .style('fill',d=>{
              // let normlizedVal = (d.text-lowDimKeyTotalDataRange.min)/(lowDimKeyTotalDataRange.max-lowDimKeyTotalDataRange.min);
              let normlizedVal = (d.text-lowDimKeyDataRange.min)/(lowDimKeyDataRange.max-lowDimKeyDataRange.min);
              return colorScale(normlizedVal);
            });
        let key1Text = key1GridGroup.append('text').attr("text-anchor","middle");
        key1Text
          .attr('transform',`translate(${ -xOffsetDescription },${ySizeOfEachMat/2})`)
          .attr('class','description')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/2)
          .text(`K${headNum+1}`);
        
        // 绘制 value 1
        let value1Data = this.nodeData.mat_QKV[headNum][2];
        let value1ConstraintGridCellWidth = getVisualizationSizeConstraint(value1Data[0].length,'x',xSizeOfEachMat,ySizeOfEachMat,maximumCellSize);
        let value1ConstraintGridCellHeight = getVisualizationSizeConstraint(value1Data.length,'y',xSizeOfEachMat,ySizeOfEachMat,maximumCellSize);
        let value1GridData = getGridData(value1Data, value1ConstraintGridCellWidth, value1ConstraintGridCellHeight);
        let value1GridGroup = group1.append("g").attr("class","grid").attr("transform",`translate(${0},${ySizeOfEachMat*2 + yInterval*2})`);
        let value1GridRow = value1GridGroup.selectAll(".row")  // 绘制每一行
            .data(value1GridData).enter().append('g').attr('class','row');
        // let lowDimValueDataRange = this.lowDimValueDataRangeArray[headNum];
        value1GridRow.selectAll(".square")
            .data(d=>d).enter().append('rect')
            .attr('class','square')
            .attr("x",d=>d.x).attr("y",d=>d.y)
            .attr("width",d=>d.width).attr("height",d=>d.height)
            .attr('opacity',0.9)
            .style('fill',d=>{
              // let normlizedVal = (d.text-lowDimValueTotalDataRange.min)/(lowDimValueTotalDataRange.max-lowDimValueTotalDataRange.min);
              // let normlizedVal = (d.text-lowDimValueDataRange.min)/(lowDimValueDataRange.max-lowDimValueDataRange.min);
              let normlizedVal = (d.text-this.attentionOuputTotalDataRange.min)/(this.attentionOuputTotalDataRange.max-this.attentionOuputTotalDataRange.min);
              return colorScale(normlizedVal);
            });
        let value1Text = value1GridGroup.append('text').attr("text-anchor","middle");
        value1Text
          .attr('transform',`translate(${ -xOffsetDescription },${ySizeOfEachMat/2})`)
          .attr('class','description')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/2)
          .text(`V${headNum+1}`);

        // 绘制 用以提供交互的矩形
        // draw softmax box
        // let softmaxArg = {
        //   symbolX: symbolX,
        //   // symbolY: symbolY + ,
        //   symbolY: outputRowTransY + constraintOutputGridCellHeigh + plusSymbolRadius*4 ,
        //   width:60,
        //   height:plusSymbolRadius * 2,
        // }
        let headSymbolWidth = xOffsetDescription*4;
        let headSymbolHeight = 20;
        let headSymbol = group1.append('g').attr('class','head-symbol').attr('transform',`translate(${-xOffsetDescription*4.25},${ySizeOfEachMat*1.5 + yInterval})`);

        headSymbol.append('rect')
          .attr('x', -headSymbolWidth/2) 
          .attr('y', -headSymbolHeight/2) // 这两步相当于把最外层的矩形的中心设置成锚点
          .attr('width', headSymbolWidth)
          .attr('height', headSymbolHeight)
          .attr('rx', 3)  // 使得矩形的边角变圆
          .attr('ry', 3)
          .style('fill', '#FAFAFA')
          .style('stroke', 'gray')
          .style('cursor', 'pointer')
          .on('click',()=>{
            this.onHeadClick(headNum);
          });

        headSymbol.append('text')
          .attr('x', 0)
          .attr('y', 0)
          .style("text-anchor", "middle")
          .style('dominant-baseline', 'middle')
          .style('font-size', fontSize/2)
          .style('opacity', 0.8)
          .text(`Head ${headNum+1}`)
          .style('cursor', 'pointer')
          .on('click',()=>{
            this.onHeadClick(headNum);
          });
        
        
        let attentionSymbolGroupX = xSizeOfEachHead*1.25;
        let attentionSymbolWidth = 100;
        let attentionSymbolHeight = 30;
        let attentionSymbol = group1.append('g').attr('class','attention-symbol').attr('transform',`translate(${attentionSymbolGroupX},${ySizeOfEachMat*1.5 + yInterval})`);

        attentionSymbol.append('rect')
          .attr('x', -attentionSymbolWidth/2) 
          .attr('y', -attentionSymbolHeight/2) // 这两步相当于把最外层的矩形的中心设置成锚点
          .attr('width', attentionSymbolWidth)
          .attr('height', attentionSymbolHeight)
          .attr('rx', 3)  // 使得矩形的边角变圆
          .attr('ry', 3)
          .style('fill', '#FAFAFA')
          .style('stroke', 'gray')
          .style('cursor', 'pointer')
          .on('click',()=>{
            this.onAttentionClick(headNum);
          });

        attentionSymbol.append('text')
          .attr('x', 0)
          .attr('y', 0)
          .style("text-anchor", "middle")
          .style('dominant-baseline', 'middle')
          .style('font-size', fontSize/1.4)
          .style('opacity', 0.8)
          .text(` Attention  ops. `)
          .style('cursor', 'pointer')
          .on('click',()=>{
            this.onAttentionClick(headNum);
          });

        // 绘制 attention 的结果
        let attentionOuputGridGroupX = attentionSymbolGroupX + 0.4*xSizeOfEachHead;
        let attentionOuputData = this.nodeData.attention_output[headNum];
        let attentionOuputConstraintGridCellWidth = getVisualizationSizeConstraint(attentionOuputData[0].length,'x',xSizeOfEachHead,ySizeOfEachHead*1.25,maximumCellSize);
        let attentionOuputConstraintGridCellHeight = getVisualizationSizeConstraint(attentionOuputData.length,'y',xSizeOfEachHead,ySizeOfEachHead*1.25,maximumCellSize);
        let attentionOuputGridData = getGridData(attentionOuputData, attentionOuputConstraintGridCellWidth, attentionOuputConstraintGridCellHeight);
        let attentionOuputGridGroup = group1.append("g").attr("class","grid").attr("transform",`translate(${attentionOuputGridGroupX},${0})`);
        let attentionOuputGridRow = attentionOuputGridGroup.selectAll(".row")  // 绘制每一行
            .data(attentionOuputGridData).enter().append('g').attr('class','row');
        attentionOuputGridRow.selectAll(".square")
            .data(d=>d).enter().append('rect')
            .attr('class','square')
            .attr("x",d=>d.x).attr("y",d=>d.y)
            .attr("width",d=>d.width).attr("height",d=>d.height)
            .attr('opacity',0.9)
            .style('fill',d=>{
              // console.log(d);
              let normlizedVal = (d.text-attentionOuputTotalDataRange.min)/(attentionOuputTotalDataRange.max-attentionOuputTotalDataRange.min);
              // console.log(normlizedVal);
              return colorScale(normlizedVal);
            });
        
        let attentionOuputText = attentionOuputGridGroup.append('text').attr("text-anchor","middle");
        attentionOuputText
          .attr('transform',`translate(${ -xOffsetDescription*1.5 },${ySizeOfEachMat/2})`)
          .attr('class','description')
          .attr('dy','.3em')
          .style('font-weight','bold')
          .style('font-size',fontSize/2.2)
          // .text(`Head ${headNum+1}`);
          .selectAll('.tspan')
          .data([`Head`, `Output`, `in Head ${headNum+1}`])
          .enter().append('tspan')
          .attr('x',0)
          .attr('dy','1.5em')
          .text(d=>d);
        
        this.outputAttentionGridDataArray.push(attentionOuputGridData);
      }

    },
    redraw(){
      // 移除之前所绘制的内容
      d3.select(this.$el).selectAll('#crossAttentionSvg > *').remove();
      d3.select(this.$el).select('#crossAttentionSvg').attr('width',1550);
      this.drawSvgLeft();
      this.drawSvgRight();
    },
    onHeadClick(headNum){
      console.log(`点击了 第${headNum}个 head, 后续将开启 detailed view`);
      // this.$emit('openHeadDetailView',headNum);
      this.$emit('openHeadDetailView',headNum,this.attentionOuputTotalDataRange);
    },
    onAttentionClick(headNum){
      // console.log(`点击了 第${headNum}个 attention, 后续将开启 detailed view`);
      // this.$emit('openAttentionDetailView',headNum);
      console.log(`点击了 第${headNum}个 attention, 后续将开启 detailed view`);
      this.$emit('openAttentionDetailView',headNum,this.attentionOuputTotalDataRange);
    },
    
    onConcatenateAndLinearClick(){
      console.log(`点击了 concatenate & linear , 后续将开启 detailed view`);
      this.$emit('openConcaAndLinearDetailView');
    }
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