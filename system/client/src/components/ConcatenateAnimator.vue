<template>
<div class="container">
  <svg id="concatenateSvg"></svg>
</div>
</template>

<script>
import * as d3 from "d3";
import {getVisualizationSizeConstraint, getDataRange, getGridData} from '../utils/detailview-utils'
// import {getVisualizationSizeConstraint, getGridData} from '../utils/detailview-utils'
// import {getDataRange} from '../utils/detailview-utils'
// import {config} from '../utils/config'
export default {
  name:"ConcatenateAnimator",
  components:{
    // EmbeddingAnimator,
  },
  props:{
    nodeData:{
      type: Object,
      default: function(){return {};},
    },
    highlights:{
      type: Array,
      default: function(){return [];},
    },
    curOrder:{
      type: Number,
      default: 0,
    },
    openHighlights:{
      type: Boolean,
      default: true,
    },

  },
  emits:["exit","changeOrderAndHilights"],
  data(){
    return {
      oldNodeData:{},
      oldHighlights:[],
      oldOrder:0,
      // curTokenIndex:0,
      // tokenNums:1,
      // curEquationIndex:0,
      // curOutputColumnIndex:0,
    };
  },
  created(){
    // console.log('this.nodeData in AttentionHeadView.vue:', this.nodeData);
    // this.tokenNums = this.tokens.length;
    // this.curTokenIndex = 0;
    // console.log('this.tokens:',this.tokens);
    // console.log('this.embeddings:',this.embeddings);
    // console.log('this.pe:',this.pe);
    // console.log('this.output:',this.output);
  },
  beforeUpdate(){
    // if(this.oldNodeData != this.nodeData){
    //   this.oldNodeData = this.nodeData;
    //   this.init();
    // }
    // this.redraw();
  },
  mounted(){
    this.init();
    this.redraw();
  },
  methods:{
    onExit(){
      console.log("exit from the current detailview.");
      this.$emit('exit');
    },
    init(){
      this.concatenationDataRange = getDataRange(this.nodeData.concatenation);
      this.weightDataRange = getDataRange(this.nodeData.Wo);
      this.biasDataRange = getDataRange([this.nodeData.bo]);
      this.outputDataRange = getDataRange(this.nodeData.output);
    }, 
    drawConcatenate(){
      let svg = d3.select(this.$el).select('#concatenateSvg');
      // let svgWidth = +(svg.attr('width'));
      let attention_output = this.nodeData.attention_output; // Array
      let concatenation = this.nodeData.concatenation; // Matrix
      let concatenationDataRange = this.concatenationDataRange;
      let colorScale = d3.interpolateRdBu;
      // let paramsColorScale = d3.interpolateBrBG;
      let fontSize = 20;
      // let fontSize = 25;

      let attnOuputGridGroupX = 30;
      let attnOuputGridGroupY = 30;
      let attnOuputXSizeOfGrid = 128;
      let attnOuputYSizeOfGrid = 100;
      let interval = 25;
      let maximumCellSize = 30;
      let attnOutputGroup = svg.append('g').attr('class','headOutputs-group')
          .attr('transform',`translate(${attnOuputGridGroupX},${attnOuputGridGroupY})`);

      drawOutputOfEachHead.call(this, attnOutputGroup, attention_output[0], 0, interval, attnOuputXSizeOfGrid, attnOuputYSizeOfGrid, maximumCellSize);
      drawOutputOfEachHead.call(this, attnOutputGroup, attention_output[1], 1, interval, attnOuputXSizeOfGrid, attnOuputYSizeOfGrid, maximumCellSize);
      drawOutputOfEachHead.call(this, attnOutputGroup, attention_output[2], 2, interval, attnOuputXSizeOfGrid, attnOuputYSizeOfGrid, maximumCellSize);
      drawOutputOfEachHead.call(this, attnOutputGroup, attention_output[3], 3, interval, attnOuputXSizeOfGrid, attnOuputYSizeOfGrid, maximumCellSize);
      
      let concatenationGridGroupX = attnOuputGridGroupX + 4*(attnOuputXSizeOfGrid+interval);
      let concatenationGridGroupY = attnOuputGridGroupY;
      let concatenationXSizeOfGrid = attnOuputXSizeOfGrid*4;
      let concatenationYSizeOfGrid = attnOuputYSizeOfGrid;

      let concatenationGroup = svg.append('g').attr('class','concatenation-group')
          .attr('transform',`translate(${concatenationGridGroupX},${concatenationGridGroupY})`);

      drawOutputOfConcatenation.call(this, concatenationGroup, concatenation, concatenationXSizeOfGrid, concatenationYSizeOfGrid, maximumCellSize);

      function drawOutputOfEachHead(group, data, headNum, betweenInterval, sizeX, sizeY, maximumCellSize) {

        let constraintGridCellWidth = getVisualizationSizeConstraint(data[0].length, 'x', sizeX, sizeY, maximumCellSize);
        let constraintGridCellHeight = getVisualizationSizeConstraint(data.length, 'y', sizeX, sizeY, maximumCellSize);

        let gridData = getGridData(data, constraintGridCellWidth, constraintGridCellHeight);
        let gridGroup = group.append("g").attr("class","grid").attr("transform",`translate(${headNum * ( sizeX + betweenInterval ) },${0})`);
        let gridRow = gridGroup.selectAll(".row")  // 绘制每一行
            .data(gridData).enter().append('g').attr('class','row');
        gridRow
          .selectAll(".square")
            .data(d=>d).enter().append('rect')
            .attr('class','square')
            .attr("x",d=>d.x).attr("y",d=>d.y)
            .attr("width",d=>d.width).attr("height",d=>d.height)
            .attr('opacity',0.9)
            .style('fill',d=>{
              let normlizedVal = (d.text-concatenationDataRange.min)/(concatenationDataRange.max-concatenationDataRange.min);
              return colorScale(normlizedVal);
            });
        let totalGridWidth = constraintGridCellWidth * data[0].length;
        let totalGridHeight = constraintGridCellHeight * data.length;
        let gridText = group.append('text').attr("text-anchor","middle");
          gridText
            .attr('transform',`translate(${ headNum * ( sizeX + betweenInterval ) + totalGridWidth/2},${-attnOuputGridGroupY/2})`)
            .attr('class','title-text')
            .attr('dy','.3em')
            .style('font-weight','bold')
            .style('font-size',fontSize/2)
            .text(`Output (${data.length},${data[0].length}) of Head ${headNum+1}`);
        let symbolText = headNum==3?'=':'⊕';
        let symbolGridText = group.append('text').attr("text-anchor","middle");
          symbolGridText
            .attr('transform',`translate(${ headNum * ( sizeX + betweenInterval ) + totalGridWidth + betweenInterval/2 },${totalGridHeight/2})`)
            .attr('class','title-text')
            .attr('dy','.3em')
            .style('font-weight','bold')
            .style('font-size',fontSize/1.2)
            .text(symbolText);
      }

      function drawOutputOfConcatenation(group, data, sizeX, sizeY, maximumCellSize) {
        let constraintGridCellWidth = getVisualizationSizeConstraint(data[0].length, 'x', sizeX, sizeY, maximumCellSize);
        let constraintGridCellHeight = getVisualizationSizeConstraint(data.length, 'y', sizeX, sizeY, maximumCellSize);

        let gridData = getGridData(data, constraintGridCellWidth, constraintGridCellHeight);
        let gridGroup = group.append("g").attr("class","grid")//.attr("transform",`translate(${0},${0})`);
        let gridRow = gridGroup.selectAll(".row")  // 绘制每一行
            .data(gridData).enter().append('g').attr('class','row');
        gridRow
          .selectAll(".square")
            .data(d=>d).enter().append('rect')
            .attr('class','square')
            .attr("x",d=>d.x).attr("y",d=>d.y)
            .attr("width",d=>d.width).attr("height",d=>d.height)
            .attr('opacity',0.9)
            .style('fill',d=>{
              let normlizedVal = (d.text-concatenationDataRange.min)/(concatenationDataRange.max-concatenationDataRange.min);
              return colorScale(normlizedVal);
            });
        let totalGridWidth = constraintGridCellWidth * data[0].length;
        // let totalGridHeight = constraintGridCellHeight * data.length;
        let gridText = group.append('text').attr("text-anchor","middle");
          gridText
            .attr('transform',`translate(${totalGridWidth/2},${-attnOuputGridGroupY/2})`)
            .attr('class','title-text')
            .attr('dy','.3em')
            .style('font-weight','bold')
            .style('font-size',fontSize/2)
            .text(`Output (${data.length},${data[0].length}) of Concatenation of all heads`);
        // let symbolText = headNum==3?'=':'⊕';
        // let symbolGridText = group.append('text').attr("text-anchor","middle");
        //   symbolGridText
        //     .attr('transform',`translate(${ headNum * ( sizeX + betweenInterval ) + totalGridWidth + betweenInterval/2 },${totalGridHeight/2})`)
        //     .attr('class','title-text')
        //     .attr('dy','.3em')
        //     .style('font-weight','bold')
        //     .style('font-size',fontSize/1.2)
        //     .text(symbolText);
      }

    },
    drawLinearProjection(){
      // width 1000, height 300;
      let svg = d3.select(this.$el).select('#concatenateSvg');

      let colorScale = d3.interpolateRdBu;
      let paramsColorScale = d3.interpolateBrBG;
      // let fontSize = 20;
      let fontSize = 25;


      let groupX = 75;
      let groupY = 170;
      let xSizeOfWeightGrid = 128*4;
      let ySizeOfWeightGrid = 128*4;
      let xSizeOfConcatenationGrid = 100;
      let ySizeOfConcatenationGrid = 128*4;
      let xSizeOfBiasGrid = 20;
      let ySizeOfBiasGrid = 128*4;
      let xSizeOfOutputGrid = 100;
      let ySizeOfOutputGrid = 128*4;
      let interval = 100;
      let maximumCellSize = 30;

      let groupWeight = svg.append('g').attr('class','weight-group')
          .attr('transform',`translate(${groupX},${groupY})`);
      let groupConcatenation = svg.append('g').attr('class','concatenation-group')
          .attr('transform',`translate(${groupX + (xSizeOfWeightGrid + interval)},${groupY})`);
      let groupBias = svg.append('g').attr('class','bias-group')
          .attr('transform',`translate(${groupX + xSizeOfWeightGrid + xSizeOfConcatenationGrid + 2*interval},${groupY})`);
      let groupOutput = svg.append('g').attr('class','output-group')
          .attr('transform',`translate(${groupX + xSizeOfWeightGrid + xSizeOfConcatenationGrid + xSizeOfBiasGrid + 3*interval},${groupY})`);

      let weightData =  this.nodeData.Wo;
      let concatenationData =  transpose(this.nodeData.concatenation) // 需要转置
      let biasData =  this.nodeData.bo.map(d=>[d]); // 需要转置
      let outputData =  transpose(this.nodeData.output) // 需要转置

      drawMatirx.call(this, groupWeight, weightData, xSizeOfWeightGrid, ySizeOfWeightGrid, maximumCellSize, this.weightDataRange, 
          paramsColorScale, `Projection Weight (${weightData.length},${weightData[0].length})`,'*');
      drawMatirx.call(this, groupConcatenation, concatenationData, xSizeOfConcatenationGrid, ySizeOfConcatenationGrid, maximumCellSize, this.concatenationDataRange, 
          colorScale, `Concatenation (${concatenationData.length},${concatenationData[0].length})`,'+');
      drawMatirx.call(this, groupBias, biasData, xSizeOfBiasGrid, ySizeOfBiasGrid, maximumCellSize, this.biasDataRange, 
          paramsColorScale, `Projection Bias (${biasData.length},${biasData[0].length})`,'=');
      drawMatirx.call(this, groupOutput, outputData, xSizeOfOutputGrid, ySizeOfOutputGrid, maximumCellSize, this.outputDataRange, 
          colorScale, `Projection Output (${outputData.length},${outputData[0].length})`,null);

      function transpose(data){
        let rows = data.length;
        let cols = data[0].length;
        let transposedData = [];
        for(let c=0; c<cols; c++){
          let column = [];
          for(let r=0; r<rows; r++){
            column.push(data[r][c]);
          }
          transposedData.push(column);
        }
        return transposedData;
      }

      function drawMatirx(group, data, sizeX, sizeY, maximumCellSize, dataRange, colorMapper, text, symbol){

        let constraintGridCellWidth = getVisualizationSizeConstraint(data[0].length, 'x', sizeX, sizeY, maximumCellSize);
        let constraintGridCellHeight = getVisualizationSizeConstraint(data.length, 'y', sizeX, sizeY, maximumCellSize);

        let gridData = getGridData(data, constraintGridCellWidth, constraintGridCellHeight);
        let gridGroup = group.append("g").attr("class","grid")//.attr("transform",`translate(${headNum * ( sizeX + betweenInterval ) },${0})`);
        let gridRow = gridGroup.selectAll(".row")  // 绘制每一行
            .data(gridData).enter().append('g').attr('class','row');
        gridRow
          .selectAll(".square")
            .data(d=>d).enter().append('rect')
            .attr('class','square')
            .attr("x",d=>d.x).attr("y",d=>d.y)
            .attr("width",d=>d.width).attr("height",d=>d.height)
            .attr('opacity',0.9)
            .style('fill',d=>{
              let normlizedVal = (d.text-dataRange.min)/(dataRange.max-dataRange.min);
              return colorMapper(normlizedVal);
            });

        let totalGridWidth = constraintGridCellWidth * data[0].length;
        let totalGridHeight = constraintGridCellHeight * data.length;

        let gridText = group.append('text').attr("text-anchor","middle");
          gridText
            .attr('transform',`translate(${ totalGridWidth/2},${-15})`)
            .attr('class','title-text')
            .attr('dy','.3em')
            .style('font-weight','bold')
            .style('font-size',fontSize/2.25)
            .text(text);

        if(symbol!=null){
          let symbolText = group.append('text').attr("text-anchor","middle");
          symbolText
            .attr('transform',`translate(${ totalGridWidth + interval/2},${totalGridHeight/2})`)
            .attr('class','title-text')
            .attr('dy',symbol=="*"?'.55em':'.3em')
            .style('font-weight','bold')
            .style('font-size',symbol=="*"?fontSize*2:fontSize)
            .text(symbol);
        }
      }

    },
    redraw(){
      d3.select(this.$el).selectAll('#concatenateSvg > *').remove();
      d3.select(this.$el).select('#concatenateSvg').attr('width',1200).attr('height',700);
      // // let svg = d3.select(this.$el).select('#embeddingSvg').attr('width',1550);
      // // let svgWidth = +(svg.attr('width'));
      // this.drawWeights();
      // this.drawInput();
      // this.drawBiasesAndOuputs();
      this.drawConcatenate();
      this.drawLinearProjection();
      

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
  margin-left:5px;
  margin-right:5px;
  margin-top:5px;
  margin-bottom:5px;
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