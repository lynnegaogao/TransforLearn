export function array1d(length, f) {
  return Array.from({length: length}, f ? ((v, i) => f(i)) : undefined);
}

export function array2d(height, width, f) {
  return Array.from({length: height}, (v, i) => Array.from({length: width}, f ? ((w, j) => f(i, j)) : undefined));
}

// Edit these values to change size of low-level conv visualization.
export function getVisualizationSizeConstraint(dims, axis='y', sizeX=550, sizeY=200, maxSizeOfGridCell=35) {
  let sizeOfGrid = axis=='y'?sizeY:sizeX;
  // let maxSizeOfGridCell = 35;
  return sizeOfGrid / dims > maxSizeOfGridCell ? maxSizeOfGridCell : sizeOfGrid / dims;
}

export function getDataRange(data) {
  // console.log('getDataRange - data:',data.length);
  // console.log('getDataRange - data:',data[0].length);
  let maxRow = data.map(function(row){ return Math.max.apply(Math, row); });
  let max = Math.max.apply(null, maxRow);
  let minRow = data.map(function(row){ return Math.min.apply(Math, row); });
  let min = Math.min.apply(null, minRow);
  let range = {
    range: 2 * Math.max(Math.abs(min), Math.abs(max)),
    min: min,
    max: max
  };
  return range;
}

export function getGapGridData(data,gridCellWidth,gridCellHeight,cellGap){
  let gridData = [],
      xpos = 1,
      ypos = 1;
  for(let row=0; row<data.length; row++){
    gridData.push([]);
    for(let col=0; col<data[0].length; col++){
      gridData[row].push({
        text: Math.round(data[row][col] * 1000) / 1000,
        row,
        col,
        x: xpos,
        y: ypos,
        width:gridCellWidth,
        height:gridCellHeight,
      });
      xpos += gridCellWidth;
    }
    xpos = 1;
    ypos += gridCellHeight+cellGap;
  }
  return gridData;
}

export function getGridData(data,gridCellWidth,gridCellHeight){
  let gridData = [],
      xpos = 1,
      ypos = 1;
  for(let row=0; row<data.length; row++){
    gridData.push([]);
    for(let col=0; col<data[0].length; col++){
      gridData[row].push({
        text: Math.round(data[row][col] * 1000) / 1000,
        row,
        col,
        x: xpos,
        y: ypos,
        width:gridCellWidth,
        height:gridCellHeight,
      });
      xpos += gridCellWidth;
    }
    xpos = 1;
    ypos += gridCellHeight;
  }
  return gridData;
}