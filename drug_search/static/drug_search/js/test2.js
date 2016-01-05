var data_set=[
{"name":"rs5759182",
"x":41869595,
"y":0.130000,
},
{"name":"rs138903",
"x":41873898,
"y":0.006500,
},
{"name":"rs138908"
,"x":41878099,
"y":0.100000,
},
{"name":"rs138909"
,"x":41879683,
"y":0.120000,
},
{"name":"rs138910"
,"x":41879999,
"y":0.002300,
},
{"name":"rs5759197"
,"x":41880093,
"y":0.250000,
},
{"name":"rs762960"
,"x":41880996,
"y":0.180000,
},
{"name":"rs5759198"
,"x":41881352,
"y":0.072000,
},
{"name":"rs2284099"
,"x":41881780,
"y":0.270000,
},
{"name":"rs138911"
,"x":41883361,
"y":0.006900,
},
{"name":"rs138913"
,"x":41884970,
"y":0.120000,
},
{"name":"rs2012930"
,"x":41885835,
"y":0.240000,
},
{"name":"rs138914"
,"x":41885865,
"y":0.120000,
},
{"name":"rs138915"
,"x":41886260,
"y":0.002200,
},
{"name":"rs113515"
,"x":41886866,
"y":0.140000,
},
{"name":"rs8135638"
,"x":41887372,
"y":0.810000,
},
{"name":"rs105585"
,"x":41887436,
"y":0.120000,
},
{"name":"rs2157248"
,"x":41887803,
"y":0.390000,
},
{"name":"rs6971"
,"x":41888870,
"y":0.003600,
},
{"name":"rs6972"
,"x":41888916,
"y":0.280000,
},
{"name":"rs6973"
,"x":41889081,
"y":0.230000,
},
{"name":"rs9333347"
,"x":41889656,
"y":0.870000,
},
{"name":"rs9333348"
,"x":41889666,
"y":0.300000,
},
{"name":"rs1005658"
,"x":41889681,
"y":0.420000,
},
{"name":"rs129401"
,"x":41890910,
"y":0.009200,
},
{"name":"rs5759205"
,"x":41891057,
"y":0.520000,
},
{"name":"rs80411"
,"x":41891619,
"y":0.002400,
},
{"name":"rs138921"
,"x":41891703,
"y":0.027000,
},
{"name":"rs138922"
,"x":41891747,
"y":0.006100,
},
{"name":"rs2071729"
,"x":41892287,
"y":0.520000,
},
{"name":"rs138927"
,"x":41892325,
"y":0.009400,
},
{"name":"rs9463"
,"x":41892649,
"y":0.018000,
},
{"name":"rs47340"
,"x":41892773,
"y":0.160000,
},
{"name":"rs107402"
,"x":41893655,
"y":0.230000,
},
{"name":"rs2071727"
,"x":41895647,
"y":0.077000,
},
{"name":"rs138933"
,"x":41895799,
"y":0.210000,
},
{"name":"rs138937"
,"x":41898004,
"y":0.220000,
},
{"name":"rs762953"
,"x":41900012,
"y":0.820000,
},
{"name":"rs2269526"
,"x":41900603,
"y":0.640000,
},
{"name":"rs2269527"
,"x":41900738,
"y":0.750000,
},
{"name":"rs743807"
,"x":41900863,
"y":0.690000,
},
{"name":"rs6003097"
,"x":41902124,
"y":0.540000,
},
{"name":"rs6519365"
,"x":41903890,
"y":0.590000,
},
{"name":"rs138945"
,"x":41905718,
"y":0.850000,
},
{"name":"rs2071724"
,"x":41906992,
"y":0.520000,
},
{"name":"rs138949"
,"x":41907568,
"y":0.770000,
},
{"name":"rs13058467"
,"x":41908993,
"y":0.090000,
},
{"name":"rs875307"
,"x":41909266,
"y":0.630000,
},
{"name":"rs138957"
,"x":41914173,
"y":0.180000,
},
{"name":"rs138958"
,"x":41914225,
"y":0.087000,
},
{"name":"rs138960"
,"x":41915249,
"y":0.150000,
},
{"name":"rs138963"
,"x":41915792,
"y":0.580000,
},
{"name":"rs9623776"
,"x":41917251,
"y":0.970000,
},
{"name":"rs138965"
,"x":41917900,
"y":0.180000,
},
{"name":"rs138967"
,"x":41918227,
"y":0.160000,
},
{"name":"rs138973"
,"x":41923076,
"y":0.490000,
},
{"name":"rs12158070"
,"x":41923533,
"y":0.630000,
},
{"name":"rs17515719"
,"x":41923905,
"y":0.280000,
},
{"name":"rs138975"
,"x":41924171,
"y":0.660000,
},
{"name":"rs1543792"
,"x":41924777,
"y":0.190000,
},
{"name":"rs1543793"
,"x":41924990,
"y":0.190000,
}
];
var margin={
"left":40,
"right":40,
"top":20,
"bottom":30
};
var test;
var svg;
function load(data)
{
    var max_height = 600;
    var max_width = 1000;
    var GWAS = 5e-8;
    width = max_width - margin.left - margin.right,
    height = max_height - margin.top - margin.bottom;

    //top left starts at 0
    var yScale = d3.scale.linear().domain([Math.log10(1),-Math.log10(1e-10)]).range([height,0]);
    var xScale = d3.scale.linear().domain([41865128,41924993]).range([0,width]);
    var yAxis = d3.svg.axis().scale(yScale).orient("left");
    var xAxis = d3.svg.axis().scale(xScale).ticks(5).orient("bottom");
    svg = d3.select("#scatterplot").append("svg")
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
    .attr("transform", "rotate(0)")
    .attr("x", width)
    .attr("y", -6)
    .style("text-anchor", "end")
    .text("MegaBase");

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
    .text("-log(P-Value)");

     svg.selectAll(".dot")
      .data(data)
    .enter().append("circle")
      .attr("class", function(d){if (d.y <= GWAS) {return "dot"} else {return "dot insig"}})
      .attr("r", 5)
      .attr("cx", function(d){return xScale(d.x)})
      .attr("cy", function(d){return yScale(-Math.log10(d.y))})
      .style("fill", "red");

    /*svg.selectAll(".dottext")
        .data(data)
        .enter().append("text")
        .attr("class",function(d){if (d.y <= GWAS) {return "dottext"} else {return "dottext insig"}})
        .text(function(d){return d.name})
        .attr("x", function(d){return xScale(d.x);})
        .attr("y", function(d){return yScale(-Math.log10(d.y));});*/

    /*svg.selectAll(".dotline")
    .data(data)
    .enter().append("line")
    .attr("class", function(d){if (d.y <= GWAS) {return "dotline"} else {return "dotline insig"}})
    .attr("x1",function(d){return xScale(d.x);})
    .attr("y1",height)
    .attr("x2", function(d){return xScale(d.x);})
    .attr("y2", function(d){return yScale(d.y);})
    .attr("stroke", "black")
    .attr("stroke-width", 2);*/

    svg.append("line")
    .attr("class", "GWAS")
    .attr("x1",0)
    .attr("y1",yScale(-Math.log10(GWAS)))
    .attr("x2", width)
    .attr("y2", yScale(-Math.log10(GWAS)))
    .attr("stroke", "gold")
    .attr("opacity", .9)
    .attr("stroke-width", 2)
    .attr("stroke-dasharray","5,5")
    .on("click",mousedown);

    svg.append("rect")
    .attr("x", 0)
    .attr("y", yScale(-Math.log10(GWAS)))
    .attr("width", width)
    .attr("height", height-yScale(-Math.log10(GWAS)))
    .attr("opacity", 0.4)
    .attr("fill", "Gray")
    .on("click",mousedown);
}

