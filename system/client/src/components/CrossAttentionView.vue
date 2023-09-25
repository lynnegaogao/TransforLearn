<template>
<div class="container">
  <div class="box">
    <div class="control-pannel">
      <div>
      </div>
      <div class="title-text">
        Multi-Head Cross-Attention View 
      </div>
      <!--<button class="buttons" @click="onClean()">x</button>-->
      <el-tooltip content="Quit from Multi-Head Cross-Attention View." placement="top" effect="dark">
        <el-button type="primary" :icon="CloseBold" plain circle @click="onClean()" />
      </el-tooltip>
    </div>
    <CrossAttentionAnimator
      @openHeadDetailView="onOpenHeadDetailView"
      @openAttentionDetailView="onOpenAttentionDetailView"
      @openConcaAndLinearDetailView="onOpenConcaAndLinearDetailView"
      :nodeData="nodeData"
      :nodeParams="nodeParams"
    />
  </div>
</div>
</template>

<script>
import CrossAttentionAnimator from "./CrossAttentionAnimator"

import { shallowRef } from "vue"
import { CloseBold } from '@element-plus/icons-vue'
export default {
  name:"CrossAttentionView",
  components:{
    CrossAttentionAnimator,
  },
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
      CloseBold:shallowRef(CloseBold),
      highlightsIndex:0,
      curTokenIndex:0,
      tokenNums:1,
      curEquationIndex:0,
      curOutputColumnIndex:0,
    };
  },
  created(){
    console.log('CrossAttentionView - this.nodeData:',this.nodeData);
    console.log('CrossAttentionView - this.nodeParams:',this.nodeParams);

  },
  beforeUpdate(){
    // console.log('this.nodeData:',this.nodeData);
    // console.log('this.nodeParams:',this.nodeParams);
  },
  methods:{
    onClean(){
      this.$emit('cleanComponentView');
    },
    // self-attention;
    // input 3个都相同, 所以只需要取其中一个;
    onOpenHeadDetailView(headNum,attentionOuputTotalDataRange){
      let qInput = this.nodeData.input[0];
      let kvInput = this.nodeData.input[1];
      let matQKV = this.nodeData.mat_QKV[headNum];
      let paramQKV = this.nodeParams[0][headNum];
      this.$emit('openHeadDetailView',{
        head: headNum,
        qInput,
        kvInput,
        Q: matQKV[0],
        K: matQKV[1],
        V: matQKV[2],
        Wq: paramQKV[0][0],
        bq: paramQKV[0][1],
        Wk: paramQKV[1][0],
        bk: paramQKV[1][1],
        Wv: paramQKV[2][0],
        bv: paramQKV[2][1],
        attentionOuputTotalDataRange,
      })
    },
    onOpenAttentionDetailView(headNum,attentionOuputTotalDataRange){
    // onOpenAttentionDetailView(headNum){
      // this.$emit('openAttentionDetailView',{
      //   head:headNum,
      // })
      let matQKV = this.nodeData.mat_QKV[headNum];
      this.$emit('openAttentionDetailView',{
        type:"cross",
        head:headNum,
        coefficient:this.nodeData.coefficient,
        Q: matQKV[0],
        K: matQKV[1],
        V: matQKV[2],
        'Q*KT': this.nodeData['Q*KT'][headNum],
        'Q*KT/coefficient': this.nodeData['Q*KT/coefficient'][headNum],
        mask: this.nodeData.mask,
        after_mask: this.nodeData.after_mask[headNum],
        after_softmax: this.nodeData.after_softmax[headNum],
        output: this.nodeData.attention_output[headNum],
        attentionOuputTotalDataRange,
      })
    },
    onOpenConcaAndLinearDetailView(){
      let attention_output = this.nodeData.attention_output;
      let concatenation = this.nodeData.concatenation;
      let output = this.nodeData.output;
      let Wo = this.nodeParams[1][0];
      let bo = this.nodeParams[1][1];
      this.$emit('openConcaAndLinearDetailView',{
        attention_output,
        concatenation,
        output,
        Wo,
        bo,
      })
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