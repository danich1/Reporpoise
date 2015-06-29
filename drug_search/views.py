from django.shortcuts import render

from django.http import HttpResponse,Http404
from collections import defaultdict
from .models import *
import re, math, json,pickle,ast

#This is the initial method that gets called to show the homepages
def initialize(request):
    return render(request, 'drug_search/gene_select.html')

#This will render the reference page
def reference(request):
    return render(request,'drug_search/references.html')

#This method gets called to render the gene network
def network(request):
    if request.method=='POST':
        gene_name = request.POST.get("gene_name","")
        phenotypes = request.POST.get("phenotypes","")
        mode = request.POST.get("mode","")
    return render(request,'drug_search/network.html',{"gene_network":gene_name,"phenotypes":phenotypes,"mode":mode})

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
                gene_dict.update({gene_name:[]})
                if len(gene_obj) > 0:
                    if len(gene_obj) % 2 == 1:
                        raise Http404("The input is in valid!! Please check the input and try again!!")
                    for index in range(len(gene_obj)-1):
                        gene_dict[gene_name].append((gene_obj[index],float(gene_obj[index+1])))
        translate = int(round(105/math.tan(math.pi/len(gene_dict)))) if len(gene_dict) > 2 else 180 if len(gene_dict) == 2 else 0
        return render(request, 'drug_search/report.html', {"genes":json.dumps(gene_dict),"translate":translate})
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
        #created a dictionary of drug objects based on a gene name matched within the targets table
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
                #for each drug action append the action ex {"F2":{"categories":["inducer"],"uniprot":"P00734"}}
                for tar in drug.targets_set.all():
                    if tar.gene.gene_name in target:
                        target[tar.gene.gene_name]["categories"].append(tar.action)
                    else:
                        target.update({tar.gene.gene_name:{"categories":[tar.action],"uniprot":tar.gene.uniprot_id}})
                #Create the drug object and place it into drugs dictionary {"ATM":{"Caffeine":{"group":["approved"],"DrugID":["DB00201"."APRD00673"],"Targets":[{"F2":{"categories":["inducer"],"uniprot":"P00734"}}]}}}
                drugs[key].append({drug.name:{"group":[group.name for group in drug.group.all()],"DrugID":[drugID.drug_id for drugID in drug.drugid_set.all()],"Targets":target}})
                target={}
            #finalize the categories object using gene name as a key ex {"ATM": {"approved":{"approved":["UREA"etc..],"name":"approved"}}}
            categories[key] = [drug_group_dict[drug_group_element] for drug_group_element in drug_group_dict]
            #empty out drug group
            drug_group_dict = {}
        #return json object containing the data
        return HttpResponse(json.dumps({"drugs":drugs,"categories":categories,"phenotypes":gene_dict}),content_type='application/json')
    return Http404("ERROR")

#This method returns gene network json data based on a given gene list
#work on getting the links to only show drugs that have more then one gene target
def networktize(request):
    if request.method == 'GET':
        index = 1
        #get parameters
        gene_name = request.GET['gene']
        mode = request.GET['mode']
        acceptable_genes = dict(ast.literal_eval(request.GET['acceptable_genes']))
        #this is the json data that gets passed into the d3 network ex {"Nodes":[{}],"links":[{}]}
        network_graph ={"nodes":[{"name":gene_name,"type":"gene","url":"drug_search/search"}],"links":[]}
        #keep track of which genes interact with eachother and the drug interactions
        interaction_indicies = {gene_name:0}
        double_interaction = {}
        #load preprocessed data from python pickle (change to do real loading later)
        interactions = pickle.load(open('drug_search/data/interact.p','rb'))
        #Sift through the preprocessed data to graph all the gene-gene interactions that match given genes
        gene_interaction = filter(lambda x: x[0] == gene_name or x[1] == gene_name,interactions)
        if mode=='mini':
            gene_interaction = filter(lambda x: x[0] in acceptable_genes.keys() and x[1] in acceptable_genes.keys(), gene_interaction)
            other_genes = [interact[0] if interact[0] != gene_name else interact[1] for interact in gene_interaction if interact[0]]
        else:
            #grab the genes that don't match the query gene
            other_genes = [interact[0] if interact[0] != gene_name else interact[1] for interact in gene_interaction]
        #include the initial gene in the associated drug object
        other_genes.append(gene_name)
        #grab all the associated drugs that target a given gene
        associated_drugs = {gene: Drug.objects.filter(targets__gene__gene_name__iexact=gene) for gene in other_genes if len(Drug.objects.filter(targets__gene__gene_name__iexact=gene)) > 0}
        #for each associated drug
        for network_gene_name in associated_drugs:
            #if new gene add it into the interaction dictionary
            if network_gene_name not in interaction_indicies:
                network_graph["nodes"].append({"name":network_gene_name,"type":"gene","url":"drug_search/search"})
                interaction_indicies[network_gene_name] = index
                index = index + 1
            #append an interaction of a given gene with the target gene
            network_graph["links"].append({"source":interaction_indicies[network_gene_name],"target":interaction_indicies[gene_name],"type":"double"})
            #for each associated drug append a link from it to a gene (modify to only include drugs that target two genes)
            for drug in associated_drugs[network_gene_name]:
                if drug.name in double_interaction:
                    if drug.name not in interaction_indicies:
                        network_graph["nodes"].append({"name":drug.name,"type":"drug","url":drug.drugid_set.all()[0].drug_id})
                        interaction_indicies[drug.name] = index
                        index = index + 1
                    #only include drugs that target more than one gene
                    for interaction_gene_name in double_interaction[drug.name]:
                        network_graph["links"].append({"source":interaction_indicies[drug.name],"target":interaction_indicies[interaction_gene_name],"type":"single"})
                    double_interaction[drug.name]=[]
                    #append link
                    network_graph["links"].append({"source":interaction_indicies[drug.name],"target":interaction_indicies[network_gene_name],"type":"single"})
                else:
                    double_interaction.update({drug.name:[]})
                    double_interaction[drug.name].append(network_gene_name)
        #append a legend as well
        network_graph.update({"legend":{"line":[{"data":"gene-gene","type":"double"},{"data":"drug-gene","type":"single"}],"circle":[{"data":"gene"},{"data":"drug"}]}})
        network_graph.update({"genes":{gene:[] for gene in associated_drugs.keys()}})
        #return the json data
        return HttpResponse(json.dumps(network_graph), content_type='application/json')
    else:
        return Http404("Error Invalid Request")