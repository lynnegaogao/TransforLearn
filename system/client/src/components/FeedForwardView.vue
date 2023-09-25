<template>
<div class="container">
  <div class="box">
    <div class="control-pannel">
      <div>
        <!--
        <button class="buttons" @click="onLastToken()">Last Token</button>
        Token Index: {{curTokenIndex+1}}
        <button class="buttons" @click="onNextToken()">Next Token</button>
        -->
        <el-button type="primary" :icon="ArrowLeftBold" style="margin-right:5px" plain
          @click="onLastToken()">Last Token</el-button>
        Token Index: {{curTokenIndex+1}}
        <el-button type="primary" @click="onNextToken()" plain> 
          Next Token<el-icon class="el-icon--right"><ArrowRightBold /></el-icon>
        </el-button>
        <!--<el-button-group>
        </el-button-group>-->
      </div>
      <div class="title-text">
        Feed Forward View 
      </div>
      <!--<button class="buttons" @click="onClean()">x</button>-->
      <el-tooltip content="Quit from Feed-Forward View." placement="top" effect="dark">
        <el-button type="primary" :icon="CloseBold" plain circle @click="onClean()" />
      </el-tooltip>
    </div>
    <FeedForwardAnimator
    @changeEquationIndex="onChangeEquationIndex"
    @changeOutputColumnIndex="onChangeOutputColumnIndex"
    :curEquationIndex="curEquationIndex"
    :curOutputColumnIndex="curOutputColumnIndex"
    :input="input"
    :output="output"
    :intermediate="intermediate"
    :activation="activation"
    :curTokenIndex="curTokenIndex"/>
  </div>
</div>
</template>

<script>
import FeedForwardAnimator from "./FeedForwardAnimator"
import { shallowRef } from "vue"
import { CloseBold, ArrowLeftBold, ArrowRightBold } from '@element-plus/icons-vue'
export default {
  name:"FeedForwardView",
  components:{
    FeedForwardAnimator,
    ArrowRightBold,
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
    intermediate: {
      type: Array,
      default: function(){return [];},
    },
    activation: {
      type: Array,
      default: function(){return [];}
    },
  },
  emits:['cleanComponentView'],
  data(){
    return {
      CloseBold:shallowRef(CloseBold),
      ArrowLeftBold:shallowRef(ArrowLeftBold),
      curTokenIndex:0,
      tokenNums:1,
      curEquationIndex:0,
      curOutputColumnIndex:0,
    };
  },
  created(){
    this.tokenNums = this.input.length;
    this.curTokenIndex = 0;
  },
  beforeUpdate(){
    if(this.tokenNums != this.input.length){
      this.tokenNums = this.input.length;
    }
    if(this.tokenNums <= this.curTokenIndex){
      this.curTokenIndex = 0;
    }
  },
  methods:{
    onClean(){
      this.$emit('cleanComponentView');
    },
    onNextToken(){
      console.log('this.curTokenIndex:',this.curTokenIndex);
      if(this.curTokenIndex == this.tokenNums-1){
        console.log('current token index reaches maximum.');
      } else {
        this.curTokenIndex += 1;
      }
    },
    onLastToken(){
      console.log('this.curTokenIndex:',this.curTokenIndex);
      if(this.curTokenIndex == 0){
        console.log('current token index reaches minimum.');
      } else {
        this.curTokenIndex -= 1;
      }
    },
    onChangeEquationIndex(newCurEquationIndex){
      this.curEquationIndex = newCurEquationIndex;
      // this.curOutputColumnIndex = -1;
    },
    onChangeOutputColumnIndex(newCurOutputColumnIndex){
      this.curOutputColumnIndex = newCurOutputColumnIndex;
      // this.curEquationIndex = -1
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