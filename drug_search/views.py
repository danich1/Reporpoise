from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse,Http404
from collections import defaultdict
from .models import *
import re, math, json,pickle,ast

def test(request):
    return render(request, 'drug_search/test.html')

def gene_table(request):
    return render(request, 'drug_search/gene_association.html')

#This is the initial method that gets called to show the homepages
def initialize(request):
    #return render(request, 'drug_search/gene_select.html', {"Dapple":len(Interactions.objects.filter(source="Dapple")), "String":len(Interactions.objects.filter(source="String"))})
    return render(request, 'drug_search/gene_select.html', {"Dapple":139738, "String":620720})

#This will render the reference page
def reference(request):
    return render(request,'drug_search/references.html')

#This method gets called to render the gene network
def network(request):
    if request.method=='POST':
        gene_name = request.POST.get("gene_name","")
        phenotypes = request.POST.get("phenotypes","")
        mode = request.POST.get("mode","")
        source = request.POST.get("source", "")
        connection = request.POST.get("connection", "")
    return render(request,'drug_search/network.html',{"gene_network":json.dumps({gene_name:""}),"phenotypes":phenotypes,"mode":mode,"connection":connection,"source":source})

# This method will parse the file or a gene list in order to render the gene wagon page correctly
def search(request):
    if request.method == 'POST':
        gene_dict = {}
        if(len(request.FILES.keys()) > 0):
            gene = "".join([chunk for chunk in request.FILES['file_upload'].chunks()])
        else:
            gene = request.POST.get("gene_name", "")
        gene = re.sub(r'\r+', '', gene)
        for gene_obj in re.split(r'[\n]+',gene):
            gene_obj = gene_obj.split(",")
            gene_name = gene_obj.pop(0)
            if gene_name != '':
                #using ensemble gene ids
                if "ENSG" in gene_name:
                    gene_name = Gene.objects.filter(gene_id__iexact=gene_name)[0].gene_name
                gene_dict.update({gene_name:[]})
                if len(gene_obj) > 0:
                    # if the user forgets to input a z-score for a trait. 
                    if len(gene_obj) % 2 == 1:
                        raise Http404("The input is in valid!! Please check the input and try again!!")
                    for index in range(len(gene_obj)-1):
                        gene_dict[gene_name].append((gene_obj[index],float(gene_obj[index+1])))
        translate = int(round(105/math.tan(math.pi/len(gene_dict)))) if len(gene_dict) > 2 else 180 if len(gene_dict) == 2 else 0
        return render(request, 'drug_search/report.html', {"genes":json.dumps(gene_dict),"translate":translate,"source":",".join(request.POST.getlist("source"))})
    raise Http404("Invalid Request Please Try Again!")

#This method returns drug json data based on a given gene list
def grab_data(request):
    if request.method == 'GET':
        #because I love convoluted things
        gene_dict = dict(ast.literal_eval(request.GET['genes']))
        gene_list = gene_dict.keys()
        #grab the phenotype data from the database if flag is true 
        if(request.GET['flag']=="fill"):
            temp_gene_dict = {}
            pheno_list = set([])
            gene_dict = {gene_id: Phenotype.objects.filter(phenotypemap__gene__gene_name__iexact=gene_id) for gene_id in gene_list}
            for gene_id in gene_dict:
                temp_gene_dict.update({gene_id:[]})
                for gene_pheno in gene_dict[gene_id]:
                    pheno_list.append(gene_pheno.phenotype.name)
                    temp_gene_dict[gene_id].append((gene_pheno.phenotype.name,gene_pheno.z_score))
            gene_dict={"pheno_data":temp_gene_dict,"pheno_list":list(pheno_list)}
        drugs = {}
        target = {}
        categories = {}
        drug_group_dict = {}
        #created a dictionary of drug objects based on a gene name or ensembl gene id matched within the targets table
        drug_list = {gene_name: Drug.objects.filter(targets__gene__gene_name__iexact=gene_name).distinct() for gene_name in gene_list}
        #for each key in the drug_list dictionary 
        for key in drug_list:
            #created the categories and drug dictionaries where the key is the gene name ex {"MAPK1":{}}
            categories.update({key:[]})
            drugs.update({key:[]})    
            #for each drug in the list of drugs based on gene key
            for drug in drug_list[key]:
                #for each drug group grab the drug group name ex {"approved":{"approved":["UREA"etc..],"name":"approved"}}
                for drug_group in drug.group.all():
                    if drug_group.name not in drug_group_dict:
                        drug_group_dict.update({drug_group.name:{drug_group.name:[],"name":drug_group.name}})
                    drug_group_dict[drug_group.name][drug_group.name].append(drug.name)
                #for each drug action append the action ex {"F2":{"categories":["inducer"],"ensembl":"ENSG00000180210"}}
                for tar in drug.targets_set.all():
                    if tar.gene.gene_name in target:
                        target[tar.gene.gene_name]["categories"].append(tar.action)
                    else:
                        target.update({tar.gene.gene_name:{"categories":[tar.action],"ensembl":tar.gene.gene_id}})
                #Create the drug object and place it into drugs dictionary {"ATM":{"Caffeine":{"group":["approved"],"DrugID":["DB00201"."APRD00673"],"Targets":[{"F2":{"categories":["inducer"],"uniprot":"P00734"}}]}}}
                drugs[key].append({drug.name:{"group":[group.name for group in drug.group.all()],"DrugID":[drugID.drug_id for drugID in drug.drugid_set.all()],"Targets":target}})
                target={}
            #a dictionary to manually order the group options
            drug_group_order_map = {"approved":0, "investigational":1, "experimental":2,"nutraceutical":3,"withdrawn":4,"illicit":5}
            #I am sorting the categories here
            drug_group_keys = sorted(drug_group_dict.keys(), key=lambda x: drug_group_order_map[x])
            #take a closer look might end up removing this
            #finalize the categories object using gene name as a key ex {"ATM": {"approved":{"approved":["UREA"etc..],"name":"approved"}}}
            if len(drug_list[key]) == 0:
                categories[key] = [{"unknown":[], "name":"unknown"}]
            else:
                categories[key] = [drug_group_dict[drug_group_element] for drug_group_element in drug_group_keys]
            #empty out drug group
            drug_group_dict = {}
        #return json object containing the data
        return HttpResponse(json.dumps({"drugs":drugs,"categories":categories,"phenotypes":gene_dict}),content_type='application/json')
    return Http404("ERROR")

