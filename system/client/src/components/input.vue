<template>
  <div id="cpnInputGroup" >
    <link rel="stylesheet" type="text/css" href="https://blog.huangwx.cn/css/sweetalert.css">
    <div id="inputText" >
      Sentence to be translated:
    </div>
    <div id="inputBox" style="width: 90%">
      <el-input v-model="input" class="w-50 m-2" placeholder="Type source text" :prefix-icon="Search" @blur="inputBlur"
        @keyup.enter="inputEnter">
        <template #append>
          <el-tooltip content="Please press ENTER to confirm." placement="top" effect="dark">
            <el-icon>
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </template>
      </el-input>
    </div>
  </div>
</template>


<script>
import { ref } from "vue"
import { shallowRef } from "vue"
import { Search, InfoFilled } from '@element-plus/icons-vue'
export default {
  name: "cpnInput",
  components: {
    // Search,
  },
  props: {
    disableControl: {
      type: Boolean,
      default: false,
    },
  },
  // emits: ['selected'], // 子组件发射事件, 父组件接收事件并完成相应数据交互
  emits: ["translate", "keyEnter", "cleanComponentView"], // 子组件发射事件, 父组件接收事件并完成相应数据交互
  data() {
    return {
      // icons
      // Search,
      Search: shallowRef(Search),
      InfoFilled: shallowRef(InfoFilled),
      // svg: null,
      isBtnDisabled: true,
      isShowAlertError: false,
      isShowAlertSuccess: false,
      inputText: "",
      input: ref(""),
    }
  },
  watch: {
    // loadData: function () {
    //   // When data is changed in parent, render this component
    //   this.renderBarChart();
    // },
  },
  mounted() {
    this.initTranslateInputText();
  },
  methods: {
    handleClick() {
      console.log('点击');
    },
    inputBlur() {
      if (this.inputText != this.input) {
        this.$message({
          type: 'info',
          // message:"Translation of empty text is not allowed!",
          message: "输入操作中止!",
          showClose: true,
        });
        this.input = this.inputText
      }
    },
    inputEnter() {
      if (this.input == "") {
        this.$message({
          type: 'error',
          // message:"Translation of empty text is not allowed!",
          message: "翻译文本输入失败, 请勿输入空白文本!",
          showClose: true,
        });
        this.isShowAlertError = true;
        this.input = this.inputText;
      } else {
        this.inputText = this.input;
        // console.log(this.$el);
        console.log("begin translated...");
        this.$emit('translate', this.inputText);
        this.isShowAlertSuccess = true;
        this.$message({
          type: 'success',
          // message:"Translation of empty text is not allowed!",
          message: "Successfully entered, waiting for the translation!",
          showClose: true,
        });
      }
    },

    initTranslateInputText() {
      this.inputText = "Why are you so happy?";
      // this.inputText = "I have an idea.";
      this.input = this.inputText;
      // document.getElementById("inputText").value = this.inputText;
      console.log("begin translate");
      this.$emit('translate', this.inputText);
    },

    // initTranslateInputText(){
    //   this.inputText = "Why are you so happy?";
    //   document.getElementById("inputText").value = this.inputText;
    //   console.log("begin translate");
    //   this.$emit('translate', this.inputText);
    // },

    translateInputText() {
      const text = document.getElementById("inputText").value;
      if (text == "") {
        // alert("Translation of empty text is not allowed!");
        this.$message({
          type: 'error',
          // message:"Translation of empty text is not allowed!",
          message: "翻译文本输入失败, 请勿输入空白文本!",
          showClose: true,
        });
        // alert 如何美化？！—— 使用 Vue 组件库!
        this.isShowAlertError = true;
      } else {
        this.inputText = text;
        console.log(this.$el);
        console.log("begin translate");
        this.$emit('translate', text);
        this.isShowAlertSuccess = true;
        this.$message({
          type: 'success',
          // message:"Translation of empty text is not allowed!",
          message: "Successfully entered, waiting for the translation!",
          showClose: true,
        });
      }
    },

    blurInputText() {
      console.log("Input text blured. Restore original text...");
      document.getElementById("inputText").value = this.inputText;
    },

    onClean() {
      this.$emit('cleanComponentView');
    }
  }
}
</script>

<style>
#cpnInputGroup {
  margin-top: 20px;
  display: flex;
  flex-direction: row;
}
#inputText {
  /* margin-top: 10px; */
  flex: 1;
}

#inputBox {
  margin-top: 10px;
  margin-right: 20px;
  flex: 3;
}

</style>