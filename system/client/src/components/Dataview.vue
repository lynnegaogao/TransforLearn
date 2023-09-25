<template>
  <div style="display: inline-block; vertical-align: middle;" class="grid">
    <!-- <svg id="grid" width=100% height=100%></svg> -->
    <svg id="grid" ></svg>
  </div>
</template>

<script>
import * as d3 from "d3";
// import {getVisualizationSizeConstraint, getDataRange, getGridData} from '../utils/detailview-utils'
// import {array1d} from '../utils/detailview-utils'
import {getVisualizationSizeConstraint} from '../utils/detailview-utils'
// import {getDataRange} from '../utils/detailview-utils'
import {getGridData} from '../utils/detailview-utils'
export default {
  name:"Detailview",
  props:{
    data: {
      type: Array,
      default: function(){return [];},
    },
    colorRange: {
      type: Object,
      default: function(){return {};},
    },
    highlights:{
      type: Array,
      default: function(){return [];},
    },
    isEquation:{
      type: Boolean,
      default: false,
    },
    isParams:{
      type: Boolean,
      default: false,
    },
    isColumn:{
      type: Boolean,
      default: false,
    },
    isRow:{
      type: Boolean,
      default: false,
    },
  },
  emits:["message","update:highlights"],
  data(){
    return {
      svgSize:{},
      dataRange:{},
      gridData:[],
      oldHighlights:[],
      oldData:[],
    }
  },
  mounted(){
    // console.log('detailview - mounted');
    this.redraw();
  },
  beforeUpdate(){
    // console.log('detailview - beforeUpdate');
    if(this.oldData != this.data){
      this.redraw();
      this.oldData = this.data;
    }
    if(this.oldHighlights != this.highlights){
      let grid = d3.select(this.$el).select('#grid').select("svg");
      grid.selectAll(".square")
      .style("stroke",(d)=>(this.isEquation || (this.highlights.length && this.highlights[d.row * this.gridData[0].length + d.col]))?'black':null);
      this.oldHighlights = this.highlights;
    }
  },
  methods:{
    redraw(){
      // 初始化一些相关变量
      this.oldHighlights = this.highlights;
      this.oldData = this.data;

      // 清空原来所有的绘图
      d3.select(this.$el).selectAll('#grid > *').remove();
      const textConstraintDivisor = 3.2;
      // textConstraintDivisor;
      let colorScale = d3.interpolateRdBu;
      let paramsColorScale = d3.interpolateBrBG;
      // mouseover获取的数据 newOrganizedData
      let newOrganizedData;
      if(this.isColumn){  //  标记是否为列向量
        newOrganizedData = [];
        this.data.forEach(d=>{
          newOrganizedData.push([d]);
        });
      } else if(this.isRow) {
        newOrganizedData = [this.data];
      }
      else {
        newOrganizedData = this.data;
      }
      //  console.log('newOrganizedData:',newOrganizedData )
      // console.log('this.data:',this.data )
      let constraintGridCellWidth = getVisualizationSizeConstraint(newOrganizedData[0].length,'x');
      let constraintGridCellHeigh = getVisualizationSizeConstraint(newOrganizedData.length,'y');
      this.svgSize = {width: newOrganizedData[0].length * constraintGridCellWidth + 2,
                      height: newOrganizedData.length * constraintGridCellHeigh + 2};
      // this.dataRange = getDataRange(newOrganizedData);
      // console.time();
      this.gridData = getGridData(newOrganizedData, constraintGridCellWidth, constraintGridCellHeigh);
      // console.timeEnd();

      // 实现双向绑定
      // this.$emit("update:highlights",array1d(newOrganizedData.length * newOrganizedData[0].length,()=>true))


      // 绘制 grid
      let grid = d3.select(this.$el).select('#grid')
          .attr('width',this.svgSize.width+"px")
          .attr('height',this.svgSize.height+"px")
          .append('svg')
          .attr('width',this.svgSize.width+"px")
          .attr('height',this.svgSize.height+"px");
      let row = grid.selectAll(".row")  // 绘制每一行
          .data(this.gridData)
          .enter().append("g")
          .attr("class","row");
      // let column = row.selectAll(".square") // 绘制每一列/每一个各自
      row.selectAll(".square") // 绘制每一列/每一个各自
          .data(d=>d)
          .enter().append("rect")
          .attr("class","square")
          .attr("x",d=>d.x)
          .attr("y",d=>d.y)
          .attr("width",d=>d.width)
          .attr("height",d=>d.height)
          .style('opacity', 0.9)
          .style('stroke',(d)=>(this.isEquation || (this.highlights.length && this.highlights[d.row * this.gridData[0].length + d.col]))?'black':null)
          .style('fill',d=>{
            // let normlizedVal = (d.text-this.dataRange.min)/(this.dataRange.max-this.dataRange.min);
            // return this.isParams?paramsColorScale(normlizedVal):colorScale(normlizedVal);
            // :colorRange="stdTotalRange"
            // let normlizedVal = (d.text-this.colorRange.min)/this.colorRange.range;
            let normlizedVal = (d.text-this.colorRange.min)/(this.colorRange.max-this.colorRange.min);
            return this.isParams?paramsColorScale(normlizedVal):colorScale(normlizedVal);
          })
          .on('mouseover',(event,d)=>{
            if(!this.isColumn && !this.isRow && !this.isEquation ){
              this.$emit('message',{
                hoverH: d.row,
                hoverW: d.col,
              });
            }
          });
      if (this.isEquation) {
        row.selectAll(".text")
        .data(d=>d)
        .enter().append("text")
        .attr("class","text")
        .style("font-size", Math.floor(Math.min(constraintGridCellHeigh,constraintGridCellWidth)/textConstraintDivisor))
        .attr("x", d=>d.x+d.width/2)
        .attr("y", d=>d.y+d.height/2)
        .style("fill", d=>{  // 为颜色设置填充色
          // let normlizedVal = (d.text-this.dataRange.min)/(this.dataRange.max-this.dataRange.min);
          // let normlizedVal = (d.text-this.colorRange.min)/this.colorRange.range;
          let normlizedVal = (d.text-this.colorRange.min)/(this.colorRange.max-this.colorRange.min);
          if(normlizedVal < 0.2 || normlizedVal > 0.8){
            return 'white';
          } else {
            return 'black';
          }
        })
        .style("text-anchor","middle")
        .style("dominant-baseline","middle")
        .text(d=>d.text.toString())
      }
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>