#This method returns gene network json data based on a given gene list
#work on getting the links to only show drugs that have more then one gene target
#mini network is genes within the query list only
#full network is all the iteractions a given gene has
def networktize(request):
    if request.method == 'GET':
        index = 0
        #get parameters
        mode = request.GET['mode']
        #print request.GET['genes']
        gene_list = dict(ast.literal_eval(request.GET['genes'])).keys()
        #need interaction source
        source = request.GET['source'].split(",")
        #if the user wants indirect connections as well
        indirect = request.GET['connection'] == 'Indirect'
        #this is the json data that gets passed into the d3 network ex {"Nodes":[{}],"links":[{}]}
        network_graph = {"nodes":[],"links":[]}
        #keep track of each gene interaction
        interaction_indicies = {}
        total_genes = {}
        #keep track of the gene groups approved, drugable, etc 
        gene_group = set({})
        for gene_name in gene_list:
            interactions = Interactions.objects.filter((Q(gene_source=gene_name)|Q(gene_target=gene_name))&Q(source__in=source))
            for interaction in interactions:
                case = "direct"
                if mode=="mini":
                    #only include iteractions that are in the query list
                    # if both genes are in the gene query
                    if interaction.gene_source.gene_name in gene_list and interaction.gene_target.gene_name in gene_list:
                        if interaction.gene_source.gene_name not in interaction_indicies:
                            interaction_indicies.update({interaction.gene_source.gene_name:index})
                            network_graph["nodes"].append({"name":interaction.gene_source.gene_name,"url":"drug_search/search","type": interaction.gene_source.category.all()[0].name if len(interaction.gene_source.category.all())>0 else "none"})
                            gene_group.add(interaction.gene_source.category.all()[0].name if len(interaction.gene_source.category.all())>0 else "none")
                            index = index + 1
                        if interaction.gene_target.gene_name not in interaction_indicies:
                            interaction_indicies.update({interaction.gene_target.gene_name:index})
                            network_graph["nodes"].append({"name":interaction.gene_target.gene_name,"url":"drug_search/search","type": interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none"})
                            gene_group.add(interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none")
                            index = index + 1
                        #don't want the gene to target itself
                        if interaction.gene_source.gene_name != interaction.gene_target.gene_name:
                            network_graph["links"].append({"source":interaction_indicies[interaction.gene_source.gene_name],"target":interaction_indicies[interaction.gene_target.gene_name],"type":case})
                    elif interaction.gene_source.gene_name in gene_list:
                        if interaction.gene_source.gene_name not in interaction_indicies:
                            interaction_indicies.update({interaction.gene_source.gene_name:index})
                            network_graph["nodes"].append({"name":interaction.gene_source.gene_name,"url":"drug_search/search","type": interaction.gene_source.category.all()[0].name if len(interaction.gene_source.category.all())>0 else "none"})
                            gene_group.add(interaction.gene_source.category.all()[0].name if len(interaction.gene_source.category.all())>0 else "none")
                            index = index + 1
                    else:
                        if interaction.gene_target.gene_name not in interaction_indicies:
                            interaction_indicies.update({interaction.gene_target.gene_name:index})
                            network_graph["nodes"].append({"name":interaction.gene_target.gene_name,"url":"drug_search/search","type": interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none"})
                            gene_group.add(interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none")
                            index = index + 1
                else:
                    #if one of the genes is in the gene query
                    if interaction.gene_source.gene_name in gene_list:
                        #if the gene has not been seen then add it to the full network and add the node into the full network node list
                        if interaction.gene_source.gene_name not in interaction_indicies:
                            total_genes.update({interaction.gene_source.gene_name:""})
                            interaction_indicies.update({interaction.gene_source.gene_name:0,"count":1})
                            network_graph["nodes"].append({"name":interaction.gene_source.gene_name,"url":"drug_search/search","type": interaction.gene_source.category.all()[0].name if len(interaction.gene_source.category.all())>0 else "none"})
                            gene_group.add(interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none")
                        if interaction.gene_target.gene_name not in interaction_indicies:
                            total_genes.update({interaction.gene_target.gene_name:""})
                            interaction_indicies[interaction.gene_target.gene_name] = interaction_indicies["count"]
                            interaction_indicies["count"] = interaction_indicies["count"] + 1
                            network_graph["nodes"].append({"name":interaction.gene_target.gene_name,"url":"drug_search/search","type": interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none"})
                            gene_group.add(interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none")
                        network_graph["links"].append({"source":interaction_indicies[interaction.gene_source.gene_name],"target":interaction_indicies[interaction.gene_target.gene_name],"type":case})
                        if indirect:
                            other_interactions = Interactions.objects.filter((Q(gene_source=interaction.gene_target.gene_name)&Q(gene_target__in=filter(lambda x:x != "count" and x != interaction.gene_source.gene_name,interaction_indicies.keys()))|Q(gene_target=interaction.gene_target.gene_name)&Q(gene_source__in=filter(lambda x:x != "count" and x != interaction.gene_source.gene_name,interaction_indicies.keys())))&Q(source__in=["Dapple"]))
                            for other_interaction in other_interactions:
                                network_graph["links"].append({"source":interaction_indicies[other_interaction.gene_source.gene_name],"target":interaction_indicies[other_interaction.gene_target.gene_name],"type":"indirect"})
                    else:
                        #if the gene has not been seen then add it to the full network and add the node into the full network node list
                        if interaction.gene_target.gene_name not in interaction_indicies:
                            total_genes.update({interaction.gene_target.gene_name:""})
                            interaction_indicies.update({interaction.gene_target.gene_name:0,"count":1})
                            network_graph["nodes"].append({"name":interaction.gene_target.gene_name,"url":"drug_search/search","type": interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none"})
                            gene_group.add(interaction.gene_target.category.all()[0].name if len(interaction.gene_target.category.all())>0 else "none")
                        if interaction.gene_source.gene_name not in interaction_indicies:
                            total_genes.update({interaction.gene_source.gene_name:""})
                            interaction_indicies[interaction.gene_source.gene_name] = interaction_indicies["count"]
                            interaction_indicies["count"] = interaction_indicies["count"] + 1
                            network_graph["nodes"].append({"name":interaction.gene_source.gene_name,"url":"drug_search/search","type": interaction.gene_source.category.all()[0].name if len(interaction.gene_source.category.all())>0 else "none"})
                            gene_group.add(interaction.gene_source.category.all()[0].name if len(interaction.gene_source.category.all())>0 else "none")
                        network_graph["links"].append({"source":interaction_indicies[interaction.gene_target.gene_name],"target":interaction_indicies[interaction.gene_source.gene_name],"type":case})
                        if indirect:
                            other_interactions = Interactions.objects.filter((Q(gene_source=interaction.gene_source.gene_name)&Q(gene_target__in=filter(lambda x:x != "count" and x != interaction.gene_target.gene_name,interaction_indicies.keys()))|Q(gene_target=interaction.gene_source.gene_name)&Q(gene_source__in=filter(lambda x:x != "count" and x != interaction.gene_target.gene_name,interaction_indicies.keys())))&Q(source__in=["Dapple"]))
                            for other_interaction in other_interactions:
                                network_graph["links"].append({"source":interaction_indicies[other_interaction.gene_source.gene_name],"target":interaction_indicies[other_interaction.gene_target.gene_name],"type":"indirect"})
        if mode == 'mini':
            network_graph.update({"legend":{"line":[{"data":"Direct","type":"direct"}],"circle":[]}})
            network_graph["legend"]["circle"] = [{"data":group.capitalize(), "type":group} for group in gene_group]
        else:
            if indirect:
                network_graph.update({"legend":{"line":[{"data":"Direct","type":"direct"}, {"data":"Indirect","type":"indirect"}],"circle":[]}})
            else:
                network_graph.update({"legend":{"line":[{"data":"Direct","type":"direct"}],"circle":[]}})
            network_graph["legend"]["circle"] = [{"data":group.capitalize(), "type":group} for group in gene_group]
            network_graph.update({"genes":total_genes})
        #return the json data
        return HttpResponse(json.dumps(network_graph), content_type='application/json')
    else:
        return Http404("Error Invalid Request")