<template>
<div class="container">
  <div class="box">
    <div class="title-text">
        Embedding View 
      </div>
    <EmbeddingAnimator
    @changeHilightsIndex="onChangeHilightsIndex"
    :curTokenIndex="curTokenIndex"
    :tokens="tokens"
    :embeddings="embeddings"
    :pe="pe"
    :output="output"
    :highlightsIndex="highlightsIndex"
    />
  </div>
</div>
</template>

<script>
// import EmbeddingView from "./EmbeddingView"
import EmbeddingAnimator from "./EmbeddingAnimator"

export default {
  name:"EmbeddingView",
  components:{
    EmbeddingAnimator,
  },
  props:{
    tokens: {
      type: Array,
      default: function(){return [2,3];},
    },
    embeddings: {
      type: Array,
      default: function(){return [];},
    },
    pe: {
      type: Array,
      default: function(){return [];},
    },
    output: {
      type: Array,
      default: function(){return [];}
    },
  },
  emits:['cleanComponentView'],
  data(){
    return {
      highlightsIndex:0,
      curTokenIndex:0,
      tokenNums:1,
      curEquationIndex:0,
      curOutputColumnIndex:0,
    };
  },
  created(){
    this.tokenNums = this.tokens.length;
    this.curTokenIndex = 0;
    // console.log('this.tokens:',this.tokens);
    // console.log('this.embeddings:',this.embeddings);
    // console.log('this.pe:',this.pe);
    // console.log('this.output:',this.output);
  },
  beforeUpdate(){
    this.tokenNums = this.tokens.length;
    if(this.curTokenIndex >= this.tokenNums) this.curTokenIndex = this.tokenNums-1;
  //   if(this.tokenNums != this.input.length){
  //     this.tokenNums = this.input.length;
  //   }
  //   if(this.tokenNums <= this.curTokenIndex){
  //     this.curTokenIndex = 0;
  //   }
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
    onChangeHilightsIndex(newHighlightsIndex){
      this.highlightsIndex = newHighlightsIndex;
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.container {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: .5rem;
  background-color: rgb(240, 239, 239);
  ;
}

.title-text {
  font-size: 1.2em;
  font-weight: bold;
  color: #4a4a4a;
}



</style>