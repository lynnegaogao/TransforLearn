<template>
    <div id="layout">
        <div id="title">TransforLearn: Interactive Visual Tutorial for the Transformer Model</div>
        <div id="textGroup">
            <div id="inputGroup">
                <div className="chartHeader">Input View</div>
                <cpnInput :disableControl='disableControl' @translate="onTranslate" />
            </div>
            <div id="translateGroup">
                <div className="chartHeader">Translation View</div>
                <cpnTranslation :currentTranslation='currentTranslation' :fullTranslation='fullTranslation'
                    :currentPrediction='curIterPred' :cumulativeProb='cumulativeProb' :disableControl='disableControl' @last='onLast' @next='onNext'
                    @getParams='onGetParams' />
            </div>
        </div>
        <div id="architectureGroup">
            <div id="overviewGroup" v-if="data.length > 0">
                <div className="chartHeader">Architecture View</div>
                <cpnArchitecture :encoder='data[0]' :decoder='data[curIter]' :curIter='curIter'
                    :disableControl='disableControl' @changeHilightsIndex='onChangeHilightsIndex'
                    :highlightsIndex="highlightsIndex" @changeTokenIndex='onChangeTokenIndex' :curTokenIndex="curTokenIndex"
                    @changeTokenHighLightIndex='onChangeTokenHighLightIndex' :tokenHighLightIndex='tokenHighLightIndex'
                    @getParams='onGetParams' :encoderPEParams='encoderPEParams' :decoderPEParams='decoderPEParams'
                    :layerNormParams='layerNormParams' :detailViewNodeType='detailViewNodeType'
                    :detailViewNodeId='detailViewNodeId' @openAttentionHead='onOpenAttentionHead'
                    @openAttentionOperation='onOpenAttentionOperation'
                    @openAttentionConcaAndLinear='onOpenAttentionConcaAndLinear' @openGenerator='onOpenGenerator'>
                </cpnArchitecture>
            </div>
        </div>
        <div id="detailviewGroup" v-if="data.length > 0">
            <AttentionHeadView v-if="detailViewNodeType === 'openAttentionHead' && isShowDetailview" @exit="quitDetailView"
                :encoder='data[0]' :decoder='data[curIter]' :disableControl='disableControl' :curIter='curIter'
                :detailViewNodeType='detailViewNodeType' :detailViewNodeId='detailViewNodeId'
                :attentionParams='attentionParams' @getParams='onGetParams'
                @changeOrderAndHilights="onChangeOrderAndHilights" :curOrder='QKVorder' :highlights='QKVhighlights' />

            <AttentionMechanismView v-if="detailViewNodeType === 'openAttentionOperation' && isShowDetailview"
                @exit="quitDetailView" :encoder='data[0]' :decoder='data[curIter]' :disableControl='disableControl'
                :curIter='curIter' :detailViewNodeType='detailViewNodeType' :detailViewNodeId='detailViewNodeId'
                :openButtonHight='openButtonHight' @changeButtonHight='onChangeButtonHight' />

            <AttentionConcaAndLinear v-if="detailViewNodeType === 'openAttentionConcaAndLinear' && isShowDetailview"
                @exit="quitDetailView" :encoder='data[0]' :decoder='data[curIter]' :disableControl='disableControl'
                :curIter='curIter' :detailViewNodeType='detailViewNodeType' :detailViewNodeId='detailViewNodeId'
                :attentionParams='attentionParams' @getParams='onGetParams' />

            <LinearSoftmaxView v-if="detailViewNodeType === 'openGenerator' && isShowDetailview" @exit="quitDetailView"
                :encoder='data[0]' :decoder='data[curIter]' :disableControl='disableControl' :curIter='curIter'
                :detailViewNodeType='detailViewNodeType' :detailViewNodeId='detailViewNodeId' @getParams='onGetParams' 
                :generatorParams='generatorParams'/>
        </div>

    </div>
</template> 

<script>
import cpnInput from "./components/input"
import cpnTranslation from "./components/translation"
import cpnArchitecture from "./components/Architecture"
import AttentionHeadView from "./components/AttentionHeadView"
import AttentionMechanismView from "./components/AttentionMechanismView"
import AttentionConcaAndLinear from "./components/ConcatenateView.vue"
import LinearSoftmaxView from "./components/LinearSoftmaxView.vue"

