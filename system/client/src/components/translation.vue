<template>
  <div id="cpnTranslateGroup" style="height: 100%; width: 100%">
    <div id="translateLeft">
      <div id="fullTranslate">
        <div class="translateText">
          Translation:
        </div>
        <div class="translateBox" style="width: 90%">
          <el-input v-model="fullTranslationData" disabled>
            <template #append>
              <el-tooltip content="The text displayed on the left is the final translation of the source text."
                placement="top" effect="dark">
                <el-icon>
                  <InfoFilled />
                </el-icon>
              </el-tooltip>
            </template>
          </el-input>
        </div>
      </div>
      <div id="curTranslate">
        <div class="translateText">
          Current translation:
        </div>
        <div class="translateBox">
          <el-input v-model="currentTranslationData" disabled>
            <template #append>
              <el-button-group>
                <el-tooltip content="Last predicted word" placement="bottom" effect="light">
                  <el-button type="primary" plain @click="onLast($event)">
                    <el-icon class="el-icon--right">
                      <ArrowLeftBold />
                    </el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="Next predicted word" placement="bottom" effect="light">
                  <el-button type="primary" plain @click="onNext($event)">
                    <el-icon class="el-icon--right">
                      <ArrowRightBold />
                    </el-icon>
                  </el-button>
                </el-tooltip>
              </el-button-group>
            </template>
          </el-input>
        </div>
      </div>
    </div>
    <div id="translateRight">
      <div id="predicIterationText">
        <div class="predictText">
          Prediction in current iteration:
        </div>
        <div class="predictBox" style="width: 90%">
          <span id="predictionOfCurrentIteration" text-align="left" :innerHTML="currentPredictionData"></span>
        </div>
      </div>
      <div id="predictionIterationScore">
        <div class="predictText">
          Cumulative Score (Probabilities):
        </div>
        <div class="predictBox" style="width: 90%">
          <span id="predictionOfCurrentIteration" text-align="left" :innerHTML="cumulativeProb"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/*
This component demonstrates one way to construct d3 visualization.
d3 example source: https://observablehq.com/@d3/sortable-bar-chart
 */
// import * as d3 from "d3";
// import {shallowRef} from "vue"
import { InfoFilled } from '@element-plus/icons-vue'
import { ArrowLeftBold, ArrowRightBold } from '@element-plus/icons-vue'
export default {
  name: "cpnTranslation",
  components: {
    ArrowLeftBold,
    ArrowRightBold,
    InfoFilled,
  },
  props: {
    fullTranslation: {
      type: String,
      default: '',
    },
    currentTranslation: {
      type: String,
      default: '',
    },
    currentPrediction: {
      type: String,
      default: '',
    },
    disableControl: {
      type: Boolean,
      default: false,
    },
    cumulativeProb:{
      type: Number,
      default: 1,
    }
  },
  // emits: ['selected'], // 子组件发射事件, 父组件接收事件并完成相应数据交互
  emits: ["last", "next"], // 子组件发射事件, 父组件接收事件并完成相应数据交互
  data() {
    return {
      // svg: null,
      currentTranslationData: '',
      currentPredictionData: '',
      fullTranslationData: '',
    }
  },
  watch: {
    // loadData: function () {
    //   // When data is changed in parent, render this component
    //   this.renderBarChart();
    // },
  },
  beforeUpdate() {
    this.currentTranslationData = this.currentTranslation;
    this.currentPredictionData = this.currentPrediction;
    this.fullTranslationData = this.fullTranslation;
  },
  mounted() {
    // this.onGetParams()
  },
  methods: {

    onLast(e) {
      // console.log(e);
      e.stopPropagation();
      this.$emit('last');
    },
    onNext(e) {
      // console.log(e);
      e.stopPropagation();
      this.$emit('next');
    },
  }
}
</script>

<style scoped>
#cpnTranslateGroup {
  margin-top: 10px;
  display: flex;
  flex-direction: row;
}

#translateLeft {
  margin-top: 5px;
  margin-right: 20px;
  flex: 3;
  display: flex;
  flex-direction: column;
}

#fullTranslate {
  display: flex;
  flex-direction: row;
}

#curTranslate {
  margin-top: 5px;
  margin-bottom: 10px;
  display: flex;
  flex-direction: row;
}

.translateText {
  flex: 1;
}

.translateBox {
  flex: 2;
}

#translateRight {
  margin-top: 10px;
  flex: 2;
  display: flex;
  flex-direction: column;
}

#predicIterationText{
  flex: 0.5;
  display: flex;
  flex-direction: row;
}

#predictionIterationScore{
  flex: 1;
  display: flex;
  flex-direction: row;
}

.predictText {
  flex: 1;
}

.predictBox {
  /* margin-top: 10px; */
  flex: 1;
}

#predictionOfCurrentIteration {
  font-weight: bolder;
}
</style>