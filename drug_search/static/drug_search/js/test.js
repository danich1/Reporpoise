var data_set = [{
"name":"test",
"x":2,
"y":3,
},
{
"name":"test2",
"x":1,
"y":10,
},
{
"name":"test3",
"x":10,
"y":3,
},
{
"name":"test4",
"x":4,
"y":9,
}
];
var margin={
"left":40,
"right":20,
"top":20,
"bottom":30
};
function load(data,margin)
{
width = 960 - margin.left - margin.right,
height = 500 - margin.top - margin.bottom;

var xValue = function(d) {return d.x;}, // data -> value
xScale = d3.scale.linear().range([0, width]), // value -> display
xMap = function(d) { console.log(d.x);console.log(xScale(d.x));return xScale(xValue(d));}, // data -> display
xAxis = d3.svg.axis().scale(xScale).orient("bottom");
console.log(xScale(.1));
var yValue = function(d) { return d.y;}, // data -> value
yScale = d3.scale.linear().range([height, 0]), // value -> display
yMap = function(d) { console.log(d.y); console.log(yScale(d.y));return yScale(yValue(d));}, // data -> display
yAxis = d3.svg.axis().scale(yScale).orient("left");
// don't want dots overlapping axis, so add in buffer to data domain
xScale.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
yScale.domain([d3.min(data, yValue)-1, d3.max(data, yValue)+1]);
var svg = d3.select("body").append("svg")
.attr("width", width + margin.left + margin.right)
.attr("height", height + margin.top + margin.bottom)
.append("g")
.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// x-axis
svg.append("g")
.attr("class", "x axis")
.attr("transform", "translate(0," + height + ")")
.call(xAxis)
.append("text")
.attr("class", "label")
.attr("x", width)
.attr("y", -6)
.style("text-anchor", "end")
.text("Test X-axis");

// y-axis
svg.append("g")
.attr("class", "y axis")
.call(yAxis)
.append("text")
.attr("class", "label")
.attr("transform", "rotate(-90)")
.attr("y", 6)
.attr("dy", ".71em")
.style("text-anchor", "end")
.text("Test Y-axis");

svg.selectAll(".dot")
  .data(data)
.enter().append("circle")
  .attr("class", "dot")
  .attr("r", 3.5)
  .attr("cx", xMap)
  .attr("cy", yMap)
  .style("fill", "black");
}