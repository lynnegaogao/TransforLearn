<!-- <template>
  <div>    <div id="cpnArchitectureGroup" style="height: 100%; width: 100%; overflow-y:scroll;">
    </div>
    <Tooltip></Tooltip></div>

</template> -->
<template>
  <div style="position: relative;height: 100%; width: 100%">
    <div id="cpnArchitectureGroup" style="height: 100%; width: 100%; overflow-y:scroll;">
    </div>
    <div id="tokenTooltip"
      style="transform-origin:center center;position: absolute; z-index: 999;display: flex; align-items: center; justify-content: center;">
      <Tooltip title="11111">
        <text id="tokenTooltip" class="label">Input Text</text>
      </Tooltip>
    </div>
    <div id="wordSegTooltip"
      style="transform-origin:center center;position: absolute; z-index: 999;display: flex; align-items: center; justify-content: center;">
      <Tooltip title="11111">
        <text id="wordSegTooltip" class="label">Word Segmentations</text>
      </Tooltip>
    </div>
    <div id="wordTokenTooltip"
      style="transform-origin:center center;position: absolute; z-index: 999;display: flex; align-items: center; justify-content: center;">
      <Tooltip title="11111">
        <text id="wordTokenTooltip" class="label">Word Token</text>
      </Tooltip>
    </div>
    <div id="embeddingTooltip"
      style="transform-origin:center center;position: absolute; z-index: 999;display: flex; align-items: center; justify-content: center;">
      <Tooltip title="11111">
        <text id="embeddingTooltip" class="label">Embeddings</text>
      </Tooltip>
    </div>
    <div id="peTooltip"
      style="transform-origin:center center;position: absolute; z-index: 999;display: flex; align-items: center; justify-content: center;">
      <Tooltip title="11111">
        <text id="peTooltip" class="label">After positional encoding</text>
      </Tooltip>
    </div>
    <div id="blocksTooltip"
      style="transform-origin:center center;position: absolute; z-index: 999;display: flex; align-items: center; justify-content: center;">
      <Tooltip title="11111">
        <tspan class="label">Encoder</tspan>
        <tspan class="label">blocks</tspan>
      </Tooltip>
    </div>
  </div>
