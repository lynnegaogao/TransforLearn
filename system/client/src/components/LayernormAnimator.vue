<template>

  <div id="inputColumn" class="column">
    <div class="header-text">
      Input ({{input.length}},{{input[0].length}})
    </div>
    <Dataview 
      :data="input"
      :colorRange="inputDataRange"
      :highlights="input_highlights"
      @update:highlights="input_highlights=$event"
      :isEquation="false"
      :isColumn="false"
      @message="onMessage"
    />
    
    <svg id='inputLegend'></svg>


    <div class="header-text">
      Parameter: Alpha ({{alpha.length}})
    </div>
    <Dataview
      :data="alpha"
      :colorRange="alphaDataRange"
      :highlights="alpha_highlights"
      @update:highlights="alpha_highlights=$event"
      :isRow="true"
      :isEquation="false"
      :isParams="true"
      @message="onMessage"
    />

    <svg id='alphaLegend'></svg>

  </div>

  <div class="column">
    <div class="header-text">
      Mean ({{mean.length}})
    </div>
    <Dataview 
      :data="mean"
      :colorRange="inputDataRange"
      :highlights="mean_highlights"
      @update:highlights="mean_highlights=$event"
      :isEquation="false"
      :isColumn="true"
      @message="onMessage"
    />
  </div>

  <div class="column">
    <div class="header-text">
      Std ({{std.length}})
    </div>
    <Dataview 
      :data="std"
      :colorRange="stdDataRange"
      :highlights="std_highlights"
      @update:highlights="std_highlights=$event"
      :isEquation="false"
      :isColumn="true"
      @message="onMessage"
    />
  </div>

  <div id="equation" class="column">
    <!--<svg id="ln-equation"></svg>-->
    <span>
    <!--Alpha &nbsp; x ( input &nbsp;- mean ) / std&nbsp; + &nbsp;Beta&nbsp; = &nbsp;output-->
      Alpha &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; input &nbsp;&nbsp;&nbsp; mean &nbsp;&nbsp;&nbsp;&nbsp; std &nbsp;&nbsp;&nbsp;&nbsp; Beta &nbsp;&nbsp;&nbsp; output
    </span>
    <br>
    <span>
      <Dataview 
        :data="alphaDataEq"
        :colorRange="alphaDataRange"
        :isEquation="true"
        :isColumn="false"
        :isParams="true"
        @message="onMessage"
      />
      x (
      <Dataview 
        :data="inputDataEq"
        :colorRange="inputDataRange"
        :isEquation="true"
        :isColumn="false"
        @message="onMessage"
      />
      -
      <Dataview 
        :data="meanDataEq"
        :colorRange="inputDataRange"
        :isEquation="true"
        :isColumn="false"
        @message="onMessage"
      />
      ) / 
      <Dataview 
        :data="stdDataEq"
        :colorRange="stdDataRange"
        :isEquation="true"
        :isColumn="false"
        @message="onMessage"
      /> 
      + 
      <Dataview 
        :data="betaDataEq"
        :colorRange="betaDataRange"
        :isEquation="true"
        :isColumn="false"
        :isParams="true"
        @message="onMessage"
      /> 
      = 
      <Dataview 
        :data="outputDataEq"
        :colorRange="outputDataRange"
        :isEquation="true"
        :isColumn="false"
        @message="onMessage"
      />

    </span>
  </div>

  <div id="outputColumn" class="column">
    <div class="header-text">
      Output ({{output.length}},{{output[0].length}})
    </div>
    <Dataview 
      :data="output"
      :colorRange="outputDataRange"
      :highlights="output_highlights"
      @update:highlights="output_highlights=$event"
      :isEquation="false"
      :isColumn="false"
      @message="onMessage"
    />

    <svg id='outputLegend'></svg>

    <div class="header-text">
      Parameter: Beta ({{beta.length}})
    </div>
    <Dataview
      :data="beta"
      :colorRange="betaDataRange"
      :highlights="beta_highlights"
      @update:highlights="beta_highlights=$event"
      :isRow="true"
      :isEquation="false"
      :isParams="true"
      @message="onMessage"
    />
    <svg id='betaLegend'></svg>
  </div>

</template>

