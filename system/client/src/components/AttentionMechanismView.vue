<template>
    <div class="container">
        <div class="box">
            <div class="control-pannel">
                <div class="title-text">
                    Attention mechanism in each head
                </div>
                <el-tooltip content="Quit from Attention Mechanism View." placement="top" effect="dark">
                    <el-button type="primary" :icon="CloseBold" plain circle @click="onExit()" />
                </el-tooltip>
            </div>
            <div id="attention-mechanism-svg">
                <div id="attention-mechanism-overflow">
                </div>
                <div id="attention-mechanism-detail">
                    <AttentionCalScore v-if="openMechanismPart === 'MatMul-1'" :encoder='encoder' :decoder='decoder'
                        :detailViewNodeType='detailViewNodeType' :detailViewNodeId='detailViewNodeId'
                        :highLightArray='highLightArray' @changeHighLightArray='onChangeHighLightArray' />

                    <AttentionScaleOut v-if="openMechanismPart === 'Scale'" :encoder='encoder' :decoder='decoder'
                        :detailViewNodeType='detailViewNodeType' :detailViewNodeId='detailViewNodeId'
                        :highLightArray='highLightArray' @changeHighLightArray='onChangeHighLightArray' />

                    <AttentionSoftmax v-if="openMechanismPart === 'Softmax'" :encoder='encoder' :decoder='decoder'
                        :detailViewNodeType='detailViewNodeType' :detailViewNodeId='detailViewNodeId'
                        :highLightArray='highLightArray' @changeHighLightArray='onChangeHighLightArray' />

                    <AttentionGenerateOutput v-if="openMechanismPart === 'MatMul-2'" :encoder='encoder' :decoder='decoder'
                        :detailViewNodeType='detailViewNodeType' :detailViewNodeId='detailViewNodeId'
                        :highLightArray='highLightArray' @changeHighLightArray='onChangeHighLightArray' />
                </div>
            </div>
        </div>
    </div>
</template>
  