</template>
<script>
import * as d3 from "d3";
import { Tooltip } from 'ant-design-vue';
import { getDataRange, getGridData, getGapGridData, getVisualizationSizeConstraint } from '../utils/detailview-utils'
import { config } from '../utils/config'
export default {
  name: "cpnArchitecture",
  components: {
    Tooltip
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
    highlightsIndex: {
      type: Number,
      default: 0,
    },
    curTokenIndex: {
      type: Number,
      default: 0,
    },
    tokenHighLightIndex: {
      type: Number,
      default: 0,
    },
    decoderPEParams: {
      type: Array,
      default: function () { return []; },
    },
    encoderPEParams: {
      type: Array,
      default: function () { return []; },
    },
    layerNormParams: {
      type: Object,
      default: function () { return {}; },
    },
    disableControl: {
      type: Boolean,
      default: false,
    },
    detailViewNodeType: {
      type: String,
      default: '',
    },
    detailViewNodeId: {
      type: String,
      default: '',
    },
  },
  emits: ['changeHilightsIndex', 'changeTokenIndex', 'changeTokenHighLightIndex', 'getParams',
    'openAttentionHead', 'openAttentionOperation', 'openAttentionConcaAndLinear', 'openGenerator'],
  data() {
    return {
      status: 'initial',
      blockStatus: '',
      coderStatus: 'close',
      focus: 0,
      legalHighlightsIndex: 0,
      oldHighlightsIndex: 0,
      oldCurIter: 1,
      selfAttentionObj: [],
      layerNormObj: [],
      feedForwardNetworkObj: [],
    }
  },
  watch: {
    decoder(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        if (this.status == 'openDecoderBlock') {
          if (this.blockStatus == 'attention') {
            this.openSelfAttention(
              this.selfAttentionObj[0],
              this.selfAttentionObj[1],
              this.selfAttentionObj[2],
              this.selfAttentionObj[3],
              this.selfAttentionObj[4],
              this.selfAttentionObj[5],
              this.selfAttentionObj[6])
          } else if (this.blockStatus == 'layer-normalization') {
            this.openLayerNorm(
              this.layerNormObj[0],
              this.layerNormObj[1],
              this.layerNormObj[2],
              this.layerNormObj[3],
              this.layerNormObj[4],
              this.layerNormObj[5]);
          } else if (this.blockStatus == 'feed-forward-network') {
            this.openFeedForwardNetwork(
              this.feedForwardNetworkObj[0],
              this.feedForwardNetworkObj[1],
              this.feedForwardNetworkObj[2],
              this.feedForwardNetworkObj[3],
              this.feedForwardNetworkObj[4]);
          }
        }
      })
    },
    decoderPEParams(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        if (this.status == 'openPE') {
          this.openPE();
        }
      })
    },
    layerNormParams(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        if (this.status == 'openEncoderBlock' || this.status == 'openDecoderBlock') {
          this.openLayerNorm();
        }
      })
    },
    highlightsIndex(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        if (this.status == 'openEncoderBlock' || this.status == 'openDecoderBlock') {
          if (this.blockStatus == 'layer-normalization') {
            this.openLayerNorm(
              this.layerNormObj[0],
              this.layerNormObj[1],
              this.layerNormObj[2],
              this.layerNormObj[3],
              this.layerNormObj[4],
              this.layerNormObj[5]);
          }
        }
      })
    },
    tokenHighLightIndex(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        if (this.status == 'openEncoderBlock' || this.status == 'openDecoderBlock') {
          if (this.blockStatus == 'feed-forward-network') {
            this.openFeedForwardNetwork(
              this.feedForwardNetworkObj[0],
              this.feedForwardNetworkObj[1],
              this.feedForwardNetworkObj[2],
              this.feedForwardNetworkObj[3],
              this.feedForwardNetworkObj[4]);
          }
        }
      })
    },
    curTokenIndex(newValue, oldValue) {
      console.log(newValue, oldValue)
      this.$nextTick(() => {
        if (this.status == 'openEncoderBlock' || this.status == 'openDecoderBlock') {
          this.openFeedForwardNetwork(
            this.feedForwardNetworkObj[0],
            this.feedForwardNetworkObj[1],
            this.feedForwardNetworkObj[2],
            this.feedForwardNetworkObj[3],
            this.feedForwardNetworkObj[4]);
        }
      })
    }
  },
  beforeUpdate() {
    if (this.status == 'initial') {
      if (this.oldHighlightsIndex != this.highlightsIndex) {
        this.oldHighlightsIndex = this.highlightsIndex;
        this.legalHighlightsIndex = this.highlightsIndex;
      }
      this.initArchitecture();
    }
    else if (this.status == 'openEmbedding') {
      if (this.oldHighlightsIndex != this.highlightsIndex) {
        this.oldHighlightsIndex = this.highlightsIndex;
        this.legalHighlightsIndex = this.highlightsIndex;

      }
      this.openEmbedding();
    }
    else if (this.status == 'openPE') {
      if (this.oldHighlightsIndex != this.highlightsIndex) {
        this.oldHighlightsIndex = this.highlightsIndex;
        this.legalHighlightsIndex = this.highlightsIndex;
      }
      this.openPE();
    }
    else if (this.status == 'openEncoderBlock') {
      if (this.oldHighlightsIndex != this.highlightsIndex) {
        this.oldHighlightsIndex = this.highlightsIndex;
        this.legalHighlightsIndex = this.highlightsIndex;
      }
      this.openEncoderBlock();
    }
    else if (this.status == 'openDecoderBlock') {
      if (this.oldHighlightsIndex != this.highlightsIndex) {
        this.oldHighlightsIndex = this.highlightsIndex;
        this.legalHighlightsIndex = this.highlightsIndex;
      }
      this.openDecoderBlock();
    }




  },
  mounted() {
    this.onGetParams();
    this.initArchitecture();

  },
  methods: {
    onGetParams() {
      this.$emit('getParams', 'encoder-PE')
      this.$emit('getParams', 'encoder-1-1-LN')
      this.$emit('getParams', 'encoder-1-full-self-attention')
    },

    initArchitecture() {
      let processGap = 50
      let encoderOffsetX = processGap
      let encoderOffsetY = 30
      let encoderEmbeddingDataRange = getDataRange(this.encoder.embedding.output)
      let encoderPEDataRange = getDataRange(this.encoder.PE.output)
      let encoderTotalDataRange = {
        max: Math.max(encoderEmbeddingDataRange.max, encoderPEDataRange.max),
        min: Math.min(encoderEmbeddingDataRange.min, encoderPEDataRange.min),
      }
      let decoderEmbeddingDataRange = getDataRange(this.decoder.embedding.output)
      let decoderPEDataRange = getDataRange(this.decoder.PE.output)
      let decoderTotalDataRange = {
        max: Math.max(decoderEmbeddingDataRange.max, decoderPEDataRange.max),
        min: Math.min(decoderEmbeddingDataRange.min, decoderPEDataRange.min),
      }

      d3.select('#cpnArchitectureGroup')
        .selectAll('*').remove()
      let svg = d3.select('#cpnArchitectureGroup')
        .append('svg')
        .attr('id', "architectureSvg")
        .attr("width", "200%")
        .attr('height', "120%")

      let detailedCoderPart = svg.append('g')
        .attr('id', 'detailedcoder-g')
      // 定义open-detailed-encoder
      let openDetailedCoderPart = svg.append('g')
        .attr('id', 'open-detailed-coder')
      let encoderPart =
        svg.append('g')
          .attr('id', 'encoder-g')
          .attr('transform', `translate(${encoderOffsetX},${encoderOffsetY})`);
      let encoderTokenPos = this.drawTokenize(encoderPart, 'encoder', 0, 0, this.encoder.tokenize, false, 1, 1)
      let encoderEmbeddingPos = this.drawEmbedding(encoderPart, 'encoder', encoderTokenPos[0], encoderTokenPos[1], this.encoder.embedding, 'closed', encoderTotalDataRange, false, 1, 1)
      let encoderPEPos = this.drawPE(encoderPart, 'encoder', encoderEmbeddingPos[0], encoderEmbeddingPos[1], this.encoder.PE, 'closed', encoderTotalDataRange, 1)
      this.drawCoders(encoderPart, openDetailedCoderPart, 'encoder', encoderPEPos[0], encoderPEPos[1], '#E1D2D2', detailedCoderPart, 1)

      let decoderOffsetX = processGap
      let decoderOffsetY = encoderTokenPos[2] + 50
      let decoderPart =
        svg.append('g')
          .attr('id', 'decoder-g')
          .attr('transform', `translate(${decoderOffsetX},${decoderOffsetY})`);
      let decoderTokenPos = this.drawTokenize(decoderPart, 'decoder', 0, 0, this.decoder.tokenize, false, 1, 1)
      let decoderEmbeddingPos = this.drawEmbedding(decoderPart, 'decoder', decoderTokenPos[0], decoderTokenPos[1], this.decoder.embedding, 'closed', decoderTotalDataRange, false, 1, 1)
      let decoderPEPos = this.drawPE(decoderPart, 'decoder', decoderEmbeddingPos[0], decoderEmbeddingPos[1], this.decoder.PE, 'closed', decoderTotalDataRange, 1)
      let decoderCodersPos = this.drawCoders(decoderPart, openDetailedCoderPart, 'decoder', decoderPEPos[0], decoderPEPos[1], "rgb(213, 231, 240)", detailedCoderPart, 1)


      let generatorPart =
        svg.append('g')
          .attr('id', 'encoder-g')
          .attr('transform', `translate(${decoderCodersPos[0]},${decoderOffsetY + decoderCodersPos[1]})`);
      this.drawGenerator(generatorPart)
      function Legend(color, {
        title,
        tickSize = 6,
        width = 200,
        height = 44 + tickSize,
        marginTop = 18,
        marginRight = 0,
        marginBottom = 16 + tickSize,
        marginLeft = 0,
        ticks = width / 64,
        tickFormat,
        tickValues
      } = {}) {

        function ramp(color, n = 256) {
          const canvas = document.createElement("canvas");
          canvas.width = n;
          canvas.height = 1;
          const context = canvas.getContext("2d");
          for (let i = 0; i < n; ++i) {
            context.fillStyle = color(i / (n - 1));
            context.fillRect(i, 0, 1, 1);
          }
          return canvas;
        }

        const svg = d3.create("svg")
          .attr("width", width)
          .attr("height", height)
          .attr("viewBox", [0, 0, width, height])
          .style("overflow", "visible")
          .style("display", "block");

        let tickAdjust = g => g.selectAll(".tick line").attr("y1", marginTop + marginBottom - height);
        let x;

        // Continuous
        if (color.interpolate) {
          const n = Math.min(color.domain().length, color.range().length);

          x = color.copy().rangeRound(d3.quantize(d3.interpolate(marginLeft, width - marginRight), n));

          svg.append("image")
            .attr("x", marginLeft)
            .attr("y", marginTop)
            .attr("width", width - marginLeft - marginRight)
            .attr("height", height - marginTop - marginBottom)
            .attr("preserveAspectRatio", "none")
            .attr("xlink:href", ramp(color.copy().domain(d3.quantize(d3.interpolate(0, 1), n))).toDataURL());
        }

        // Sequential
        else if (color.interpolator) {
          x = Object.assign(color.copy()
            .interpolator(d3.interpolateRound(marginLeft, width - marginRight)),
            { range() { return [marginLeft, width - marginRight]; } });

          svg.append("image")
            .attr("x", marginLeft)
            .attr("y", marginTop)
            .attr("width", width - marginLeft - marginRight)
            .attr("height", height - marginTop - marginBottom)
            .attr("preserveAspectRatio", "none")
            .attr("xlink:href", ramp(color.interpolator()).toDataURL());

          // scaleSequentialQuantile doesn’t implement ticks or tickFormat.
          if (!x.ticks) {
            if (tickValues === undefined) {
              const n = Math.round(ticks + 1);
              tickValues = d3.range(n).map(i => d3.quantile(color.domain(), i / (n - 1)));
            }
            if (typeof tickFormat !== "function") {
              tickFormat = d3.format(tickFormat === undefined ? ",f" : tickFormat);
            }
          }
        }

        // Threshold
        else if (color.invertExtent) {
          const thresholds
            = color.thresholds ? color.thresholds() // scaleQuantize
              : color.quantiles ? color.quantiles() // scaleQuantile
                : color.domain(); // scaleThreshold

          const thresholdFormat
            = tickFormat === undefined ? d => d
              : typeof tickFormat === "string" ? d3.format(tickFormat)
                : tickFormat;

          x = d3.scaleLinear()
            .domain([-1, color.range().length - 1])
            .rangeRound([marginLeft, width - marginRight]);

          svg.append("g")
            .selectAll("rect")
            .data(color.range())
            .join("rect")
            .attr("x", (d, i) => x(i - 1))
            .attr("y", marginTop)
            .attr("width", (d, i) => x(i) - x(i - 1))
            .attr("height", height - marginTop - marginBottom)
            .attr("fill", d => d);

          tickValues = d3.range(thresholds.length);
          tickFormat = i => thresholdFormat(thresholds[i], i);
        }

        // Ordinal
        else {
          x = d3.scaleBand()
            .domain(color.domain())
            .rangeRound([marginLeft, width - marginRight]);

          svg.append("g")
            .selectAll("rect")
            .data(color.domain())
            .join("rect")
            .attr("x", x)
            .attr("y", marginTop)
            .attr("width", Math.max(0, x.bandwidth() - 1))
            .attr("height", height - marginTop - marginBottom)
            .attr("fill", color);

          tickAdjust = () => { };
        }

        svg.append("g")
          .attr("transform", `translate(0,${height - marginBottom})`)
          .call(d3.axisBottom(x)
            .ticks(ticks, typeof tickFormat === "string" ? tickFormat : undefined)
            .tickFormat(typeof tickFormat === "function" ? tickFormat : undefined)
            .tickSize(tickSize)
            .tickValues(tickValues))
          .call(tickAdjust)
          .call(g => g.select(".domain").remove())
          .call(g => g.append("text")
            .attr("x", marginLeft)
            .attr("y", marginTop + marginBottom - height - 6)
            .attr("fill", "currentColor")
            .attr("text-anchor", "start")
            .attr("font-weight", "bold")
            .attr("class", "title")
            .text(title));

        return svg.node();
      }

      let dataLegend = Legend(d3.scaleDivergingSqrt([], d3.interpolateRdBu), {
        title: "Sequece Data",
        tickFormat: "+%"
      })
      let parameterLegend = Legend(d3.scaleDivergingSqrt([], d3.interpolateBrBG), {
        title: "Parameter",
        tickFormat: "+%"
      })
      var drag = d3.drag()
        .on("drag", dragmove);

      function dragmove(event) {
        var x = event.x
        var y = event.y
        d3.select(this)
          .attr("transform", `translate(${x},${y})`)
      }
      let legendSvg = svg.append('g')
        .attr('transform', `translate(${20},${10})`)
        .attr('id', 'legend-g')
        .call(drag)
      let dataLegendSvg = legendSvg.append('g')
      let parameterLegendSvg = legendSvg.append('g')
        .attr('transform', `translate(${0},${30})`)
      dataLegendSvg.append(() => dataLegend)
      parameterLegendSvg.append(() => parameterLegend)


    },

    drawTokenize(svg, type, offsetX, offsetY, inputData, openStatus, allOpacity, highlightOpacity) {
      let edgeOpacity = 0.5
      let fontSize = 15
      // let unitLength = type == "encoder" ? 9 : 25
      let unitLength = 9
      let textHeight = 40
      let pieceWidth = 80
      let tokenWidth = 60
      let tokenHeight = 30
      let pieceHeight = 30
      let tokenGap = 15
      let processGap = 50
      let textLength = inputData.input.length
      let tokensLength = inputData.pieces.length
      let height = (tokenGap + tokenHeight) * (tokensLength + 1)
      let textWidth = (textLength * unitLength) > this.encoder.tokenize.input.length * 9 ? (textLength * unitLength) : this.encoder.tokenize.input.length * 9
      let width = textWidth + pieceWidth + tokenWidth + processGap * 3
      let nodeColor = ["#D8D8D8", "#D8D8D8", "#F5EFE6"]
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);

      let tokenizePart = svg.append('g')
        .attr('id', type + '-tokenize-g')

      // input text
      let textRect = tokenizePart.append('g')
        .attr('id', type + '-input-text')
        .attr('class', "tooltipTarget")
        .style('opacity', allOpacity)
        .attr('transform', `translate(${offsetX},${offsetY + height / 2})`);
      textRect.append('rect')
        .attr('class', 'node')
        .attr('width', textWidth)
        .attr('height', textHeight)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr('fill', nodeColor[0]);
      textRect.append('text')
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .attr("x", (textWidth) / 2)
        .attr("y", textHeight / 2)
        .attr("font-size", fontSize + 'px')
        .text(inputData.input == '' ? '<BOS>' : inputData.input);

      // d3.select('#tokenTooltip')
      //   .style('left', d3.select('#encoder-input-text').node().getBoundingClientRect().left + (textWidth) / 2 -document.getElementById('tokenTooltip').offsetWidth/2+ 'px')
      //   .style('top', d3.select('#encoder-input-text').node().getBoundingClientRect().top - textHeight/2- 180+ 'px');
      // d3.select("#tokenTooltip").text("woshiliuziao")
      //         let tooltip = textRect.append('Tooltip').attr('title','11111').        
      //           append('text')
      //         .attr('class', 'label')
      //         .attr("x", (textWidth) / 2)
      //         .attr("y", -textHeight / 2)
      //         .text("Input Text");


      textRect.append('text')
        .attr('class', 'label')
        .attr("x", (textWidth) / 2)
        .attr("y", -textHeight / 2)
        .text("Input Text");



      // word segmentations
      let piecesRect = tokenizePart.append('g')
        .attr('id', type + '-word-segmentations')
        .style('opacity', allOpacity)
        .attr('transform', `translate(${(textWidth) + processGap},${offsetY})`);
      let toolTip = piecesRect.append('g')
        .attr('id', type + '-word-segmentations-tooltip')
      for (let i = 0; i < tokensLength; i++) {
        let translateY = height / 2 + textHeight / 2 + (i - Math.round(tokensLength / 2)) * (tokenGap + tokenHeight)
        if (i == 0) {
          piecesRect.append('text')
            .attr('id', type + '-word-segmentations-label')
            .attr('class', 'label')
            .attr("x", pieceWidth / 2)
            .attr("y", translateY - 20)
            .text("Word Segmentations");
          toolTip.attr('transform', `translate(${-35},${translateY - 68})`)
          // d3.select('#wordSegTooltip')
          //   .style('left', d3.select('#encoder-word-segmentations').node().getBoundingClientRect().left +pieceWidth / 2+processGap-document.getElementById('wordSegTooltip').offsetWidth/2 + 'px')
          //   .style('top', d3.select('#encoder-word-segmentations').node().getBoundingClientRect().top+translateY - 40 - 180 + 'px');
        }
        let unitPiece = piecesRect.append('g')
          .attr("id", "piece-" + (i + 1))
          .attr('transform', `translate(0,${translateY})`);
        unitPiece.append('rect').attr('class', 'node')
          .attr('width', pieceWidth)
          .attr('height', pieceHeight)
          .attr("rx", 5)
          .attr("ry", 5)
          .attr('fill', nodeColor[1]);
        unitPiece.append('text')
          .style("text-anchor", "middle")
          .style("dominant-baseline", "middle")
          .attr("x", pieceWidth / 2)
          .attr("y", pieceHeight / 2)
          .attr("font-size", fontSize + 'px')
          .text(inputData.pieces[i]);
        let linkDataElement = [{
          source: {
            x: -processGap,
            y: (Math.round(tokensLength / 2) - i) * (tokenGap + tokenHeight),
          },
          target: {
            x: 0,
            y: pieceHeight / 2,
          },
        }]
        unitPiece.append('path')
          .attr('class', 'edge')
          .data(linkDataElement)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)');
      }

      d3.select('#' + type + '-word-segmentations-label')
        .on('mouseover', () => {
          toolTip.append('rect')
            .attr('tansform', `translate(-10)`)
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("width", 155)
            .attr("height", 35)
            .attr("fill", "rgb(245, 245, 245)")
            .attr('stroke', 'rgb(175, 175, 175)')
            .attr('stroke-width', 1)
            .style('stroke-dasharray', '5,3')
            .style('opacity', 0.8)
          toolTip.append('text')
            .selectAll('.tspan')
            .data(["Breaking text into individual", "word segmentations."])
            .enter().append('tspan')
            .attr("x", 5)
            .attr("dy", '1.3em')
            .attr('font-size', '11px')
            .attr('fill', '#4a4a4a')
            .text(d => d)
          // .text("Breaking text into individual word segmentations.")
        })
        .style('cursor', 'hand')
      d3.select('#' + type + '-word-segmentations-label')
        .on('mouseout', () => {
          d3.select('#' + type + '-word-segmentations-tooltip').selectAll('*').remove()
        })

      // word tokens
      let tokensRect = tokenizePart.append('g')
        .attr('id', type + '-word-tokens')
        .style('opacity', highlightOpacity)
        .attr('transform', `translate(${(textWidth) + pieceWidth + processGap * 2},${offsetY})`);
      let tokenToolTip = tokensRect.append('g')
        .attr('id', type + '-word-tokens-tooltip')
      for (let i = 0; i < tokensLength; i++) {
        let translateY = height / 2 + textHeight / 2 + (i - Math.round(tokensLength / 2)) * (tokenGap + tokenHeight)
        if (i == 0) {
          tokensRect.append('text')
            .attr('class', 'label')
            .attr('id', type + '-word-tokens-label')
            .attr("x", tokenWidth / 2)
            .attr("y", translateY - 20)
            .text("Word Tokens");
          tokenToolTip.attr('transform', `translate(${-17},${translateY - 68})`);
        }
        let unitToken = tokensRect.append('g')
          .attr("id", "token-" + (i + 1))
          .attr('transform', `translate(0,${translateY})`);
        unitToken.append('rect').attr('class', 'node')
          .attr("id", "token-rect-" + (i + 1))
          .attr('width', tokenWidth)
          .attr('height', tokenHeight)
          .style('opacity', highlightOpacity)
          .attr("rx", 5)
          .attr("ry", 5)
          .attr('fill', nodeColor[2]);
        unitToken.append('text')
          .style("text-anchor", "middle")
          .style('opacity', highlightOpacity)
          .style("dominant-baseline", "middle")
          .attr("x", tokenWidth / 2)
          .attr("y", tokenHeight / 2)
          .attr("font-size", fontSize + 'px')
          .text(inputData.output[i]);
        let linkDataElement1 = [{
          source: {
            x: -processGap,
            y: tokenHeight / 2,
          },
          target: {
            x: 0,
            y: tokenHeight / 2,
          },
        },]
        let linkDataElement2 = openStatus == false ? [{
          source: {
            x: tokenWidth,
            y: tokenHeight / 2,
          },
          target: {
            x: tokenWidth + processGap,
            y: tokenHeight / 2,
          },
        },] : []
        unitToken.append('path')
          .attr('class', 'edge')
          .data(linkDataElement1)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)');
        unitToken.append('path')
          .attr('class', 'edge')
          .data(linkDataElement2)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)');

      }
      d3.select('#' + type + '-word-tokens-label')
        .on('mouseover', () => {
          tokenToolTip.append('rect')
            .attr('tansform', `translate(-10)`)
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("width", 100)
            .attr("height", 35)
            .attr("fill", "rgb(245, 245, 245)")
            .attr('stroke', 'rgb(175, 175, 175)')
            .attr('stroke-width', 1)
            .style('stroke-dasharray', '5,3')
            .style('opacity', 0.8)
          tokenToolTip.append('text')
            .selectAll('.tspan')
            .data(["Index in word", "token dictionary."])
            .enter().append('tspan')
            .attr("x", 5)
            .attr("dy", '1.3em')
            .attr('font-size', '11px')
            .attr('fill', '#4a4a4a')
            .text(d => d)
          // .text("Breaking text into individual word segmentations.")
        })
        .style('cursor', 'hand')
      d3.select('#' + type + '-word-tokens-label')
        .on('mouseout', () => {
          d3.select('#' + type + '-word-tokens-tooltip').selectAll('*').remove()
        })

      let nextOffsetY = height / 2 + textHeight / 2 + (0 - Math.round(tokensLength / 2)) * (tokenGap + tokenHeight) - 2
      return [width, nextOffsetY, height + offsetY]

    },

    drawEmbedding(svg, type, offsetX, offsetY, inputData, openStatus, encoderTotalDataRange, allOpacity, highlightOpacity) {
      let textOffset = offsetY - 20
      let tokensLength = inputData.input.length
      let tokenGap = 10
      let processGap = 50
      let embeddingsDataRange = encoderTotalDataRange
      let colorScale = d3.interpolateRdBu;
      let edgeOpacity = 0.5;
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);

      let embeddingPart = svg.append('g')
        .attr('id', type + '-embedding-g')

      // 绘制 embeddings
      let xSize = 325;
      let ySize = 240;
      let embeddingsGridGroupX = offsetX;
      let embeddingsGridGroupY = offsetY;
      let embeddingsConstraintGridCellWidth = getVisualizationSizeConstraint(inputData.output[0].length, 'x', xSize, ySize, 40);
      // let embeddingsConstraintGridCellHeight = getVisualizationSizeConstraint(inputData.output.length, 'y', xSize, ySize, 40);
      let embeddingsConstraintGridCellHeight = 35
      let embeddingsGridData = getGapGridData(inputData.output, embeddingsConstraintGridCellWidth, embeddingsConstraintGridCellHeight, tokenGap);
      let embeddingsGridGroup = embeddingPart.append("g")
        .style('opacity', highlightOpacity)
        .attr("class", "grid")
        .attr("transform", `translate(${embeddingsGridGroupX},${embeddingsGridGroupY})`);
      let embeddingsGridRow = embeddingsGridGroup.selectAll(".row")  // 绘制每一行
        .data(embeddingsGridData).enter().append('g').attr('class', 'row');
      embeddingsGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('fill', d => {
          let normlizedVal = (d.text - embeddingsDataRange.min) / (embeddingsDataRange.max - embeddingsDataRange.min);
          return colorScale(normlizedVal);
        });
      let embeddingsTotalGridWidth = embeddingsConstraintGridCellWidth * inputData.output[0].length;
      // let embeddingsTotalGridHeight = (embeddingsConstraintGridCellHeight + tokenGap) * inputData.output.length;
      let embeddingsGridText = embeddingPart.append('text').attr("text-anchor", "middle");
      embeddingsGridText
        .attr('transform', `translate(${embeddingsGridGroupX + embeddingsTotalGridWidth / 2},${textOffset})`)
        .attr('id', type + '-embedding-label')
        .attr('class', 'label')
        .text(`embeddings (${inputData.output.length},${inputData.output[0].length})`);
      let embeddingToolTip = embeddingPart.append('g')
        .attr('id', type + '-embedding-tooltip')
        .attr('transform', `translate(${embeddingsGridGroupX + embeddingsTotalGridWidth / 2 - 70},${textOffset - 45})`)
      d3.select('#' + type + '-embedding-label')
        .on('mouseover', () => {
          embeddingToolTip.append('rect')
            .attr('tansform', `translate(-10)`)
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("width", 135)
            .attr("height", 35)
            .attr("fill", "rgb(245, 245, 245)")
            .attr('stroke', 'rgb(175, 175, 175)')
            .attr('stroke-width', 1)
            .style('stroke-dasharray', '5,3')
            .style('opacity', 0.8)
          embeddingToolTip.append('text')
            .selectAll('.tspan')
            .data(["Mapping words to dense", "vector representations."])
            .enter().append('tspan')
            .attr("x", 5)
            .attr("dy", '1.3em')
            .attr('font-size', '11px')
            .attr('fill', '#4a4a4a')
            .text(d => d)
          // .text("Breaking text into individual word segmentations.")
        })
        .style('cursor', 'hand')
      d3.select('#' + type + '-embedding-label')
        .on('mouseout', () => {
          d3.select('#' + type + '-embedding-tooltip').selectAll('*').remove()
        })
      if (openStatus == 'closed') {
        let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
        let instructiveArrowWidth = 30
        let instructiveArrowHeight = 30
        let clickIcon = require("../../src/assets/click.svg")
        let clickIconWidth = 13
        let clickIconHeight = 13
        let instructiveArrowOffsetX = embeddingsGridGroupX + embeddingsTotalGridWidth - 80
        let instructiveArrowOffsetY = textOffset - 5
        let instructiveText = embeddingPart.append('g')
          .attr('transform', `translate(${instructiveArrowOffsetX},${instructiveArrowOffsetY})`)
        instructiveText.append('svg:image')
          .attr('xlink:href', instructiveArrow)
          .attr("width", instructiveArrowWidth)
          .attr("height", instructiveArrowHeight)
        instructiveText.append('svg:image')
          .attr('transform', `translate(${25},${-10})`)
          .attr('xlink:href', clickIcon)
          .attr("width", clickIconWidth)
          .attr("height", clickIconHeight)
        instructiveText.append('text')
          .text('Click')
          .attr("font-size", '10px')
          .attr("font-weight", 'bold')
          .attr("font-style", 'italic')
          .attr("fill", '#4a4a4a')
          .attr("x", 40)
          .attr("y", 0)
        instructiveText.append('text')
          .text('to learn')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 70)
          .attr("y", 0)
        instructiveText.append('text')
          .text('how to get embeddings!')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 35)
          .attr("y", 13)
      }


      let linkData = []
      for (let i = 0; i < tokensLength; i++) {
        let embeddingLinkData = {
          source: {
            x: embeddingsGridGroupX + embeddingsGridData[i][0].x + xSize,
            y: embeddingsGridGroupY + embeddingsGridData[i][0].y + embeddingsGridData[i][0].height / 2,
          },
          target: {
            x: embeddingsGridGroupX + embeddingsGridData[i][0].x + xSize + processGap,
            y: embeddingsGridGroupY + embeddingsGridData[i][0].y + embeddingsGridData[i][0].height / 2,
          },
          class: 'embedding-link',
          id: (i + 1)
        }
        linkData.push(embeddingLinkData)
      }
      let edgeGroup = embeddingPart.append("g")
        .style('opacity', allOpacity)
        .attr("class", "edge-group");
      edgeGroup.selectAll("path.edge").data(linkData).enter().append('path')
        .attr('id', d => d.id != undefined ? d.id : null)
        .attr('class', d => d.class != undefined ? d.class : null)
        .attr('d', d => linkGen({ source: d.source, target: d.target }))
        .style('fill', 'none')
        .style('stroke-width', '2px')
        .style('opacity', edgeOpacity)
        .style('stroke', 'rgb(175, 175, 175)');
      var self = this
      // 添加点击事件--openEmbedding
      embeddingsGridGroup.on('click', function () {
        self.status = 'openEmbedding'
        self.openEmbedding()
      })
        .style('cursor', 'hand')

      let width = processGap + xSize
      return [width + offsetX, offsetY]
    },

    drawPE(svg, type, offsetX, offsetY, inputData, openStatus, encoderTotalDataRange, allOpacity) {
      let textOffset = offsetY - 20
      let tokensLength = inputData.input.length
      let tokenGap = 10
      let processGap = 50
      let pesDataRange = encoderTotalDataRange
      let colorScale = d3.interpolateRdBu;
      let edgeOpacity = 0.5;
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);

      let pePart = svg.append('g')
        .attr('id', type + '-pe-g')
        .style('opacity', allOpacity)
      // 绘制 embeddings after PE
      let xSize = 325;
      let ySize = 240;
      let pesGridGroupX = offsetX;
      let pesGridGroupY = offsetY;
      let pesConstraintGridCellWidth = getVisualizationSizeConstraint(inputData.output[0].length, 'x', xSize, ySize, 40);
      // let pesConstraintGridCellHeight = getVisualizationSizeConstraint(inputData.output.length, 'y', xSize, ySize, 40);
      let pesConstraintGridCellHeight = 35
      let pesGridData = getGapGridData(inputData.output, pesConstraintGridCellWidth, pesConstraintGridCellHeight, tokenGap);
      let pesGridGroup = pePart.append("g").attr("class", "grid").attr("transform", `translate(${pesGridGroupX},${pesGridGroupY})`);
      let pesGridRow = pesGridGroup.selectAll(".row")  // 绘制每一行
        .data(pesGridData).enter().append('g').attr('class', 'row');
      pesGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('fill', d => {
          let normlizedVal = (d.text - pesDataRange.min) / (pesDataRange.max - pesDataRange.min);
          return colorScale(normlizedVal);
        });
      let pesTotalGridWidth = pesConstraintGridCellWidth * inputData.output[0].length;
      // let embeddingsTotalGridHeight = (embeddingsConstraintGridCellHeight + tokenGap) * inputData.output.length;
      let pesGridText = pePart.append('text').attr("text-anchor", "middle");
      pesGridText
        .attr('transform', `translate(${pesGridGroupX + pesTotalGridWidth / 2},${textOffset})`)
        .attr('id', type + '-pe-label')
        .attr('class', 'label')
        .text(`after positional encoding (${inputData.output.length},${inputData.output[0].length})`);
      let peToolTip = pePart.append('g')
        .attr('id', type + '-pe-tooltip')
        .attr('transform', `translate(${pesGridGroupX + pesTotalGridWidth / 2 - 70},${textOffset - 45})`)
      d3.select('#' + type + '-pe-label')
        .on('mouseover', () => {
          peToolTip.append('rect')
            .attr('tansform', `translate(-10)`)
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("width", 145)
            .attr("height", 35)
            .attr("fill", "rgb(245, 245, 245)")
            .attr('stroke', 'rgb(175, 175, 175)')
            .attr('stroke-width', 1)
            .style('stroke-dasharray', '5,3')
            .style('opacity', 0.8)
          peToolTip.append('text')
            .selectAll('.tspan')
            .data(["Add positional information", "to original embeddings."])
            .enter().append('tspan')
            .attr("x", 5)
            .attr("dy", '1.3em')
            .attr('font-size', '11px')
            .attr('fill', '#4a4a4a')
            .text(d => d)
          // .text("Breaking text into individual word segmentations.")
        })
        .style('cursor', 'hand')
      d3.select('#' + type + '-pe-label')
        .on('mouseout', () => {
          d3.select('#' + type + '-pe-tooltip').selectAll('*').remove()
        })

      if (openStatus == 'closed') {
        let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
        let instructiveArrowWidth = 30
        let instructiveArrowHeight = 30
        let clickIcon = require("../../src/assets/click.svg")
        let clickIconWidth = 13
        let clickIconHeight = 13
        let instructiveArrowOffsetX = pesGridGroupX + pesTotalGridWidth - 75
        let instructiveArrowOffsetY = textOffset - 5
        let instructiveText = pePart.append('g')
          .attr('transform', `translate(${instructiveArrowOffsetX},${instructiveArrowOffsetY})`)
        instructiveText.append('svg:image')
          .attr('xlink:href', instructiveArrow)
          .attr("width", instructiveArrowWidth)
          .attr("height", instructiveArrowHeight)
        instructiveText.append('svg:image')
          .attr('transform', `translate(${25},${-10})`)
          .attr('xlink:href', clickIcon)
          .attr("width", clickIconWidth)
          .attr("height", clickIconHeight)
        instructiveText.append('text')
          .text('Click')
          .attr("font-size", '10px')
          .attr("font-weight", 'bold')
          .attr("font-style", 'italic')
          .attr("fill", '#4a4a4a')
          .attr("x", 40)
          .attr("y", 0)
        instructiveText.append('text')
          .text('to learn')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 70)
          .attr("y", 0)
        instructiveText.append('text')
          .text('positional encoding!')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 33)
          .attr("y", 13)
      }

      let linkData = []
      for (let i = 0; i < tokensLength; i++) {
        let peLinkData = {
          source: {
            x: pesGridGroupX + pesGridData[i][0].x + xSize,
            y: pesGridGroupY + pesGridData[i][0].y + pesGridData[i][0].height / 2,
          },
          target: {
            x: pesGridGroupX + pesGridData[i][0].x + xSize + processGap,
            y: tokenGap + offsetY,
          },
          class: 'pe-link',
          id: (i + 1)
        }
        linkData.push(peLinkData)
      }
      let edgeGroup = pePart.append("g").attr("class", "edge-group");
      edgeGroup.selectAll("path.edge").data(linkData).enter().append('path')
        .attr('id', d => d.id != undefined ? d.id : null)
        .attr('class', d => d.class != undefined ? d.class : null)
        .attr('d', d => linkGen({ source: d.source, target: d.target }))
        .style('fill', 'none')
        .style('stroke-width', '2px')
        .style('opacity', edgeOpacity)
        .style('stroke', 'rgb(175, 175, 175)');

      var self = this
      // 添加点击事件--openPE
      pesGridGroup.on('click', function () {
        self.$emit('getParams', 'encoder-PE')
        self.status = 'openPE'
        self.$nextTick(() => {
          self.openPE(Object(self.params));
        })
      })
        .style('cursor', 'hand')
      let width = processGap + xSize
      return [width + offsetX, offsetY]

    },

    drawCoders(svg, openDetailedCoderSvg, type, offsetX, offsetY, blockColor, detailedCoderSvg, allOpacity) {
      let self = this
      let tokenGap = 23
      let processGap = 50
      let nodeWidth = 100
      let nodeHeight = 35
      let textOffset = 15
      let linePath = d3.line();
      let width = processGap + nodeWidth

      let coderPart = svg.append('g')
        .attr('id', type + '-blocks-g')
        .attr('transform', `translate(${offsetX},${offsetY})`)
        .style('opacity', allOpacity)
      detailedCoderSvg.style('opacity', allOpacity)
      coderPart.append('text')
        .attr('transform', `translate(${nodeWidth / 2},${-textOffset * 4})`)
        .style('text-anchor', 'middle')
        .style('font-size', '14px')
        .attr("fill", '#4a4a4a')
        .attr('class', 'label')
        .selectAll('.tspan')
        .data([type, `blocks`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);
      if (type == 'encoder') {
        let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
        let instructiveArrowWidth = 30
        let instructiveArrowHeight = 30
        let instructiveArrowOffsetX = nodeWidth - 5
        let instructiveArrowOffsetY = -textOffset * 2
        let instructiveText = coderPart.append('g')
          .attr('transform', `translate(${instructiveArrowOffsetX},${instructiveArrowOffsetY})`)
          .attr('id', "instructiveSvg")
          .attr('opacity', 1)
        instructiveText.append('svg:image')
          .attr('xlink:href', instructiveArrow)
          .attr("width", instructiveArrowWidth)
          .attr("height", instructiveArrowHeight)
        instructiveText.append('text')
          .text('Hover over')
          .attr("font-size", '10px')
          .attr("font-weight", 'bold')
          .attr("font-style", 'italic')
          .attr("fill", '#4a4a4a')
          .attr("x", 35)
          .attr("y", 0)
        instructiveText.append('text')
          .text('to explore each block!')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 33)
          .attr("y", 13)
      }

      if (type == 'encoder') {
        drawDetailedEncoder(detailedCoderSvg, width + offsetX + processGap, offsetY + (nodeHeight + tokenGap), 1)
      }
      drawArrow(coderPart)

      for (let i = 0; i < 6; i++) {
        let translateY = (nodeHeight + tokenGap) * i
        let unitCoder = coderPart.append('g')
          .attr("id", type + '-block-' + (i + 1))
          .attr('transform', `translate(0,${translateY})`)
        unitCoder.append('rect')
          .attr('id', type + '-block-' + (i + 1))
          .attr("class", "node")
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", nodeWidth)
          .attr("height", nodeHeight)
          .attr("fill", blockColor)
        unitCoder.append('text')
          .style("text-anchor", "middle")
          .style("dominant-baseline", "middle")
          .attr("x", nodeWidth / 2)
          .attr("y", nodeHeight / 2)
          .text(type + ' #' + (i + 1))
          .attr("class", "text")
        let unitLine = []
        if (i == 5 && type == 'decoder') {
          unitLine = []
        } else {
          unitLine = [[nodeWidth / 2, nodeHeight], [nodeWidth / 2, nodeHeight + tokenGap]]
        }
        unitCoder
          .append('path')
          .attr('d', linePath(unitLine))
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 3)
          .attr('marker-end', "url(#arrow)");
        // 添加交互，点击获得detailed coder
        unitCoder.on('mouseover', function (event) {
          if (event.srcElement.id.toString().split('-')[0] == 'encoder') {
            d3.select("#detailedcoder-g").selectAll('*').remove()
            d3.select("#instructiveSvg").attr('opacity', 1)
            drawDetailedEncoder(detailedCoderSvg, width + offsetX + processGap, offsetY + (nodeHeight + tokenGap), event.srcElement.id.toString().split('-')[2])
          } else if (event.srcElement.id.toString().split('-')[0] == 'decoder') {
            d3.select("#detailedcoder-g").selectAll('*').remove()
            d3.select("#instructiveSvg").attr('opacity', 0)
            drawDetailedDecoder(detailedCoderSvg, width + offsetX + processGap, offsetY + (nodeHeight + tokenGap) - 30, event.srcElement.id.toString().split('-')[2])
          }
        })
          .style('cursor', 'hand')

        unitCoder.on('click', function (event) {
          openDetailedCoderSvg.selectAll('*').remove()
          if (event.srcElement.id.toString().split('-')[0] == 'encoder') {
            self.status = 'openEncoderBlock'
            self.openEncoderBlock(openDetailedCoderSvg, event.srcElement.id.toString().split('-')[2], 0, 'self-attention')
          } else if (event.srcElement.id.toString().split('-')[0] == 'decoder') {
            self.status = 'openDecoderBlock'
            self.openDecoderBlock(openDetailedCoderSvg, event.srcElement.id.toString().split('-')[2], 0, 'self-attention')
          }
        })
          .style('cursor', 'hand')
      }
      let lastCoderOffsetX = nodeWidth + processGap * 2
      let lastCoderOffsetY = (nodeHeight + tokenGap) * 5


      function drawDetailedEncoder(svg, offsetX, offsetY, blockNum) {
        let detailedEncoderWidth = 450
        let detailedEncoderHeight = 420
        let textOffsetX = 35
        let textOffsetY = 15
        let attentionOffsetX = 25
        let attentionOffsetY = 25
        let attentionWidth = 400
        let attentionHeight = 152
        let processGap = 20
        let addOffsetX_1 = attentionOffsetX + attentionWidth / 2
        let addOffsetY_1 = attentionOffsetY + attentionHeight + processGap
        let addHeight = 10
        let layerNormWidth = 190
        let layerNormHeight = 35
        let layerNormOffsetX_1 = attentionOffsetX + (attentionWidth - layerNormWidth) / 2
        let layerNormOffsetY_1 = addOffsetY_1 + addHeight + processGap
        let ffnWidth = 100
        let ffnHeight = 15
        let ffnOffsetX = attentionOffsetX + (attentionWidth - ffnWidth) / 2
        let ffnOffsetY = layerNormOffsetY_1 + layerNormHeight + processGap
        let addOffsetX_2 = attentionOffsetX + attentionWidth / 2
        let addOffsetY_2 = ffnOffsetY + ffnHeight + processGap
        let layerNormOffsetX_2 = attentionOffsetX + (attentionWidth - layerNormWidth) / 2
        let layerNormOffsetY_2 = addOffsetY_2 + addHeight + processGap
        let nextBlock = blockNum == 6 ? 'decoder' : 'encoder'
        let nextBlockOffsetX = detailedEncoderWidth / 2
        let nextBlockOffsetY = layerNormOffsetY_2 + layerNormHeight + processGap * 1.2
        let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);
        let linePath = d3.line();
        let edgeOpacity = 0.5;

        let detailedEncoderPart = svg.append('g')
          .attr('id', 'encoder-block-' + blockNum + '-g')
          .attr('transform', `translate(${offsetX},${offsetY - 20})`)
        detailedEncoderPart.append('rect')
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", detailedEncoderWidth)
          .attr("height", detailedEncoderHeight)
          // .attr("fill", "rgb(240, 239, 239)")
          .attr("fill", "rgb(255, 255, 255)")
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 2)
        let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
        let instructiveArrowWidth = 30
        let instructiveArrowHeight = 30
        let clickIcon = require("../../src/assets/click.svg")
        let clickIconWidth = 13
        let clickIconHeight = 13
        let instructiveArrowOffsetX = detailedEncoderWidth - 120
        let instructiveArrowOffsetY = detailedEncoderHeight
        let instructiveText = detailedEncoderPart.append('g')
          .attr('transform', `translate(${instructiveArrowOffsetX},${instructiveArrowOffsetY})`)
          .attr('id', "instructiveSvg")
          .attr('opacity', 1)
        instructiveText.append('svg:image')
          .attr('xlink:href', instructiveArrow)
          .attr("width", instructiveArrowWidth)
          .attr("height", instructiveArrowHeight)
          .attr('transform', 'rotate(50)')
        instructiveText.append('svg:image')
          .attr('transform', `translate(${20},${10})`)
          .attr('xlink:href', clickIcon)
          .attr("width", clickIconWidth)
          .attr("height", clickIconHeight)
        instructiveText.append('text')
          .text('Click')
          .attr("font-size", '10px')
          .attr("font-weight", 'bold')
          .attr("font-style", 'italic')
          .attr("fill", '#4a4a4a')
          .attr("x", 35)
          .attr("y", 20)
        instructiveText.append('text')
          .text('to explore')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 65)
          .attr("y", 20)
        instructiveText.append('text')
          .text('each layer operation!')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 25)
          .attr("y", 33)

        detailedEncoderPart.append('text')
          .attr('class', 'label')
          .attr("x", textOffsetX * 2)
          .attr("y", textOffsetY)
          .text('detailed encoder #' + blockNum);
        detailedEncoderPart.append('path')
          .attr('d', linePath([[-processGap * 2.5 - 3, -5 + (nodeHeight + tokenGap) * (blockNum - 1)], [1, 1]]))
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', 5)
        detailedEncoderPart.append('path')
          .attr('d', linePath([[-processGap * 2.5 - 3, -10 + nodeHeight + (nodeHeight + tokenGap) * (blockNum - 1)], [1, detailedEncoderHeight - 1]]))
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', 5)


        drawAttention(detailedEncoderPart, blockNum, 'encoder', 'self-attention', attentionOffsetX, attentionOffsetY, attentionWidth, attentionHeight)
        drawAdd(detailedEncoderPart, addOffsetX_1, addOffsetY_1, addHeight, "word vectors", "attention scores")
        drawLayerNorm(detailedEncoderPart, blockNum, 'encoder', 0, layerNormOffsetX_1, layerNormOffsetY_1, layerNormWidth, layerNormHeight)

        drawFeedForwardNetwork(detailedEncoderPart, blockNum, 'encoder', ffnOffsetX, ffnOffsetY, ffnWidth, ffnHeight)
        drawAdd(detailedEncoderPart, addOffsetX_2, addOffsetY_2, addHeight, "layer normalizations", "feed-forward network results")
        drawLayerNorm(detailedEncoderPart, blockNum, 'encoder', 1, layerNormOffsetX_2, layerNormOffsetY_2, layerNormWidth, layerNormHeight)
        detailedEncoderPart.append('text')
          .attr('font-size', '12px')
          .attr('font-weight', 'bold')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', ' rgb(175, 175, 175)')
          .attr("x", nextBlockOffsetX)
          .attr("y", nextBlockOffsetY)
          .text('to next ' + nextBlock + ' block');

        drawArrow(detailedEncoderPart)
        let linkData = [
          {
            source: { x: attentionOffsetX + attentionWidth / 2, y: attentionOffsetY + attentionHeight },
            target: { x: attentionOffsetX + attentionWidth / 2, y: attentionOffsetY + attentionHeight + processGap - addHeight / 2 }
          },
          {
            source: { x: attentionOffsetX + attentionWidth / 2, y: addOffsetY_1 + addHeight * 1.5 },
            target: { x: attentionOffsetX + attentionWidth / 2, y: addOffsetY_1 + addHeight + processGap }
          },
          {
            source: { x: attentionOffsetX + attentionWidth / 2, y: layerNormOffsetY_1 + layerNormHeight },
            target: { x: attentionOffsetX + attentionWidth / 2, y: layerNormOffsetY_1 + layerNormHeight + processGap }
          },
          {
            source: { x: attentionOffsetX + attentionWidth / 2, y: ffnOffsetY + ffnHeight },
            target: { x: attentionOffsetX + attentionWidth / 2, y: ffnOffsetY + ffnHeight + processGap - addHeight / 2 }
          },
          {
            source: { x: attentionOffsetX + attentionWidth / 2, y: addOffsetY_2 + addHeight * 1.5 },
            target: { x: attentionOffsetX + attentionWidth / 2, y: addOffsetY_2 + addHeight + processGap }
          },
          {
            source: { x: attentionOffsetX + attentionWidth / 2, y: layerNormOffsetY_2 + layerNormHeight },
            target: { x: attentionOffsetX + attentionWidth / 2, y: layerNormOffsetY_2 + layerNormHeight + processGap * 0.8 }
          },
        ]
        detailedEncoderPart
          .append('g')
          .attr('id', 'encoderblock-path')
          .selectAll('path')
          .attr('class', 'edge')
          .data(linkData)
          .enter()
          .append('path')
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)')
          .attr('marker-end', "url(#arrow)")


      }

      function drawDetailedDecoder(svg, offsetX, offsetY, blockNum) {
        let detailedDecoderWidth = 450
        let detailedDecoderHeight = 670
        let textOffsetX = 35
        let textOffsetY = 15
        let attentionOffsetX_1 = 25
        let attentionOffsetY_1 = 25
        let attentionWidth = 400
        let attentionHeight = 152
        let processGap = 20
        let addOffsetX_1 = attentionOffsetX_1 + attentionWidth / 2
        let addOffsetY_1 = attentionOffsetY_1 + attentionHeight + processGap
        let addHeight = 10
        let layerNormWidth = 190
        let layerNormHeight = 35
        let layerNormOffsetX_1 = attentionOffsetX_1 + (attentionWidth - layerNormWidth) / 2
        let layerNormOffsetY_1 = addOffsetY_1 + addHeight + processGap

        let attentionOffsetX_2 = attentionOffsetX_1
        let attentionOffsetY_2 = layerNormOffsetY_1 + layerNormHeight + processGap
        let addOffsetX_2 = attentionOffsetX_2 + attentionWidth / 2
        let addOffsetY_2 = attentionOffsetY_2 + attentionHeight + processGap
        let layerNormOffsetX_2 = attentionOffsetX_2 + (attentionWidth - layerNormWidth) / 2
        let layerNormOffsetY_2 = addOffsetY_2 + addHeight + processGap

        let ffnWidth = 100
        let ffnHeight = 15
        let ffnOffsetX = attentionOffsetX_2 + (attentionWidth - ffnWidth) / 2
        let ffnOffsetY = layerNormOffsetY_2 + layerNormHeight + processGap
        let addOffsetX_3 = attentionOffsetX_2 + attentionWidth / 2
        let addOffsetY_3 = ffnOffsetY + ffnHeight + processGap
        let layerNormOffsetX_3 = attentionOffsetX_2 + (attentionWidth - layerNormWidth) / 2
        let layerNormOffsetY_3 = addOffsetY_3 + addHeight + processGap
        let nextBlock = blockNum == 6 ? 'decoder' : 'encoder'
        let nextBlockOffsetX = detailedDecoderWidth / 2
        let nextBlockOffsetY = layerNormOffsetY_3 + layerNormHeight + processGap * 1.2
        let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);
        let linePath = d3.line();
        let edgeOpacity = 0.5;

        let detailedDecoderPart = svg.append('g')
          .attr('id', 'decoder-block-' + blockNum + '-g')
          .attr('transform', `translate(${offsetX},${offsetY - 20})`)
        detailedDecoderPart.append('rect')
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", detailedDecoderWidth)
          .attr("height", detailedDecoderHeight)
          // .attr("fill", "rgb(240, 239, 239)")
          .attr("fill", "rgb(255, 255, 255)")
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 2)
        detailedDecoderPart.append('text')
          .attr('class', 'label')
          .attr("x", textOffsetX * 2)
          .attr("y", textOffsetY)
          .text('detailed decoder #' + blockNum);
        let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
        let instructiveArrowWidth = 30
        let instructiveArrowHeight = 30
        let clickIcon = require("../../src/assets/click.svg")
        let clickIconWidth = 13
        let clickIconHeight = 13
        let instructiveArrowOffsetX = detailedDecoderWidth - 120
        let instructiveArrowOffsetY = detailedDecoderHeight
        let instructiveText = detailedDecoderPart.append('g')
          .attr('transform', `translate(${instructiveArrowOffsetX},${instructiveArrowOffsetY})`)
          .attr('id', "instructiveSvg")
          .attr('opacity', 1)
        instructiveText.append('svg:image')
          .attr('xlink:href', instructiveArrow)
          .attr("width", instructiveArrowWidth)
          .attr("height", instructiveArrowHeight)
          .attr('transform', 'rotate(50)')
        instructiveText.append('svg:image')
          .attr('transform', `translate(${20},${10})`)
          .attr('xlink:href', clickIcon)
          .attr("width", clickIconWidth)
          .attr("height", clickIconHeight)
        instructiveText.append('text')
          .text('Click')
          .attr("font-size", '10px')
          .attr("font-weight", 'bold')
          .attr("font-style", 'italic')
          .attr("fill", '#4a4a4a')
          .attr("x", 35)
          .attr("y", 20)
        instructiveText.append('text')
          .text('to explore')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 65)
          .attr("y", 20)
        instructiveText.append('text')
          .text('each layer operation!')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", 25)
          .attr("y", 33)
        detailedDecoderPart.append('path')
          .attr('d', linePath([[-processGap * 2.5 - 3, 450 + (nodeHeight + tokenGap) * (blockNum - 1)], [1, 1]]))
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', 5)
        detailedDecoderPart.append('path')
          .attr('d', linePath([[-processGap * 2.5 - 3, 450 + nodeHeight + (nodeHeight + tokenGap) * (blockNum - 1)], [1, detailedDecoderHeight - 1]]))
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', 5)

        drawAttention(detailedDecoderPart, blockNum, 'decoder', 'masked self-attention', attentionOffsetX_1, attentionOffsetY_1, attentionWidth, attentionHeight)
        drawAdd(detailedDecoderPart, addOffsetX_1, addOffsetY_1, addHeight, "word vectors", "attention scores")
        drawLayerNorm(detailedDecoderPart, blockNum, 'decoder', 0, layerNormOffsetX_1, layerNormOffsetY_1, layerNormWidth, layerNormHeight)
        drawAttention(detailedDecoderPart, blockNum, 'decoder', 'cross-attention', attentionOffsetX_2, attentionOffsetY_2, attentionWidth, attentionHeight)
        drawAdd(detailedDecoderPart, addOffsetX_2, addOffsetY_2, addHeight, "layer normalizations", "attention scores")
        drawLayerNorm(detailedDecoderPart, blockNum, 'decoder', 1, layerNormOffsetX_2, layerNormOffsetY_2, layerNormWidth, layerNormHeight)
        drawFeedForwardNetwork(detailedDecoderPart, blockNum, 'decoder', ffnOffsetX, ffnOffsetY, ffnWidth, ffnHeight)
        drawAdd(detailedDecoderPart, addOffsetX_3, addOffsetY_3, addHeight, "layer normalizations", "feed-forward network results")
        drawLayerNorm(detailedDecoderPart, blockNum, 'decoder', 2, layerNormOffsetX_3, layerNormOffsetY_3, layerNormWidth, layerNormHeight)

        detailedDecoderPart.append('text')
          .attr('font-size', '12px')
          .attr('font-weight', 'bold')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', ' rgb(175, 175, 175)')
          .attr("x", nextBlockOffsetX)
          .attr("y", nextBlockOffsetY)
          .text('to next ' + nextBlock + ' block');

        drawArrow(detailedDecoderPart)
        let linkData = [
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: attentionOffsetY_1 + attentionHeight },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: attentionOffsetY_1 + attentionHeight + processGap - addHeight / 2 }
          },
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: attentionOffsetY_2 + attentionHeight },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: attentionOffsetY_2 + attentionHeight + processGap - addHeight / 2 }
          },
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: addOffsetY_1 + addHeight * 1.5 },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: addOffsetY_1 + addHeight + processGap }
          },
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: layerNormOffsetY_1 + layerNormHeight },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: layerNormOffsetY_1 + layerNormHeight + processGap }
          },
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: layerNormOffsetY_2 + layerNormHeight },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: layerNormOffsetY_2 + layerNormHeight + processGap }
          },
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: layerNormOffsetY_3 + layerNormHeight },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: layerNormOffsetY_3 + layerNormHeight + processGap * 0.8 }
          },
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: ffnOffsetY + ffnHeight },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: ffnOffsetY + ffnHeight + processGap - addHeight / 2 }
          },
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: addOffsetY_2 + addHeight * 1.5 },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: addOffsetY_2 + addHeight + processGap }
          },
          {
            source: { x: attentionOffsetX_1 + attentionWidth / 2, y: addOffsetY_3 + addHeight * 1.5 },
            target: { x: attentionOffsetX_1 + attentionWidth / 2, y: addOffsetY_3 + addHeight + processGap }
          },
        ]
        detailedDecoderPart
          .append('g')
          .attr('id', 'decoderblock-path')
          .selectAll('path')
          .attr('class', 'edge')
          .data(linkData)
          .enter()
          .append('path')
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)')
          .attr('marker-end', "url(#arrow)")
      }

      function drawAttention(svg, blockNum, block, type, offsetX, offsetY, attentionWidth, attentionHeight) {
        let wordVectorWidth = 15
        let wordVectorHeight = 80
        let wordVectorOffsetX = 15
        let wordVectorOffsetY = 45
        let attentionHeadWidth = 100
        let attentionHeadHeight = 15
        let attentionHeadOffsetX = type == 'self-attention' || type == 'cross-attention' ? 150 : 150
        let attentionHeadOffsetY = wordVectorOffsetY
        let openAttentionHeadWidth = type == 'self-attention' || type == 'cross-attention' ? 190 : 250
        let textOffsetX = type == 'self-attention' || type == 'cross-attention' ? 45 : 40
        let textOffsetY = 10
        let processGap = type == 'self-attention' || type == 'cross-attention' ? 28 : 15
        let blockGap = 15
        let attentionScoreOffsetX = attentionWidth - wordVectorOffsetX - wordVectorWidth * 2 - processGap
        let attentionScoreOffsetY = wordVectorOffsetY
        let linePath = d3.line();
        let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);
        let edgeOpacity = 0.5;

        let attentionPart = svg.append('g')
          .attr('id', type + '-g')
          .attr('transform', `translate(${offsetX},${offsetY})`)

        attentionPart.append('rect')
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", attentionWidth)
          .attr("height", attentionHeight)
          .attr("fill", "#F8F4EA")
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 2)
        attentionPart.append('text')
          .attr('class', 'label')
          .attr("x", type == 'self-attention' || type == 'cross-attention' ? textOffsetX * 2 : textOffsetX * 3)
          .attr("y", textOffsetY)
          .text('multi-head ' + type);
        

        // word vector
        let wordVector = attentionPart.append('g')
          .attr('id', 'wordvector-g')
          .attr('transform', `translate(${wordVectorOffsetX},${wordVectorOffsetY})`)
        wordVector.append('rect')
          .attr("rx", 3)
          .attr("ry", 3)
          .attr("width", wordVectorWidth)
          .attr("height", wordVectorHeight)
          .attr("fill", "rgb(237, 251, 195)")
          .attr('stroke', 'rgb(193, 200, 133)')
          .attr('stroke-width', 2)
        wordVector.append('text')
          .attr('class', 'context')
          .text('word vector')
          .attr("transform", getRotateCenter(25, 15))
        for (let i = 0; i < 3; i++) {
          wordVector.append('rect')
            .attr("x", wordVectorWidth + processGap)
            .attr("y", -20 + (wordVectorWidth + blockGap + 23) * i)
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("width", wordVectorWidth)
            .attr("height", wordVectorWidth)
            .attr("fill", "rgb(237, 251, 195)")
            .attr('stroke', 'rgb(193, 200, 133)')
            .attr('stroke-width', 2)
          if (i != 2) {
            wordVector.append('text')
              .text('…')
              .attr("font-size", '15px')
              .attr("font-weight", 'bold')
              .attr("fill", '#4a4a4a')
              .attr("y", 15 + (wordVectorWidth + blockGap + 25) * i)
              .attr("x", wordVectorWidth + processGap)

          }
        }

        // attention head
        let attentionHead = attentionPart.append('g')
          .attr('id', 'attentionhead-g')
          .attr('transform', `translate(${attentionHeadOffsetX},${attentionHeadOffsetY})`)
        for (let i = 0; i < 2; i++) {
          let num = i == 0 ? 1 : 8
          attentionHead.append('rect')
            .attr("y", -20 + (wordVectorWidth * 2 + blockGap * 2 + 46) * i)
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("width", attentionHeadWidth)
            .attr("height", attentionHeadHeight)
            .attr("fill", "rgb(238, 238, 238)")
            .attr('stroke', 'rgb(184, 184, 184)')
            .attr('stroke-width', 2)
          attentionHead.append('text')
            .text('attention head #' + num)
            .attr("class", 'context')
            .attr('x', 50)
            .attr("y", -10 + (wordVectorWidth * 2 + blockGap * 2 + 46) * i)
          attentionHead.append('text')
            .text('…')
            .attr("font-size", '15px')
            .attr("font-weight", 'bold')
            .attr("fill", '#4a4a4a')
            .attr("y", 5 + (wordVectorWidth * 2 + blockGap * 2 + 15) * i)
            .attr("x", textOffsetX)
        }
        openAttentionHead(attentionHead, type, -(attentionHeadOffsetX - wordVectorOffsetX - wordVectorWidth * 2 - processGap * 2), blockGap - 5, openAttentionHeadWidth)

        // attention score
        let attentionScore = attentionPart.append('g')
          .attr('id', 'attentionscore-g')
          .attr('transform', `translate(${attentionScoreOffsetX},${attentionScoreOffsetY})`)
        attentionScore.append('rect')
          .attr('x', wordVectorWidth + processGap)
          .attr("rx", 3)
          .attr("ry", 3)
          .attr("width", wordVectorWidth)
          .attr("height", wordVectorHeight)
          .attr("fill", "#F3C5C5")
          .attr('stroke', '#C1A3A3')
          .attr('stroke-width', 2)
        attentionScore.append('text')
          .attr('y', wordVectorWidth + processGap)
          .attr('class', 'context')
          .text('attention score')
          .attr("transform", getRotateCenter(25, 15))
        for (let i = 0; i < 3; i++) {
          attentionScore.append('rect')
            .attr("x", 0)
            .attr("y", -20 + (wordVectorWidth + blockGap + 23) * i)
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("width", wordVectorWidth)
            .attr("height", wordVectorWidth)
            .attr("fill", "#F3C5C5")
            .attr('stroke', '#C1A3A3')
            .attr('stroke-width', 2)
          if (i != 2) {
            attentionScore.append('text')
              .text('…')
              .attr("font-size", '15px')
              .attr("font-weight", 'bold')
              .attr("fill", '#4a4a4a')
              .attr("y", 15 + (wordVectorWidth + blockGap + 25) * i)
              .attr("x", 0)

          }
        }

        // lines
        let linkData = []
        for (let i = 0; i < 3; i++) {
          let wordVector =
          {
            source: { x: wordVectorOffsetX + wordVectorWidth, y: wordVectorOffsetY + wordVectorHeight / 2 },
            target: { x: wordVectorOffsetX + wordVectorWidth + processGap, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 }
          }
          let wordVector2AttentionHead = i != 1 ?
            {
              source: { x: wordVectorOffsetX + wordVectorWidth * 2 + processGap, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 },
              target: { x: attentionHeadOffsetX, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 }
            } :
            {
              source: { x: wordVectorOffsetX + wordVectorWidth * 2 + processGap, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 },
              target: { x: attentionHeadOffsetX - (attentionHeadOffsetX - wordVectorOffsetX - wordVectorWidth * 2 - processGap * 2), y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 }
            }
          let attentionHead2AttentionScore = i != 1 ?
            {
              source: { x: attentionHeadOffsetX + attentionHeadWidth, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 },
              target: { x: attentionScoreOffsetX, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 }
            } :
            {
              source: { x: attentionHeadOffsetX - (attentionHeadOffsetX - wordVectorOffsetX - wordVectorWidth * 2 - processGap * 2) + openAttentionHeadWidth, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 },
              target: { x: attentionScoreOffsetX, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 }
            }
          let attentionScore =
          {
            source: { x: attentionScoreOffsetX + wordVectorWidth, y: wordVectorOffsetY - 20 + (wordVectorOffsetY + blockGap - 7) * i + wordVectorWidth / 2 },
            target: { x: attentionScoreOffsetX + wordVectorWidth + processGap, y: wordVectorOffsetY + wordVectorHeight / 2 }
          }
          linkData.push(wordVector)
          linkData.push(wordVector2AttentionHead)
          linkData.push(attentionHead2AttentionScore)
          linkData.push(attentionScore)
        }
        attentionPart.append('g')
          .attr('id', 'attention-path')
          .selectAll('path')
          .attr('class', 'edge')
          .data(linkData)
          .enter()
          .append('path')
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)')
          .attr('marker-end', "url(#arrow)")

        attentionPart.on('click', function () {
          openDetailedCoderSvg.selectAll('*').remove()
          if (block == 'encoder') {
            self.status = 'openEncoderBlock'
            self.openEncoderBlock(openDetailedCoderSvg, blockNum, 0, type)
          } else if (block == 'decoder') {
            self.status = 'openDecoderBlock'
            self.openDecoderBlock(openDetailedCoderSvg, blockNum, 0, type)
          }
        })
          .style('cursor', 'hand')

        function openAttentionHead(g, type, offsetX, offsetY, openAttentionHeadWidth) {
          let height = 60
          let softmaxOffsetX = 25
          let softmaxOffsetY = (height / 5) * 2.8
          let leftbracketOffsetX = 35
          let leftbracketOffsetY = (height / 5) * 2
          let leftbracketWidth = 20
          let leftbracketHeight = 20
          let rightbracketOffsetX = type == 'self-attention' || type == 'cross-attention' ? 130 : 185
          let rightbracketOffsetY = (height / 5) * 2
          let rightbracketWidth = 20
          let rightbracketHeight = 20
          let leftbracket = require("../../src/assets/leftbracket.svg")
          let rightbracket = require("../../src/assets/rightbracket.svg")
          let scaleWidth = 50
          let scaleHeight = 50
          let scale = require("../../src/assets/scale.svg")
          let blockWidth = 6
          let blockHeight = 6
          let blockGap = 8
          let operatorRadius = 4
          let openAttentionHead = g.append('g')
            .attr('id', 'open-' + type + 'attentionhead-g')
            .attr('transform', `translate(${offsetX},${offsetY})`)

          openAttentionHead.append('rect')
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("width", openAttentionHeadWidth)
            .attr("height", height)
            .attr("fill", "rgb(238, 238, 238)")
            .attr('stroke', 'rgb(184, 184, 184)')
            .attr('stroke-width', 2)
          openAttentionHead.append('text')
            .text('softmax')
            .attr("x", softmaxOffsetX)
            .attr("y", softmaxOffsetY)
            .attr("class", 'context')

          // 左右括号
          openAttentionHead.append('svg:image')
            .attr('xlink:href', leftbracket)
            .attr("x", leftbracketOffsetX)
            .attr("y", leftbracketOffsetY)
            .attr("width", leftbracketWidth)
            .attr("height", leftbracketHeight)
          openAttentionHead.append('svg:image')
            .attr('xlink:href', rightbracket)
            .attr("x", rightbracketOffsetX)
            .attr("y", rightbracketOffsetY)
            .attr("width", rightbracketWidth)
            .attr("height", rightbracketHeight)

          // 分数分割线
          openAttentionHead.append('path')
            .attr('d', linePath([[leftbracketOffsetX + 18, softmaxOffsetY], [leftbracketOffsetX + 95, softmaxOffsetY]]))
            .attr('stroke', 'rgb(175, 175, 175)')
            .attr('stroke-width', 1)

          for (let i = 0; i < 4; i++) {
            // Query
            openAttentionHead.append('rect')
              .attr("x", leftbracketOffsetX + 25 + blockGap * i)
              .attr("y", (height / 5) * 2)
              .attr("rx", 1)
              .attr("ry", 1)
              .attr("width", blockWidth)
              .attr("height", blockHeight)
              .attr("fill", "rgb(186, 175, 211)")
              .attr('stroke', 'rgb(169, 128, 170)')
              .attr('stroke-width', 1)
            // Key
            openAttentionHead.append('rect')
              .attr("x", leftbracketOffsetX + 22 + blockGap * 7)
              .attr("y", 2 + blockGap * i)
              .attr("rx", 1)
              .attr("ry", 1)
              .attr("width", blockWidth)
              .attr("height", blockHeight)
              .attr("fill", "rgb(154, 214, 221)")
              .attr('stroke', 'rgb(156, 170, 183)')
              .attr('stroke-width', 1)
            // Value
            openAttentionHead.append('rect')
              .attr("x", rightbracketOffsetX + 17 + blockGap * (i + 1))
              .attr("y", height / 2)
              .attr("rx", 1)
              .attr("ry", 1)
              .attr("width", blockWidth)
              .attr("height", blockHeight)
              .attr("fill", "rgb(252, 252, 141)")
              .attr('stroke', 'rgb(198, 179, 94)')
              .attr('stroke-width', 1)
          }
          // scale
          openAttentionHead.append('svg:image')
            .attr('xlink:href', scale)
            .attr("x", leftbracketOffsetX + 35)
            .attr("y", (height / 5) * 1.8)
            .attr("width", scaleWidth)
            .attr("height", scaleHeight)

          // point multiply
          let pointMultiply = openAttentionHead.append('g')
            .attr('id', 'pointMultiply-g')
            .attr('transform', `translate(${leftbracketOffsetX + 22 + blockGap * 5.5},${(height / 5) * 2})`)
          pointMultiply.append('circle')
            .attr('class', 'operator')
            .attr("r", operatorRadius)
          pointMultiply.append('text')
            .attr("class", "operatorText")
            .text('·')

          // cross multiply
          let crossMultiply = openAttentionHead.append('g')
            .attr('id', 'crossMultiply-g')
            .attr('transform', `translate(${rightbracketOffsetX + 15},${softmaxOffsetY})`)
          crossMultiply.append('circle')
            .attr('class', 'operator')
            .attr("r", operatorRadius)
          crossMultiply.append('text')
            .attr("class", "operatorText")
            .attr('y', 3)
            .text('*')

          // cross attention
          if (type == 'masked self-attention') {
            let maskedAttention = openAttentionHead.append('g')
              .attr('id', 'masked-attention-g')
              .attr('transform', `translate(${leftbracketOffsetX + 105},${softmaxOffsetY})`)

            let maskedAttentionMultiply = maskedAttention.append('g')
              .attr('id', 'maskedMultiply-g')
              .attr('transform', `translate(4,0)`)
            maskedAttentionMultiply.append('circle')
              .attr('class', 'operator')
              .attr("r", operatorRadius)
            maskedAttentionMultiply.append('text')
              .attr("class", "operatorText")
              .attr('y', 3)
              .text('*')

            // mask operator
            for (let i = 0; i < 4; i++) {
              for (let j = 0; j < 4; j++) {
                maskedAttention.append('rect')
                  .attr("x", 15 + blockGap * i)
                  .attr("y", -17 + blockGap * j)
                  .attr("rx", 1)
                  .attr("ry", 1)
                  .attr("width", blockWidth)
                  .attr("height", blockHeight)
                  .attr("fill", i <= j ? '#B7C4CF' : '#F0A28E')
                  .attr('stroke', i <= j ? '#889EAF' : '#C36839')
                  .attr('stroke-width', 1)
              }
            }

            // 添加文字解释
            maskedAttention.append('text')
              .text('Mask operator')
              .attr("font-size", '8px')
              .attr("fill", '#4a4a4a')
              .attr("x", 0)
              .attr("y", -17 + blockGap * 5)
          }

          // 添加文字解释
          openAttentionHead.append('text')
            .text('Query')
            .attr("font-size", '8px')
            .attr("fill", '#4a4a4a')
            .attr("x", leftbracketOffsetX + 28)
            .attr("y", (height / 5) * 1.5)
          openAttentionHead.append('text')
            .text('Key(transposed)')
            .attr("font-size", '8px')
            .attr("fill", '#4a4a4a')
            .attr("x", leftbracketOffsetX + 88)
            .attr("y", (height / 5))
          openAttentionHead.append('text')
            .text('Value')
            .attr("font-size", '8px')
            .attr("fill", '#4a4a4a')
            .attr("x", rightbracketOffsetX + 30)
            .attr("y", softmaxOffsetY + 13)

        }


      }

      function drawAdd(svg, offsetX, offsetY, addHeight, source, target) {
        let textOffsetX = -addHeight * 10
        let textOffsetY = 5
        let explainOffsetX = addHeight * 1.5
        let explainOffsetY = 0
        let textGap = 13
        let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);
        let edgeOpacity = 0.5;

        let addPart = svg.append('g')
          .attr('id', 'add-g')
          .attr('transform', `translate(${offsetX},${offsetY})`)

        addPart.append('circle')
          .attr('cy', addHeight / 2)
          .attr("r", addHeight)
          .attr('fill', 'rgb(235,235,235)')
          .attr('stroke', 'rgb(175,175,175)')
          .attr('stroke-width', 2)
        addPart.append('text')
          .text('+')
          .attr('y', addHeight / 2)
          .attr('font-size', '20px')
          .attr('font-weight', 'bold')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', 'rgb(175,175,175)')

        // 添加文字解释
        addPart.append('text')
          .attr('class', 'label')
          .attr("x", textOffsetX)
          .attr("y", textOffsetY)
          .text('residual connection');

        let explainText = addPart.append('g')
          .attr('id', 'add-explain-g')
          .attr('transform', `translate(${explainOffsetX},${explainOffsetY})`)
        explainText.append('text')
          .text('Add the original')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", addHeight)
          .attr("y", 0)
        explainText.append('text')
          .text(source)
          .attr("font-size", '10px')
          .attr("fill", source == 'word vectors' ? 'rgb(193, 200, 133)' : '#ADC2A9')
          .attr("font-style", "italic")
          .attr('font-weight', 'bold')
          .attr("x", addHeight + 80)
          .attr("y", 0)
        explainText.append('text')
          .text('into')
          .attr("font-size", '10px')
          .attr("fill", '#4a4a4a')
          .attr("x", addHeight)
          .attr("y", textGap)
        explainText.append('text')
          .text(target)
          .attr("font-size", '10px')
          .attr("fill", target == 'attention scores' ? '#C1A3A3' : 'rgb(190, 175, 101)')
          .attr("font-style", "italic")
          .attr('font-weight', 'bold')
          .attr("x", addHeight + 23)
          .attr("y", textGap)
        let linkData = [{
          source: {
            x: addHeight - 2,
            y: textGap / 2 - 3,
          },
          target: {
            x: -addHeight + 10,
            y: addHeight / 2,
          },
        }]
        explainText.append('g')
          .attr('id', 'add-path')
          .selectAll('path')
          .attr('class', 'edge')
          .data(linkData)
          .enter()
          .append('path')
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none').style('stroke-width', '2px').style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)')
          .attr('marker-end', "url(#arrow)")
      }

      function drawLayerNorm(svg, blockNum, block, sublayer, offsetX, offsetY, layerNormWidth, layerNormHeight) {
        let textOffsetX = -layerNormWidth / 3
        let textOffsetY = layerNormHeight / 2
        let leftbracketOffsetX = -6
        let leftbracketOffsetY = layerNormHeight / 5
        let leftbracketWidth = 20
        let leftbracketHeight = 20
        let leftbracket = require("../../src/assets/leftbracket.svg")
        let processGap = 12
        let intermediateWidth = 80
        let intermediateHeight = 15
        let intermediateOffsetX = 15
        let intermediateOffsetY = (layerNormHeight - intermediateHeight) / 2
        let operatorRadius = 7
        let minusOffsetX = intermediateOffsetX + intermediateWidth + processGap
        let minusOffsetY = layerNormHeight / 2
        let meanWidth = intermediateHeight
        let meanHeight = intermediateHeight
        let meanOffsetX = minusOffsetX + processGap
        let meanOffsetY = (layerNormHeight - meanHeight) / 2
        let meanTextWidth = 20
        let meanTextHeight = 20
        let mean = require("../../src/assets/mean.svg")
        let rightbracketOffsetX = meanOffsetX + meanWidth
        let rightbracketOffsetY = leftbracketOffsetY
        let rightbracketWidth = 20
        let rightbracketHeight = 20
        let rightbracket = require("../../src/assets/rightbracket.svg")
        let divisionOffsetX = rightbracketOffsetX + processGap + rightbracketWidth / 3
        let divisionOffsetY = layerNormHeight / 2
        let standardWidth = intermediateHeight
        let standardHeight = intermediateHeight
        let standardOffsetX = divisionOffsetX + processGap
        let standardOffsetY = (layerNormHeight - standardHeight) / 2
        let standardTextWidth = 20
        let standardTextHeight = 20
        let standard = require("../../src/assets/sigma.svg")

        let layerNormPart = svg.append('g')
          .attr('id', 'layernorm-g-' + sublayer)
          .attr('transform', `translate(${offsetX},${offsetY})`)
        layerNormPart.append('rect')
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", layerNormWidth)
          .attr("height", layerNormHeight)
          .attr("fill", "#F8F4EA")
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 2)
        // 添加文字解释
        layerNormPart.append('text')
          .attr('class', 'label')
          .attr("x", textOffsetX)
          .attr("y", textOffsetY)
          .text('layer normalization');
        // 左右括号
        layerNormPart.append('svg:image')
          .attr('xlink:href', leftbracket)
          .attr("x", leftbracketOffsetX)
          .attr("y", leftbracketOffsetY)
          .attr("width", leftbracketWidth)
          .attr("height", leftbracketHeight)
        layerNormPart.append('svg:image')
          .attr('xlink:href', rightbracket)
          .attr("x", rightbracketOffsetX)
          .attr("y", rightbracketOffsetY)
          .attr("width", rightbracketWidth)
          .attr("height", rightbracketHeight)

        // intermediate amount
        let intermediate = layerNormPart.append('g')
          .attr('transform', `translate(${intermediateOffsetX},${intermediateOffsetY})`)
        intermediate.append('rect')
          .attr("rx", 3)
          .attr("ry", 3)
          .attr("width", intermediateWidth)
          .attr("height", intermediateHeight)
          .attr("fill", "#D3E4CD")
          .attr('stroke', '#ADC2A9')
          .attr('stroke-width', 2)
        intermediate.append('text')
          .attr("x", intermediateWidth / 2)
          .attr("y", intermediateHeight / 2)
          .attr('font-size', '7px')
          .attr("fill", '#4a4a4a')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .text('intermediate amount')

        // minus
        let minus = layerNormPart.append('g')
          .attr('id', 'minus-g')
          .attr('transform', `translate(${minusOffsetX},${minusOffsetY})`)
        minus.append('circle')
          .attr('class', 'operator')
          .attr("r", operatorRadius)
        minus.append('text')
          .attr("class", "operatorText")
          .text('-')
        // division
        let division = layerNormPart.append('g')
          .attr('id', 'division-g')
          .attr('transform', `translate(${divisionOffsetX},${divisionOffsetY})`)
        division.append('circle')
          .attr('class', 'operator')
          .attr("r", operatorRadius)
        division.append('text')
          .attr("class", "operatorText")
          .text('/')

        // mean
        let meanSvg = layerNormPart.append('g')
          .attr('id', 'mean-g')
          .attr('transform', `translate(${meanOffsetX},${meanOffsetY})`)
        meanSvg.append('rect')
          .attr("rx", 3)
          .attr("ry", 3)
          .attr("width", meanWidth)
          .attr("height", meanHeight)
          .attr("fill", "#D0E8F2")
          .attr('stroke', '#9BA4B4')
          .attr('stroke-width', 2)
        meanSvg.append('svg:image')
          .attr('xlink:href', mean)
          .attr("x", 3)
          .attr("y", 3)
          .attr("width", meanTextWidth / 2)
          .attr("height", meanTextHeight / 2)
        meanSvg.append('text')
          .attr("x", meanWidth / 2)
          .attr("y", meanHeight + 6)
          .attr('font-size', '7px')
          .attr("fill", '#4a4a4a')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .text('mean')

        // standard 
        let standardSvg = layerNormPart.append('g')
          .attr('id', 'standard-g')
          .attr('transform', `translate(${standardOffsetX},${standardOffsetY})`)
        standardSvg.append('rect')
          .attr("rx", 3)
          .attr("ry", 3)
          .attr("width", standardWidth)
          .attr("height", standardHeight)
          .attr("fill", "#D0E8F2")
          .attr('stroke', '#9BA4B4')
          .attr('stroke-width', 2)
        standardSvg.append('svg:image')
          .attr('xlink:href', standard)
          .attr("x", 4)
          .attr("y", 4)
          .attr("width", standardTextWidth / 2.5)
          .attr("height", standardTextHeight / 2.5)
        standardSvg.append('text')
          .attr("x", standardWidth / 2)
          .attr("y", standardHeight + 6)
          .attr('font-size', '7px')
          .attr("fill", '#4a4a4a')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .text('standard')

        layerNormPart.on('click', function () {
          openDetailedCoderSvg.selectAll('*').remove()
          if (block == 'encoder') {
            self.status = 'openEncoderBlock'
            self.openEncoderBlock(openDetailedCoderSvg, blockNum, sublayer, 'layer-normalization')
          } else if (block == 'decoder') {
            self.status = 'openDecoderBlock'
            self.openDecoderBlock(openDetailedCoderSvg, blockNum, sublayer, 'layer-normalization')
          }
        })
          .style('cursor', 'hand')

      }

      function drawFeedForwardNetwork(svg, blockNum, block, offsetX, offsetY, ffnWidth, ffnHeight) {
        let textOffsetX = -ffnWidth
        let textOffsetY = ffnHeight / 2
        let ffnPart = svg.append('g')
          .attr('id', 'ffn-g')
          .attr('transform', `translate(${offsetX},${offsetY})`)
        // 添加文字解释
        ffnPart.append('text')
          .attr('class', 'label')
          .attr("x", textOffsetX)
          .attr("y", textOffsetY)
          .text('feed-forward network');
        for (let i = 0; i < 2; i++) {
          ffnPart.append('text')
            .text('linear')
            .attr("font-size", '10px')
            .attr("fill", 'rgb(190, 175, 101)')
            .attr("font-style", "italic")
            .attr('font-weight', 'bold')
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr("x", 100 * i)
            .attr("y", ffnHeight / 2)
          ffnPart.append('text')
            .text('+')
            .attr("font-size", '10px')
            .attr("fill", 'rgb(175, 175, 175)')
            .attr('font-weight', 'bold')
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr("x", 25 + 50 * i)
            .attr("y", ffnHeight / 2)
        }
        ffnPart.append('text')
          .text('ReLU')
          .attr("font-size", '10px')
          .attr("fill", 'rgb(172, 150, 186)')
          .attr("font-style", "italic")
          .attr('font-weight', 'bold')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr("x", ffnWidth / 2)
          .attr("y", ffnHeight / 2)

        ffnPart.on('click', function () {
          openDetailedCoderSvg.selectAll('*').remove()
          if (block == 'encoder') {
            self.status = 'openEncoderBlock'
            self.openEncoderBlock(openDetailedCoderSvg, blockNum, 0, 'feed-forward-network')
          } else if (block == 'decoder') {
            self.status = 'openDecoderBlock'
            self.openDecoderBlock(openDetailedCoderSvg, blockNum, 0, 'feed-forward-network')
          }
        })
          .style('cursor', 'hand')
      }

      function drawArrow(svg) {
        var defs = svg.append("defs");
        var arrowMarker = defs.append("marker")
          .attr("id", "arrow")
          .attr("markerUnits", "strokeWidth")
          .attr("markerWidth", "8")
          .attr("markerHeight", "4")
          .attr("viewBox", "0 0 12 12")
          .attr("refX", "8.5")
          .attr("refY", "6")
          .attr("orient", "auto");

        var arrow_path = "M2,2 L2,10 L10,6 L2,2";
        arrowMarker.append("path")
          .attr("d", arrow_path)
          .attr("fill", 'rgb(175, 175, 175)');
      }

      function getRotateCenter(x, y) {
        return "rotate(270 " + x + " " + y + ")"
      }

      return [offsetX + lastCoderOffsetX, offsetY + lastCoderOffsetY]

    },

    drawGenerator(svg) {
      let self = this
      let processGap = 50
      let nodeWidth = 130
      let nodeHeight = 35
      let outputOffsetX = nodeWidth + processGap
      let outputOffsetY = -nodeHeight / 2

      let linearPart = svg.append('g')
        .attr("id", 'linear-g')
      linearPart.append('rect')
        .attr("class", "node")
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("width", nodeWidth)
        .attr("height", nodeHeight)
        .attr("fill", '#C3ACD0')
      linearPart.append('text')
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
        .attr("x", nodeWidth / 2)
        .attr("y", nodeHeight / 2)
        .text('Linear & Softmax')
      let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
      let instructiveArrowWidth = 30
      let instructiveArrowHeight = 30
      let clickIcon = require("../../src/assets/click.svg")
      let clickIconWidth = 13
      let clickIconHeight = 13
      let instructiveArrowOffsetX = nodeWidth - 20
      let instructiveArrowOffsetY = -30
      let instructiveText = linearPart.append('g')
        .attr('transform', `translate(${instructiveArrowOffsetX},${instructiveArrowOffsetY})`)
      instructiveText.append('svg:image')
        .attr('xlink:href', instructiveArrow)
        .attr("width", instructiveArrowWidth)
        .attr("height", instructiveArrowHeight)
      instructiveText.append('svg:image')
        .attr('transform', `translate(${25},${-10})`)
        .attr('xlink:href', clickIcon)
        .attr("width", clickIconWidth)
        .attr("height", clickIconHeight)
      instructiveText.append('text')
        .text('Click')
        .attr("font-size", '10px')
        .attr("font-weight", 'bold')
        .attr("font-style", 'italic')
        .attr("fill", '#4a4a4a')
        .attr("x", 40)
        .attr("y", 0)
      instructiveText.append('text')
        .text('to learn')
        .attr("font-size", '10px')
        .attr("fill", '#4a4a4a')
        .attr("x", 70)
        .attr("y", 0)
      instructiveText.append('text')
        .text('generator!')
        .attr("font-size", '10px')
        .attr("fill", '#4a4a4a')
        .attr("x", 33)
        .attr("y", 13)
      linearPart.on('click', () => {
        self.$emit('openGenerator', 'openGenerator', 'generator')
      })
        .style('cursor', 'hand')
      let outputText = svg.append('text').attr("text-anchor", "middle");
      outputText
        .attr('transform', `translate(${outputOffsetX + 50},${outputOffsetY})`)
        .style('text-anchor', 'middle')
        .style('font-size', '15px')
        .style('font-weight', 'bold')
        .attr("fill", '#4a4a4a')
        .selectAll('.tspan')
        .data([`Output`, `Probabilities`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);

      let linePath = d3.line()
      let lines = [
        [[-processGap, nodeHeight / 2], [0, nodeHeight / 2]],
        [[nodeWidth, nodeHeight / 2], [nodeWidth + processGap - 5, nodeHeight / 2]]
      ]
      for (let i = 0; i < lines.length; i++) {
        svg
          .append('path')
          .attr('d', linePath(lines[i]))
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 3)
          .attr('marker-end', "url(#arrow)");
      }


    },

    openEmbedding() {
      let speed = 1000
      let processGap = 50
      let weakenOpacity = 0.3
      let encoderOffsetX = processGap
      let encoderOffsetY = 30
      let encoderEmbeddingDataRange = getDataRange(this.encoder.embedding.output)
      let encoderPEDataRange = getDataRange(this.encoder.PE.output)
      let encoderTotalDataRange = {
        max: Math.max(encoderEmbeddingDataRange.max, encoderPEDataRange.max),
        min: Math.min(encoderEmbeddingDataRange.min, encoderPEDataRange.min),
      }
      let decoderEmbeddingDataRange = getDataRange(this.decoder.embedding.output)
      let decoderPEDataRange = getDataRange(this.decoder.PE.output)
      let decoderTotalDataRange = {
        max: Math.max(decoderEmbeddingDataRange.max, decoderPEDataRange.max),
        min: Math.min(decoderEmbeddingDataRange.min, decoderPEDataRange.min),
      }
      let linkData = []
      let edgeOpacity = 0.5;
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);

      function OpenEmbedding(svg, type, offsetX, offsetY, matrixHeight, inputData) {
        let tokenHeight = 30
        let tokenGap = 15
        let vocabSize = 32000

        let embeddingPart = svg.append('g')
          .attr('id', type + '-open-embedding-g')
          .attr('transform', `translate(${offsetX},${offsetY})`)
          .attr('opacity', 0)

        let embeddingMatrixConstraintGridCellWidth = 300;
        let embeddingMatrixConstraintGridCellHeight = matrixHeight - 60;
        let embeddingMatrixGridGroupX = 0;
        let embeddingMatrixGridGroupY = 0;
        let embeddingMatrixGridData = getGridData([[0]], embeddingMatrixConstraintGridCellWidth, embeddingMatrixConstraintGridCellHeight);
        let embeddingMatrixGridGroup = embeddingPart.append("g").attr("class", "grid").attr("transform", `translate(${embeddingMatrixGridGroupX},${embeddingMatrixGridGroupY})`);
        let embeddingMatrixGridRow = embeddingMatrixGridGroup.selectAll(".row")  // 绘制每一行
          .data(embeddingMatrixGridData).enter().append('g').attr('class', 'row');
        embeddingMatrixGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('fill', 'rgb(220, 220, 220)');

        linkData = []
        for (let i = 0; i < inputData.input.length; i++) {
          let tokenMatrixLinkData = {
            source: {
              x: -processGap,
              y: tokenHeight / 2 + (tokenGap + tokenHeight) * i,
            },
            target: {
              x: embeddingMatrixGridGroupX + embeddingMatrixGridData[0][0].x,
              y: embeddingMatrixGridGroupY + embeddingMatrixGridData[0][0].y + (inputData.input[i] / vocabSize) * embeddingMatrixGridData[0][0].height,
            },
            id: 'token-matrix-' + (i + 1),
            class: 'token-matrix'
          }
          let matrixEmbeddingLinkData = {
            source: {
              x: embeddingMatrixGridGroupX + embeddingMatrixGridData[0][0].x + embeddingMatrixGridData[0][0].width,
              y: embeddingMatrixGridGroupY + embeddingMatrixGridData[0][0].y + (inputData.input[i] / vocabSize) * embeddingMatrixGridData[0][0].height,
            },
            target: {
              x: embeddingMatrixGridGroupX + embeddingMatrixGridData[0][0].x + embeddingMatrixGridData[0][0].width + processGap,
              y: tokenHeight / 2 + (tokenGap + tokenHeight) * i,
            },
            id: 'matrix-embedding-' + (i + 1),
            class: 'matrix-embedding'
          }
          let matrixLinkData = {
            source: {
              x: embeddingMatrixGridGroupX + embeddingMatrixGridData[0][0].x,
              y: embeddingMatrixGridGroupY + embeddingMatrixGridData[0][0].y + (inputData.input[i] / vocabSize) * embeddingMatrixGridData[0][0].height,
            },
            target: {
              x: embeddingMatrixGridGroupX + embeddingMatrixGridData[0][0].x + embeddingMatrixGridData[0][0].width,
              y: embeddingMatrixGridGroupY + embeddingMatrixGridData[0][0].y + (inputData.input[i] / vocabSize) * embeddingMatrixGridData[0][0].height,
            },
            id: type + '-matrix-' + (i + 1),
            class: 'matrix'
          }
          linkData.push(tokenMatrixLinkData)
          linkData.push(matrixEmbeddingLinkData)
          linkData.push(matrixLinkData)
        }
        let edgeGroup = embeddingPart.append("g").attr("class", "edge-group");
        edgeGroup.selectAll("path.edge").data(linkData).enter().append('path')
          .attr('id', d => d.id != undefined ? d.id : null)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none')
          .style('stroke-width', '2px')
          .style('opacity', d => d.class == 'token-matrix' || d.class == 'matrix-embedding' ? edgeOpacity : 0)
          .style('stroke', 'rgb(175, 175, 175)');



        // 添加文字解释
        let embeddingMatrixTotalGridWidth = embeddingMatrixConstraintGridCellWidth;
        let embeddingMatrixGridText = embeddingPart.append('text').attr("text-anchor", "middle");
        embeddingMatrixGridText
          .attr('transform', `translate(${embeddingMatrixGridGroupX + embeddingMatrixTotalGridWidth / 2},${embeddingMatrixGridGroupY - 20})`)
          .attr('class', 'label')
          .text(`embedding matrix (${vocabSize},${inputData.output[0].length})`)

        d3.select('#' + type + '-open-embedding-g')
          .transition()
          .duration(2000)
          .attr('opacity', 1)


        let width = offsetX + embeddingMatrixConstraintGridCellWidth + processGap
        return width

      }

      d3.select('#cpnArchitectureGroup').selectAll('*').remove();
      let svg = d3.select('#cpnArchitectureGroup')
        .append('svg')
        .attr("width", "100%")
        .attr('height', "100%")
      let openDetailedCoderPart = svg.append('g')
        .attr('id', 'open-detailed-coder')
      let detailedCoderPart = svg.append('g')
        .attr('id', 'detailedcoder-g')
      let encoderPart =
        svg.append('g')
          .attr('id', 'encoder-g')
          .attr('transform', `translate(${encoderOffsetX},${encoderOffsetY})`);
      let encoderTokenPos = this.drawTokenize(encoderPart, 'encoder', 0, 0, this.encoder.tokenize, true, weakenOpacity, 1)
      let openenEmbeddingPos = OpenEmbedding(encoderPart, 'encoder', encoderTokenPos[0], encoderTokenPos[1], encoderTokenPos[2], this.encoder.embedding)
      let encoderEmbeddingPos = this.drawEmbedding(encoderPart, 'encoder', encoderTokenPos[0], encoderTokenPos[1], this.encoder.embedding, 'opened', encoderTotalDataRange, weakenOpacity, 1)
      let encoderPEPos = this.drawPE(encoderPart, 'encoder', encoderEmbeddingPos[0], encoderEmbeddingPos[1], this.encoder.PE, 'opened', encoderTotalDataRange, weakenOpacity)
      this.drawCoders(encoderPart, openDetailedCoderPart, 'encoder', encoderPEPos[0], encoderPEPos[1], '#E1D2D2', detailedCoderPart, weakenOpacity)

      d3.select('#encoder-embedding-g')
        .transition()
        .duration(speed)
        .style('transform', `translate(${openenEmbeddingPos - encoderTokenPos[0]}px,0px)`)
      d3.select('#encoder-pe-g')
        .transition()
        .duration(speed)
        .style('transform', `translate(${(openenEmbeddingPos - encoderTokenPos[0])}px,0px)`)
      d3.select('#encoder-blocks-g')
        .transition()
        .duration(speed)
        .style('transform', `translate(${encoderPEPos[0] + (openenEmbeddingPos - encoderTokenPos[0])}px,${encoderPEPos[1]}px)`)
      d3.select('#detailedcoder-g')
        .transition()
        .duration(speed)
        .style('transform', `translate(${(openenEmbeddingPos - encoderTokenPos[0])}px,0px)`)
      // console.log(openenEmbeddingPos)


      let decoderOffsetX = processGap
      let decoderOffsetY = encoderTokenPos[2] + 50
      let decoderPart =
        svg.append('g')
          .attr('id', 'decoder-g')
          .attr('transform', `translate(${decoderOffsetX},${decoderOffsetY})`);
      let decoderTokenPos = this.drawTokenize(decoderPart, 'decoder', 0, 0, this.decoder.tokenize, true, weakenOpacity, 1)
      let opendeEmbeddingPos = OpenEmbedding(decoderPart, 'decoder', decoderTokenPos[0], decoderTokenPos[1], encoderTokenPos[2], this.decoder.embedding)
      let decoderEmbeddingPos = this.drawEmbedding(decoderPart, 'decoder', decoderTokenPos[0], decoderTokenPos[1], this.decoder.embedding, 'opened', decoderTotalDataRange, weakenOpacity, 1)
      let decoderPEPos = this.drawPE(decoderPart, 'decoder', decoderEmbeddingPos[0], decoderEmbeddingPos[1], this.decoder.PE, 'opened', decoderTotalDataRange, weakenOpacity)
      this.drawCoders(decoderPart, openDetailedCoderPart, 'decoder', decoderPEPos[0], decoderPEPos[1], "rgb(213, 231, 240)", detailedCoderPart, weakenOpacity)
      d3.select('#decoder-embedding-g')
        .transition()
        .duration(speed)
        .style('transform', `translate(${opendeEmbeddingPos - decoderTokenPos[0]}px,0px)`)
      d3.select('#decoder-pe-g')
        .transition()
        .duration(speed)
        .style('transform', `translate(${(opendeEmbeddingPos - decoderTokenPos[0])}px,0px)`)
      d3.select('#decoder-blocks-g')
        .transition()
        .duration(speed)
        .style('transform', `translate(${decoderPEPos[0] + (opendeEmbeddingPos - decoderTokenPos[0])}px,${decoderPEPos[1]}px)`)


      // 点击空白处 返回初始界面
      var self = this
      svg.on('click', function (event) {
        if (event.srcElement.nodeName == 'svg') {
          self.status = 'initial'
          self.initArchitecture()
        }
      })
        .style('cursor', 'hand')


      // 添加交互事件
      d3.select('#encoder-word-tokens')
        .on('mouseover', (event) => {
          if (event.srcElement.id.split('-')[0] == 'token') {
            d3.select('#encoder-matrix-' + event.srcElement.id.split('-')[2])
              .style('opacity', 1)
          }
        })
        .on('mouseout', (event) => {
          if (event.srcElement.id.split('-')[0] == 'token') {
            d3.select('#encoder-matrix-' + event.srcElement.id.split('-')[2])
              .style('opacity', 0)
          }
        })
      d3.select('#decoder-word-tokens')
        .on('mouseover', (event) => {
          if (event.srcElement.id.split('-')[0] == 'token') {
            d3.select('#decoder-matrix-' + event.srcElement.id.split('-')[2])
              .style('opacity', 1)
          }
        })
        .on('mouseout', (event) => {
          if (event.srcElement.id.split('-')[0] == 'token') {
            d3.select('#decoder-matrix-' + event.srcElement.id.split('-')[2])
              .style('opacity', 0)
          }
        })
    },

    openPE() {
      let processGap = 50
      let weakenOpacity = 0.3
      let encoderOffsetX = processGap
      let encoderOffsetY = 30
      let encoderEmbeddingDataRange = getDataRange(this.encoder.embedding.output)
      let encoderPEDataRange = getDataRange(this.encoder.PE.output)
      let encoderTotalDataRange = {
        max: Math.max(encoderEmbeddingDataRange.max, encoderPEDataRange.max),
        min: Math.min(encoderEmbeddingDataRange.min, encoderPEDataRange.min),
      }
      let decoderEmbeddingDataRange = getDataRange(this.decoder.embedding.output)
      let decoderPEDataRange = getDataRange(this.decoder.PE.output)
      let decoderTotalDataRange = {
        max: Math.max(decoderEmbeddingDataRange.max, decoderPEDataRange.max),
        min: Math.min(decoderEmbeddingDataRange.min, decoderPEDataRange.min),
      }

      var self = this

      function openPE(svg, type, offsetX, offsetY, inputData, peData) {
        let xSize = 325;
        let ySize = 240;
        let tokenGap = 10
        let processGap = 50
        let textOffset = - 20
        let operatorRadius = 10
        let dataRange = type == 'encoder' ? encoderTotalDataRange : decoderTotalDataRange
        let peParamsDataRange = getDataRange(peData)
        let colorScale = d3.interpolateRdBu;
        let edgeOpacity = 0.5;
        let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);

        let pePart = svg.append('g')
          .attr('id', type + '-open-pe-g')
          .attr('transform', `translate(${offsetX},${offsetY})`)

        // 绘制 embeddings
        let embeddingsGridGroupX = 0;
        let embeddingsGridGroupY = 0;
        let embeddingsConstraintGridCellWidth = getVisualizationSizeConstraint(inputData.input[0].length, 'x', xSize, ySize, 40);
        // let embeddingsConstraintGridCellHeight = getVisualizationSizeConstraint(inputData.output.length, 'y', xSize, ySize, 40);
        let embeddingsConstraintGridCellHeight = 35
        let embeddingsGridData = getGapGridData(inputData.input, embeddingsConstraintGridCellWidth, embeddingsConstraintGridCellHeight, tokenGap);
        let embeddingsGridGroup = pePart.append("g")
          .attr("class", "grid")
          .attr("transform", `translate(${embeddingsGridGroupX},${embeddingsGridGroupY})`);
        let embeddingsGridRow = embeddingsGridGroup.selectAll(".row")  // 绘制每一行
          .data(embeddingsGridData).enter().append('g').attr('class', 'row');
        embeddingsGridRow.selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', d => d.row * embeddingsGridData[0].length + d.col == self.legalHighlightsIndex ? 'black' : null)
          .on('mouseover', (event, d) => {
            self.$emit('changeHilightsIndex', d.row * embeddingsGridData[0].length + d.col)
            peTooltip(tooltipGroup, type, event, self.legalHighlightsIndex, inputData.input, peData, inputData.output)
          })
          .style('cursor', 'hand')
          .on('mouseout', () => {
            d3.select('#pe-tooltip').selectAll('*').remove();
          })
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorScale(normlizedVal);
          });
        let embeddingsTotalGridWidth = embeddingsConstraintGridCellWidth * inputData.input[0].length;
        // let embeddingsTotalGridHeight = (embeddingsConstraintGridCellHeight + tokenGap) * inputData.output.length;
        let embeddingsGridText = pePart.append('text').attr("text-anchor", "middle");
        embeddingsGridText
          .attr('transform', `translate(${embeddingsGridGroupX + embeddingsTotalGridWidth / 2},${textOffset})`)
          .attr('class', 'label')
          .text(`embeddings (${inputData.input.length},${inputData.input[0].length})`);


        // 绘制 PE params
        let peParamsGridGroupX = embeddingsGridGroupX + embeddingsTotalGridWidth + processGap;
        let peParamsGridGroupY = embeddingsGridGroupY;
        let peParamsConstraintGridCellWidth = getVisualizationSizeConstraint(peData[0].length, 'x', xSize, ySize, 40);
        // let pesConstraintGridCellHeight = getVisualizationSizeConstraint(inputData.output.length, 'y', xSize, ySize, 40);
        let peParamsConstraintGridCellHeight = 35
        let peParamsGridData = getGapGridData(peData, peParamsConstraintGridCellWidth, peParamsConstraintGridCellHeight, tokenGap);
        let peParamsGridGroup = pePart.append("g")
          .attr("class", "grid")
          .attr('id', 'pePramas-grid-g')
          .attr("transform", `translate(${peParamsGridGroupX},${peParamsGridGroupY})`)
        // .style('opacity', 0)
        let peParamsGridRow = peParamsGridGroup.selectAll(".row")  // 绘制每一行
          .data(peParamsGridData).enter().append('g').attr('class', 'row');
        peParamsGridRow.selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', d => d.row * peParamsGridData[0].length + d.col == self.legalHighlightsIndex ? 'black' : null)
          .on('mouseover', (event, d) => {
            self.$emit('changeHilightsIndex', d.row * peParamsGridData[0].length + d.col)// this.$emit('changeEquationIndex',newEquationIndex)
            peTooltip(tooltipGroup, type, event, self.legalHighlightsIndex, inputData.input, peData, inputData.output)
          })
          .style('cursor', 'hand')
          .on('mouseout', () => {
            d3.select('#pe-tooltip').selectAll('*').remove();
          })
          .style('fill', d => {
            let normlizedVal = (d.text - peParamsDataRange.min) / (peParamsDataRange.max - peParamsDataRange.min);
            return colorScale(normlizedVal);
          });
        let peParamsTotalGridWidth = peParamsConstraintGridCellWidth * inputData.output[0].length;
        // let embeddingsTotalGridHeight = (embeddingsConstraintGridCellHeight + tokenGap) * inputData.output.length;
        let peParamsGridText = pePart.append('text')
          .attr("text-anchor", "middle")
          .attr('id', 'pePramas-grid-text')
        // .style('opacity', 0)
        peParamsGridText
          .attr('transform', `translate(${peParamsGridGroupX + peParamsTotalGridWidth / 2},${textOffset})`)
          .attr('class', 'label')
          .text(`positional encoding (${inputData.output.length},${inputData.output[0].length})`)


        // 绘制 embeddings after PE
        let pesGridGroupX = peParamsGridGroupX + peParamsTotalGridWidth + processGap;
        let pesGridGroupY = peParamsGridGroupY;
        let pesConstraintGridCellWidth = getVisualizationSizeConstraint(inputData.output[0].length, 'x', xSize, ySize, 40);
        // let pesConstraintGridCellHeight = getVisualizationSizeConstraint(inputData.output.length, 'y', xSize, ySize, 40);
        let pesConstraintGridCellHeight = 35
        let pesGridData = getGapGridData(inputData.output, pesConstraintGridCellWidth, pesConstraintGridCellHeight, tokenGap);
        let pesGridGroup = pePart.append("g").attr("class", "grid").attr("transform", `translate(${pesGridGroupX},${pesGridGroupY})`);
        let pesGridRow = pesGridGroup.selectAll(".row")  // 绘制每一行
          .data(pesGridData).enter().append('g').attr('class', 'row');
        pesGridRow.selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', d => d.row * pesGridData[0].length + d.col == self.legalHighlightsIndex ? 'black' : null)
          .on('mouseover', (event, d) => {
            self.$emit('changeHilightsIndex', d.row * pesGridData[0].length + d.col)// this.$emit('changeEquationIndex',newEquationIndex)
            peTooltip(tooltipGroup, type, event, self.legalHighlightsIndex, inputData.input, peData, inputData.output)
          })
          .style('cursor', 'hand')
          .on('mouseout', () => {
            d3.select('#pe-tooltip').selectAll('*').remove();
          })
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorScale(normlizedVal);
          });
        let pesTotalGridWidth = pesConstraintGridCellWidth * inputData.output[0].length;
        // let embeddingsTotalGridHeight = (embeddingsConstraintGridCellHeight + tokenGap) * inputData.output.length;
        let pesGridText = pePart.append('text').attr("text-anchor", "middle");
        pesGridText
          .attr('transform', `translate(${pesGridGroupX + pesTotalGridWidth / 2},${textOffset})`)
          .attr('class', 'label')
          .text(`after positional encoding (${inputData.output.length},${inputData.output[0].length})`);

        // 添加运算符号
        let plusOperators = pePart.append('g')
          .attr('id', type + '-plusoperators-g')
          .attr('transform', `translate(${embeddingsGridGroupX + xSize + processGap / 2},${embeddingsGridGroupY + (embeddingsConstraintGridCellHeight) / 2})`)
        let equationOperators = pePart.append('g')
          .attr('id', type + '-equationoperators-g')
          .attr('transform', `translate(${peParamsGridGroupX + xSize + processGap / 2},${peParamsGridGroupY + (embeddingsConstraintGridCellHeight) / 2})`)
        for (let i = 0; i < (inputData.input.length); i++) {
          let plus = plusOperators.append('g')
            .attr('id', 'plus-g-' + i)
            .attr('transform', `translate(0,${(tokenGap + embeddingsConstraintGridCellHeight) * i})`)
          plus.append('circle')
            .attr('class', 'operator')
            .attr('r', operatorRadius)
          plus.append('text')
            .attr('class', 'operatorText')
            .text('+')
          let equation = equationOperators.append('g')
            .attr('id', 'equation-g-' + i)
            .attr('transform', `translate(0,${(tokenGap + embeddingsConstraintGridCellHeight) * i})`)
          equation.append('circle')
            .attr('class', 'operator')
            .attr('r', operatorRadius)
          equation.append('text')
            .attr('class', 'operatorText')
            .text('=')
        }

        // 绘制PE-Coders连线
        let linkData = []
        for (let i = 0; i < inputData.input.length; i++) {
          let peLinkData = {
            source: {
              x: pesGridGroupX + pesGridData[i][0].x + xSize,
              y: pesGridGroupY + pesGridData[i][0].y + pesGridData[i][0].height / 2,
            },
            target: {
              x: pesGridGroupX + pesGridData[i][0].x + xSize + processGap,
              y: tokenGap + 5,
            },
            class: 'pe-link',
            id: (i + 1)
          }
          linkData.push(peLinkData)
        }
        let edgeGroup = pePart.append("g").attr("class", "edge-group");
        edgeGroup.selectAll("path.edge").data(linkData).enter().append('path')
          .attr('id', d => d.id != undefined ? d.id : null)
          .attr('class', d => d.class != undefined ? d.class : null)
          .attr('d', d => linkGen({ source: d.source, target: d.target }))
          .style('fill', 'none')
          .style('stroke-width', '2px')
          .style('opacity', edgeOpacity)
          .style('stroke', 'rgb(175, 175, 175)');

        // tooltip
        let tooltipGroup = pePart.append("g")
          .attr('id', 'pe-tooltip')

        return [offsetX + pesGridGroupX + pesTotalGridWidth + processGap, offsetY, offsetX + peParamsGridGroupX + peParamsTotalGridWidth + processGap]
      }

      function peTooltip(svg, type, event, highlightIndex, embeddingData, peParamData, peData) {
        let offsetX = type == 'encoder' ? event.screenX - 500 : event.screenX - 500
        let offsetY = type == 'encoder' ? event.screenY - 300 : event.screenY - 700
        let processGap = 20
        let rectWidth = 300
        let rectHeight = 160
        let gridLength = 35
        let operatorRadius = 10
        let xSize = 325
        let ySize = 240
        let fontSize = '10px'
        let dataRange = type == 'encoder' ? encoderTotalDataRange : decoderTotalDataRange
        let backgroundOpacity = 0.8
        let opacity = 1
        let embeddingsSingleGridGroupX = 40;
        let embeddingsSingleGridGroupY = rectHeight - 75;
        let peParamSingleGridGroupX = embeddingsSingleGridGroupX + gridLength + operatorRadius * 2 + processGap * 2;
        let peParamSingleGridGroupY = embeddingsSingleGridGroupY;
        let peParamsDataRange = getDataRange(peParamData)
        let peSingleGridGroupX = peParamSingleGridGroupX + gridLength + operatorRadius * 2 + processGap * 2;
        let peSingleGridGroupY = peParamSingleGridGroupY;
        let plusOffsetX = embeddingsSingleGridGroupX + gridLength + processGap * 1.6
        let plusOffsetY = embeddingsSingleGridGroupY + 20
        let eqautionOffsetX = peParamSingleGridGroupX + gridLength + processGap * 1.6
        let equationOffsetY = plusOffsetY

        let colorScale = d3.interpolateRdBu

        let peTooltipPart = svg.append('g')
          .attr('id', 'detailed-pe')
          .attr('transform', `translate(${offsetX},${offsetY})`)
        peTooltipPart.append('rect')
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", rectWidth)
          .attr("height", rectHeight)
          .attr("fill", "rgb(235, 235, 235)")
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 1)
          .style('opacity', backgroundOpacity)

        // embedding single grid
        let embeddingsSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let embeddingsSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let embeddingsSingleGridData = getGridData([[embeddingData[Math.floor(highlightIndex / embeddingData[0].length)][highlightIndex % embeddingData[0].length]]]
          , embeddingsSingleConstraintGridCellWidth, embeddingsSingleConstraintGridCellHeight);
        let embeddingsSingleGridGroup = peTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${embeddingsSingleGridGroupX},${embeddingsSingleGridGroupY})`);
        let embeddingsSingleGridRow = embeddingsSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(embeddingsSingleGridData).enter().append('g').attr('class', 'row');
        embeddingsSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorScale(normlizedVal);
          });
        embeddingsSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);

        let embeddingsSingleGridText = peTooltipPart.append('text').attr("text-anchor", "middle");
        embeddingsSingleGridText
          .attr('transform', `translate(${embeddingsSingleGridGroupX + gridLength / 2},${embeddingsSingleGridGroupY + gridLength + 20})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`embedding`);


        // pe param single grid
        let peParamSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let peParamSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let peParamSingleGridData = getGridData([[peParamData[Math.floor(highlightIndex / peParamData[0].length)][highlightIndex % peParamData[0].length]]]
          , peParamSingleConstraintGridCellWidth, peParamSingleConstraintGridCellHeight);
        let peParamSingleGridGroup = peTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${peParamSingleGridGroupX},${peParamSingleGridGroupY})`);
        let peParamSingleGridRow = peParamSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(peParamSingleGridData).enter().append('g').attr('class', 'row');
        peParamSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - peParamsDataRange.min) / (peParamsDataRange.max - peParamsDataRange.min);
            return colorScale(normlizedVal);
          });
        peParamSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - peParamsDataRange.min) / (peParamsDataRange.max - peParamsDataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);

        let peParamSingleGridText = peTooltipPart.append('text').attr("text-anchor", "middle");
        peParamSingleGridText
          .attr('transform', `translate(${peParamSingleGridGroupX + gridLength / 2},${peParamSingleGridGroupY + gridLength})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .selectAll('.tspan')
          .data([`positional`, `encoding`])
          .enter().append('tspan')
          .attr('x', 0)
          .attr('dy', '1.5em')
          .text(d => d);

        // pe single grid
        let peSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let peSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let peSingleGridData = getGridData([[peData[Math.floor(highlightIndex / peData[0].length)][highlightIndex % peData[0].length]]]
          , peSingleConstraintGridCellWidth, peSingleConstraintGridCellHeight);
        let peSingleGridGroup = peTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${peSingleGridGroupX},${peSingleGridGroupY})`);
        let peSingleGridRow = peSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(peSingleGridData).enter().append('g').attr('class', 'row');
        peSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorScale(normlizedVal);
          });
        peSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);

        let peSingleGridText = peTooltipPart.append('text').attr("text-anchor", "middle");
        peSingleGridText
          .attr('transform', `translate(${peSingleGridGroupX + gridLength / 2},${peSingleGridGroupY + gridLength})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .selectAll('.tspan')
          .data([`embedding after`, `positional encoding`])
          .enter().append('tspan')
          .attr('x', 0)
          .attr('dy', '1.5em')
          .text(d => d);

        // plus
        let plus = peTooltipPart.append('g')
          .attr('id', 'plus-g')
          .attr('transform', `translate(${plusOffsetX},${plusOffsetY})`)
        plus.append('circle')
          .attr('class', 'operator')
          .attr('r', operatorRadius)
        plus.append('text')
          .attr('class', 'operatorText')
          .text('+')

        // equation
        let equation = peTooltipPart.append('g')
          .attr('id', 'equation-g')
          .attr('transform', `translate(${eqautionOffsetX},${equationOffsetY})`)
        equation.append('circle')
          .attr('class', 'operator')
          .attr('r', operatorRadius)
        equation.append('text')
          .attr('class', 'operatorText')
          .text('=')

        let rCord = Math.floor(highlightIndex / peData[0].length);
        let cCord = highlightIndex % peData[0].length;
        let peSingleTextOffsetX = 20
        let peSingleTextOffsetY = -60
        let sinWidth = 200
        let sinHeight = 200
        let numeratorOffsetX = sinWidth + 35
        let numeratorOffsetY = 85
        let denominatorOffsetX = numeratorOffsetX
        let denominatorOffsetY = numeratorOffsetY + 20
        let cos = require("../../src/assets/PEcos.svg")
        let sin = require("../../src/assets/PEsin.svg")

        let peSingleText = peTooltipPart.append('g')
          .attr('id', 'pe-single-text')
          .attr('transform', `translate(${peSingleTextOffsetX},${peSingleTextOffsetY})`)
          .style("z-index", 100);

        peSingleText.append('svg:image')
          .attr('xlink:href', cCord % 2 == 0 ? sin : cos)
          .attr("width", sinWidth)
          .attr("height", sinHeight)

        //分子
        peSingleText.append('text')
          .attr('transform', `translate(${numeratorOffsetX},${numeratorOffsetY})`)
          .style('text-anchor', 'middle')
          .style('font-size', '12px')
          // .style('font-weight', 'bold')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`pos=${rCord}`);
        //分母
        peSingleText.append('text')
          .attr('transform', `translate(${denominatorOffsetX},${denominatorOffsetY})`)
          .style('text-anchor', 'middle')
          .style('font-size', '12px')
          // .style('font-weight', 'bold')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(cCord % 2 == 0 ? `2i=${cCord}` : `2i+1=${cCord}`);

        peSingleText.append('text')
          .attr('transform', `translate(${denominatorOffsetX},${denominatorOffsetY + 20})`)
          .style('text-anchor', 'middle')
          .style('font-size', '12px')
          // .style('font-weight', 'bold')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`d_model=${peData[0].length}`);



      }



      d3.select('#cpnArchitectureGroup').selectAll('*').remove();
      let svg = d3.select('#cpnArchitectureGroup')
        .append('svg')
        .attr("width", "100%")
        .attr('height', "100%")
      let openDetailedCoderPart = svg.append('g')
        .attr('id', 'open-detailed-coder')
      let detailedCoderPart = svg.append('g')
        .attr('id', 'detailedcoder-g')

      let decoderPart =
        svg.append('g')
          .attr('id', 'decoder-g')


      let encoderPart =
        svg.append('g')
          .attr('id', 'encoder-g')
          .attr('transform', `translate(${encoderOffsetX},${encoderOffsetY})`);

      let encoderTokenPos = this.drawTokenize(encoderPart, 'encoder', 0, 0, this.encoder.tokenize, false, weakenOpacity, weakenOpacity)
      let encoderOpenPEPos = openPE(encoderPart, 'encoder', encoderTokenPos[0], encoderTokenPos[1], this.encoder.PE, this.encoderPEParams)
      this.drawCoders(encoderPart, openDetailedCoderPart, 'encoder', encoderOpenPEPos[0], encoderOpenPEPos[1], '#E1D2D2', detailedCoderPart, weakenOpacity)

      let decoderOffsetX = processGap
      let decoderOffsetY = encoderTokenPos[2] + 50
      d3.select('#decoder-g')
        .attr('transform', `translate(${decoderOffsetX},${decoderOffsetY})`);
      // let decoderTokenPos = 
      let decoderTokenPos = this.drawTokenize(decoderPart, 'decoder', 0, 0, this.decoder.tokenize, false, weakenOpacity, weakenOpacity)
      let decoderOpenPEPos = openPE(decoderPart, 'decoder', decoderTokenPos[0], decoderTokenPos[1], this.decoder.PE, this.decoderPEParams)
      this.drawCoders(decoderPart, openDetailedCoderPart, 'decoder', decoderOpenPEPos[0], decoderOpenPEPos[1], "rgb(213, 231, 240)", detailedCoderPart, weakenOpacity)


      // 点击空白处 返回初始界面
      svg.on('click', function (event) {
        if (event.srcElement.nodeName == 'svg') {
          self.status = 'initial'
          self.initArchitecture()
        }
      })


    },

    openEncoderBlock(svg, blockNum, sublayer, openDetailedCoder) {
      let moveOffsetX = -1200
      let speed = 1000
      let self = this
      let openSelfAttentionOffsetX = 2040
      let openSelfAttentionOffsetY = 80
      let openLayerNormOffsetX = openSelfAttentionOffsetX + 100
      let openLayerNormOffsetY = openSelfAttentionOffsetY
      let openFFNOffsetX = openLayerNormOffsetX
      let openFFNOffsetY = openLayerNormOffsetY

      d3.select('#architectureSvg')
        .transition()
        .duration(speed)
        .style('transform', `translate(${moveOffsetX}px,0px)`)

      // 删除重画 防止多次点击事件导致的重叠
      // svg.selectAll('*').remove()
      if (openDetailedCoder == 'self-attention' || openDetailedCoder == 'cross-attention' || openDetailedCoder == 'masked self-attention') {
        this.openSelfAttention(svg, 'encoder', openDetailedCoder, openSelfAttentionOffsetX, openSelfAttentionOffsetY, blockNum - 1, 1)
      } else if (openDetailedCoder == 'layer-normalization') {
        // 获取数据
        this.$emit('getParams', 'encoder-' + blockNum + '-' + (sublayer + 1) + '-LN')
        this.openLayerNorm(svg, 'encoder', openLayerNormOffsetX, openLayerNormOffsetY, blockNum - 1, sublayer, 1)
      } else if (openDetailedCoder == 'feed-forward-network') {
        this.openFeedForwardNetwork(svg, 'encoder', openFFNOffsetX, openFFNOffsetY, blockNum - 1, 1)
      }


      // 点击空白处 返回初始界面
      d3.select('#architectureSvg').on('click', function (event) {
        if (event.srcElement.nodeName == 'svg') {
          self.status = 'initial'
          d3.select('#architectureSvg')
            .transition()
            .duration(speed)
            .style('transform', `translate(${0}px,0px)`)
        }
      })
    },

    openDecoderBlock(svg, blockNum, sublayer, openDetailedCoder) {
      let moveOffsetX = -1200
      let speed = 1000
      let self = this
      let openSelfAttentionOffsetX = 2040
      let openSelfAttentionOffsetY = 80
      let openLayerNormOffsetX = openSelfAttentionOffsetX + 100
      let openLayerNormOffsetY = openSelfAttentionOffsetY
      let openFFNOffsetX = openLayerNormOffsetX
      let openFFNOffsetY = openLayerNormOffsetY

      d3.select('#architectureSvg')
        .transition()
        .duration(speed)
        .style('transform', `translate(${moveOffsetX}px,0px)`)

      // 删除重画 防止多次点击事件导致的重叠
      // svg.selectAll('*').remove()
      if (openDetailedCoder == 'self-attention' || openDetailedCoder == 'cross-attention' || openDetailedCoder == 'masked self-attention') {
        this.openSelfAttention(svg, 'decoder', openDetailedCoder, openSelfAttentionOffsetX, openSelfAttentionOffsetY, blockNum - 1, 1)
      } else if (openDetailedCoder == 'layer-normalization') {
        // 获取数据
        this.$emit('getParams', 'decoder-' + (blockNum + 1) + '-' + (sublayer + 1) + '-LN')
        this.openLayerNorm(svg, 'decoder', openLayerNormOffsetX, openLayerNormOffsetY, blockNum - 1, sublayer, 1)
      } else if (openDetailedCoder == 'feed-forward-network') {
        this.openFeedForwardNetwork(svg, 'decoder', openFFNOffsetX, openFFNOffsetY, blockNum - 1, 1)
      }
      // 点击空白处 返回初始界面
      d3.select('#architectureSvg').on('click', function (event) {
        if (event.srcElement.nodeName == 'svg') {
          self.status = 'initial'
          d3.select('#architectureSvg')
            .transition()
            .duration(speed)
            .style('transform', `translate(${0}px,0px)`)
        }
      })
    },

    openSelfAttention(svg, type, openDetailedCoder, offsetX, offsetY, blockNum, allOpacity) {
      this.blockStatus = 'attention'
      this.selfAttentionObj = [svg, type, openDetailedCoder, offsetX, offsetY, blockNum, allOpacity]
      svg.selectAll('*').remove()
      var self = this
      // let embeddingDataRange = type == 'encoder' ? getDataRange(this.encoder.embedding.output) : getDataRange(this.decoder.embedding.output)
      let inputData = type == 'encoder' ? this.encoder : this.decoder
      let textOffsetX = 500
      let xSize = 325;
      let ySize = 240;
      let tokenGap = 10
      let processGap = 25
      let headNodeWidth = 70
      let headNodeHeight = 30
      let attentionNodeWidth = 80
      let attentionNodeHeight = 50
      let concatAndLinearNodeWidth = 100
      let concatAndLinearNodeHeight = 50
      let colorScale = d3.interpolateRdBu;
      // 计算 attention output 内的 total datarange 
      let attentionOuputDataRangeArray = [];
      inputData.self_attn[blockNum].attention_output.forEach(attn_output => {
        attentionOuputDataRangeArray.push(getDataRange(attn_output));
      });

      let attentionOuputTotalDataRange = { max: -1E5, min: 1E5, };
      attentionOuputDataRangeArray.forEach(obj => {
        attentionOuputTotalDataRange.max = Math.max(attentionOuputTotalDataRange.max, obj.max);
        attentionOuputTotalDataRange.min = Math.min(attentionOuputTotalDataRange.min, obj.min);
      });
      let outputDataRange = getDataRange(inputData.self_attn[blockNum].output)
      let xSizeOfEachHead = 180;
      let ySizeOfEachHead = 55;
      let maximumCellSize = 30;
      let edgeOpacity = 0.5;
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);

      let openSelfAttentionPart = svg.append('g')
        .attr('id', 'open-self-attention-g')
        .attr('transform', `translate(${offsetX},${offsetY})`)
        .style('opacity', allOpacity)
      openSelfAttentionPart.append('text')
        .attr('class', 'label')
        .style('font-weight', 'bold')
        .attr('transform', `translate(${textOffsetX},${-20})`)
        .text(type == 'encoder' ? 'Multi-head Self-Attention Mechanism of Encoder Block #' + (blockNum + 1) : 'Multi-head Masked Self-Attention Mechanism of Decoder Block #' + (blockNum + 1));

      let inputGridGroupX = -150;
      let inputGridGroupY = 200;
      let inputTotalGridWidth = 0
      let inputTotalGridHeight = 0
      // 绘制 Input(需要区分self-attn还是cross-attn)
      if (openDetailedCoder == 'cross-attention') {
        inputGridGroupY = 50
      }
      let inputRawData = blockNum == 0 ? inputData.embedding.output : inputData.self_attn[blockNum - 1].output
      let inputDataRange = getDataRange(inputRawData)
      let inputConstraintGridCellWidth = getVisualizationSizeConstraint(inputRawData[0].length, 'x', xSize, ySize, 40);
      let inputConstraintGridCellHeight = 35
      let inputGridData = getGapGridData(inputRawData, inputConstraintGridCellWidth, inputConstraintGridCellHeight, tokenGap);
      let inputGridGroup = openSelfAttentionPart.append("g").attr("class", "grid").attr("transform", `translate(${inputGridGroupX},${inputGridGroupY})`);
      let inputGridRow = inputGridGroup.selectAll(".row")  // 绘制每一行
        .data(inputGridData).enter().append('g').attr('class', 'row');
      inputGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        // .style('stroke', d => d.row * inputGridData[0].length + d.col == this.legalHighlightsIndex ? 'black' : null)
        // .on('mouseover', (event, d) => {
        //   this.$emit('changeHilightsIndex', d.row * inputGridData[0].length + d.col)
        // })
        .style('fill', d => {
          let normlizedVal = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
          return colorScale(normlizedVal);
        });
      inputTotalGridWidth = inputConstraintGridCellWidth * inputRawData[0].length;
      inputTotalGridHeight = (inputConstraintGridCellHeight + tokenGap) * inputRawData.length;
      let inputGridText = openSelfAttentionPart.append('text').attr("text-anchor", "middle");
      if (openDetailedCoder == 'cross-attention') {
        inputGridText
          .attr('transform', `translate(${inputGridGroupX + inputTotalGridWidth / 2},${inputGridGroupY - 60})`)
          .attr('class', 'label')
          .selectAll('.tspan')
          .data([`Input(${inputRawData.length},${inputRawData[0].length}) to get Query`, `from decoder embedding`])
          .enter().append('tspan')
          .attr('x', 0)
          .attr('dy', '1.5em')
          .text(d => d);
      } else {
        inputGridText
          .attr('transform', `translate(${inputGridGroupX + inputTotalGridWidth / 2},${inputGridGroupY - 20})`)
          .attr('class', 'label')
          .text(`Input(${inputRawData.length},${inputRawData[0].length}) to get Query, Key, Value`);
      }
      // 绘制 cross-attn
      let inputCrossGridGroupX = 0
      let inputCrossGridGroupY = 0
      let inputCrossTotalGridWidth = 0
      let inputCrossTotalGridHeight = 0
      if (openDetailedCoder == 'cross-attention') {
        inputCrossGridGroupX = inputGridGroupX
        inputCrossGridGroupY = inputGridGroupY + inputTotalGridHeight + processGap * 2
        let inputCrossConstraintGridCellWidth = getVisualizationSizeConstraint(this.encoder.self_attn[5].output[0].length, 'x', xSize, ySize, 40);
        let inputCrossConstraintGridCellHeight = 35
        let inputCrossGridDataRange = getDataRange(this.encoder.self_attn[5].output)
        let inputCrossGridData = getGapGridData(this.encoder.self_attn[5].output, inputCrossConstraintGridCellWidth, inputCrossConstraintGridCellHeight, tokenGap);
        let inputCrossGridGroup = openSelfAttentionPart.append("g").attr("class", "grid").attr("transform", `translate(${inputCrossGridGroupX},${inputCrossGridGroupY})`);
        let inputCrossGridRow = inputCrossGridGroup.selectAll(".row")  // 绘制每一行
          .data(inputCrossGridData).enter().append('g').attr('class', 'row');
        inputCrossGridRow.selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          // .style('stroke', d => d.row * inputCrossGridData[0].length + d.col == this.legalHighlightsIndex ? 'black' : null)
          // .on('mouseover', (event, d) => {
          //   this.$emit('changeHilightsIndex', d.row * inputCrossGridData[0].length + d.col)
          // })
          .style('fill', d => {
            let normlizedVal = (d.text - inputCrossGridDataRange.min) / (inputCrossGridDataRange.max - inputCrossGridDataRange.min);
            return colorScale(normlizedVal);
          });
        inputCrossTotalGridWidth = inputCrossConstraintGridCellWidth * this.encoder.self_attn[5].output[0].length;
        inputCrossTotalGridHeight = (inputCrossConstraintGridCellHeight + tokenGap) * this.encoder.self_attn[5].output.length;
        let inputCrossGridText = openSelfAttentionPart.append('text').attr("text-anchor", "middle");
        inputCrossGridText
          .attr('transform', `translate(${inputCrossGridGroupX + inputCrossTotalGridWidth / 2},${inputCrossGridGroupY - 60})`)
          .attr('class', 'label')
          .selectAll('.tspan')
          .data([`Input(${this.encoder.embedding.output.length},${this.encoder.embedding.output[0].length}) to get Key, Value`, `from encoder output`])
          .enter().append('tspan')
          .attr('x', 0)
          .attr('dy', '1.5em')
          .text(d => d);

      }

      let instructiveArrow = require("../../src/assets/rightArrow_3.svg")
      let instructiveArrowWidth = 30
      let instructiveArrowHeight = 30
      let clickIcon = require("../../src/assets/click.svg")
      let clickIconWidth = 13
      let clickIconHeight = 13
      let instructiveArrowOffsetX_1 = inputGridGroupX + inputTotalGridWidth + 50
      let instructiveArrowOffsetY_1 = 60
      let instructiveText_1 = openSelfAttentionPart.append('g')
        .attr('transform', `translate(${instructiveArrowOffsetX_1},${instructiveArrowOffsetY_1})`)
      instructiveText_1.append('svg:image')
        .attr('xlink:href', instructiveArrow)
        .attr("width", instructiveArrowWidth)
        .attr("height", instructiveArrowHeight)
        .attr('transform', `rotate(250)`)
      instructiveText_1.append('svg:image')
        .attr('transform', `translate(${-85},${-40})`)
        .attr('xlink:href', clickIcon)
        .attr("width", clickIconWidth)
        .attr("height", clickIconHeight)
      instructiveText_1.append('text')
        .text('Click ')
        .attr("font-size", '10px')
        .attr("font-weight", 'bold')
        .attr("font-style", 'italic')
        .attr("fill", '#4a4a4a')
        .attr("x", -70)
        .attr("y", -30)
      instructiveText_1.append('text')
        .text('to learn')
        .attr("font-size", '10px')
        .attr("fill", '#4a4a4a')
        .attr("x", -40)
        .attr("y", -30)
      instructiveText_1.append('text')
        .text('how to generate Q,K,V!')
        .attr("font-size", '10px')
        .attr("fill", '#4a4a4a')
        .attr("x", -110)
        .attr("y", -15)
      let instructiveArrowOffsetX_2 = instructiveArrowOffsetX_1 + 100
      let instructiveArrowOffsetY_2 = instructiveArrowOffsetY_1 + 80
      let instructiveText_2 = openSelfAttentionPart.append('g')
        .attr('transform', `translate(${instructiveArrowOffsetX_2},${instructiveArrowOffsetY_2})`)
      instructiveText_2.append('svg:image')
        .attr('xlink:href', instructiveArrow)
        .attr("width", instructiveArrowWidth)
        .attr("height", instructiveArrowHeight)
        .attr('transform', `translate(0,-20) rotate(170)`)
      instructiveText_2.append('svg:image')
        .attr('transform', `translate(${-125},${-40})`)
        .attr('xlink:href', clickIcon)
        .attr("width", clickIconWidth)
        .attr("height", clickIconHeight)
      instructiveText_2.append('text')
        .text('Click ')
        .attr("font-size", '10px')
        .attr("font-weight", 'bold')
        .attr("font-style", 'italic')
        .attr("fill", '#4a4a4a')
        .attr("x", -110)
        .attr("y", -30)
      instructiveText_2.append('text')
        .text('to explore')
        .attr("font-size", '10px')
        .attr("fill", '#4a4a4a')
        .attr("x", -80)
        .attr("y", -30)
      instructiveText_2.append('text')
        .text('attention operation!')
        .attr("font-size", '10px')
        .attr("fill", '#4a4a4a')
        .attr("x", -120)
        .attr("y", -15)

      let linkData = [];
      for (let i = 0; i < 8; i++) {
        // 绘制 head
        let headOffsetY = 60 + (headNodeHeight + tokenGap * 6) * i
        let headOffsetX = inputGridGroupX + inputTotalGridWidth + processGap
        let unitHead = openSelfAttentionPart.append('g')
          .attr("id", 'self-attention-head-' + (i + 1))
          .attr('transform', `translate(${headOffsetX},${headOffsetY})`)
        unitHead.append('rect')
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", headNodeWidth)
          .attr("height", headNodeHeight)
          .attr('fill', 'rgb(235,235,235)')
          .attr('stroke', 'rgb(175,175,175)')
          .attr('stroke-width', 2)
        unitHead.append('text')
          .style("text-anchor", "middle")
          .style("dominant-baseline", "middle")
          .attr("x", headNodeWidth / 2)
          .attr("y", headNodeHeight / 2)
          .text('head #' + (i + 1))
          .attr("class", "label")
        unitHead.on('click', function () {
          self.$emit('openAttentionHead', 'openAttentionHead', type + '-' + openDetailedCoder + '-block-' + (blockNum + 1) + '-head-' + i)
          if (type == 'encoder') {
            self.$emit('getParams', type + '-' + (blockNum + 1) + '-full-self-attention')
          } else {
            if (openDetailedCoder == 'masked self-attention') {
              self.$emit('getParams', type + '-' + (blockNum + 1) + '-masked-self-attention')
            } else {
              self.$emit('getParams', type + '-' + (blockNum + 1) + '-full-cross-attention')
            }
          }
        })
          .style('cursor', 'hand')
        // 绘制attention operation
        let attentionOffsetY = 50 + (headNodeHeight + tokenGap * 6) * i
        let attentionOffsetX = headOffsetX + headNodeWidth + processGap
        let unitAttention = openSelfAttentionPart.append('g')
          .attr("id", 'self-attention-operation-' + (i + 1))
          .attr('transform', `translate(${attentionOffsetX},${attentionOffsetY})`)
        unitAttention.append('rect')
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", attentionNodeWidth)
          .attr("height", attentionNodeHeight)
          .attr('fill', 'rgb(235,235,235)')
          .attr('stroke', 'rgb(175,175,175)')
          .attr('stroke-width', 2)
        unitAttention.append('text')
          .attr('transform', `translate(${0},${-2})`)
          .selectAll('.tspan')
          .data([`attention`, `operation`])
          .enter().append('tspan')
          .attr('x', attentionNodeWidth / 2)
          .attr('dy', '1.3em')
          .text(d => d)
          .attr("class", "label")
          .style("text-anchor", "middle")
          .style("dominant-baseline", "middle")
        unitAttention.on('click', function () {
          self.$emit('openAttentionOperation', 'openAttentionOperation', type + '-' + openDetailedCoder + '-block-' + (blockNum + 1) + '-operation-' + i)
        })
          .style('cursor', 'hand')
        // 绘制 attention output of each head
        let attentionOutputOffsetY = 40 + (headNodeHeight + tokenGap * 6) * i
        let attentionOutputOffsetX = attentionOffsetX + attentionNodeWidth + processGap
        let unitAttentionOutput = openSelfAttentionPart.append('g')
          .attr("id", 'self-attention-output-' + (i + 1))
          .attr('transform', `translate(${attentionOutputOffsetX},${attentionOutputOffsetY})`)
        drawAttentionOutput(unitAttentionOutput, blockNum, i, inputData.self_attn, attentionOuputTotalDataRange)
        // 添加连线
        let inputHeadLinkData = {
          source: {
            x: inputGridGroupX + inputTotalGridWidth,
            y: openDetailedCoder == 'cross-attention' ? inputGridGroupY + (inputTotalGridHeight + inputCrossTotalGridHeight + processGap * 2) / 2 : inputGridGroupY + inputTotalGridHeight / 2,
          },
          target: {
            x: headOffsetX,
            y: headOffsetY + headNodeHeight / 2,
          },
          class: 'input-head-link',
          id: (i + 1)
        }
        let headOperationLinkData = {
          source: {
            x: headOffsetX + headNodeWidth,
            y: headOffsetY + headNodeHeight / 2,
          },
          target: {
            x: headOffsetX + headNodeWidth + processGap,
            y: headOffsetY + headNodeHeight / 2,
          },
          class: 'head-operation-link',
          id: (i + 1)
        }
        let operationOutputLinkData = {
          source: {
            x: headOffsetX + headNodeWidth + attentionNodeWidth + processGap,
            y: headOffsetY + headNodeHeight / 2,
          },
          target: {
            x: headOffsetX + headNodeWidth + attentionNodeWidth + processGap * 2,
            y: headOffsetY + headNodeHeight / 2,
          },
          class: 'operation-output-link',
          id: (i + 1)
        }
        let outputConcatLinkData = {
          source: {
            x: headOffsetX + headNodeWidth + attentionNodeWidth + xSizeOfEachHead + processGap * 2,
            y: headOffsetY + headNodeHeight / 2,
          },
          target: {
            x: headOffsetX + headNodeWidth + attentionNodeWidth + xSizeOfEachHead + processGap * 3,
            y: openDetailedCoder == 'cross-attention' ? inputGridGroupY + (inputTotalGridHeight + inputCrossTotalGridHeight + processGap * 2) / 2 : inputGridGroupY + inputTotalGridHeight / 2,
          },
          class: 'output-concat-link',
          id: (i + 1)
        }
        linkData.push(inputHeadLinkData)
        linkData.push(headOperationLinkData)
        linkData.push(operationOutputLinkData)
        linkData.push(outputConcatLinkData)
      }
      openSelfAttentionPart.append('text')
        .attr("text-anchor", "middle")
        .attr('transform', `translate(${inputGridGroupX + inputTotalGridWidth + headNodeWidth + attentionNodeWidth + processGap * 3 + xSizeOfEachHead / 2},${offsetY - 60})`)
        .attr('class', 'label')
        .text(`Attention output of each head(${inputData.self_attn[blockNum].attention_output[0].length},${inputData.self_attn[blockNum].attention_output[0][0].length})`);

      // 绘制 concatenate+linear
      let concatAndLinearOffsetX = inputGridGroupX + inputTotalGridWidth + headNodeWidth + attentionNodeWidth + processGap * 4 + xSizeOfEachHead
      let concatAndLinearOffsetY = openDetailedCoder == 'cross-attention' ? inputGridGroupY + (inputTotalGridHeight + inputCrossTotalGridHeight + processGap * 2 - concatAndLinearNodeHeight) / 2 : inputGridGroupY + (inputTotalGridHeight - concatAndLinearNodeHeight) / 2
      let concatAndLinear = openSelfAttentionPart.append('g')
        .attr('transform', `translate(${concatAndLinearOffsetX},${concatAndLinearOffsetY})`)
      concatAndLinear.append('rect')
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("width", concatAndLinearNodeWidth)
        .attr("height", concatAndLinearNodeHeight)
        .attr('fill', 'rgb(235,235,235)')
        .attr('stroke', 'rgb(175,175,175)')
        .attr('stroke-width', 2)
      concatAndLinear.append('text')
        .attr('transform', `translate(${0},${-2})`)
        .selectAll('.tspan')
        .data([`concatenate`, `& linear`])
        .enter().append('tspan')
        .attr('x', concatAndLinearNodeWidth / 2)
        .attr('dy', '1.3em')
        .text(d => d)
        .attr("class", "label")
        .style("text-anchor", "middle")
        .style("dominant-baseline", "middle")
      concatAndLinear.on('click', function () {
        self.$emit('openAttentionConcaAndLinear', 'openAttentionConcaAndLinear', type + '-' + openDetailedCoder + '-block-' + (blockNum + 1) + '-ConcaAndLinear')
        self.$emit('getParams', 'generator-linear')
      })
        .style('cursor', 'hand')
      let instructiveArrowOffsetX_3 = concatAndLinearNodeWidth - 60
      let instructiveArrowOffsetY_3 = concatAndLinearNodeHeight
      let instructiveText_3 = concatAndLinear.append('g')
        .attr('transform', `translate(${instructiveArrowOffsetX_3},${instructiveArrowOffsetY_3})`)
        .attr('id', "instructiveSvg")
        .attr('opacity', 1)
      instructiveText_3.append('svg:image')
        .attr('xlink:href', instructiveArrow)
        .attr("width", instructiveArrowWidth)
        .attr("height", instructiveArrowHeight)
        .attr('transform', 'rotate(50)')
      instructiveText_3.append('svg:image')
        .attr('transform', `translate(${15},${10})`)
        .attr('xlink:href', clickIcon)
        .attr("width", clickIconWidth)
        .attr("height", clickIconHeight)
      instructiveText_3.append('text')
        .text('Click')
        .attr("font-size", '10px')
        .attr("font-weight", 'bold')
        .attr("font-style", 'italic')
        .attr("fill", '#4a4a4a')
        .attr("x", 30)
        .attr("y", 20)
      instructiveText_3.append('text')
        .text('to')
        .attr("font-size", '10px')
        .attr("fill", '#4a4a4a')
        .attr("x", 60)
        .attr("y", 20)
      instructiveText_3.append('text')
        .text('learn more!')
        .attr("font-size", '10px')
        .attr("fill", '#4a4a4a')
        .attr("x", 20)
        .attr("y", 33)
      // 绘制 final output
      let outputGridGroupX = concatAndLinearOffsetX + concatAndLinearNodeWidth + processGap;
      let outputGridGroupY = openDetailedCoder == 'cross-attention' ? inputGridGroupY + (inputTotalGridHeight + inputCrossTotalGridHeight) / 2 : inputGridGroupY
      // let outputGridGroupY =concatAndLinearOffsetY
      let outputData = inputData.self_attn[blockNum].output;
      let outputConstraintGridCellWidth = getVisualizationSizeConstraint(outputData[0].length, 'x', xSize, ySize, 40);
      let outputConstraintGridCellHeight = 35
      let outputGridData = getGapGridData(outputData, outputConstraintGridCellWidth, outputConstraintGridCellHeight, tokenGap);
      let outputGridGroup = openSelfAttentionPart.append("g").attr("class", "grid").attr("transform", `translate(${outputGridGroupX},${outputGridGroupY})`);
      let outputGridRow = outputGridGroup.selectAll(".row")  // 绘制每一行
        .data(outputGridData).enter().append('g').attr('class', 'row');
      outputGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('fill', d => {
          let normlizedVal = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
          return colorScale(normlizedVal);
        });
      let outputTotalGridWidth = outputConstraintGridCellWidth * outputData[0].length;
      // let outputTotalGridHeight = (outputConstraintGridCellHeight+tokenGap) * outputData.length;
      let outputGridText = openSelfAttentionPart.append('text').attr("text-anchor", "middle");
      outputGridText
        .attr('transform', `translate(${outputGridGroupX + outputTotalGridWidth / 2},${outputGridGroupY - 60})`)
        .attr('class', 'label')
        .attr('dy', '.3em')
        // .text(`Final Output (${outputData.length},${outputData[0].length}) of Multi-Head Attention`);
        .selectAll('.tspan')
        .data([`Final Output (${outputData.length},${outputData[0].length})`, `of Multi-Head Attention`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);


      // 绘制 attention output of each head
      function drawAttentionOutput(svg, blockNum, headNum, inputData, dataRange) {
        let attentionOuputData = inputData[blockNum].attention_output[headNum];
        let attentionOuputConstraintGridCellWidth = getVisualizationSizeConstraint(attentionOuputData[0].length, 'x', xSizeOfEachHead, ySizeOfEachHead * 1.25, maximumCellSize);
        let attentionOuputConstraintGridCellHeight = getVisualizationSizeConstraint(attentionOuputData.length, 'y', xSizeOfEachHead, ySizeOfEachHead * 1.25, maximumCellSize);
        let attentionOuputGridData = getGridData(attentionOuputData, attentionOuputConstraintGridCellWidth, attentionOuputConstraintGridCellHeight);
        let attentionOuputGridGroup = svg.append("g").attr("class", "grid")
        let attentionOuputGridRow = attentionOuputGridGroup.selectAll(".row")  // 绘制每一行
          .data(attentionOuputGridData).enter().append('g').attr('class', 'row');
        attentionOuputGridRow.selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('fill', d => {
            let normlizedVal = (d.text - dataRange.min) / (dataRange.max - dataRange.min);
            return colorScale(normlizedVal);
          });
      }

      // 添加连线
      let concatFinalOutputLinkData = {
        source: {
          x: outputGridGroupX - processGap,
          y: openDetailedCoder == 'cross-attention' ? inputGridGroupY + (inputTotalGridHeight + inputCrossTotalGridHeight + processGap * 2) / 2 : inputGridGroupY + inputTotalGridHeight / 2,
        },
        target: {
          x: outputGridGroupX,
          y: openDetailedCoder == 'cross-attention' ? inputGridGroupY + (inputTotalGridHeight + inputCrossTotalGridHeight + processGap * 2) / 2 : inputGridGroupY + inputTotalGridHeight / 2,
        },
        class: 'concat-final-link',
      }
      linkData.push(concatFinalOutputLinkData)
      let edgeGroup = openSelfAttentionPart.append("g")
        .style('opacity', allOpacity)
        .attr("class", "edge-group");
      edgeGroup.selectAll("path.edge").data(linkData).enter().append('path')
        .attr('id', d => d.id != undefined ? d.id : null)
        .attr('class', d => d.class != undefined ? d.class : null)
        .attr('d', d => linkGen({ source: d.source, target: d.target }))
        .style('fill', 'none')
        .style('stroke-width', '2px')
        .style('opacity', edgeOpacity)
        .style('stroke', 'rgb(175, 175, 175)');

    },

    openLayerNorm(svg, type, offsetX, offsetY, blockNum, sublayer) {
      this.blockStatus = 'layer-normalization'
      this.layerNormObj = [svg, type, offsetX, offsetY, blockNum, sublayer]
      svg.selectAll('*').remove()
      var self = this
      let textOffsetX = 500
      let xSize = 325
      let ySize = 240
      let tokenGap = 10
      let processGap = 20
      let operatorRadius = 10
      let leftbracketWidth = 100
      let leftbracketHeight = 100
      let leftbracket = require("../../src/assets/leftbracket.svg")
      let rightbracket = require("../../src/assets/rightbracket.svg")
      let colorScale = d3.interpolateRdBu;
      let paramsColorScale = d3.interpolateBrBG;
      let alphaDataRange = getDataRange([this.layerNormParams.alpha]);
      let betaDataRange = getDataRange([this.layerNormParams.beta]);
      let inputDataRange = type == 'encoder' ? getDataRange(this.encoder.LN[blockNum][sublayer].input) : getDataRange(this.decoder.LN[blockNum][sublayer].input)
      let outputDataRange = type == 'encoder' ? getDataRange(this.encoder.LN[blockNum][sublayer].output) : getDataRange(this.decoder.LN[blockNum][sublayer].output)
      let stdDataRange = type == 'encoder' ? getDataRange([this.encoder.LN[blockNum][sublayer].std]) : getDataRange([this.decoder.LN[blockNum][sublayer].std])
      let openLayerNormPart = svg.append('g')
        .attr('id', 'open-layer-normalization-g')
        .attr('transform', `translate(${offsetX},${offsetY})`)
      openLayerNormPart.append('text')
        .attr('class', 'label')
        .style('font-weight', 'bold')
        .attr('transform', `translate(${textOffsetX - 80},${-20})`)
        .text(type == 'encoder' ? 'Layer Normalization of Encoder Block #' + (blockNum + 1) : 'Layer Normalization of Decoder Block #' + (blockNum + 1));

      // 绘制 alpha
      let alphaGridGroupX = 10;
      let alphaGridGroupY = 50;
      let alphaConstraintGridCellWidth = getVisualizationSizeConstraint(this.layerNormParams.alpha.length, 'x', xSize, ySize, 40);
      let alphaConstraintGridCellHeight = 35
      let alphaGridData = getGapGridData([this.layerNormParams.alpha], alphaConstraintGridCellWidth, alphaConstraintGridCellHeight, tokenGap);
      let alphaGridGroup = openLayerNormPart.append("g").attr("class", "grid").attr("transform", `translate(${alphaGridGroupX},${alphaGridGroupY})`);
      let alphaGridRow = alphaGridGroup.selectAll(".row")  // 绘制每一行
        .data(alphaGridData).enter().append('g').attr('class', 'row');
      console.log(alphaGridRow)
      alphaGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * alphaGridData[0].length + d.col == (this.highlightsIndex % alphaGridData[0].length) ? 'black' : null)
        .style('fill', d => {
          let normlizedVal = (d.text - alphaDataRange.min) / (alphaDataRange.max - alphaDataRange.min);
          return paramsColorScale(normlizedVal);
        });
      let alphaTotalGridWidth = alphaConstraintGridCellWidth * this.layerNormParams.alpha.length;
      let alphaTotalGridHeight = alphaConstraintGridCellHeight;
      let alphaGridText = openLayerNormPart.append('text').attr("text-anchor", "middle");
      alphaGridText
        .attr('transform', `translate(${alphaGridGroupX + alphaTotalGridWidth / 2},${alphaGridGroupY - 20})`)
        .attr('class', 'label')
        .text(`Parameter: Alpha(${1},${this.layerNormParams.alpha.length})`);

      // cross-multiply
      let crossMultiplyOffsetX = alphaGridGroupX + alphaTotalGridWidth / 2
      let crossMultiplyOffsetY = alphaGridGroupY + alphaTotalGridHeight + processGap
      let crossMultiply = openLayerNormPart.append('g')
        .attr('id', 'crossmultiply-g')
        .attr('transform', `translate(${crossMultiplyOffsetX},${crossMultiplyOffsetY})`)
      crossMultiply.append('circle')
        .attr('fill', 'rgb(235,235,235)')
        .attr('stroke', 'rgb(175,175,175)')
        .attr('stroke-width', 2)
        .attr('r', operatorRadius)
      crossMultiply.append('text')
        .attr('y', 5.5)
        .attr('font-weight', 'bold')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('fill', 'rgb(175, 175, 175)')
        .attr('font-size', '23px')
        .text('*')

      // input
      let inputData = type == 'encoder' ? this.encoder.LN[blockNum][sublayer].input : this.decoder.LN[blockNum][sublayer].input
      let inputConstraintGridCellWidth = getVisualizationSizeConstraint(inputData[0].length, 'x', xSize, ySize, 40);
      let inputConstraintGridCellHeight = 35
      let inputGridGroupX = alphaGridGroupX - 100;
      let inputGridGroupY = crossMultiplyOffsetY + processGap + (inputConstraintGridCellHeight + tokenGap) * Math.round(this.encoder.LN[blockNum][0].input.length / 2) / 6;
      let inputGridData = getGapGridData(inputData, inputConstraintGridCellWidth, inputConstraintGridCellHeight, tokenGap);
      let inputGridGroup = openLayerNormPart.append("g").attr("class", "grid").attr("transform", `translate(${inputGridGroupX},${inputGridGroupY})`);
      let inputGridRow = inputGridGroup.selectAll(".row")  // 绘制每一行
        .data(inputGridData).enter().append('g').attr('class', 'row');
      inputGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * inputGridData[0].length + d.col == this.highlightsIndex ? 'black' : null)
        .on('mouseover', (event, d) => {
          self.layerNormObj = [svg, type, offsetX, offsetY, blockNum, sublayer]
          this.$emit('changeHilightsIndex', d.row * inputGridData[0].length + d.col)
          layerNormTooltip(tooltipGroup, 'input', event, self.highlightsIndex, [self.layerNormParams.alpha], inputData, meanColomnData, stdColomnData, [self.layerNormParams.beta], outputData)
        })
        .style('cursor', 'hand')
        .on('mouseout', () => {
          d3.select('#layernorm-tooltip').selectAll('*').remove();
        })
        .style('fill', d => {
          let normlizedVal = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
          return colorScale(normlizedVal);
        });
      let inputTotalGridWidth = inputConstraintGridCellWidth * inputData[0].length;
      let inputTotalGridHeight = (inputConstraintGridCellHeight + tokenGap) * inputData.length;
      let inputGridText = openLayerNormPart.append('text').attr("text-anchor", "middle");
      inputGridText
        .attr('transform', `translate(${inputGridGroupX + inputTotalGridWidth / 2},${inputGridGroupY - 20})`)
        .attr('class', 'label')
        .text(`Input(${inputData.length},${inputData[0].length})`);

      // brackets
      let leftbracketOffsetX = alphaGridGroupX - 200
      let leftbracketOffsetY = inputGridGroupY + inputTotalGridHeight / 2 - 50
      let rightbracketOffsetX = leftbracketOffsetX + 490
      let rightbracketOffsetY = leftbracketOffsetY
      openLayerNormPart.append('svg:image')
        .attr('xlink:href', leftbracket)
        .attr("x", leftbracketOffsetX)
        .attr("y", leftbracketOffsetY)
        .attr("width", leftbracketWidth)
        .attr("height", leftbracketHeight)
      openLayerNormPart.append('svg:image')
        .attr('xlink:href', rightbracket)
        .attr("x", rightbracketOffsetX)
        .attr("y", rightbracketOffsetY)
        .attr("width", leftbracketWidth)
        .attr("height", leftbracketHeight)

      // minus
      let minusOffsetX = inputGridGroupX + inputTotalGridWidth + processGap
      let minusOffsetY = inputGridGroupY + inputTotalGridHeight / 2
      let minus = openLayerNormPart.append('g')
        .attr('id', 'minus-g')
        .attr('transform', `translate(${minusOffsetX},${minusOffsetY})`)
      minus.append('circle')
        .attr('fill', 'rgb(235,235,235)')
        .attr('stroke', 'rgb(175,175,175)')
        .attr('stroke-width', 2)
        .attr('r', operatorRadius)
      minus.append('text')
        .attr('class', 'operatorText')
        .text('—')

      // mean
      let meanData = type == 'encoder' ? this.encoder.LN[blockNum][sublayer].mean : this.decoder.LN[blockNum][sublayer].mean
      let meanColomnData = []
      meanData.forEach(d => { meanColomnData.push([d]) })
      let meanConstraintGridCellWidth = getVisualizationSizeConstraint(meanColomnData[0].length, 'x', xSize, ySize, 35);
      let meanConstraintGridCellHeight = 35
      let meanGridGroupX = minusOffsetX + processGap;
      let meanGridGroupY = inputGridGroupY;
      let meanGridData = getGapGridData(meanColomnData, meanConstraintGridCellWidth, meanConstraintGridCellHeight, tokenGap);
      let meanGridGroup = openLayerNormPart.append("g").attr("class", "grid").attr("transform", `translate(${meanGridGroupX},${meanGridGroupY})`);
      let meanGridRow = meanGridGroup.selectAll(".row")  // 绘制每一行
        .data(meanGridData).enter().append('g').attr('class', 'row');
      meanGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * meanGridData[0].length + d.col == parseInt(this.highlightsIndex / 512) ? 'black' : null)
        .style('fill', d => {
          let normlizedVal = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
          return colorScale(normlizedVal);
        });
      let meanTotalGridWidth = meanConstraintGridCellWidth * meanColomnData[0].length;
      // let meanTotalGridHeight = (meanConstraintGridCellHeight + tokenGap) * this.encoder.LN[blockNum][0].mean.length;
      let meanGridText = openLayerNormPart.append('text').attr("text-anchor", "middle");
      meanGridText
        .attr('transform', `translate(${meanGridGroupX + meanTotalGridWidth / 2},${meanGridGroupY - 20})`)
        .attr('class', 'label')
        .text(`Mean`);

      // division
      let divisionOffsetX = meanGridGroupX + meanTotalGridWidth + processGap * 3
      let divisionOffsetY = minusOffsetY
      let division = openLayerNormPart.append('g')
        .attr('id', 'division-g')
        .attr('transform', `translate(${divisionOffsetX},${divisionOffsetY})`)
      division.append('circle')
        .attr('fill', 'rgb(235,235,235)')
        .attr('stroke', 'rgb(175,175,175)')
        .attr('stroke-width', 2)
        .attr("r", operatorRadius)
      division.append('text')
        .attr("class", "operatorText")
        .text('/')


      // std
      let stdData = type == 'encoder' ? this.encoder.LN[blockNum][sublayer].std : this.decoder.LN[blockNum][sublayer].std
      let stdColomnData = []
      stdData.forEach(d => { stdColomnData.push([d]) })
      let stdConstraintGridCellWidth = getVisualizationSizeConstraint(stdColomnData[0].length, 'x', xSize, ySize, 35);
      let stdConstraintGridCellHeight = 35
      let stdGridGroupX = divisionOffsetX + processGap;
      let stdGridGroupY = inputGridGroupY;
      let stdGridData = getGapGridData(stdColomnData, stdConstraintGridCellWidth, stdConstraintGridCellHeight, tokenGap);
      let stdGridGroup = openLayerNormPart.append("g").attr("class", "grid").attr("transform", `translate(${stdGridGroupX},${stdGridGroupY})`);
      let stdGridRow = stdGridGroup.selectAll(".row")  // 绘制每一行
        .data(stdGridData).enter().append('g').attr('class', 'row');
      stdGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * stdGridData[0].length + d.col == parseInt(this.highlightsIndex / 512) ? 'black' : null)
        .style('fill', d => {
          let normlizedVal = (d.text - stdDataRange.min) / (stdDataRange.max - stdDataRange.min);
          return colorScale(normlizedVal);
        });
      let stdTotalGridWidth = stdConstraintGridCellWidth * stdColomnData[0].length;
      // let stdTotalGridHeight = (stdConstraintGridCellHeight + tokenGap) * this.encoder.LN[blockNum][0].std.length;
      let stdGridText = openLayerNormPart.append('text').attr("text-anchor", "middle");
      stdGridText
        .attr('transform', `translate(${stdGridGroupX + stdTotalGridWidth / 2},${stdGridGroupY - 20})`)
        .attr('class', 'label')
        .text(`Std`);

      // plus
      let plusOffsetX = crossMultiplyOffsetX
      let plusOffsetY = inputGridGroupY + inputTotalGridHeight + processGap
      let plus = openLayerNormPart.append('g')
        .attr('id', 'plus-g')
        .attr('transform', `translate(${plusOffsetX},${plusOffsetY})`)
      plus.append('circle')
        .attr('fill', 'rgb(235,235,235)')
        .attr('stroke', 'rgb(175,175,175)')
        .attr('stroke-width', 2)
        .attr("r", operatorRadius)
      plus.append('text')
        .attr("class", "operatorText")
        .text('+')

      // beta
      let betaGridGroupX = alphaGridGroupX
      let betaGridGroupY = plusOffsetY + processGap * 3
      let betaConstraintGridCellWidth = getVisualizationSizeConstraint(this.layerNormParams.beta.length, 'x', xSize, ySize, 40);
      let betaConstraintGridCellHeight = 35
      let betaGridData = getGapGridData([this.layerNormParams.beta], betaConstraintGridCellWidth, betaConstraintGridCellHeight, tokenGap);
      let betaGridGroup = openLayerNormPart.append("g").attr("class", "grid").attr("transform", `translate(${betaGridGroupX},${betaGridGroupY})`);
      let betaGridRow = betaGridGroup.selectAll(".row")  // 绘制每一行
        .data(betaGridData).enter().append('g').attr('class', 'row');
      betaGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * betaGridData[0].length + d.col == (this.highlightsIndex % betaGridData[0].length) ? 'black' : null)
        .style('fill', d => {
          let normlizedVal = (d.text - betaDataRange.min) / (betaDataRange.max - betaDataRange.min);
          return paramsColorScale(normlizedVal);
        });
      let betaTotalGridWidth = betaConstraintGridCellWidth * this.layerNormParams.beta.length;
      // let betaTotalGridHeight = betaConstraintGridCellHeight;
      let betaGridText = openLayerNormPart.append('text').attr("text-anchor", "middle");
      betaGridText
        .attr('transform', `translate(${betaGridGroupX + betaTotalGridWidth / 2},${betaGridGroupY - 20})`)
        .attr('class', 'label')
        .text(`Parameter: Beta(${1},${this.layerNormParams.beta.length})`);

      // equation
      let equationOffsetX = stdGridGroupX + stdTotalGridWidth + processGap * 3
      let equationOffsetY = minusOffsetY
      let equation = openLayerNormPart.append('g')
        .attr('id', 'equation-g')
        .attr('transform', `translate(${equationOffsetX},${equationOffsetY})`)
      equation.append('circle')
        .attr('fill', 'rgb(235,235,235)')
        .attr('stroke', 'rgb(175,175,175)')
        .attr('stroke-width', 2)
        .attr("r", operatorRadius)
      equation.append('text')
        .attr("class", "operatorText")
        .text('=')

      // output
      let outputData = type == 'encoder' ? this.encoder.LN[blockNum][sublayer].output : this.decoder.LN[blockNum][sublayer].output
      let outputConstraintGridCellWidth = getVisualizationSizeConstraint(outputData[0].length, 'x', xSize, ySize, 40);
      let outputConstraintGridCellHeight = 35
      let outputGridGroupX = equationOffsetX + processGap;
      let outputGridGroupY = inputGridGroupY;
      let outputGridData = getGapGridData(outputData, outputConstraintGridCellWidth, outputConstraintGridCellHeight, tokenGap);
      let outputGridGroup = openLayerNormPart.append("g").attr("class", "grid").attr("transform", `translate(${outputGridGroupX},${outputGridGroupY})`);
      let outputGridRow = outputGridGroup.selectAll(".row")  // 绘制每一行
        .data(outputGridData).enter().append('g').attr('class', 'row');
      outputGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * outputGridData[0].length + d.col == this.highlightsIndex ? 'black' : null)
        .on('mouseover', (event, d) => {
          self.layerNormObj = [svg, type, offsetX, offsetY, blockNum, sublayer]
          this.$emit('changeHilightsIndex', d.row * outputGridData[0].length + d.col)// this.$emit('changeEquationIndex',newEquationIndex)
          layerNormTooltip(tooltipGroup, 'output', event, self.highlightsIndex, [self.layerNormParams.alpha], inputData, meanColomnData, stdColomnData, [self.layerNormParams.beta], outputData)
        })
        .style('cursor', 'hand')
        .on('mouseout', () => {
          d3.select('#layernorm-tooltip').selectAll('*').remove();
        })
        .style('fill', d => {
          let normlizedVal = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
          return colorScale(normlizedVal);
        });
      let outputTotalGridWidth = outputConstraintGridCellWidth * outputData[0].length;
      // let outputTotalGridHeight = (outputConstraintGridCellHeight + tokenGap) * this.encoder.LN[blockNum][0].output.length;
      let outputGridText = openLayerNormPart.append('text').attr("text-anchor", "middle");
      outputGridText
        .attr('transform', `translate(${outputGridGroupX + outputTotalGridWidth / 2},${outputGridGroupY - 20})`)
        .attr('class', 'label')
        .text(`Output(${outputData.length},${outputData[0].length})`);

      // tooltip
      let tooltipGroup = openLayerNormPart.append("g")
        .attr('id', 'layernorm-tooltip')

      function layerNormTooltip(svg, mouseoverType, event, highlightIndex, alphaData, inputData, meanData, stdData, betaData, outputData) {
        let offsetX = mouseoverType == 'input' ? event.screenX - 900 : event.screenX - 1300
        let offsetY = event.screenY - 250
        let processGap = 20
        let rectWidth = 500
        let rectHeight = 100
        let backgroundOpacity = 0.8
        let gridLength = 35
        let xSize = 325
        let ySize = 240
        let fontSize = '10px'
        let opacity = 1
        let alphaSingleGridGroupX = 20
        let alphaSingleGridGroupY = rectHeight / 2 - 25

        let layerNormTooltipPart = svg.append('g')
          .attr('id', 'detailed-layernorm')
          .attr('transform', `translate(${offsetX},${offsetY})`)
        layerNormTooltipPart.append('rect')
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("width", rectWidth)
          .attr("height", rectHeight)
          .attr("fill", "rgb(235, 235, 235)")
          .attr('stroke', 'rgb(175, 175, 175)')
          .attr('stroke-width', 1)
          .style('opacity', backgroundOpacity)

        // alpha single grid
        let alphaSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let alphaSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let alphaSingleGridData = getGridData([[alphaData[0][highlightIndex % alphaData[0].length]]]
          , alphaSingleConstraintGridCellWidth, alphaSingleConstraintGridCellHeight);
        let alphaSingleGridGroup = layerNormTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${alphaSingleGridGroupX},${alphaSingleGridGroupY})`);
        let alphaSingleGridRow = alphaSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(alphaSingleGridData).enter().append('g').attr('class', 'row');
        alphaSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - alphaDataRange.min) / (alphaDataRange.max - alphaDataRange.min);
            return paramsColorScale(normlizedVal);
          });
        alphaSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - alphaDataRange.min) / (alphaDataRange.max - alphaDataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);
        let alphaSingleGridText = layerNormTooltipPart.append('text').attr("text-anchor", "middle");
        alphaSingleGridText
          .attr('transform', `translate(${alphaSingleGridGroupX + gridLength / 2},${alphaSingleGridGroupY + gridLength + 20})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`alpha`);

        // cross multiply
        let crossMultiplyOffsetX = alphaSingleGridGroupX + alphaSingleConstraintGridCellWidth + processGap
        let crossMultiplyOffsetY = alphaSingleGridGroupY + alphaSingleConstraintGridCellWidth / 2
        let crossMultiply = layerNormTooltipPart.append('g')
          .attr('id', 'cross-multiply-g')
          .attr('transform', `translate(${crossMultiplyOffsetX},${crossMultiplyOffsetY})`)
        crossMultiply.append('circle')
          .attr('fill', 'rgb(235,235,235)')
          .attr('stroke', 'rgb(175,175,175)')
          .attr('stroke-width', 2)
          .attr('r', operatorRadius)
        crossMultiply.append('text')
          .attr('y', 5.5)
          .attr('font-weight', 'bold')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', 'rgb(175, 175, 175)')
          .attr('font-size', '23px')
          .text('*')

        // brackets
        let leftbracketWidth = 20
        let leftbracketHeight = 20
        let leftbracket = require("../../src/assets/leftbracket.svg")
        let rightbracket = require("../../src/assets/rightbracket.svg")
        let leftbracketOffsetX = crossMultiplyOffsetX + 8
        let leftbracketOffsetY = crossMultiplyOffsetY - 10
        let rightbracketOffsetX = leftbracketOffsetX + 150
        let rightbracketOffsetY = leftbracketOffsetY
        layerNormTooltipPart.append('svg:image')
          .attr('xlink:href', leftbracket)
          .attr("x", leftbracketOffsetX)
          .attr("y", leftbracketOffsetY)
          .attr("width", leftbracketWidth)
          .attr("height", leftbracketHeight)
        layerNormTooltipPart.append('svg:image')
          .attr('xlink:href', rightbracket)
          .attr("x", rightbracketOffsetX)
          .attr("y", rightbracketOffsetY)
          .attr("width", leftbracketWidth)
          .attr("height", leftbracketHeight)

        // input single grid
        let inputSingleGridGroupX = leftbracketOffsetX + processGap + 10
        let inputSingleGridGroupY = alphaSingleGridGroupY
        let inputSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let inputSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let inputSingleGridData = getGridData([[inputData[Math.floor(highlightIndex / inputData[0].length)][highlightIndex % inputData[0].length]]]
          , inputSingleConstraintGridCellWidth, inputSingleConstraintGridCellHeight);
        let inputSingleGridGroup = layerNormTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${inputSingleGridGroupX},${inputSingleGridGroupY})`);
        let inputSingleGridRow = inputSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(inputSingleGridData).enter().append('g').attr('class', 'row');
        inputSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
            return colorScale(normlizedVal);
          });
        inputSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);

        let inputSingleGridText = layerNormTooltipPart.append('text').attr("text-anchor", "middle");
        inputSingleGridText
          .attr('transform', `translate(${inputSingleGridGroupX + gridLength / 2},${inputSingleGridGroupY + gridLength + 20})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`input`);

        // minus
        let minusOffsetX = inputSingleGridGroupX + inputSingleConstraintGridCellWidth + processGap
        let minusOffsetY = crossMultiplyOffsetY
        let minus = layerNormTooltipPart.append('g')
          .attr('id', 'minus-g')
          .attr('transform', `translate(${minusOffsetX},${minusOffsetY})`)
        minus.append('circle')
          .attr('fill', 'rgb(235,235,235)')
          .attr('stroke', 'rgb(175,175,175)')
          .attr('stroke-width', 2)
          .attr('r', operatorRadius)
        minus.append('text')
          .attr('class', 'operatorText')
          .text('—')


        // mean single grid
        let meanSingleGridGroupX = minusOffsetX + processGap
        let meanSingleGridGroupY = inputSingleGridGroupY
        let meanSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let meanSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let meanSingleGridData = getGridData([[meanData[parseInt(highlightIndex / inputData[0].length)][0]]]
          , meanSingleConstraintGridCellWidth, meanSingleConstraintGridCellHeight);
        let meanSingleGridGroup = layerNormTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${meanSingleGridGroupX},${meanSingleGridGroupY})`);
        let meanSingleGridRow = meanSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(meanSingleGridData).enter().append('g').attr('class', 'row');
        meanSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
            return colorScale(normlizedVal);
          });
        meanSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);

        let meanSingleGridText = layerNormTooltipPart.append('text').attr("text-anchor", "middle");
        meanSingleGridText
          .attr('transform', `translate(${meanSingleGridGroupX + gridLength / 2},${meanSingleGridGroupY + gridLength + 20})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`mean`);

        // division
        let divisionOffsetX = meanSingleGridGroupX + meanSingleConstraintGridCellWidth + processGap * 2
        let divisionOffsetY = minusOffsetY
        let division = layerNormTooltipPart.append('g')
          .attr('id', 'division-g')
          .attr('transform', `translate(${divisionOffsetX},${divisionOffsetY})`)
        division.append('circle')
          .attr('fill', 'rgb(235,235,235)')
          .attr('stroke', 'rgb(175,175,175)')
          .attr('stroke-width', 2)
          .attr("r", operatorRadius)
        division.append('text')
          .attr("class", "operatorText")
          .text('/')


        // std single grid
        let stdSingleGridGroupX = minusOffsetX + processGap * 6
        let stdSingleGridGroupY = inputSingleGridGroupY
        let stdSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let stdSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let stdSingleGridData = getGridData([[stdData[Math.floor(highlightIndex / inputData[0].length)][0]]]
          , stdSingleConstraintGridCellWidth, stdSingleConstraintGridCellHeight);
        let stdSingleGridGroup = layerNormTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${stdSingleGridGroupX},${stdSingleGridGroupY})`);
        let stdSingleGridRow = stdSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(stdSingleGridData).enter().append('g').attr('class', 'row');
        stdSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - stdDataRange.min) / (stdDataRange.max - stdDataRange.min);
            return colorScale(normlizedVal);
          });
        stdSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - stdDataRange.min) / (stdDataRange.max - stdDataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);

        let stdSingleGridText = layerNormTooltipPart.append('text').attr("text-anchor", "middle");
        stdSingleGridText
          .attr('transform', `translate(${stdSingleGridGroupX + gridLength / 2},${stdSingleGridGroupY + gridLength + 20})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`std`);

        // plus
        let plusOffsetX = stdSingleGridGroupX + stdSingleConstraintGridCellWidth + processGap
        let plusOffsetY = divisionOffsetY
        let plus = layerNormTooltipPart.append('g')
          .attr('id', 'plus-g')
          .attr('transform', `translate(${plusOffsetX},${plusOffsetY})`)
        plus.append('circle')
          .attr('fill', 'rgb(235,235,235)')
          .attr('stroke', 'rgb(175,175,175)')
          .attr('stroke-width', 2)
          .attr("r", operatorRadius)
        plus.append('text')
          .attr("class", "operatorText")
          .text('+')

        // beta single grid
        let betaSingleGridGroupX = plusOffsetX + processGap
        let betaSingleGridGroupY = inputSingleGridGroupY
        let betaSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let betaSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let betaSingleGridData = getGridData([[betaData[0][highlightIndex % betaData[0].length]]]
          , betaSingleConstraintGridCellWidth, betaSingleConstraintGridCellHeight);
        let betaSingleGridGroup = layerNormTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${betaSingleGridGroupX},${betaSingleGridGroupY})`);
        let betaSingleGridRow = betaSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(betaSingleGridData).enter().append('g').attr('class', 'row');
        betaSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - betaDataRange.min) / (betaDataRange.max - betaDataRange.min);
            return paramsColorScale(normlizedVal);
          });
        betaSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - betaDataRange.min) / (betaDataRange.max - betaDataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);

        let betaSingleGridText = layerNormTooltipPart.append('text').attr("text-anchor", "middle");
        betaSingleGridText
          .attr('transform', `translate(${betaSingleGridGroupX + gridLength / 2},${betaSingleGridGroupY + gridLength + 20})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`beta`);

        // equation
        let equationOffsetX = betaSingleGridGroupX + betaSingleConstraintGridCellWidth + processGap
        let equationOffsetY = minusOffsetY
        let equation = layerNormTooltipPart.append('g')
          .attr('id', 'equation-g')
          .attr('transform', `translate(${equationOffsetX},${equationOffsetY})`)
        equation.append('circle')
          .attr('fill', 'rgb(235,235,235)')
          .attr('stroke', 'rgb(175,175,175)')
          .attr('stroke-width', 2)
          .attr("r", operatorRadius)
        equation.append('text')
          .attr("class", "operatorText")
          .text('=')

        // output single grid
        let outputSingleGridGroupX = equationOffsetX + processGap
        let outputSingleGridGroupY = alphaSingleGridGroupY
        let outputSingleConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, gridLength);
        let outputSingleConstraintGridCellHeight = getVisualizationSizeConstraint(1, 'y', xSize, ySize, gridLength);
        let outputSingleGridData = getGridData([[outputData[Math.floor(highlightIndex / outputData[0].length)][highlightIndex % outputData[0].length]]]
          , outputSingleConstraintGridCellWidth, outputSingleConstraintGridCellHeight);
        let outputSingleGridGroup = layerNormTooltipPart.append("g").attr("class", "grid").style('opacity', opacity).attr("transform", `translate(${outputSingleGridGroupX},${outputSingleGridGroupY})`);
        let outputSingleGridRow = outputSingleGridGroup.selectAll(".row")  // 绘制每一行
          .data(outputSingleGridData).enter().append('g').attr('class', 'row');
        outputSingleGridRow
          .selectAll(".square")
          .data(d => d).enter().append('rect')
          .attr('class', 'square')
          .attr("x", d => d.x).attr("y", d => d.y)
          .attr("width", d => d.width).attr("height", d => d.height)
          .attr('opacity', 0.9)
          .style('stroke', '#4a4a4a')
          .style('fill', d => {
            let normlizedVal = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
            return colorScale(normlizedVal);
          });
        outputSingleGridRow
          .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
          .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
          .style("text-anchor", "middle").style("dominant-baseline", "middle")
          .style('font-size', fontSize)
          .style('fill', d => {
            let normalizedValue = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
            if (normalizedValue < 0.2 || normalizedValue > 0.8) {
              return 'white';
            } else {
              return '#4a4a4a';
            }
          })
          .text(d => d.text);

        let outputSingleGridText = layerNormTooltipPart.append('text').attr("text-anchor", "middle");
        outputSingleGridText
          .attr('transform', `translate(${outputSingleGridGroupX + gridLength / 2},${outputSingleGridGroupY + gridLength + 20})`)
          .style('text-anchor', 'middle')
          .style('font-size', '10px')
          .attr("fill", '#4a4a4a')
          .attr('opacity', 0.9)
          .text(`output`);

      }

    },

    openFeedForwardNetwork(svg, type, offsetX, offsetY, blockNum) {
      this.blockStatus = 'feed-forward-network'
      this.feedForwardNetworkObj = [svg, type, offsetX, offsetY, blockNum]
      svg.selectAll('*').remove()
      var self = this
      let textOffsetX = 500
      let xSize = 325
      let ySize = 240
      let ySizeMax = 300
      let tokenGap = 10
      let processGap = 40
      let backgroundOpacity = 0.8
      let colorScale = d3.interpolateRdBu
      let openFFNPart = svg.append('g')
        .attr('id', 'open-feed-forward-network-g')
        .attr('transform', `translate(${offsetX - 100},${offsetY})`)
      openFFNPart.append('text')
        .attr('class', 'label')
        .style('font-weight', 'bold')
        .attr('transform', `translate(${textOffsetX},${-20})`)
        .text(type == 'encoder' ? 'Feed Forward Network of Encoder Block #' + (blockNum + 1) : 'Feed Forward Network of Decoder Block #' + (blockNum + 1));

      // input 
      let inputData = type == 'encoder' ? this.encoder.feed_forward[blockNum].input : this.decoder.feed_forward[blockNum].input
      let inputDataRange = getDataRange(inputData)
      let outputData = type == 'encoder' ? this.encoder.feed_forward[blockNum].output : this.decoder.feed_forward[blockNum].output
      let outputDataRange = getDataRange(outputData)
      let inputGridGroupX = -140;
      let inputGridGroupY = 100;
      let inputConstraintGridCellWidth = getVisualizationSizeConstraint(inputData[0].length, 'x', xSize, ySize, 40);
      let inputConstraintGridCellHeight = 35
      let inputGridData = getGapGridData(inputData, inputConstraintGridCellWidth, inputConstraintGridCellHeight, tokenGap);
      let inputGridGroup = openFFNPart.append("g").attr("class", "grid").attr("transform", `translate(${inputGridGroupX},${inputGridGroupY})`);
      let inputGridRow = inputGridGroup.selectAll(".row")  // 绘制每一行
        .data(inputGridData).enter().append('g').attr('class', 'row');
      inputGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', d => {
          if (d.row != this.curTokenIndex) return 0.25;
          else return 0.9;
        })
        .on('mouseover', (event, d) => {
          self.feedForwardNetworkObj = [svg, type, offsetX, offsetY, blockNum]
          this.$emit('changeTokenIndex', d.row)
        })
        .style('cursor', 'hand')
        .style('fill', d => {
          let normlizedVal = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
          return colorScale(normlizedVal);
        });
      let inputTotalGridWidth = inputConstraintGridCellWidth * inputData[0].length;
      let inputTotalGridHeight = (inputConstraintGridCellHeight + tokenGap) * inputData.length;
      let inputGridText = openFFNPart.append('text').attr("text-anchor", "middle");
      inputGridText
        .attr('transform', `translate(${inputGridGroupX + inputTotalGridWidth / 2},${inputGridGroupY - 20})`)
        .attr('class', 'label')
        .text(`Input (${inputData.length},${inputData[0].length})`);

      // input column
      let inputColumnConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, 35);
      let inputColumnConstraintGridCellHeight = getVisualizationSizeConstraint(inputData[0].length, 'y', xSize, ySize, 35);
      let inputColumnGridGroupX = inputGridGroupX + inputTotalGridWidth + processGap;
      let inputColumnGridGroupY = inputGridGroupY + (inputTotalGridHeight + tokenGap - inputConstraintGridCellHeight * inputData.length) / 2;
      let inputColumnData = inputData[this.curTokenIndex].map(d => [d]); // 把行向量转化为列向量
      let inputColumnGridData = getGridData(inputColumnData, inputColumnConstraintGridCellWidth, inputColumnConstraintGridCellHeight);
      let inputColumnGridGroup = openFFNPart.append("g").attr("class", "grid").attr("transform", `translate(${inputColumnGridGroupX},${inputColumnGridGroupY})`);
      let inputColumnGridRow = inputColumnGridGroup.selectAll(".row")  // 绘制每一行
        .data(inputColumnGridData).enter().append('g').attr('class', 'row');
      inputColumnGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('fill', d => {
          let normlizedVal = (d.text - inputDataRange.min) / (inputDataRange.max - inputDataRange.min);
          return colorScale(normlizedVal);
        });
      let inputColumnTotalGridWidth = inputColumnConstraintGridCellWidth;
      let inputColumnTotalGridHeight = inputColumnConstraintGridCellHeight * inputColumnData.length
      let inputColumnGridText = openFFNPart.append('text').attr("text-anchor", "middle");
      inputColumnGridText
        .attr('transform', `translate(${inputColumnGridGroupX + inputColumnTotalGridWidth / 2},${inputColumnGridGroupY - 80})`)
        .attr('class', 'label')
        .selectAll('.tspan')
        .data([`Input`, `Embed`, `(1,${inputColumnData.length})`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);

      // intermediate column
      let intermediateData = type == 'encoder' ? this.encoder.feed_forward[blockNum].intermediate : this.decoder.feed_forward[blockNum].intermediate
      let intermediateDataRange = getDataRange(intermediateData)
      let activationData = type == 'encoder' ? this.encoder.feed_forward[blockNum].activation : this.decoder.feed_forward[blockNum].activation
      let activationDataRange = getDataRange(activationData)
      let equationDataRange = {
        max: Math.max(intermediateDataRange.max, activationDataRange.max),
        min: Math.min(intermediateDataRange.min, activationDataRange.min)
      }
      let intermediateColumnConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySizeMax, 35);
      let intermediateColumnConstraintGridCellHeight = getVisualizationSizeConstraint(intermediateData[0].length, 'y', xSize, ySizeMax, 35);
      let intermediateColumnGridGroupX = inputColumnGridGroupX + inputColumnTotalGridWidth + processGap * 2;
      let intermediateColumnGridGroupY = inputColumnGridGroupY - (intermediateColumnConstraintGridCellHeight * intermediateData[0].length - inputColumnTotalGridHeight) / 2;
      let intermediateColumnData = intermediateData[this.curTokenIndex].map(d => [d]); // 把行向量转化为列向量
      let intermediateColumnGridData = getGridData(intermediateColumnData, intermediateColumnConstraintGridCellWidth, intermediateColumnConstraintGridCellHeight);
      let intermediateColumnGridGroup = openFFNPart.append("g").attr("class", "grid").attr("transform", `translate(${intermediateColumnGridGroupX},${intermediateColumnGridGroupY})`);
      let intermediateColumnGridRow = intermediateColumnGridGroup.selectAll(".row")  // 绘制每一行
        .data(intermediateColumnGridData).enter().append('g').attr('class', 'row');
      intermediateColumnGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * intermediateColumnGridData[0].length + d.col == this.tokenHighLightIndex ? 'black' : null)
        .on('mouseover', (event, d) => {
          self.feedForwardNetworkObj = [svg, type, offsetX, offsetY, blockNum]
          this.$emit('changeTokenHighLightIndex', d.row * intermediateColumnGridData[0].length + d.col)
        })
        .style('cursor', 'hand')
        .style('fill', d => {
          let normlizedVal = (d.text - intermediateDataRange.min) / (intermediateDataRange.max - intermediateDataRange.min);
          return colorScale(normlizedVal);
        });
      let intermediateColumnTotalGridWidth = intermediateColumnConstraintGridCellWidth;
      let intermediateColumnTotalGridHeight = intermediateColumnConstraintGridCellHeight * intermediateColumnData.length
      let intermediateColumnGridText = openFFNPart.append('text').attr("text-anchor", "middle");
      intermediateColumnGridText
        .attr('transform', `translate(${intermediateColumnGridGroupX + intermediateColumnTotalGridWidth / 2},${intermediateColumnGridGroupY - 80})`)
        .attr('class', 'label')
        .selectAll('.tspan')
        .data([`Intermediate`, `Embed`, `(1,${intermediateColumnData.length})`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);

      // plus symbol
      const plusSymbolRadius = config.plusSymbolRadius;
      const intermediateColor = config.intermediateColor;
      const kernelRectLength = config.kernelRectLength;
      const nodeLength = config.nodeLength;
      let symbolRectHeight = 1;

      let linearGroup_1OffsetX = inputColumnGridGroupX + inputColumnTotalGridWidth + processGap * 1.5
      let linearGroup_1OffsetY = intermediateColumnGridGroupY + (this.tokenHighLightIndex / intermediateColumnGridData.length) * intermediateColumnTotalGridHeight + 1
      let linearGroup_1 = openFFNPart.append('g').attr('class', 'plus-symbol').attr('transform', `translate(${linearGroup_1OffsetX},${linearGroup_1OffsetY})`);
      linearGroup_1.append('rect')
        .attr('x', -plusSymbolRadius).attr('y', -plusSymbolRadius)
        .attr('width', plusSymbolRadius * 2).attr('height', plusSymbolRadius * 2)
        .attr('rx', 3).attr('ry', 3)
        .style('fill', 'none').style('stroke', intermediateColor);
      linearGroup_1.append('rect')
        .attr('x', -(plusSymbolRadius - 3)).attr('y', -symbolRectHeight / 2)
        .attr('width', 2 * (plusSymbolRadius - 3)).attr('height', symbolRectHeight)
        .style('fill', intermediateColor);
      linearGroup_1.append('rect')
        .attr('x', -symbolRectHeight / 2).attr('y', -(plusSymbolRadius - 3))
        .attr('width', symbolRectHeight).attr('height', 2 * (plusSymbolRadius - 3))
        .style('fill', intermediateColor);
      linearGroup_1.append('circle')
        .attr('cx', 0).attr('cy', -nodeLength / 2 - 0.5 * kernelRectLength)
        .attr('r', kernelRectLength * 1.5)
        .style('stroke', intermediateColor)
        .style('cursor', 'crosshair')
        .style('fill', '#DDDDDD');
      linearGroup_1.append('path')
        .attr('d', (d3.linkHorizontal().x(d => d.x).y(d => d.y))({
          source: { x: 0, y: 0 },
          target: { x: 0, y: -nodeLength / 2 - 0.5 * kernelRectLength }
        }))
        .attr('id', 'bias-plus')
        .attr('stroke-width', 1.2)
        .attr('stroke', '#E5E5E5')
        .lower();
      linearGroup_1.append('text')
        .attr('x', symbolRectHeight).attr('y', plusSymbolRadius * 3)
        .attr('class', 'label')
        .text('Linear');

      // ReLU
      let reluRectWidth = 120
      let reluRectHeight = 50
      let reluOffsetX = intermediateColumnGridGroupX + intermediateColumnTotalGridWidth + processGap * 0.5
      let reluOffsetY = intermediateColumnGridGroupY + (this.tokenHighLightIndex / intermediateColumnData.length) * intermediateColumnTotalGridHeight - reluRectHeight / 2
      let maxOffsetX = 3
      let maxOffsetY = reluRectHeight / 2 - 10
      let maxWidth = 20
      let maxHeight = 20
      let max = require("../../src/assets/max.svg")
      let leftbracketOffsetX = 13
      let leftbracketOffsetY = reluRectHeight / 2 - 10
      let rightbracketOffsetX = leftbracketOffsetX + 90
      let rightbracketOffsetY = leftbracketOffsetY
      let leftbracketWidth = 20
      let leftbracketHeight = 20
      let leftbracket = require("../../src/assets/leftbracket.svg")
      let rightbracket = require("../../src/assets/rightbracket.svg")
      let reluPart = openFFNPart.append('g')
        .attr('id', 'relu-g')
        .attr('transform', `translate(${reluOffsetX},${reluOffsetY})`)
      reluPart.append('rect')
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("width", reluRectWidth)
        .attr("height", reluRectHeight)
        .attr("fill", "rgb(235, 235, 235)")
        .attr('stroke', 'rgb(175, 175, 175)')
        .attr('stroke-width', 1)
        .style('opacity', backgroundOpacity)
      reluPart.append('text')
        .attr('transform', `translate(${reluRectWidth / 2},${reluRectHeight + 20})`)
        .attr('class', 'label')
        .text('ReLU')
      // max
      reluPart.append('svg:image')
        .attr('xlink:href', max)
        .attr("x", maxOffsetX)
        .attr("y", maxOffsetY)
        .attr("width", maxWidth)
        .attr("height", maxHeight)
      reluPart.append('svg:image')
        .attr('xlink:href', leftbracket)
        .attr("x", leftbracketOffsetX)
        .attr("y", leftbracketOffsetY)
        .attr("width", leftbracketWidth)
        .attr("height", leftbracketHeight)
      reluPart.append('svg:image')
        .attr('xlink:href', rightbracket)
        .attr("x", rightbracketOffsetX)
        .attr("y", rightbracketOffsetY)
        .attr("width", leftbracketWidth)
        .attr("height", leftbracketHeight)

      let equationGridLength = 28
      let zeroOffsetX = 35
      let zeroOffsetY = reluRectHeight / 2 - equationGridLength / 2
      let zeroGirdRow = reluPart.append('g').attr('class', 'equation-group').attr('transform', `translate(${zeroOffsetX},${zeroOffsetY})`)
        .selectAll('.row').data(getGridData([[0]], equationGridLength, equationGridLength)).enter().append('g').attr('class', 'row');
      zeroGirdRow
        .selectAll('.square').data(d => d).enter().append('rect').attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y).attr("width", d => d.width).attr("height", d => d.height).attr('opacity', 0.8)
        .style('stroke', 'black')
        .style("fill", (d) => {
          let normalizedValue = (d.text - equationDataRange.min) / (equationDataRange.max - equationDataRange.min);
          return colorScale(normalizedValue);
        });
      zeroGirdRow
        .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
        .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
        .style("text-anchor", "middle").style("dominant-baseline", "middle")
        .style('font-size', '10px')
        .style('fill', d => {
          let normalizedValue = (d.text - equationDataRange.min) / (equationDataRange.max - equationDataRange.min);
          if (normalizedValue < 0.2 || normalizedValue > 0.8) {
            return 'white';
          } else {
            return 'black';
          }
        }).text(d => d.text.toString());

      reluPart.append('text').attr('transform', `translate(${zeroOffsetX + equationGridLength + 5},${reluRectHeight / 2})`)
        .attr('class', 'label')
        .text(' , ');

      let interGridOffsetX = zeroOffsetX + equationGridLength + 10
      let interGridOffsetY = zeroOffsetY
      let interGridRow = reluPart.append('g').attr('class', 'equation-group').attr('transform', `translate(${interGridOffsetX},${interGridOffsetY})`)
        .selectAll('.row').data(getGridData([[intermediateData[this.curTokenIndex][this.tokenHighLightIndex]]], equationGridLength, equationGridLength))
        .enter().append('g').attr('class', 'row');
      interGridRow
        .selectAll('.square').data(d => d).enter().append('rect').attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y).attr("width", d => d.width).attr("height", d => d.height).attr('opacity', 0.8)
        .style('stroke', 'black')
        .style("fill", (d) => {
          let normalizedValue = (d.text - equationDataRange.min) / (equationDataRange.max - equationDataRange.min);
          return colorScale(normalizedValue);
        }).text(d => d.text);
      interGridRow
        .selectAll('.text').data(d => d).enter().append('text').attr('class', 'text')
        .attr("x", d => d.x + d.width / 2).attr("y", d => d.y + d.height / 2)
        .style("text-anchor", "middle").style("dominant-baseline", "middle").style('font-size', '10px')
        .style('fill', d => {
          let normalizedValue = (d.text - equationDataRange.min) / (equationDataRange.max - equationDataRange.min);
          if (normalizedValue < 0.2 || normalizedValue > 0.8) {
            return 'white';
          } else {
            return 'black';
          }
        }).text(d => Math.round(d.text * 100) / 100);

      // activation column
      let activationColumnConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySizeMax, 35);
      let activationColumnConstraintGridCellHeight = getVisualizationSizeConstraint(activationData[0].length, 'y', xSize, ySizeMax, 35);
      let activationColumnGridGroupX = reluOffsetX + reluRectWidth + processGap * 0.5;
      let activationColumnGridGroupY = intermediateColumnGridGroupY - (activationColumnConstraintGridCellHeight * activationData[0].length - intermediateColumnTotalGridHeight) / 2;
      let activationColumnData = activationData[this.curTokenIndex].map(d => [d]); // 把行向量转化为列向量
      let activationColumnGridData = getGridData(activationColumnData, activationColumnConstraintGridCellWidth, activationColumnConstraintGridCellHeight);
      let activationColumnGridGroup = openFFNPart.append("g").attr("class", "grid").attr("transform", `translate(${activationColumnGridGroupX},${activationColumnGridGroupY})`);
      let activationColumnGridRow = activationColumnGridGroup.selectAll(".row")  // 绘制每一行
        .data(activationColumnGridData).enter().append('g').attr('class', 'row');
      activationColumnGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('stroke', d => d.row * activationColumnData[0].length + d.col == this.tokenHighLightIndex ? 'black' : null)
        .on('mouseover', (event, d) => {
          self.feedForwardNetworkObj = [svg, type, offsetX, offsetY, blockNum]
          this.$emit('changeTokenHighLightIndex', d.row * activationColumnData[0].length + d.col)
        })
        .style('cursor', 'hand')
        .style('fill', d => {
          let normlizedVal = (d.text - equationDataRange.min) / (equationDataRange.max - equationDataRange.min);
          return colorScale(normlizedVal);
        });
      let activationColumnTotalGridWidth = activationColumnConstraintGridCellWidth;
      // let activationColumnTotalGridHeight = activationColumnConstraintGridCellHeight * activationColumnData.length
      let activationColumnGridText = openFFNPart.append('text').attr("text-anchor", "middle");
      activationColumnGridText
        .attr('transform', `translate(${activationColumnGridGroupX + activationColumnTotalGridWidth / 2},${activationColumnGridGroupY - 80})`)
        .attr('class', 'label')
        .selectAll('.tspan')
        .data([`Activation`, `Embed`, `(1,${activationColumnData.length})`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);

      let linearGroup_2OffsetX = activationColumnGridGroupX + activationColumnTotalGridWidth + processGap * 0.5
      let linearGroup_2OffsetY = intermediateColumnGridGroupY + (this.tokenHighLightIndex / intermediateColumnGridData.length) * intermediateColumnTotalGridHeight + 1
      let linearGroup_2 = openFFNPart.append('g').attr('class', 'plus-symbol').attr('transform', `translate(${linearGroup_2OffsetX},${linearGroup_2OffsetY})`);
      linearGroup_2.append('rect')
        .attr('x', -plusSymbolRadius).attr('y', -plusSymbolRadius)
        .attr('width', plusSymbolRadius * 2).attr('height', plusSymbolRadius * 2)
        .attr('rx', 3).attr('ry', 3)
        .style('fill', 'none').style('stroke', intermediateColor);
      linearGroup_2.append('rect')
        .attr('x', -(plusSymbolRadius - 3)).attr('y', -symbolRectHeight / 2)
        .attr('width', 2 * (plusSymbolRadius - 3)).attr('height', symbolRectHeight)
        .style('fill', intermediateColor);
      linearGroup_2.append('rect')
        .attr('x', -symbolRectHeight / 2).attr('y', -(plusSymbolRadius - 3))
        .attr('width', symbolRectHeight).attr('height', 2 * (plusSymbolRadius - 3))
        .style('fill', intermediateColor);
      linearGroup_2.append('circle')
        .attr('cx', 0).attr('cy', -nodeLength / 2 - 0.5 * kernelRectLength)
        .attr('r', kernelRectLength * 1.5)
        .style('stroke', intermediateColor)
        .style('cursor', 'crosshair')
        .style('fill', '#DDDDDD');
      linearGroup_2.append('path')
        .attr('d', (d3.linkHorizontal().x(d => d.x).y(d => d.y))({
          source: { x: 0, y: 0 },
          target: { x: 0, y: -nodeLength / 2 - 0.5 * kernelRectLength }
        }))
        .attr('id', 'bias-plus')
        .attr('stroke-width', 1.2)
        .attr('stroke', '#E5E5E5')
        .lower();
      linearGroup_2.append('text')
        .attr('x', symbolRectHeight).attr('y', plusSymbolRadius * 3)
        .attr('class', 'label')
        .text('Linear');

      // output column
      let outputColumnConstraintGridCellWidth = getVisualizationSizeConstraint(1, 'x', xSize, ySize, 35);
      let outputColumnConstraintGridCellHeight = getVisualizationSizeConstraint(outputData[0].length, 'y', xSize, ySize, 35);
      let outputColumnGridGroupX = activationColumnGridGroupX + activationColumnTotalGridWidth + processGap * 2;
      let outputColumnGridGroupY = inputColumnGridGroupY;
      let outputColumnData = outputData[this.curTokenIndex].map(d => [d]); // 把行向量转化为列向量
      let outputColumnGridData = getGridData(outputColumnData, outputColumnConstraintGridCellWidth, outputColumnConstraintGridCellHeight);
      let outputColumnGridGroup = openFFNPart.append("g").attr("class", "grid").attr("transform", `translate(${outputColumnGridGroupX},${outputColumnGridGroupY})`);
      let outputColumnGridRow = outputColumnGridGroup.selectAll(".row")  // 绘制每一行
        .data(outputColumnGridData).enter().append('g').attr('class', 'row');
      outputColumnGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', 0.9)
        .style('fill', d => {
          let normlizedVal = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
          return colorScale(normlizedVal);
        });
      let outputColumnTotalGridWidth = outputColumnConstraintGridCellWidth;
      // let outputColumnTotalGridHeight = outputColumnConstraintGridCellHeight * outputColumnData.length
      let outputColumnGridText = openFFNPart.append('text').attr("text-anchor", "middle");
      outputColumnGridText
        .attr('transform', `translate(${outputColumnGridGroupX + outputColumnTotalGridWidth / 2},${outputColumnGridGroupY - 80})`)
        .attr('class', 'label')
        .selectAll('.tspan')
        .data([`Output`, `Embed`, `(1,${outputColumnData.length})`])
        .enter().append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .text(d => d);

      // output
      let outputGridGroupX = outputColumnGridGroupX + outputColumnTotalGridWidth + processGap;
      let outputGridGroupY = inputGridGroupY;
      let outputConstraintGridCellWidth = getVisualizationSizeConstraint(outputData[0].length, 'x', xSize, ySize, 40);
      let outputConstraintGridCellHeight = 35
      let outputGridData = getGapGridData(outputData, outputConstraintGridCellWidth, outputConstraintGridCellHeight, tokenGap);
      let outputGridGroup = openFFNPart.append("g").attr("class", "grid").attr("transform", `translate(${outputGridGroupX},${outputGridGroupY})`);
      let outputGridRow = outputGridGroup.selectAll(".row")  // 绘制每一行
        .data(outputGridData).enter().append('g').attr('class', 'row');
      outputGridRow.selectAll(".square")
        .data(d => d).enter().append('rect')
        .attr('class', 'square')
        .attr("x", d => d.x).attr("y", d => d.y)
        .attr("width", d => d.width).attr("height", d => d.height)
        .attr('opacity', d => {
          if (d.row != this.curTokenIndex) return 0.25;
          else return 0.9;
        })
        .on('mouseover', (event, d) => {
          self.feedForwardNetworkObj = [svg, type, offsetX, offsetY, blockNum]
          this.$emit('changeTokenIndex', d.row)
        })
        .style('cursor', 'hand')
        .style('fill', d => {
          let normlizedVal = (d.text - outputDataRange.min) / (outputDataRange.max - outputDataRange.min);
          return colorScale(normlizedVal);
        });
      let outputTotalGridWidth = outputConstraintGridCellWidth * outputData[0].length;
      // let outputTotalGridHeight = (outputConstraintGridCellHeight + tokenGap) * outputData.length;
      let outputGridText = openFFNPart.append('text').attr("text-anchor", "middle");
      outputGridText
        .attr('transform', `translate(${outputGridGroupX + outputTotalGridWidth / 2},${outputGridGroupY - 20})`)
        .attr('class', 'label')
        .text(`Output (${outputData.length},${outputData[0].length})`);

      // 连线
      const edgeStrokeWidth = config.edgeStrokeWidth;
      const edgeOpacity = config.edgeOpacity;
      const edgeInitColor = config.edgeInitColor;
      const edgeHoverColor = config.edgeHoverColor;
      let linkGen = d3.linkHorizontal().x(d => d.x).y(d => d.y);
      let linkData = [{
        source: { x: linearGroup_1OffsetX + plusSymbolRadius, y: linearGroup_1OffsetY },
        target: { x: intermediateColumnGridGroupX, y: linearGroup_1OffsetY },
        type: 'symbol-link'
      }, {
        source: { x: linearGroup_2OffsetX, y: linearGroup_2OffsetY },
        target: { x: activationColumnGridGroupX + activationColumnTotalGridWidth, y: linearGroup_2OffsetY },
        type: 'symbol-link'
      }]
      let inGrid = inputGridData[this.curTokenIndex][inputGridData[0].length - 1]
      inputColumnGridData.forEach(d => {
        linkData.push({
          target: {
            x: inputColumnGridGroupX + d[0].x,
            y: inputColumnGridGroupY + d[0].y + d[0].height / 2,
          },
          source: {
            x: inputGridGroupX + inGrid.x + inGrid.width,
            y: inputGridGroupY + inGrid.y + inGrid.height / 2,
          },
          type: 'input-inputColumn-link'
        },
          {
            target: {
              x: inputColumnGridGroupX + d[0].x + d[0].width,
              y: inputColumnGridGroupY + d[0].y + d[0].height / 2,
            },
            source: {
              x: linearGroup_1OffsetX - plusSymbolRadius - 2,
              y: linearGroup_1OffsetY,
            },
            type: 'inputColumn-linear-link'
          });
      })
      let outGrid = outputGridData[this.curTokenIndex][0]
      outputColumnGridData.forEach(d => {
        linkData.push({
          target: {
            x: outputColumnGridGroupX + d[0].x + d[0].width,
            y: outputColumnGridGroupY + d[0].y + d[0].height / 2,
          },
          source: {
            x: outputGridGroupX + outGrid.x + outGrid.width,
            y: outputGridGroupY + outGrid.y + outGrid.height / 2,
          },
          type: 'output-outputColumn-link'
        },
          {
            target: {
              x: outputColumnGridGroupX + d[0].x,
              y: outputColumnGridGroupY + d[0].y + d[0].height / 2,
            },
            source: {
              x: linearGroup_2OffsetX + plusSymbolRadius + 2,
              y: linearGroup_2OffsetY,
            },
            type: 'output-outputColumn-link'
          });
      })
      let edgeGroup = openFFNPart.append("g").attr("class", "edge-group");
      edgeGroup.selectAll("path.edge").data(linkData).enter().append('path')
        .attr('class', 'edge').attr('d', d => linkGen({ source: d.source, target: d.target }))
        .style('fill', 'none').style('stroke-width', edgeStrokeWidth).style('opacity', edgeOpacity)
        .style('stroke', d => {
          if (d.type == "symbol-link") return edgeHoverColor;
          else return edgeInitColor;
        });


    },





  },

}
</script>

