<template>
  <div class="container">
    <div class="box">
      <div></div>
      <div class="title-text">
        Softmax Score for <i>"{{predict.word}}"</i>
      </div>
      <svg id="softmax-svg" width='640' height='80%' ></svg>
      <svg id="cumulative-svg" width='640' height='10%'></svg>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";
import {getDataRange} from '../utils/detailview-utils'
// import LayernormAnimator from './LayernormAnimator'
export default {
  name:"SoftmaxView",
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
    cumulativeProb: {
      type: Number,
      default: 0,
    },
    predict: {
      type: Object,
      default: function(){return {};}
    },
  },
  emits:["exit"],
  data(){
    return {
      oldInput:[],
    }
  },
  beforeUpdate(){
    if(this.oldOput != this.output){
      this.redraw();
    }
  },
  mounted(){
    this.redraw();
  },
  methods:{
    onExit(){
      console.log("exit from the current view.");
      this.$emit('exit');
    },
    redraw(){
      this.oldOput = this.output;
      console.log("Enter SoftmaxView mounted.vue");

      let svg = d3.select(this.$el).select("#softmax-svg");
      svg.selectAll("*").remove();

      let formulaRightGroupX = 30,
          formulaRightGroupY = 100;

      let formulaRightGroup = svg.append('g')
      .attr('class', 'formula-right')
      .attr('transform', `translate(${formulaRightGroupX}, ${formulaRightGroupY})`)
      .style('font-size', '15px');
      
      let denominatorGroupX = 0,
          denominatorGroupY = 58;

      // Denominator
      let denominatorGroup = formulaRightGroup.append('g')
        .attr('class', 'denominator')
        .attr('transform', `translate(${denominatorGroupX}, ${denominatorGroupY})`);
      
  
      
      let colorScale = d3.interpolateRdBu;
      let outputDataRange = getDataRange([this.output]);
      let fontSize = 20;
      let curX = 8;
      let deltaX = 18;
      let unitY = 30;
      let offsetX_right = 2;
      let offsetX_left = 2;
      let numOfRows = 4;
      let n = this.output.length;
      let logits = [this.output[0],this.output[1],"...",this.output[this.predict.token],"...",this.output[n-2],this.output[n-1],];
      // Add the left (
      denominatorGroup.append('text')
        .attr('x', 0)
        .attr('y', 0)
        .style('fill', 'gray')
        .style('font-size',1.25*fontSize)
        .text('(');
      logits.forEach((d,i)=>{
        if(i/numOfRows >= 1 && i%numOfRows===0) curX=8;
        let curText = denominatorGroup.append('text')
        if (d=="..."){
          curText.attr('x', curX)
            .attr('y', Math.floor(i / numOfRows) * unitY)
            // .attr('y', unitY)
            .style('cursor', 'crosshair')
            .style('pointer-events', 'all')
            .style('font-size',fontSize)
            .text(` ... `);
        } else {
          // let curText = denominatorGroup.append('text')
          curText.attr('x', curX)
            .attr('y', Math.floor(i / numOfRows) * unitY)
            .style('cursor', 'crosshair')
            .style('pointer-events', 'all')
            .style('font-size',fontSize)
            .text(`exp(`);

          curText.append('tspan')
            .attr('class', `formula-term-${i} formula-term`)
            // .attr('dx', '1')
            .attr('dx', offsetX_right)
            .style('fill', colorScale((d-outputDataRange.min)/(outputDataRange.max-outputDataRange.min)))
            .style('fill-opacity', 1)
            .style('font-size',fontSize)
            .text(Math.round(d*100)/100);
          
          curText.append('tspan')
            // .attr('dx', '1')
            .attr('dx', offsetX_right)
            .style('font-size',fontSize)
            .text(')');
        }

        let curBBox = curText.node().getBBox();
        curX += curBBox.width + 4;

        if (i !== logits.length - 1) {
          denominatorGroup.append('text')
            .attr('x', curX)
            .attr('y', Math.floor(i / numOfRows) * unitY)
            .style('font-size',fontSize)
            .text('+');
          curX += deltaX;
        } else {
          denominatorGroup.append('text')
            .attr('x', curX-offsetX_left)
            .attr('y', Math.floor(i / numOfRows) * unitY)
            .style('font-size',1.25*fontSize)
            .style('fill', 'gray')
            .text(')');
        }
      });
      // Calculate the dynamic denominator group width
      let denominatorGroupBBox = denominatorGroup.node().getBBox();
      let lineOffsetX = 8;
      let ypos = 28;
      let lineStrokeWidth = 2;
      // Draw the fraction line
      formulaRightGroup.append('line')
        .attr('class', 'separation-line')
        .attr('x1', -lineOffsetX)
        .attr('x2', denominatorGroupBBox.width + lineOffsetX)
        .attr('y1', ypos)
        .attr('y2', ypos)
        .style('stroke-width', lineStrokeWidth)
        .style('stroke', 'gray');
      
      let numeratorX = 0,
          numeratorY = 18;
      // Draw the numerator
      let numeratorGroup = formulaRightGroup.append('g')
        .attr('class', 'numerator-group')
        .attr('transform', `translate(${numeratorX}, ${numeratorY})`);
      
      let numeratorText = numeratorGroup.append('text')
        .attr('x', denominatorGroupBBox.x + denominatorGroupBBox.width / 2)
        .attr('y', 0)
        .style('pointer-events', 'all')
        .style('cursor', 'crosshair')
        .style('text-anchor', 'middle')
        .style('font-size',fontSize)
        .text('exp(');
      
      numeratorText.append('tspan')
        .attr('dx', offsetX_right)
        .style('fill', colorScale((this.output[this.predict.token]-outputDataRange.min)/(outputDataRange.max-outputDataRange.min)))
        .style('font-size',fontSize)
        .text(Math.round(this.output[this.predict.token]*100)/100);

      numeratorText.append('tspan')
        .attr('dx', offsetX_right)
        .style('font-size',fontSize)
        .text(')');

      let formulaLeftGroupX = 510,
          formulaLeftGroupY = formulaRightGroupY + ypos,
          softmaxTextX = 20;
      // Draw the left part of the formula
      let formulaLeftGroup = svg.append('g')
        .attr('class', 'formula-left')
        .attr('transform', `translate(${formulaLeftGroupX}, ${formulaLeftGroupY})`);
      
      // let softmaxText = formulaLeftGroup.append('text')
      formulaLeftGroup.append('text')
        .attr('x', softmaxTextX)
        .attr('dominant-baseline', 'middle')
        .style('font-weight', 'bold')
        .style('font-size',fontSize*1.25)
        .text(Math.round(Math.exp(this.logSoftmax[this.predict.token])*10000)/10000);
        // .text(Math.exp(this.logSoftmax[this.predict.token]));
      
      // let softmaxTextBBox = softmaxText.node().getBBox();
      formulaLeftGroup.append('text')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0)
        .attr('y', 0)
        .style('fill', 'gray')
        .style('font-weight', 'bold')
        .style('font-size',fontSize)
        .text('=');

      // 绘制 cumulative Prob
      let svgCum = d3.select(this.$el).select('#cumulative-svg');
      svgCum.selectAll("*").remove();
      console.log('svgCum',svgCum);
      console.log('this.cumulativeProb',this.cumulativeProb);
      svgCum.append('text')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.1 * +(svgCum.attr('width')))
        .attr('y', 20)
        .style('fill', 'black')
        .style('font-weight', 'bold')
        .style('font-size',fontSize*1.25)
        .text('Cumulative Score (Probability): ');
      svgCum.append('text')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.7 * +(svgCum.attr('width')))
        .attr('y', 20)
        .style('fill', 'black')
        .style('font-weight', 'bold')
        .style('font-size',fontSize*1.25)
        .text(Math.round(this.cumulativeProb*1E7)/1E7);
      console.log('svgCum',svgCum);
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
  width:100%;
  height:100%;
}

.box {
  padding: 5px 15px 10px 15px;
  display: flex;
  flex-direction:column;
  justify-content: space-around;
  align-items: center;
  width:100%;
  height:100%;
}

#bottom-div {
  text-align: left;
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
  font-size: 2em;
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