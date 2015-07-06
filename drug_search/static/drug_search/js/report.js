//specify the angle to rotate initially
var theta=360;
/*give all the buttons an event listener*/
function init()
{
    //bind an event listener to the left and right button
    document.getElementById("left_button").addEventListener('click',rotate,false);
    document.getElementById("right_button").addEventListener('click',rotate,false);
}
/*this function rotates each frame on the gene wagon
params: event a event object that gets set when a button is clicked on
*/
function rotate(event)
{
    var b = document.getElementById("carousel");
    var increment = parseInt(event.target.getAttribute('data-increment'));
    var panelCount = b.children.length;
    theta += (360/panelCount) * increment * -1;
    b.style.transform="translateZ(-105px)rotateY(" + theta + "deg)";
}
/*this function loads all the information necessary from the django webserver
params: gene_list a comma seperated list of gene names
*/
function load(gene_list)
{
    //I love convoluted things
    gene_list = gene_list.replace(/&quot;/g,'\'');
    var app = angular.module('drug_search', []);
    //fixes the url for the website
    app.config(['$locationProvider', function($locationProvider){$locationProvider.html5Mode({enabled: true,requireBase: false});}]);
    app.controller('drug_search_control', function($scope,$http,$window,$location,$anchorScroll,$timeout) {
        //Hide the necessary table until a gene has been clicked on
        $scope.hide=true;
        $scope.finished = false;
        $scope.gene_color_class = {};
        //open the drug bank webpage based on gene id
        $scope.open_gene = function(link)
        {
            $window.open("http://www.drugbank.ca/biodb/polypeptides/"+link['uniprot'],"_blank");
        };
        //set up the parameters to show the table of contents
        $scope.change_table = function(active_gene)
        {
            $scope.hide=false;
            $scope.gene = active_gene;
            generate_cloud($scope.drug_data,$scope.gene);
            //draw_graph($scope.network_data,$scope.gene);
            document.getElementById("gene_network_name").value = $scope.gene;
        };
        // this will show the networkize it button
        $scope.gene_picked = function()
        {
            return typeof($scope.gene) != 'undefined';
        };
        //make the table of contents visible based on active gene
        $scope.show_table = function(active_gene)
        {
            return $scope.gene == active_gene;
        };
        // set up the parameter to show the drug content table
        $scope.change_content_table = function(active_category)
        {
            $scope.table_category = active_category;
        };
        // make the drug category table show
        $scope.show_content_table = function(active_category)
        {
            return $scope.table_category == active_category;
        };
        //set up the parameter to show the drug table
        $scope.show_drug = function(active_drug)
        {
            return $scope.drug == active_drug;
        }
        //show the selected drug table based on a given category
        $scope.show = function(id)
        {
            $scope.drug = $scope.find_drug(id);
        };
        $scope.find_drug = function(drug_name)
        {
            for(var index in $scope.drug_data[$scope.gene])
            {
                 if($scope.drug_data[$scope.gene][index][drug_name])
                {
                    return $scope.drug_data[$scope.gene][index];
                }
            }
        };
        $scope.get_category_class = function()
        {
            if(typeof($scope.table_category) != 'undefined')
            {
            return ($scope.table_category.replace($scope.gene,''));
            }
            return "none";  
        };
        $scope.set_color_class = function(drug_group)
        {
            for (var gene in drug_group)
            {
                $scope.gene_color_class[gene] = drug_group[gene][0].name;
            }    
            console.log($scope.gene_color_class);
        };
        $scope.form_submit = function(name)
        {
            var form = document.getElementById("networkform");
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", "mode");
            hiddenField.setAttribute("value", name);
            form.appendChild(hiddenField);
            form.submit();
        };
        //graph the gene-drug data from django
        $http.get("grab_data",{
            params:
            {
                "flag":"None",
                "genes":gene_list,
            }
        })
        .success(
            function(response) 
            {
                var progress = document.getElementById("bar");
                progress.style="width:100%";
                progress.textContent="Elements will appear Shortly!!";
                console.log(response);
                $scope.data_keys = Object.keys(response["drugs"]);
                $scope.drug_data = response["drugs"];
                $scope.drug_group = response["categories"];
                $scope.phenotype_list = response["phenotypes"];
                $scope.set_color_class($scope.drug_group);
                console.log($scope.gene_color_class);
                $http.get("networktize",{
                    params:
                    {
                    "genes":$scope.phenotype_list,
                    "mode":"mini"
                    }
                })
                .success(function(response)
                {
                    console.log(response);
                    $scope.network_data = response;
                    draw_graph($scope.network_data,"");
                    $timeout(function()
                    {
                        $scope.finished=true;
                    },2000);
                })
                .error(
                    function(response)
                    {
                        document.write(response);
                    }
                );

            }
        )
        //write out the error if it occurs
        .error(
            function(response)
            {
                document.write(response);
            }
        );
        }
    );
    //created my own angular filter to show the length of an object
    app.filter('object_len',function()
    {
        return function(object)
        {
            return Object.keys(object).length;
        };
    });
    app.directive('drugModal', function()
    {
        return{
            restrict:'A',
            link: function(scope, element,attrs)
            {
                scope.$watch(attrs.drugModal, function(value)
                {
                    // console.log(value);
                    if (value) element.modal('show');
                    else element.modal('hide');
                });
            }
        }
    });
}
//background-color: hsla({% verbatim %}{{drug_data[gene]|get_color}}{% endverbatim %}, 100%, 47%, 0.63);
function draw_graph(network_data,gene_name)
{
    var gene_network = document.getElementById("gene_network");
    var width = gene_network.clientWidth;
    width = 455;
    var height = 355;
    var width_offset = 10;
    var offset = 12.5;
    var offset_space = 25;
    /*if (gene_name == "")
    {
        data = network_data["mini"];
    }
    else
    {
        data = network_data["full"][gene_name];
        d3.select("#gene_network").selectAll("svg").remove();
    }*/
    data = network_data;
    console.log(data);
    var data_legend = network_data["legend"];

 //create a force graph layout https://github.com/mbostock/d3/wiki/Force-Layout
    var force = d3.layout.force()
    .nodes(d3.values(data["nodes"]))
    .links(data["links"])
    .size([width,height])
    .linkDistance(100)
    .charge(-170)
    .start();

    //create an svg object by selecting the tag that has the gene_network id 
    var svg = d3.select("#gene_network")
    .append("svg")
    .attr("width",width)
    .attr("height",height)

 //create a legend for the gene network
    var legend = svg.append("g")
    .attr("class", "legend")
    .attr("transform", "translate(" + (width_offset) + "," + 20 + ")");
    
    legend.append("rect")
    .attr("id", "legend_border")
    .attr("width", 139)
    .attr("height", 100);

    //append the symbols and the names they represent
    var legend_line = legend.selectAll("line")
    .data(data_legend.line)
    .enter().append("line")
    .attr("class",function(d){return d.type})
    .attr("x1",3)
    .attr("y1",function(d,i){return offset+(i*offset_space)})
    .attr("x2",25)
    .attr("y2",function(d,i){return offset+(i*offset_space)});

    var legend_circle = legend.selectAll("circle")
    .data(data_legend.circle)
    .enter().append("circle")
    .attr("r", 7.5)
    .attr("cx", 12.5)
    .attr("cy",function(d,i){return (offset*3)+((i+1)*offset_space)})
    .attr("class", function(d){return d.type});

    var legend_text = legend.selectAll('text')
    .data(d3.merge([data_legend.line,data_legend.circle]))
    .enter().append('text')
    .attr("x",50)
    .attr("y",function(d,i) {return offset+((i*offset_space)+4)})
    .text(function(d){return d.data});

    //create the paths using the force links
    var path = svg.append("g").selectAll(".link")
    .data(force.links())
    .enter().append("line")
    .attr("class", function(d) { return d.type});

    //create the circle nodes using the force.nodes data
    var circle = svg.append("g").attr("id","graph_nodes").selectAll("circle")
    .data(force.nodes())
    .enter().append("circle")
    .attr("r",7.5)
    .attr("class", function(d) { return d.type})
    .attr("ng-href", "#myModal")
    .on("dblclick", function(d,i)
    {
        console.log($scope.switch_case);
        if (d.type == "gene")
        {
            //console.log(d);
            $scope.switch_case = true;
            $scope.drug_list = $scope.drug_data[d.name];
            $scope.gene_name = d.name;
            $scope.$apply();
        }
    })
    .call(force.drag);
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
        text.attr("transform", transform);
    });

       
}
/* translate the groupped elements to a given position*/
function transform(d) {
  return "translate(" + d.x + "," + d.y + ")";
}
function generate_cloud(drug_data, gene_name)
{
    var word_cloud = document.getElementById("word_cloud");
    word_cloud.innerHTML="";
    var width = word_cloud.clientWidth;
    var height = 355
    //Have to figure out height later
    d3.layout.cloud().size([width,height])
    .words([
        "Hello", "world", "normally", "you", "want", "more", "words",
        "than", "this"].map(function(d) {
        return {text: d, size: 10 + Math.random() * 90};
      }))
    .rotate(function(word){return ~~(Math.random() * 2) * 90;})
    .fontSize(function(d) { return d.size; })
    .on("end", draw)
    .start()
}
function draw(words)
{
    var fill = d3.scale.category20();
    d3.select("#word_cloud").append("svg")
    .attr("width", 488)
    .attr("height", 350)
    .attr("class", "wordcloud")
    .append("g")
    .attr("transform", "translate(200,180)")
    .selectAll("text")
    .data(words)
    .enter().append("text")
    .style("font-size", function(d) { return d.size + "px"; })
    .style("font-family", "Impact")
    .style("fill", function(d, i) { return fill(i); })
    .attr("text-anchor","middle")
    .attr("transform", function(d) {
        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
    .text(function(d){return d.text;});
}