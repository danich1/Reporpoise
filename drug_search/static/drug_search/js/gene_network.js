var mode="";
//says if two indicies are neighbors
function is_neighbors(a,b,linkedByIndex)
{
    return a==b || typeof(linkedByIndex[a + "," + b]) != "undefined";
}
/* translate the groupped elements to a given position*/
function transform(d) 
{
  return "translate(" + d.x + "," + d.y + ")";
}
function logmode(mode_name)
{
    console.log(mode_name);
    mode = mode_name;
    console.log(mode);
}
//
function highlightNodes(outer_circle,inner_circle,text,links,node,linkedByIndex,toggle)
{
    //parent = all the nodes
    //text = all the texts
    if (toggle==0)
    {
        outer_circle.classed("nohighlight", function(d,i)
        {
            return is_neighbors(node.index,i,linkedByIndex) || is_neighbors(i,node.index,linkedByIndex) ? false : true;
        });
        inner_circle.classed("nohighlight", function(d,i)
        {
            return is_neighbors(node.index,i,linkedByIndex) || is_neighbors(i,node.index,linkedByIndex) ? false : true;
        });
        text.classed("nohighlight", function(d,i)
        {
            return is_neighbors(node.index,i,linkedByIndex) || is_neighbors(i,node.index,linkedByIndex) ? false : true;
        });
        links.classed("nohighlight", function(d,i)
        {
            return node.index != d.source.index && node.index != d.target.index;
        });
    }
    else
    {
       outer_circle.classed("nohighlight", false);
       inner_circle.classed("nohighlight", false);
       text.classed("nohighlight", false);
       links.classed("nohighlight", false);
    }
}
var svg;
//var zoom;
function draw_network(data,height,width,scope,categories,user_height,legend_offset,distances,layers)
{
    var index = -1;
    var offset = 10;
    var offset_space = 25;
    var midpoint = 0;
    var link_offset = 280;
    var linkedByIndex={};
    var toggle = 0;
    
    //create a force graph layout https://github.com/mbostock/d3/wiki/Force-Layout
    var force = d3.layout.force()
    .nodes(d3.values(data["nodes"]))
    .links(data["links"])
    .size([width,height])
    //Try and keep the layers in place
    .linkDistance(function(link, index){return distances[index % layers]})
    .charge(-170)
    .start();

    //build a link map for the highlight portion
    force.links().forEach(function(d)
    {
        linkedByIndex[d.source.index + "," + d.target.index] = true;
    });

    //zoom = d3.behavior.zoom()
    //.scaleExtent([1,4])
    //.on("zoom",zoomed);

    //create an svg object by selecting the tag that has the gene_network id 
    svg = d3.select("#gene_network")
    .append("svg")
    .attr("width",width)
    .attr("height",height);
    //.call(zoom);

    //create a legend for the gene network
    var legend = svg.append("g")
    .attr("class", "legend")
    .attr("transform", "translate(" + (legend_offset) + "," + 20 + ")");

    legend.append("rect")
    .attr("id", "legend_border")
    .attr("width", 150)
    .attr("height", user_height);

    //append the symbols and the names they represent
    var legend_line = legend.selectAll("line")
    .data(data.legend.line)
    .enter().append("line")
    .attr("class",function(d){return d.type})
    .attr("x1",3)
    .attr("y1",function(d,i){return offset+(i*offset_space)})
    .attr("x2",25)
    .attr("y2",function(d,i){midpoint=offset+(i*offset_space);return offset+(i*offset_space)});

    var legend_circle_container = legend.selectAll("circle").data(data.legend.circle);
    var legend_circle_outer = legend_circle_container.enter().append("circle")
    .attr("r", 10)
    .attr("cx", 14)
    .attr("cy",function(d,i){return midpoint+((i+1)*offset_space)})
    .attr("class", function(d){return "outer " + d.type});

    var legend_circle_inner = legend_circle_container.enter().append("circle")
    .attr("r", 5)
    .attr("cx",14)
    .attr("cy",function(d,i){return midpoint+((i+1)*offset_space)})
    .attr("class", function(d){if(d.type == "none"){return "inner_" + d.type} else {return "inner"}});

    var legend_text = legend.selectAll('text')
    .data(d3.merge([data.legend.line,data.legend.circle]))
    .enter().append('text')
    .attr("x",50)
    .attr("y",function(d,i) {return offset+((i*offset_space)+4)})
    .text(function(d){return d.data});

    //create the paths using the force links
    var path = svg.append("g").selectAll(".link")
    .data(force.links())
    .enter().append("line")
    .attr("class", function(d) { return d.type});

    var circle_container = svg.append("g").attr("id","graph_nodes").selectAll("circle").data(force.nodes());
    var circle2 = circle_container.enter().append("circle")
    .attr("r",10)
    .attr("class", function(d){return "outer " + d.type})
    .on("dblclick", function(d)
    {
        console.log(mode);
        if (typeof(scope) != 'undefined')
        {
            if(mode == 'highlight')
            {
                toggle = toggle > 0 ? 0 : 1;
                highlightNodes(circle,circle2,text,path,d,linkedByIndex,toggle);
            }
            else if(mode=='profile')
            {
                console.log(d);
                scope.switch_case = true;
                scope.drug_list = scope.drug_data[d.name];
                scope.gene_name = d.name;
                scope.$apply();
            }
        }
    });
    //create the circle nodes using the force.nodes data
    var circle = circle_container.enter().append("circle")
    .attr("r",5)
    .attr("class", function(d){if (d.type == "none") {return "inner_none"} else {return "inner"}})
    .attr("ng-href", "#myModal")
    .on("dblclick", function(d)
    {
        console.log(mode);
        if (typeof(scope) != 'undefined')
        {
            if(mode == 'highlight')
            {
                toggle = toggle > 0 ? 0 : 1;
                highlightNodes(circle,circle2,text,path,d,linkedByIndex,toggle);
            }
            else if(mode=='profile')
            {
                console.log(d);
                scope.switch_case = true;
                scope.drug_list = scope.drug_data[d.name];
                scope.gene_name = d.name;
                scope.$apply();
            }
        }
    })
    circle_container.call(force.drag);
    //append a title to each node
    circle2.append("title").text(function(d){return d.name});

    //append text to each gene node to show the name of each gene
    var text = svg.append("g").selectAll("text")
    .data(force.nodes())
    .enter().append("text")
    .attr("x", 10)
    .attr("y", ".31em")
    .attr("class", "text")
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
}
function zoomed()
{
    console.log(svg,d3.event.translate,d3.event.scale);
    console.log(zoom.scale());
    svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")")
}