import DataService from "./utils/data-service";
// 这里将 后端服务器 抽象为一个对象 DataService, 前端与后端的交互就通过 DataService 完成
import { nodeId2ParamIndices } from "./utils/data-utils"
import { ElLoading } from 'element-plus'
export default {
    name: 'App',
    components: {
        cpnInput,
        cpnTranslation,
        cpnArchitecture,
        AttentionHeadView,
        AttentionMechanismView,
        AttentionConcaAndLinear,
        LinearSoftmaxView
    },
    data() {
        return {
            // data for HTTP requests in DataService
            get: null,
            getData: null,
            loadParam: { 'data': 'load' },
            loadData: null,

            // data for event handling in EventService
            dataName: null,
            dataValue: null,

            // 我们所使用的一些变量
            // sentence begin
            BOS: 'BOS',
            // sentence end
            EOS: 'EOS',

            // 标记后台翻译工作是否完成
            inTranslating: false,

            // candidates input texts
            inputTextArray: ["Why are you so happy?", "I'm glad you come to see me.",],

            // index of input text in input text inputTextArray
            curInputIndex: 0,

            // input text
            inputText: '',

            // intermediate data generated from the translation
            data: [],

            // parameters of the Transformer model
            encoderPEParams: [],
            decoderPEParams: [],
            layerNormParams: {},
            attentionParams: {},
            generatorParams: {},
            cumulativeProb: 1,

            // translations
            fullTranslation: '',
            currentTranslation: '',

            // current iteration index
            totalIterations: 0,
            curIter: 1,
            curIterPred: '',
            inputTextLength: 1,

            // detail view conditions
            disableControl: false,
            isShowDetailview: false,
            detailViewNodeType: '',
            detailViewNodeId: '',

            // overlay
            mask: null,
            zIndexOverlay: "10",

            // highlight index
            curTokenIndex: 0,
            highlightsIndex: 0,
            tokenHighLightIndex: 0,
            QKVorder: 0,
            QKVhighlights: [],
            openButtonHight: '',

        }
    },
    mounted() {
    },
    methods: {
        onTranslate(text) {
            console.log("App.vue - input text: " + text);
            this.inputText = text;
            const loading = ElLoading.service({
                lock: true,
                text: 'Translating',
                background: 'rgba(0, 0, 0, 0.7)',
            })
            DataService. constructor()
            DataService.translate_input_text({ text }, (backendData) => {
                console.log('backendData:', backendData);
                this.fullTranslation = backendData.translation;
                this.data = backendData.data;
                this.totalIterations = this.data.length - 1;
                this.inputTextLength = this.data[0].tokenize.length
                this.curIter = 1;
                this.currentTranslation = this.data[this.curIter].input;
                this.curIterPred = this.data[this.curIter].predict.word;
                // 记录当前轮次的所有 pieces
                this.encoderPieces = this.data[0].tokenize.pieces;
                this.decoderPieces = this.data[this.curIter].tokenize.pieces;
                loading.close();
            });




        },

        onLast() {
            console.log('this.curIter: ', this.curIter);
            console.log('this.curIter > 1 ?', this.curIter > 1);
            if (this.curIter > 1) {
                this.curIter -= 1;
                this.currentTranslation = this.data[this.curIter].input;
                this.curIterPred = this.data[this.curIter].predict.word;
                this.decoderPieces = this.data[this.curIter].tokenize.pieces;
                // 改变各个图元绑定的 data (if needed)
                // 改变 cumulative score
                this.cumulativeProb = 1;
                for (let i = 1; i <= this.curIter; i++) {
                    this.cumulativeProb *= Math.exp((this.data[i].softmax)[this.data[i].predict.token]);
                }

                const decoderSentence_len = this.curIter;
                const decoderpeId = 'decoder-PE';
                DataService.getParams({
                    paramIndex: nodeId2ParamIndices(decoderpeId),
                    sentence_len: decoderSentence_len,
                }, (backendParams) => {
                    this.decoderPEParams = backendParams.param
                });

            } else {
                // alert("当前已是首轮预测迭代")
                console.log("当前已是首轮预测迭代");
            }
            console.log(this.curIter)
        },

        onNext() {
            console.log('this.curIter: ', this.curIter);
            console.log(`this.curIter < ${this.totalIterations}: `, this.curIter < this.totalIterations);

            if (this.curIter < this.totalIterations) {
                this.curIter += 1;
                this.currentTranslation = this.data[this.curIter].input;
                this.curIterPred = this.curIter < this.totalIterations ? this.data[this.curIter].predict.word : this.EOS;
                this.decoderPieces = this.data[this.curIter].tokenize.pieces;
                // 改变各个图元绑定的 data (if needed)
                // 改变 cumulative score
                this.cumulativeProb = 1;
                for (let i = 1; i <= this.curIter; i++) {
                    this.cumulativeProb *= Math.exp((this.data[i].softmax)[this.data[i].predict.token]);
                }

                const decoderSentence_len = this.curIter;
                const decoderpeId = 'decoder-PE';
                DataService.getParams({
                    paramIndex: nodeId2ParamIndices(decoderpeId),
                    sentence_len: decoderSentence_len,
                }, (backendParams) => {
                    this.decoderPEParams = backendParams.param
                });

            } else {
                console.log("当前已是末轮预测迭代");
            }
        },

        onChangeHilightsIndex(newHighlightsIndex) {
            this.highlightsIndex = newHighlightsIndex;
        },

        onChangeTokenIndex(newTokenIndex) {
            this.curTokenIndex = newTokenIndex;
        },

        onChangeTokenHighLightIndex(newTokenHighLightIndex) {
            this.tokenHighLightIndex = newTokenHighLightIndex;
        },

        onChangeOrderAndHilights(newValues) {
            this.QKVorder = newValues.order;
            this.QKVhighlights = newValues.highlights;
        },

        onChangeButtonHight(newHighlight) {
            this.openButtonHight = newHighlight;
        },

        onGetParams(nodeId) {
            if (nodeId != undefined) {
                // 获取 PE parameters
                if (nodeId.split('-')[1] == 'PE') {
                    const encoderSentence_len = this.data[0].embedding.input.length;
                    const encoderpeId = 'encoder-PE';
                    DataService.getParams({
                        paramIndex: nodeId2ParamIndices(encoderpeId),
                        sentence_len: encoderSentence_len,
                    }, (backendParams) => {
                        this.encoderPEParams = backendParams.param
                    });
                    const decoderSentence_len = this.curIter;
                    const decoderpeId = 'decoder-PE';
                    DataService.getParams({
                        paramIndex: nodeId2ParamIndices(decoderpeId),
                        sentence_len: decoderSentence_len,
                    }, (backendParams) => {
                        this.decoderPEParams = backendParams.param
                    });

                }
                // 获取 LN alpha/beta parameters
                else if (nodeId.split('-')[3] == 'LN') {
                    DataService.getParams({
                        paramIndex: nodeId2ParamIndices(nodeId)
                        // paramIndex: nodeId2ParamIndices(nodeId)
                    }, (backendParams) => {
                        this.layerNormParams['alpha'] = backendParams.param[0];
                        this.layerNormParams['beta'] = backendParams.param[1];
                    });
                }
                // 获取 attention parameters
                else if (nodeId.split('-')[4] == 'attention') {
                    DataService.getParams({
                        paramIndex: nodeId2ParamIndices(nodeId)
                    }, (backendParams) => {
                        this.attentionParams = backendParams.param
                    });
                }
                // 获取 generator parametors
                else if (nodeId == 'generator-linear') {
                    console.log(nodeId2ParamIndices(nodeId))
                    DataService.getParams({
                        paramIndex: nodeId2ParamIndices(nodeId)
                    }, (backendParams) => {
                        this.generatorParams = backendParams.param
                    });
                }
            }

        },

        enterDetailView(newDetailViewNodeType, newDetailViewNodeId) {
            this.isShowDetailview = true;
            this.disableControl = true;
            this.detailViewNodeType = newDetailViewNodeType
            this.detailViewNodeId = newDetailViewNodeId

            // 确定 detail view 的位置
            const detailview = document.getElementById('detailviewGroup');
            detailview.style.top = '250px';  // 设定 detailview 在 y 轴上的位置
            detailview.style.left = '450px';  // 设定 detailview 在 x 轴上的位置
            detailview.style.position = 'absolute'; // 将 detailview 的位置设定为绝对位置(i.e.出现在浏览器的相应的地方)
            detailview.style.width = '1000px';
            detailview.style.zIndex = "100";
            // 添加遮盖物
            this.mask = document.createElement('div');
            this.mask.style.width = window.innerWidth + 'px';
            this.mask.style.height = '1000px';
            this.mask.style.background = '#fff';
            this.mask.style.opacity = '.7';
            this.mask.style.position = 'fixed';
            this.mask.style.top = '190px';
            this.mask.style.left = '0';
            this.mask.style.zIndex = this.zIndexOverlay;
            this.mask.onclick = (event) => {
                event = event || window.event;
                if (event || event.stopPropagation()) {
                    event.stopPropagation();
                } else {
                    event.cancelBubble = true;
                }
                this.quitDetailView();
            }
            document.getElementById('overviewGroup').appendChild(this.mask);
        },

        quitDetailView() {
            this.isShowDetailview = false;
            this.disableControl = false;
            this.detailViewNodeType = ''
            this.detailViewNodeId = ''

            const detailview = document.getElementById('detailviewGroup');
            detailview.style.zIndex = "-100";
            // 移除覆盖物
            document.getElementById('overviewGroup').removeChild(this.mask);
        },

        onOpenAttentionHead(newDetailViewNodeType, newDetailViewNodeId) {
            console.log('Enter Attention Head View')
            this.isShowDetailview = true;
            this.disableControl = true;
            this.detailViewNodeType = newDetailViewNodeType
            this.detailViewNodeId = newDetailViewNodeId
            this.enterDetailView(newDetailViewNodeType, newDetailViewNodeId);
        },

        onOpenAttentionOperation(newDetailViewNodeType, newDetailViewNodeId) {
            console.log('Enter Attention Operation View')
            this.detailViewNodeType = newDetailViewNodeType
            this.detailViewNodeId = newDetailViewNodeId
            this.isShowDetailview = true;
            this.disableControl = true;
            this.enterDetailView(newDetailViewNodeType, newDetailViewNodeId);
        },

        onOpenAttentionConcaAndLinear(newDetailViewNodeType, newDetailViewNodeId) {
            console.log('Enter Attention Concatenate And Linear View')
            this.detailViewNodeType = newDetailViewNodeType
            this.detailViewNodeId = newDetailViewNodeId
            this.isShowDetailview = true;
            this.disableControl = true;
            this.enterDetailView(newDetailViewNodeType, newDetailViewNodeId);
        },

        onOpenGenerator(newDetailViewNodeType, newDetailViewNodeId) {
            console.log('Enter Generator View')
            this.detailViewNodeType = newDetailViewNodeType
            this.detailViewNodeId = newDetailViewNodeId
            this.isShowDetailview = true;
            this.disableControl = true;
            this.enterDetailView(newDetailViewNodeType, newDetailViewNodeId);
        },

    },

}