<style>
.two {
  width: 250px;
  height: 100px;
  line-height: 100px;
  margin: 0 auto;
  text-align: center;
  border-radius: 10px;
  border: 10px solid #A7A7DB;
  position: relative;
  background-color: aquamarine;
}

/* 2.添加伪元素before，在这里添加三角形A */
.two:before,
.two:after {
  content: "";
  width: 0;
  height: 0;
  /*IE6下，height:0;不顶用，可使用font-size:0; + overflow:hidden;修复此问题*/
  font-size: 0;
  overflow: hidden;
  display: block;
  border-width: 20px;
  border-color: transparent #A7A7DB transparent transparent;
  border-style: dashed solid dashed dashed;
  position: absolute;
  top: 30%;
  left: -50px;
  /* 向左移动 矩形的左边框 + 自己边框*2 */
}

/* 3.添加伪元素after，在这里添加三角形B */
.two:after {
  border-color: transparent #E5DEEB transparent transparent;
  border-style: dashed solid dashed dashed;
  position: absolute;
  top: 30%;
  left: -40px;
  /* 向左移动 自己边框*2 */
}

.node {
  stroke: rgb(175, 175, 175);
  stroke-width: 2
}

.text {
  font-size: 15px;
  fill: black
}

.label {
  font-size: 14px;
  text-anchor: middle;
  dominant-baseline: middle;
  fill: #4a4a4a;
  vertical-align: middle;
  /* 垂直居中对齐 */
}

.context {
  font-size: 10px;
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
</style>