<script>
import AttentionCalScore from "./AttentionCalScore"
import AttentionScaleOut from "./AttentionScaleOut"
import AttentionSoftmax from "./AttentionSoftmax"
import AttentionGenerateOutput from "./AttentionGenerateOutput"
import * as d3 from "d3";
//   import { getDataRange, getGridData, getVisualizationSizeConstraint } from '../utils/detailview-utils'
import { shallowRef } from "vue"
import { CloseBold, Switch } from '@element-plus/icons-vue'
export default {
    name: "AttentionMechanismView",
    components: {
        AttentionCalScore,
        AttentionScaleOut,
        AttentionSoftmax,
        AttentionGenerateOutput,
    },
    props: {
        encoder: {
            type: Object,
            default: function () { return {}; },
        },
        decoder: {
            type: Object,
            default: function () { return {}; },
        },
        curIter: {
            type: Number,
            default: 1,
        },
        detailViewNodeType: {
            type: String,
            default: '',
        },
        detailViewNodeId: {
            type: String,
            default: '',
        },
        openButtonHight: {
            type: String,
            default: '',
        },
    },
    emits: ["exit", 'getParams', 'changeButtonHight'],
    data() {
        return {
            CloseBold: shallowRef(CloseBold),
            Switch: shallowRef(Switch),
            openHighlights: true,
            openMechanismPart: 'MatMul-1',
            highLightArray: [0,0],
        };
    },
    watch: {
        openButtonHight(newValue, oldValue) {
            console.log(newValue, oldValue)
            this.$nextTick(() => {
                this.drawMechanismOverflow()
            })
        }
    },
    beforeUpdate() {

    },
    mounted() {
        this.drawMechanismOverflow()
    },
    methods: {
        onExit() {
            console.log("exit from the current view.");
            this.$emit('exit');
        },
        onHighlights() {
            if (this.openHighlights) {
                document.getElementById('highlightsBtn').innerHTML = 'Open  Highlights';
                this.openHighlights = false;
            } else {
                document.getElementById('highlightsBtn').innerHTML = 'Close Highlights';
                this.openHighlights = true;
            }
        },
        onChangeHighLightArray(newArray) {
            this.highLightArray = newArray
        },
        drawMechanismOverflow() {
            d3.select('#attention-mechanism-overflow').selectAll('*').remove()
            let svg = d3.select('#attention-mechanism-overflow')
                .append('svg')
                .attr('id', "attentionMechanismOverfloweSvg")
                .attr("width", "100%")
                .attr('height', "70px")
                .attr('transform', `translate(20,40)`)
            let buttonWidth = 100
            let buttonHeight = 40
            let processGap = 100

            let matMulOffsetX = 100
            let matMulOffsetY = 0
            let matMul = svg.append('g')
                .attr('id', 'matMul-button-1-g')
                .attr('transform', `translate(${matMulOffsetX},${matMulOffsetY})`)
            matMul.append('rect')
                .attr('id', 'matMul-button')
                .attr('width', buttonWidth)
                .attr('height', buttonHeight)
                .attr("y", 1)
                .attr("rx", 5)
                .attr("fill", 'rgb(247, 244, 235)')
                .attr("stroke", this.openButtonHight == 'matMul-button' ? 'black' : 'rgb(175, 175, 175)')
                .attr("stroke-width", 2)
                .on('mouseover', (event) => {
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
                .on('mouseout', () => {
                    this.$emit('changeButtonHight', '')
                })
                .on('click', (event) => {
                    this.openMechanismPart = 'MatMul-1'
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
            matMul.append('text')
                .attr('class', 'label')
                .attr('id', 'matMul-button')
                .attr('x', buttonWidth / 2)
                .attr('y', buttonHeight / 2 + 1)
                .text('MatMul')
                .on('mouseover', (event) => {
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
                .on('mouseout', () => {
                    this.$emit('changeButtonHight', '')
                })
                .on('click', (event) => {
                    this.openMechanismPart = 'MatMul-1'
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
            drawArrow(matMul, buttonWidth + 20, -10)

            let scaleOffsetX = matMulOffsetX + buttonWidth + processGap
            let scaleOffsetY = matMulOffsetY
            let scale = svg.append('g')
                .attr('id', 'scale-button-g')
                .attr('transform', `translate(${scaleOffsetX},${scaleOffsetY})`)
            scale.append('rect')
                .attr('id', 'scale-button')
                .attr('width', buttonWidth)
                .attr('height', buttonHeight)
                .attr("y", 1)
                .attr("rx", 5)
                .attr("fill", 'rgb(247, 244, 235)')
                .attr("stroke", this.openButtonHight == 'scale-button' ? 'black' : 'rgb(175, 175, 175)')
                .attr("stroke-width", 2)
                .on('mouseover', (event) => {
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
                .on('mouseout', () => {
                    this.$emit('changeButtonHight', '')
                })
                .on('click', (event) => {
                    this.openMechanismPart = 'Scale'
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
            scale.append('text')
                .attr('class', 'label')
                .attr('id', 'scale-button')
                .attr('x', buttonWidth / 2)
                .attr('y', buttonHeight / 2 + 1)
                .text('Scale & Mask')
                .on('mouseover', (event) => {
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
                .on('mouseout', () => {
                    this.$emit('changeButtonHight', '')
                })
                .on('click', (event) => {
                    this.openMechanismPart = 'Scale'
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
            drawArrow(scale, buttonWidth + 20, -10)

            let softmaxOffsetX = scaleOffsetX + buttonWidth + processGap
            let softmaxOffsetY = scaleOffsetY
            let softmax = svg.append('g')
                .attr('id', 'softmax-button-g')
                .attr('transform', `translate(${softmaxOffsetX},${softmaxOffsetY})`)
            softmax.append('rect')
                .attr('id', 'softmax-button')
                .attr('width', buttonWidth)
                .attr('height', buttonHeight)
                .attr("y", 1)
                .attr("rx", 5)
                .attr("fill", 'rgb(247, 244, 235)')
                .attr("stroke", this.openButtonHight == 'softmax-button' ? 'black' : 'rgb(175, 175, 175)')
                .attr("stroke-width", 2)
                .on('mouseover', (event) => {
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
                .on('mouseout', () => {
                    this.$emit('changeButtonHight', '')
                })
                .on('click', () => {
                    this.openMechanismPart = 'Softmax'
                })
            softmax.append('text')
                .attr('class', 'label')
                .attr('id', 'softmax-button')
                .attr('x', buttonWidth / 2)
                .attr('y', buttonHeight / 2 + 1)
                .text('Softmax')
                .on('mouseover', (event) => {
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
                .on('mouseout', () => {
                    this.$emit('changeButtonHight', '')
                })
                .on('click', (event) => {
                    this.openMechanismPart = 'Softmax'
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
            drawArrow(softmax, buttonWidth + 20, -10)
            let matMul2OffsetX = softmaxOffsetX + buttonWidth + processGap
            let matMul2OffsetY = softmaxOffsetY
            let matMul2 = svg.append('g')
                .attr('id', 'matMul2-button-g')
                .attr('transform', `translate(${matMul2OffsetX},${matMul2OffsetY})`)
            matMul2.append('rect')
                .attr('id', 'matMul2-button')
                .attr('width', buttonWidth)
                .attr('height', buttonHeight)
                .attr("y", 1)
                .attr("rx", 5)
                .attr("fill", 'rgb(247, 244, 235)')
                .attr("stroke", this.openButtonHight == 'matMul2-button' ? 'black' : 'rgb(175, 175, 175)')
                .attr("stroke-width", 2)
                .on('mouseover', (event) => {
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
                .on('mouseout', () => {
                    this.$emit('changeButtonHight', '')
                })
                .on('click', (event) => {
                    this.openMechanismPart = 'MatMul-2'
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
            matMul2.append('text')
                .attr('class', 'label')
                .attr('id', 'matMul2-button')
                .attr('x', buttonWidth / 2)
                .attr('y', buttonHeight / 2 + 1)
                .text('MatMul')
                .on('mouseover', (event) => {
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
                .on('mouseout', () => {
                    this.$emit('changeButtonHight', '')
                })
                .on('click', (event) => {
                    this.openMechanismPart = 'MatMul-2'
                    this.$emit('changeButtonHight', event.srcElement.id)
                })
            // 绘制箭头
            function drawArrow(svg, offsetX, offsetY) {
                let arrowLink = require("../../src/assets/rightArrow_1.svg")
                svg.append('svg:image')
                    .attr('xlink:href', arrowLink)
                    .attr("x", offsetX)
                    .attr("y", offsetY)
                    .attr("width", 60)
                    .attr("height", 60)
            }

        },




    }
}
</script>
  
  <!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.container {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    box-shadow: rgb(236, 231, 231) 2px 2px 11px;
    border-radius: .5rem;
    background-color: white;
    width: 100%;
    height: 100%;
}

.box {
    padding: 5px 15px 10px 15px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    align-items: stretch;
    width: 100%;
    height: 100%;
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
    font-size: 1.1em;
    margin: auto auto;
    display: inline-block;
    vertical-align: middle;
    text-align: center;
    font-weight: bold;
    color: #4a4a4a;
}

.buttons {
    cursor: pointer;
    margin-left: 5px;
    margin-right: 5px;
    margin-top: 5px;
    margin-bottom: 5px;
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

.label {
    font-size: 14px;
    text-anchor: middle;
    dominant-baseline: middle;
    fill: #4a4a4a;
}

.operator {
    fill: rgb(235, 235, 235);
    stroke: rgb(175, 175, 175);
    stroke-width: 1
}

.operatorText {
    font-size: 12px;
    font-weight: bold;
    text-anchor: middle;
    dominant-baseline: middle;
    fill: rgb(175, 175, 175);
}

#attention-mechanism-svg {
    display: flex;
    flex-direction: column;
}

#attention-mechanism-overflow {
    width: 100%;
    flex: 1;
    background-color: white;
}

#attention-mechanism-detail {
    width: 100%;
    flex: 3;
    background-color: white;
}
</style>