</script>

<style>
#app {
    /* font-family: Avenir, Helvetica, Arial, sans-serif; */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
}

#layout {
    height: 100vh;
    width: 100vw;
    /* background-color: rgb(240, 239, 239); */
    background-color:'rgb(255,255,255)';
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

#title {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    font-size: 25px;
    font-weight: bolder;
}

#textGroup {
    width: 100%;
    flex: 3;
    display: flex;
    flex-direction: row;
    box-shadow: 0 0px 10px rgb(0 0 0 / 28%);

}

#inputGroup {
    flex: 2;
    box-shadow: 0 0px 10px rgb(0 0 0 / 28%);
}

#translateGroup {
    margin-left: 2px;
    flex: 3.5;
    box-shadow: 0 0px 10px rgb(0 0 0 / 28%);
}

#architectureGroup {
    width: 100%;
    flex: 35;
    display: flex;
    flex-direction: row;
    box-shadow: 0 0px 10px rgb(0 0 0 / 28%);
}

#overviewGroup {
    width: 100%;
    box-shadow: 0 0px 10px rgb(0 0 0 / 28%);
}

#detailViewGroup {
    margin-left: 2px;
    box-shadow: 0 0px 10px rgb(0 0 0 / 28%);
    z-index: 100;
}

.chartHeader {
    width: 100%;
    /* height: 8%; */
    height: 2.8vh;
    background-color: #eee;
    text-align: left;
    text-indent: 4px;
    line-height: 1.5;
    /* line-height: 2; */
    font-weight: bold;
    font-size: 16px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
    border: 1px solid lightgrey;
}
</style>