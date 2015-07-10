function draw_network(data,height,width,scope,categories)
{
    console.log(scope);
    var index = -1;
    var width_offset = 100;
    var offset = 12.5;
    var offset_space = 25;
    var link_offset = data["nodes"].length;
    //create a force graph layout https://github.com/mbostock/d3/wiki/Force-Layout
    var force = d3.layout.force()
    .nodes(d3.values(data["nodes"]))
    .links(data["links"])
    .size([width,height])
    .linkDistance(link_offset)
    .charge(-170)
    .start();

    //create an svg object by selecting the tag that has the gene_network id 
    var svg = d3.select("#gene_network")
    .append("svg")
    .attr("width",width)
    .attr("height",height)

    //create the paths using the force links
    var path = svg.append("g").selectAll(".link")
    .data(force.links())
    .enter().append("line")
    .attr("class", function(d) { return d.type});

    var circle_container = svg.append("g").attr("id","graph_nodes").selectAll("circle").data(force.nodes());
    var circle2 = circle_container.enter().append("circle")
    .attr("r",10)
    .attr("class", "outer");
    //create the circle nodes using the force.nodes data
    var circle = circle_container.enter().append("circle")
    .attr("r",7.5)
    .attr("class", function(d) { return d.type})
    .attr("ng-href", "#myModal")
    .on("dblclick", function(d,i)
    {
        if (typeof(scope) != 'undefined')
        {
            console.log(scope.switch_case);
            //console.log(d);
            scope.switch_case = true;
            scope.drug_list = scope.drug_data[d.name];
            scope.gene_name = d.name;
            scope.$apply();
        }
    })
    circle_container.call(force.drag);
    //append a title to each node
    circle.append("title").text(function(d){return d.name});

    //append text to each gene node to show the name of each gene
    var text = svg.append("g").selectAll("text")
    .data(force.nodes())
    .enter().append("text")
    .attr("x", 8)
    .attr("y", ".31em")
    .attr("class", function(d){return d.type})
    .text(function(d){ return d.name;});

// apply the physics simulation on the gene network graph
force.on("tick", function()
{
    path.attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });
    circle.attr("transform", transform);
    circle2.attr("transform", transform);
    text.attr("transform", transform);
});

//create a legend for the gene network
var legend = svg.append("g")
.attr("class", "legend")
.attr("transform", "translate(" + (width_offset) + "," + 20 + ")");

legend.append("rect")
.attr("id", "legend_border")
.attr("width", 150)
.attr("height", 100);

//append the symbols and the names they represent
var legend_line = legend.selectAll("line")
.data(data.legend.line)
.enter().append("line")
.attr("class",function(d){return d.type})
.attr("x1",3)
.attr("y1",function(d,i){return offset+(i*offset_space)})
.attr("x2",25)
.attr("y2",function(d,i){return offset+(i*offset_space)});

var legend_circle = legend.selectAll("circle")
.data(data.legend.circle)
.enter().append("circle")
.attr("r", 7.5)
.attr("cx", 12.5)
.attr("cy",function(d,i){return (offset*3)+((i+1)*offset_space)})
.attr("class", function(d){return d.type});

var legend_text = legend.selectAll('text')
.data(d3.merge([data.legend.line,data.legend.circle]))
.enter().append('text')
.attr("x",50)
.attr("y",function(d,i) {return offset+((i*offset_space)+4)})
.text(function(d){return d.data});
}
/* translate the groupped elements to a given position*/
function transform(d) {
  return "translate(" + d.x + "," + d.y + ")";
}