import * as d3 from "d3";

export const drawGrids = function(d3group,dataRange,gridData,colorScale){
  let row = d3group.selectAll(".row") // 绘制一行
        .data(gridData)
        .enter().append("g")
        .attr("class","row")
      // let columnInput = rowInput.selectAll(".square") // 绘制每一列
  let column = row.selectAll(".square") // 绘制每一列/每一个各自
        .data(d=>d)
        .enter().append("rect")
        .attr("class","square")
        .attr("x",d=>d.x)
        .attr("y",d=>d.y)
        .attr("width",d=>d.width)
        .attr("height",d=>d.height)
        .style('opacity', 0.9)
        .style('fill',d=>{
          let normlizedVal = (d.text-dataRange.min)/(dataRange.max - dataRange.min);
          return colorScale(normlizedVal);
        })
  return row,column;
}

export const getLegendGradient = (g, colorScale, gradientName, min, max) => {
  if (min === undefined) { min = 0; }
  if (max === undefined) { max = 1; }
  let gradient = g.append('defs')
    .append('svg:linearGradient')
    .attr('id', `${gradientName}`)
    .attr('x1', '0%')
    .attr('y1', '100%')
    .attr('x2', '100%')
    .attr('y2', '100%')
    .attr('spreadMethod', 'pad');
  let interpolation = 30;
  for (let i = 0; i < interpolation; i++) {
    let curProgress = i / (interpolation - 1);
    // let curColor = colorScale(curProgress * (max - min) + min);
    let curColor = colorScale(curProgress);
    gradient.append('stop')
      .attr('offset', `${curProgress * 100}%`)
      .attr('stop-color', curColor)
      .attr('stop-opacity', 1);
  }
}