<script>
import Dataview from './Dataview'
import * as d3 from "d3";
import {getLegendGradient} from '../utils/draw-utils'
import {getDataRange} from '../utils/detailview-utils'
// import {getVisualizationSizeConstraint, getDataRange, getGridData} from '../utils/detailview-utils'
import {array1d} from '../utils/detailview-utils'
export default {
  name:"LayernormAnimator",
  components:{
    Dataview,
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
    mean: {
      type: Array,
      default: function(){return [];},
    },
    std: {
      type: Array,
      default: function(){return [];},
    },
    alpha: {
      type: Array,
      default: function(){return [];},
    },
    beta: {
      type: Array,
      default: function(){return [];},
    },
  },
  data(){
    return {
      input_highlights:[],
      output_highlights:[],
      inputEq_highlights:[],
      outputEq_highlights:[],
      mean_highlights:[],
      std_highlights:[],
      meanEq_highlights:[],
      stdEq_highlights:[],
      alpha_highlights:[],
      beta_highlights:[],

      inputRange:{},
      outputputRange:{},
      // valueTotalRange:{},
      stdTotalRange:{},
      paramsRange:{},

      inputDataEq:[],
      outputDataEq:[],
      meanDataEq:[],
      stdDataEq:[],
      alphaDataEq:[],
      betaDataEq:[],
    }
  },
  emits:["exit"],
  created(){
    console.log("Created - Enter LayernormAnimator.vue");
    // 这里做一些初始化操作, 以方便给 detailview 传递参数
    // 初始化 highlights
    this.input_highlights = array1d(this.input.length * this.input[0].length, ()=>false);
    this.output_highlights = array1d(this.output.length * this.output[0].length, ()=>false);
    this.mean_highlights = array1d(this.mean.length, ()=>false);
    this.std_highlights = array1d(this.std.length, ()=>false);
    this.alpha_highlights = array1d(this.alpha.length, ()=>false);
    this.beta_highlights = array1d(this.beta.length, ()=>false);

    this.input_highlights[0] = true;
    this.output_highlights[0] = true;
    this.mean_highlights[0] = true;
    this.std_highlights[0] = true;
    this.alpha_highlights[0] = true;
    this.beta_highlights[0] = true;

    this.outputEq_highlights = array1d(1, ()=>false);
    this.stdEq_highlights = array1d(1, ()=>false);
    this.meanEq_highlights = array1d(1, ()=>false);
    this.stdEq_highlights = array1d(1, ()=>false);
     
    // // 初始化 color(data) range 
    // this.inputRange = getDataRange(this.input);
    // // this.outputRange = getDataRange(this.output);
    // this.outputRange = getDataRange([...this.output,this.beta]);

    // 初始化 color(data) range 
    this.inputDataRange = getDataRange(this.input);
    this.outputDataRange = getDataRange(this.output);
    this.alphaDataRange = getDataRange([this.alpha]);
    this.betaDataRange = getDataRange([this.beta]);
    // this.valueTotalRange = {
    //   min:Math.min(inputRange.min, outputRange.min, this.beta),
    //   max:Math.max(inputRange.max, outputRange.max, this.beta),
    // }
    // this.valueTotalRange.range = this.valueTotalRange.max - this.valueTotalRange.min;
    // this.stdTotalRange = getDataRange([[...this.std,...this.alpha]]);
    this.stdDataRange = getDataRange([this.std]);

    // 初始化 equation data
    this.inputDataEq = [[this.input[0][0]]];
    this.outputDataEq = [[this.output[0][0]]];
    this.meanDataEq = [[this.mean[0]]];
    this.stdDataEq = [[this.std[0]]];
    this.alphaDataEq = [[this.alpha[0]]]; 
    this.betaDataEq = [[this.beta[0]]];

    // this.redraw();
  },
  mounted(){
    this.redraw();
  },
  methods:{
    redraw(){
      console.log("Mounted - Enter LayernormAnimator.vue");
      // console.log(this.input);
      // console.log(this.output);
      // console.log(this.mean);
      // console.log(this.std);
      // document.LNAnimator = this;
      let colorScale = d3.interpolateRdBu;
      let paramColorScale = d3.interpolateBrBG;

      let inputDataRange = this.inputDataRange
      let outputDataRange = this.outputDataRange
      let alphaDataRange = this.alphaDataRange;
      let betaDataRange = this.betaDataRange

      // let svgInput = d3.select(this.$el).select('#inputLegend').attr('width',550).attr('height',12);
      // let svgOutput = d3.select(this.$el).select('#outputLegend').attr('width',550).attr('height',12);
      // let svgAlpha = d3.select(this.$el).select('#alphaLegend').attr('width',550).attr('height',12);
      // let svgBeta = d3.select(this.$el).select('#betaLegend').attr('width',550).attr('height',12);
      let svgInput = d3.select('#inputLegend').attr('width',550).attr('height',23);
      let svgOutput = d3.select('#outputLegend').attr('width',550).attr('height',23);
      let svgAlpha = d3.select('#alphaLegend').attr('width',550).attr('height',23);
      let svgBeta = d3.select('#betaLegend').attr('width',550).attr('height',23);

      console.log('this.$el',this.$el);
      console.log('svgInput:',svgInput);

      getLegendGradient(svgInput,colorScale,'inputGradient',inputDataRange.min,inputDataRange.max);
      getLegendGradient(svgOutput,colorScale,'outputGradient',outputDataRange.min,outputDataRange.max);
      getLegendGradient(svgAlpha,paramColorScale,'alphaGradient',alphaDataRange.min,alphaDataRange.max);
      getLegendGradient(svgBeta,paramColorScale,'betaGradient',betaDataRange.min,betaDataRange.max);

      let gridLength = 40;
      let legendHeight = 5;



      drawLegend(svgInput, gridLength, legendHeight, inputDataRange, 275, 0, 'inputGradient');
      drawLegend(svgOutput, gridLength, legendHeight, outputDataRange, 275, 0, 'outputGradient');
      drawLegend(svgAlpha, gridLength, legendHeight, alphaDataRange, 275, 0, 'alphaGradient');
      drawLegend(svgBeta, gridLength, legendHeight, betaDataRange, 275, 0, 'betaGradient');

      function drawLegend(svg, gridLength, legendHeight, dataRange, transX, transY, gradientName){
        let legendScale = d3.scaleLinear()
          .range([0, 6 * gridLength])
          .domain([dataRange.min, dataRange.max]);
        let legendAxis = d3.axisBottom()
          .scale(legendScale)
          .tickFormat(d3.format('.2f'))
          .tickValues([dataRange.min, dataRange.min+(dataRange.max-dataRange.min)/2,dataRange.max]);
        let legend = svg.append('g')
          .attr('transform', `translate(${transX}, ${transY})`);
        legend.append('g')
          .attr('transform', `translate(${-3*gridLength}, ${legendHeight+2})`)
          .call(legendAxis)
        legend.append('rect')
          .attr('transform', `translate(${-3*gridLength}, ${0})`)
          .attr('width', 6 * gridLength).attr('height', legendHeight)
          .style('fill', `url(#${gradientName})`);
      }

    },
    onMessage(info){
      const {hoverH,hoverW} = info;

      // 修改 highlighs 
      let input_highlights = array1d(this.input.length * this.input[0].length, ()=>false);
      let output_highlights = array1d(this.output.length * this.output[0].length, ()=>false);
      let mean_highlights = array1d(this.mean.length, ()=>false);
      let std_highlights = array1d(this.std.length, ()=>false);
      let alpha_highlights = array1d(this.mean.length, ()=>false);
      let beta_highlights = array1d(this.std.length, ()=>false);

      input_highlights[hoverH * this.input[0].length + hoverW] = true;
      output_highlights[hoverH * this.output[0].length + hoverW] = true;
      mean_highlights[hoverH] = true;
      std_highlights[hoverH] = true;
      alpha_highlights[hoverW] = true;
      beta_highlights[hoverW] = true;

      this.input_highlights = input_highlights;
      this.output_highlights = output_highlights;
      this.mean_highlights = mean_highlights;
      this.std_highlights = std_highlights;
      this.alpha_highlights = alpha_highlights;
      this.beta_highlights = beta_highlights;

      // 修改 Equation
      this.inputDataEq = [[this.input[hoverH][hoverW]]];
      this.outputDataEq = [[this.output[hoverH][hoverW]]];
      this.meanDataEq = [[this.mean[hoverH]]];
      this.stdDataEq = [[this.std[hoverH]]];
      this.alphaDataEq = [[this.alpha[hoverW]]]; 
      this.betaDataEq = [[this.beta[hoverW]]];
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.column {
  padding: 5px;
}
#equation {
  min-width:340px;  
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

#inputColumn {
  min-width:565px;  
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

#outputColumn {
  min-width:565px;  
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
/* .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  border-radius: .5rem;
  background-color: white;
}

.box {
  padding: 5px 15px 10px 15px;
}

.control-pannel {
  display: flex;
  position: relative;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.title-text {
  font-size: 1.2em;
  font-weight: 500;
  color: #4a4a4a;
}

.buttons {
  cursor: pointer;
  display:flex;
  flex-direction: row;
}

.control-button {
  color: gray;
  opacity: 0.8;
  cursor: pointer;
  margin-bottom: 2.5px;
}

.control-button:not(:first-child) {
  margin-left: 5px;
} */
</style>