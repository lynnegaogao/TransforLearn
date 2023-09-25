<template>
  <div>
    <div class="container">
      <div class="box">
        <div class="control-pannel">
          <div></div> <!-- 用来展位的 html element, 使得 title居中, 且退出按钮靠右-->
          <div class="title-text">
            Layer Normalization
          </div>
          <div class="buttons">
            <!--<div class="delete-button control-button" tilte="Close"
              @click="onExit()">
              <button>x</button>
            </div>-->
            <el-tooltip content="Quit from LayerNorm View." placement="top" effect="dark">
              <el-button type="primary" :icon="CloseBold" plain circle @click="onExit()" />
            </el-tooltip>
          </div>
        </div>
        <div class="container innerContainer">
          <LayernormAnimator
          :input = "input"
          :output = "output"
          :mean = "mean"
          :std = "std"
          :alpha = "alpha"
          :beta = "beta"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LayernormAnimator from './LayernormAnimator'
import { shallowRef } from "vue"
import { CloseBold } from '@element-plus/icons-vue'
export default {
  name:"LayernormView",
  components:{
    LayernormAnimator,
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
  emits:["exit"],
  data(){
    return {
      CloseBold:shallowRef(CloseBold),
    };
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
      console.log("Enter LayernormView.vue");
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
</style>