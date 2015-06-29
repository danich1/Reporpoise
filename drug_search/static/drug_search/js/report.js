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
            document.getElementById("gene_network_name").value = $scope.gene;
        };
        // this will show the networkize it button
        $scope.gene_picked = function()
        {
            return typeof $scope.gene != 'undefined';
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
                "genes":gene_list
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
                $timeout(function()
                    {
                        $scope.finished=true;
                    },2000);

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
function generate_cloud(drug_data, gene_name)
{
    document.getElementById("word_cloud").innerHTML="";
    d3.layout.cloud().size([488,350])
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