function mousedown(d,i)
{
    console.log(d);
    svg.on("mousemove",mousemove);
}
function mousemove()
{
    console.log("test");
    var m = d3.mouse(this);
    test.attr("y1",m[1])
        .attr("y2",m[1]);
}
function mouseup(){
    svg.on("mousemove",null);
}
function updateGraph(mode)
{
    if(mode > 0)
    {
        //change the domain for new data
        //add data that is necessary for the transition
        //add effects to the new inserted data.
        //add limits towards the zoom
        var yScale = d3.scale.linear().domain([Math.log10(1),-Math.log10(1e-10)]).range([height,0]);
        var xScale = d3.scale.linear().domain([40865128,42924993]).range([0,width]);
        var xAxis = d3.svg.axis().scale(xScale).ticks(5).orient("bottom");
        /*d3.selectAll(".dot").transition().duration(9000)
        .remove();
        d3.selectAll(".dottext").transition().duration(9000).remove();
        */
        data_set.push({"name":"rs1543793","x":40870001,"y":1e-9});
        data_set.push({"name":"rs1543","x":42700001,"y":1e-6});
        data_set.push({"name":"rs13793","x":42770001,"y":1e-3});
        var newdata = svg.selectAll(".dot").data(data_set);
        newdata.enter().append("circle").style("opacity",0);
        newdata.exit().transition().duration(5000).delay(400).remove();
        newdata.transition().duration(7000).delay(200)
        .attr("class", function(d){if (d.y <= 5e-8) {return "dot"} else {return "dot insig"}})
        .attr("r", 5)
        .attr("cx", function(d){return xScale(d.x)})
        .attr("cy", function(d){return yScale(-Math.log10(d.y))})
        .style("fill", "blue")
        .style("opacity",function(d){if (d.y <= 5e-8) {return 1;} else {return 0.4;}});
        d3.select(".x_axis")
        .transition()
        .duration(7000)
        .delay(200)
        .call(xAxis);
    }
    else
    {
        //decrease the x axis space
        var yScale = d3.scale.linear().domain([Math.log10(1),-Math.log10(1e-10)]).range([height,0]);
        var xScale = d3.scale.linear().domain([41865128,41924993]).range([0,width]);
        var xAxis = d3.svg.axis().scale(xScale).ticks(5).orient("bottom");
        var newdata = svg.selectAll(".dot").data(data_set);
        newdata.enter().append("circle");
        newdata.exit().transition().duration(5000).delay(700).remove();
        newdata.transition().duration(7000).delay(700)
        .attr("class", function(d){if (d.y <= 5e-8) {return "dot"} else {return "dot insig"}})
        .attr("r", 5)
        .attr("cx", function(d){return xScale(d.x)})
        .attr("cy", function(d){return yScale(-Math.log10(d.y))})
        .style("fill", "red");
        d3.select(".x_axis")
        .transition()
        .duration(7000)
        .delay(200)
        .call(xAxis);
    }
}