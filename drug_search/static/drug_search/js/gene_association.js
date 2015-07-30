function init()
{
    var app = angular.module('gene_association', []);
    //enable angular to use html5 urls
    app.config(['$locationProvider', function($locationProvider){$locationProvider.html5Mode({enabled: true,requireBase: false});}]);
    //angular drug_search controller
    app.controller('gene_association_control', function($scope,$http,$window,$location,$anchorScroll,$sce,$timeout) {
        $http.get("networktize",{
            params:
            {
                "mode":'full',
                "genes":"{'MAPK1':''}",
                "connection":'Indirect',
                "source":'Dapple'
                //"user_phenotype_genes":$scope.phenotype_list
            }
        })
        .success(function(response)
        {
            console.log(response);
            draw_list(response);
        })
        .error(function(response)
        {
            document.write(response);
        });
    });
}
function draw_list(graph)
{
    var index1 = 0;
    var index2 = 0;
    graph["nodes"].forEach(function(d,i){
        if(d.type == "none" || d.type =="Druggable")
        {
            d.y = d.py = (index1+1) * 25; 
            d.x = d.px = 800;
            index1 = index1 + 1;
        }
        else
        {
            d.y = d.py = (index2+1) * 50;
            d.x = d.px = 200;
            index2 = index2 + 1;
        }
        d.fixed=true;
    });
    var svg = d3.select("#gene_table").append('svg')
    .attr('width', 1000)
    .attr('height', 2000);
    var force = d3.layout.force()
    .nodes(graph["nodes"])
    .links(graph["links"])
    .size([960,500])
    .charge(-170)
    .linkDistance(40)

    //create the paths using the force links
    var path = svg.append("g").selectAll(".link")
    .data(force.links())
    .enter().append("line")
    .attr("class", function(d) { return d.type})

    //emperical container
    var emperical_circle_container = svg.append("g").attr("id","graph_nodes").selectAll("circle").data(force.nodes().filter(function(d,i){return d.type!="none" && d.type!="Druggable"}));
    var emperical_circle2 = emperical_circle_container.enter().append("circle")
    .attr("r",10)
    .attr("class", function(d){return "outer " + d.type});
    //create the circle nodes using the force.nodes data
    var emperical_circle = emperical_circle_container.enter().append("circle")
    .attr("r",5)
    .attr("class", function(d){if (d.type == "none") {return "inner_none"} else {return "inner"}});

    //append a title to each node
    emperical_circle2.append("title").text(function(d){return d.name});

    //append text to each gene node to show the name of each gene
    var emperical_text = svg.append("g").selectAll("text")
    .data(force.nodes().filter(function(d,i){return d.type!="none" && d.type!="Druggable"}))
    .enter().append("text")
    .attr("x", 12)
    .attr("y", ".31em")
    .attr("class", "text")
    .text(function(d){ return d.name;});

    //theoretical container
    var theoretical_circle_container = svg.append("g").attr("id","graph_nodes").selectAll("circle").data(force.nodes().filter(function(d,i){return d.type=="none" || d.type=="Druggable"}));
    var theoretical_circle2 = theoretical_circle_container.enter().append("circle")
    .attr("r",10)
    .attr("class", function(d){return "outer " + d.type})
    //create the circle nodes using the force.nodes data
    var theoretical_circle = theoretical_circle_container.enter().append("circle")
    .attr("r",5)
    .attr("class", function(d){if (d.type == "none") {return "inner_none"} else {return "inner"}})
    //append a title to each node
    theoretical_circle2.append("title").text(function(d){return d.name});

    //append text to each gene node to show the name of each gene
    var theoretical_text = svg.append("g").selectAll("text")
    .data(force.nodes().filter(function(d,i){return d.type=="none" || d.type=="Druggable"}))
    .enter().append("text")
    .attr("x", 12)
    .attr("y", ".31em")
    .attr("class", "text")
    .text(function(d){ return d.name;});

    force.on("tick", function()
    {
        emperical_circle.attr("transform", transform);
        emperical_circle2.attr("transform", transform);
        emperical_text.attr("transform", transform);

        theoretical_circle.attr("transform", transform);
        theoretical_circle2.attr("transform", transform);
        theoretical_text.attr("transform", transform);

        path.attr("x1", function(d) {return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
    });
    force.start();
    emperical_circle_container.call(force.drag);
    theoretical_circle_container.call(force.drag);
}
function transform(d)
{
    return "translate(" + d.x + "," + d.y + ")";
}