<template>
<div class="container">
  <div class="box">
    <div class="control-pannel">
      <!--<button class="buttons" id="highlightsBtn" @click="onHighlights()">Close Highlights</button>-->
      <el-button type="primary" id="highlightsBtn" plain @click="onHighlights()">Close Highlights</el-button>
      <div class="title-text">
        Attention Mechanism View
      </div>
      <!--
      <button class="buttons" @click="onExit()">Exit</button>
      -->
      <el-tooltip content="Quit from Attention View." placement="top" effect="dark">
        <el-button type="primary" :icon="CloseBold" plain circle @click="onExit()" />
      </el-tooltip>
    </div>
    <div class="svgContainer">
      <AttentionCalScore
        @changeCalScoreHilights = 'onChangeCalScoreHilights'
        :Q="nodeData.Q"
        :K="nodeData.K"
        :QKT="nodeData['Q*KT']"
        :highlights = "calScoreHighlights"
        :openHighlights = "openHighlights"
      />
      <AttentionScaleOut
        @changeScaleMaskHilights = 'onChangeScaleMaskHilights'
        :highlights = "scaleMaskHighlights"
        :QKT="nodeData['Q*KT']"
        :QKTdivided="nodeData['Q*KT/coefficient']"
        :mask="nodeData['mask']"
        :maskedQKTdivided="nodeData['after_mask']"
        :openHighlights = "openHighlights"
        :coefficient = "nodeData.coefficient"
      />
      <AttentionSoftmax
        @changeSoftmaxHilights = 'onChangeSoftmaxHilights'
        :highlights = "softmaxHighlights"
        :QKT="nodeData['Q*KT']"
        :QKTdivided="nodeData['Q*KT/coefficient']"
        :mask="nodeData['mask']"
        :maskedQKTdivided="nodeData['after_mask']"
        :openHighlights = "openHighlights"
        :coefficient = "nodeData.coefficient"
        :afterSoftmax = "nodeData['after_softmax']"
      />
      <AttentionGenerateOutput
        @changeOutputHilights = 'onChangeOutputHilights'
        :Q="nodeData.Q"
        :K="nodeData.K"
        :QKT="nodeData['Q*KT']"
        :highlights = "outputHighlights"
        :openHighlights = "openHighlights"
        :afterSoftmax = "nodeData['after_softmax']"
        :output = "nodeData['output']"
        :V = "nodeData['V']"
        :headNum = "nodeData['head']"
        :attentionOuputTotalDataRange = "nodeData['attentionOuputTotalDataRange']"
      />
    </div>
    
  </div>
</div>
</template>

<script>
import AttentionCalScore from "./AttentionCalScore"
import AttentionScaleOut from "./AttentionScaleOut"
import AttentionSoftmax from "./AttentionSoftmax"
import AttentionGenerateOutput from "./AttentionGenerateOutput"
import { shallowRef } from "vue"
import { CloseBold,Switch } from '@element-plus/icons-vue'
export default {
  name:"AttentionView",
  components:{
    AttentionCalScore,
    AttentionScaleOut,
    AttentionSoftmax,
    AttentionGenerateOutput,
  },
  props:{
    nodeType:{
      type: String,
      default: '',
    },
    nodeData:{
      type: Object,
      default: function(){return {};},
    },
    
  },
  emits:["exit"],
  data(){
    return {
      CloseBold:shallowRef(CloseBold),
      Switch:shallowRef(Switch),
      highlights: [],
      order: 0,
      openHighlights:true,
      calScoreHighlights:[-1,-1],
      scaleMaskHighlights:[0,0],
      softmaxHighlights:[0,0],
      outputHighlights:[-1,-1],
    };
  },
  created(){
    // console.log('this.type in AttentionHeadView.vue:', this.nodeType);
    console.log('this.nodeData in AttentionView.vue:', this.nodeData);
    // console.log('this.nodeData.V in AttentionView.vue:', this.nodeData['V']);
    // console.log('HeadNum:',this.nodeData.head);
    // console.log('this.nodeData.coefficient in AttentionView.vue:', this.nodeData.coefficient);

  },
  beforeUpdate(){
  },
  methods:{
    onExit(){
      console.log("exit from the current detailview.");
      this.$emit('exit');
    },
    onHighlights(){
      // let content = document.getElementById('highlightsBtn').innerHTML;
      // if(content=='Close Highlights'){
      if(this.openHighlights){
        document.getElementById('highlightsBtn').innerHTML = 'Open  Highlights';
        this.openHighlights = false;
      } else {
        document.getElementById('highlightsBtn').innerHTML ='Close Highlights';
        this.openHighlights = true;
      }
    },
    onChangeCalScoreHilights(newHighlights){
      this.calScoreHighlights = newHighlights;
    },
    onChangeScaleMaskHilights(newHighlights){
      this.scaleMaskHighlights = newHighlights;
    },
    onChangeOutputHilights(newHighlights){
      this.outputHighlights = newHighlights;
    },
    onChangeSoftmaxHilights(newHighlights){
      this.softmaxHighlights = newHighlights;
    },
    // onChangeOrderAndHilights(newValues){
    //   this.order = newValues.order;
    //   this.highlights = newValues.highlights;
    // },
    // onNextToken(){
    //   console.log('this.curTokenIndex:',this.curTokenIndex);
    //   if(this.curTokenIndex == this.tokenNums-1){
    //     console.log('current token index reaches maximum.');
    //   } else {
    //     this.curTokenIndex += 1;
    //   }
    // },
    // onLastToken(){
    //   console.log('this.curTokenIndex:',this.curTokenIndex);
    //   if(this.curTokenIndex == 0){
    //     console.log('current token index reaches minimum.');
    //   } else {
    //     this.curTokenIndex -= 1;
    //   }
    // },
    // onChangeHilightsIndex(newHighlightsIndex){
    //   this.highlightsIndex = newHighlightsIndex;
    // },
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

.svgContainer {
  display: flex;
  flex-direction:column;
  justify-content: center;
  align-items: center;
  box-shadow: rgb(236, 231, 231) 2px 2px 11px;
  border-radius: .5rem;
  background-color: white;
  /*
  width:100%;
  height:100%;
  */
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