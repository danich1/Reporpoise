/*
This function loads the graph data.
params: data which is the gene_name of a given gene (ex MAPK1)
returns: calls the draw_graph function to use d3 to graph the gene network
*/
function load_graph(data,phenotypes,mode)
{
    // fix the data for a json object
    data = data.replace(/&quot;/g,'\'');
    phenotypes = decodeHTML(phenotypes);
    var app = angular.module('drug_search', []);
    //enable angular to use html5 urls
    app.config(['$locationProvider', function($locationProvider){$locationProvider.html5Mode({enabled: true,requireBase: false});}]);
    //angular drug_search controller
    app.controller('drug_search_control', function($scope,$http,$window,$location,$anchorScroll,$sce,$timeout) {
        //user entered phenotype data
        $scope.phenotype_list = JSON.parse(JSON.stringify(eval("(" + phenotypes + ")")));
        $scope.switch_case = false;
        $scope.class_label = "";
        $scope.finished = false;
        $scope.get_key = function(drug)
        {
            return Object.keys(drug)[0];
        };
        $scope.find_drug = function(drug_obj,gene_name)
        {
            for(var drug_index in drug_obj)
            {
                if(drug_index == gene_name)
                {
                    return drug_obj[drug_index];
                }
            }
        };
        // make sure to change when necessary
        $scope.update_graph = function(category)
        {
            var found_category = false;
            var colors = d3.scale.category10().range();
            var group = document.getElementsByClassName("gene");
            group = [].slice.call(group);
            group = group.filter(function(n){return n.nodeName=="circle"});
            for(var group_index in group)
            {
                //go back go default
                if(category=="default")
                {
                    group[group_index].style="fill:SaddleBrown;opacity:1;"
                }
                else
                {
                    if(group[group_index].textContent != "")
                    {
                        for(var pheno_category in $scope.phenotype_list[group[group_index].textContent])
                        {
                            if($scope.phenotype_list[group[group_index].textContent][pheno_category][0] == category)
                            {
                                found_category = true;
                                group[group_index].style="fill:"+colors[0]+";opacity:"+GetZPercent($scope.phenotype_list[group[group_index].textContent][pheno_category][1])+";";
                            }
                        }
                        if(!found_category)
                        {
                            group[group_index].style="fill:gray;opacity:.4;";
                        }
                        found_category=false;
                    }
                    else
                    {
                        group[group_index].style="fill:"+colors[0]+";opacity:1;";
                    }
                }
            }
        };
        $scope.loadgene=function(name)
        {
            //send the clicked gene back to the gene_wagon page using http POST method
            //csrftoken is needed or else django will throw an error
            var csrftoken = getCookie('csrftoken');
            var form = document.createElement("form");
            form.setAttribute("method", "POST");
            form.setAttribute("action", "search");
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", "gene_name");
            hiddenField.setAttribute("value",name);
            var hiddenField2 = document.createElement("input");
            hiddenField2.setAttribute("type","hidden");
            hiddenField2.setAttribute("name", "csrfmiddlewaretoken");
            hiddenField2.setAttribute("value", csrftoken);
            form.appendChild(hiddenField);
            form.appendChild(hiddenField2);
            document.body.appendChild(form);
            form.submit();
        };
        /*
        This function will draw a graph network using d3.
        params: data a listing of links and nodes needed for d3 ex {"nodes":[{"name":"MAPK1"}], "links":[{"target":<index of nodes>,"source":<index of nodes>}]}
        returns: a drawn gene node graph
        */
        $scope.draw_graph = function(data)
        {
            var index = -1;
            //The dimensions of the gene network and the offset values for the legend
            var width = document.body.offsetWidth || document.body.clientWidth;
            var width_offset = 100;
            var height = 600;
            var offset = 12.5;
            var offset_space = 25;
            var link_offset = 500;
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
                //console.log(d);
                $scope.switch_case = true;
                $scope.drug_list = $scope.drug_data[d.name];
                $scope.gene_name = d.name;
                $scope.$apply();
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
        };
        //use http get request to get the gene network id
        $http.get("networktize",{
            params:
            {
                "mode":mode,
                "genes":data,
                "acceptable_genes":$scope.phenotype_list
            }
        })
        //on success
        .success(
            function(response) 
            {
                $scope.graph = response;
                $http.get("grab_data",{
                    params:
                    {
                        "flag":"fill",
                        "genes":$scope.graph['genes']
                    }
                })
                .success(function(response)
                {
                    //console.log(response);
                    //merge the pheno type data
                    $scope.phenotype_list=merge($scope.phenotype_list, response["phenotypes"]["pheno_data"]);
                    //$scope.phenotype_categories= response["phenotypes"]["pheno_list"];
                    $scope.phenotype_categories=["CHD","T2D"];
                    $scope.drug_data=response["drugs"];
                    var progress = document.getElementById("bar");
                    progress.style="width:66%";
                    progress.textContent="Drawing The Network!!!";
                    $scope.draw_graph($scope.graph);
                    $timeout(function()
                    {
                        progress.style="width:100%";
                        progress.textContent="Elements will appear Shortly!!!!";
                        $scope.finished=true;
                    },2000);
                })
                .error(function(response)
                {
                    document.write(response);
                });
            }
            )
        //on failure
        .error(
            function(response)
            {
                document.write(response);
            }
            );   
    //still inside the controller
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

/* translate the groupped elements to a given position*/
function transform(d) {
  return "translate(" + d.x + "," + d.y + ")";
}
function decodeHTML(data_str)
{
    var txt = document.createElement("textarea");
    txt.innerHTML = data_str;
    return txt.value;
}
/* get the csrf cookie from the browser*/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function merge(phenolist1,phenolist2)
{
    var keys1 = Object.keys(phenolist1);
    //console.log(keys1);
    var keys2 = Object.keys(phenolist2);
    //console.log(keys2);
    var intersection = keys2.filter(function(n){return keys1.indexOf(n) == -1;});
    if(intersection.length > 0)
    {
        for(var index in intersection)
        {
            phenolist1[intersection[index]] = phenolist2[intersection[index]];
        }
    }
    return phenolist1;
}
//using the taylor series expansion of the normal cdf
//yay internets
function GetZPercent(z) 
  {
    //z == number of standard deviations from the mean

    //if z is greater than 6.5 standard deviations from the mean
    //the number of significant digits will be outside of a reasonable 
    //range
    if ( z < -6.5)
      return 0.0;
    if( z > 6.5) 
      return 1.0;

    var factK = 1;
    var sum = 0;
    var term = 1;
    var k = 0;
    var loopStop = Math.exp(-23);
    while(Math.abs(term) > loopStop) 
    {
      term = .3989422804 * Math.pow(-1,k) * Math.pow(z,k) / (2 * k + 1) / Math.pow(2,k) * Math.pow(z,k+1) / factK;
      sum += term;
      k++;
      factK *= k;

    }
    sum += 0.5;

    return sum;
  }