var data_set = [{
"name":"SNP12",
"x":2,
"y":5e-8,
},
{
"name":"SNP1222",
"x":1,
"y":4e-9,
},
{
"name":"SNP93",
"x":10,
"y":1e-4,
},
{
"name":"SNP3",
"x":4,
"y":2e-5,
},
{
    "name":"SNP123123",
    "x":5,
    "y":5e-10,
}
];
var margin={
"left":40,
"right":40,
"top":20,
"bottom":30
};
function load(data)
{
    var max_height = 600;
    var max_width = 960;
    var GWAS = 5e-8;
    width = max_width - margin.left - margin.right,
    height = max_height - margin.top - margin.bottom;

    //top left starts at 0
    var yScale = d3.scale.log().domain([d3.min(data,function(d){return d.y}),d3.max(data,function(d){return d.y})]).range([0,height]);
    var xScale = d3.scale.linear().domain([d3.min(data,function(d){return d.x})-1, d3.max(data, function(d){return d.x})+1]).range([0,width]);
    var yAxis = d3.svg.axis().scale(yScale).orient("left");
    var xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    var svg = d3.select("#scatterplot").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + 70 + "," + 20 + ")");

     // x-axis
    svg.append("g")
    .attr("class", "x_axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis)
    .append("text")
    .attr("class", "label")
    .attr("x", width)
    .attr("y", -6)
    .style("text-anchor", "end")
    .text("KiloBase");

    // y-axis
    svg.append("g")
    .attr("class", "y_axis")
    .call(yAxis)
    .append("text")
    .attr("class", "label")
    .attr("transform", "rotate(-90)")
    .attr("y", 6)
    .attr("dy", ".71em")
    .style("text-anchor", "end")
    .text("P-Value");

     svg.selectAll(".dot")
      .data(data)
    .enter().append("circle")
      .attr("class", function(d){if (d.y <= GWAS) {return "dot"} else {return "dot insig"}})
      .attr("r", 3.5)
      .attr("cx", function(d){return xScale(d.x)})
      .attr("cy", function(d){return yScale(d.y)})
      .style("fill", "black");

    svg.selectAll(".dottext")
        .data(data)
        .enter().append("text")
        .attr("class",function(d){if (d.y <= GWAS) {return "dottext"} else {return "dottext insig"}})
        .text(function(d){return d.name})
        .attr("x", function(d){return xScale(d.x);})
        .attr("y", function(d){return yScale(d.y);});

    svg.selectAll(".dotline")
    .data(data)
    .enter().append("line")
    .attr("class", function(d){if (d.y <= GWAS) {return "dotline"} else {return "dotline insig"}})
    .attr("x1",function(d){return xScale(d.x);})
    .attr("y1",height)
    .attr("x2", function(d){return xScale(d.x);})
    .attr("y2", function(d){return yScale(d.y);})
    .attr("stroke", "black")
    .attr("stroke-width", 2);

    svg.append("line")
    .attr("class", "GWAS")
    .attr("x1",0)
    .attr("y1",yScale(GWAS))
    .attr("x2", width)
    .attr("y2", yScale(GWAS))
    .attr("stroke", "gold")
    .attr("opacity", .9)
    .attr("stroke-width", 2)
    .attr("stroke-dasharray","5,5");

    svg.append("rect")
    .attr("x", 0)
    .attr("y", yScale(GWAS))
    .attr("width", width)
    .attr("height", height-yScale(GWAS))
    .attr("opacity", 0.4)
    .attr("fill", "Gray");
}
function updateGraph(mode)
{
    if(mode > 0)
    {
        //change the domain for new data
        //add data that is necessary for the transition
        //add effects to the new inserted data.
        //add limits towards the zoom
    }
    else
    {
        //decrease the x axis space
    }
}