/*
This function loads the graph data.
params: data which is the gene_name of a given gene (ex MAPK1)
returns: calls the draw_network function to use d3 to graph the gene network
*/
function load_graph(data,phenotypes,mode,connection,source,gene_source)
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
        $scope.mode = ""
        $scope.setmode=function(mode_name)
        {
            logmode(mode_name);
        };
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
            var categories = {"CHD":0,"T2D":1};
            var normalize = {"Vegas":{"CHD":7.0,"T2D":7.0},"Magma":{"CHD":13.694821,"T2D":10.256733}};
            var found_category = false;
            var colors = ["Red","Blue"];
            var group = document.getElementById("graph_nodes").children;
            group = [].slice.call(group);
            group = group.filter(function(n){return n.className.animVal.contains("outer")});
            console.log($scope);
            for(var group_index in group)
            {
                //go back go default
                if(category=="Default")
                {
                    group[group_index].style="fill:white;opacity:1;";
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
                                association_score = $scope.phenotype_list[group[group_index].textContent][pheno_category][1]
                                normalize_constant = normalize[$scope.phenotype_source][category];
                                group[group_index].style="fill:"+colors[categories[category]]+";opacity:"+Math.max((association_score/normalize_constant),0.05)+";";
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
            var hiddenField3 = document.createElement("input");
            hiddenField3.setAttribute("type","hidden");
            hiddenField3.setAttribute("name", "source");
            hiddenField3.setAttribute("value", source.split(","));
            var hiddenField4 = document.createElement("input");
            hiddenField4.setAttribute("type","hidden");
            hiddenField4.setAttribute("name","gene_source");
            hiddenField4.setAttribute("value",gene_source);
            form.appendChild(hiddenField);
            form.appendChild(hiddenField2);
            form.appendChild(hiddenField3);
            form.appendChild(hiddenField4);
            document.body.appendChild(form);
            form.submit();
        };
        //use http get request to get the gene network id
        $http.get("networktize",{
            params:
            {
                "mode":mode,
                "genes":data,
                "connection":connection,
                "source":source
                //"user_phenotype_genes":$scope.phenotype_list
            }
        })
        //on success
        .success(
            function(response) 
            {
                $scope.graph = response;
                console.log($scope.graph);
                $http.get("grab_data",{
                    params:
                    {
                        "flag":"fill",
                        "genes":$scope.graph['genes'],
                        "gene_source":gene_source,
                    }
                })
                .success(function(response)
                {
                    console.log(response);
                    //merge the pheno type data
                    $scope.phenotype_list=merge($scope.phenotype_list, response["phenotypes"]["pheno_data"]);
                    $scope.phenotype_source = response["phenotypes"]["gene_source"];
                    //$scope.phenotype_categories= response["phenotypes"]["pheno_list"];
                    $scope.phenotype_categories=["CHD","T2D"];
                    $scope.drug_data=response["drugs"];
                    var progress = document.getElementById("bar");
                    progress.style="width:66%";
                    progress.textContent="Drawing The Network!!!";
                    var height = ($scope.graph["legend"]["line"].length + $scope.graph["legend"]["circle"].length) * 25;
                    draw_network($scope.graph,600,1280,$scope,response["categories"],height,100,[100,150,200,250],4);
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
    console.log(keys1);
    var keys2 = Object.keys(phenolist2);
    console.log(keys2);
    var intersection = keys2.filter(function(n){return keys1.indexOf(n) == -1;});
    if(intersection.length > 0)
    {
        for(var index in intersection)
        {
            phenolist1[intersection[index]] = phenolist2[intersection[index]];
        }
    }
    console.log(phenolist1);
    console.log(phenolist2);
    return phenolist2;
}