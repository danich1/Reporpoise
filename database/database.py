# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 15:59:03 2015

@author: Dave
"""
import pandas as pd
import nltk
import xml.etree.cElementTree as ET
import codecs
import HTMLParser
import re
import tqdm
import argparse
import pdb
import os

def read_data(filename,sep,header=0,index_col=None):
    return pd.read_csv(filename,sep=sep,header=header,index_col=index_col)

def read_drug_bank(tree_root,allowed_gene_names,drug_group_order_map):
    drug_dict = {"DB_ID":[],"groups":[],"gene":[],"indication":""}
    html = HTMLParser.HTMLParser()
    gene_data = []
    gene_group_map = {}
    for drug in tqdm.tqdm(tree_root):
        for child in drug:
            if "{http://www.drugbank.ca}drugbank-id" in child.tag:
                drug_dict["DB_ID"].append(child.text)
            elif "{http://www.drugbank.ca}groups" in child.tag:
                for group_child in child:
                    if "{http://www.drugbank.ca}group" in group_child.tag:
                        drug_dict["groups"].append(group_child.text)
                if (drug_dict["groups"]) > 1:
                    sorted(drug_dict["groups"], key=lambda x: drug_group_order_map[x])
            elif "{http://www.drugbank.ca}name" in child.tag:
                drug_dict["name"] = child.text
            elif "{http://www.drugbank.ca}indication" in child.tag:
                if child.text:
                    indication = child.text
                    escaped_indication = html.unescape(indication)
                    escaped_indication = re.sub(r'<i>|</i>','',escaped_indication.strip())
                    escaped_indication = re.sub(r'(\r|\n)+','',escaped_indication)
                    if drug_dict["name"] =='Urea':
                        escaped_indication = re.sub('(<\w+>|</\w+>)+', '',escaped_indication)
                    drug_dict["indication"] = escaped_indication
            elif "{http://www.drugbank.ca}targets" in child.tag:
                for sub_child in child:
                    if len(sub_child) > 0:
                        skip = False
                        if "{http://www.drugbank.ca}target" in sub_child.tag:
                            for sub_sub_child in sub_child: #in side target
                                if "{http://www.drugbank.ca}actions" in sub_sub_child.tag:
                                    if len(list(sub_sub_child)) == 0:
                                        gene_data.append("unknown")
                                    else:
                                        for sub_sub_sub_child in sub_sub_child: #inside action
                                            if "{http://www.drugbank.ca}action" in sub_sub_sub_child.tag:
                                                gene_data.append(sub_sub_sub_child.text)
                                elif "{http://www.drugbank.ca}polypeptide" in sub_sub_child.tag:
                                    for sub_sub_sub_child in sub_sub_child:
                                        if "{http://www.drugbank.ca}gene-name" in sub_sub_sub_child.tag:
                                            if sub_sub_sub_child.text in allowed_gene_names:
                                                gene_group_map[sub_sub_sub_child.text]=drug_dict["groups"][0]
                                                drug_dict["gene"].append((gene_data,sub_sub_sub_child.text))
                                else:
                                    pass
                            gene_data = []
                    else:
                        skip = True
        if not(skip):
            yield (drug_dict,gene_group_map)
        drug_dict = {"DB_ID":[],"groups":[],"gene":[],"indication":""}
        gene_group_map = {}

def sentence_parser(sentence):
    tokens = nltk.word_tokenize(sentence)
    tokens = nltk.pos_tag(tokens)
    return tokens
    
def create_gene_string(drug_bank_gene_table,gene_table):
    output_str = ""
    for index,values in drug_bank_gene_table.iterrows():
        category = ""
        if values[1] in gene_table.index:
            category = gene_table.loc[values[1]][0]
        if category != "":
            output_str +="{\n\"fields\":{\n\"category\":[\"%s\"],\n\"gene_id\":\"%s\"\n},\n\"model\":\"drug_search.gene\",\n\"pk\":\"%s\"\n},\n" % (category,values[0],values[1])
        else:
            output_str +="{\n\"fields\":{\n\"category\":[],\n\"gene_id\":\"%s\"\n},\n\"model\":\"drug_search.gene\",\n\"pk\":\"%s\"\n},\n" % (values[0],values[1])
    output_str = output_str[:-2] + "\n]"
    return output_str
    
def create_group_string(group_list):
    output_str = ""
    for group in group_list:
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.group\",\n\"pk\":\"%s\"\n},\n"%(group)
    output_str = output_str[:-2] + "\n]"
    return output_str
    
def create_drug_string(drug_id_table,drug_group_table):
    output_str = ""
    for (name,drug_group) in drug_group_table.groupby("Name"):
        output_str +="{\n\"fields\":{\n\"group\":[%s]\n},\n\"model\":\"drug_search.drug\",\n\"pk\":\"%s\"\n},\n" % (",".join("\"%s\""% (group) for group in drug_group["Group"]),name)
    for (name,drug_id_group) in drug_id_table.groupby("Name"):
        for drug_id in drug_id_group["Drug Bank Id"]:
            output_str +="{\n\"fields\":{\n\"name\":\"%s\"\n},\n\"model\":\"drug_search.drugid\",\n\"pk\":\"%s\"\n},\n" % (name,drug_id)
    output_str = output_str[:-2] + "\n]"    
    return output_str

def create_drug_target_string(drug_gene_table):
    output_str = ""
    index = 1
    for (name,drug_target_group) in drug_gene_table.groupby("Name"):
        for gene, gene_action in zip(drug_target_group["Gene Name"],drug_target_group["Gene Action"]):
            output_str+="{\n\"fields\":{\n\"action\":\"%s\",\n\"gene\":\"%s\",\n\"drug\":\"%s\"\n},\n\"model\":\"drug_search.targets\",\n\"pk\":%d\n},\n"%(gene_action,gene,name,index)
            index = index + 1
    output_str = output_str[:-2] + "\n]"
    return output_str
    
def create_interaction_string(sources,string_interaction_list,inweb_interaction_list):
    output_str = ""
    pk = 0
    for source in sources:
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.interactionsource\",\n\"pk\":\"%s\"\n},\n" % (source)
    for interaction in string_interaction_list:
        if interaction[0] != interaction[1]:
            output_str += "{\n\"fields\":{\n\"source\":[\"String\"],\n\"gene_source\":\"%s\",\n\"gene_target\":\"%s\"\n},\n\"model\":\"drug_search.interactions\",\n\"pk\":%d\n},\n" % (interaction[0],interaction[1],pk)
            pk = pk + 1
    for interaction in inweb_interaction_list:
        if interaction[0] != interaction[1]:
            output_str += "{\n\"fields\":{\n\"source\":[\"Dapple\"],\n\"gene_source\":\"%s\",\n\"gene_target\":\"%s\"\n},\n\"model\":\"drug_search.interactions\",\n\"pk\":%d\n},\n" % (interaction[0],interaction[1],pk)
            pk = pk + 1
    output_str = output_str[:-2] + "\n]" 
    return output_str
    
def create_wordcloud_string(category_map):
    output_str = ""
    for category in category_map:
        output_str+="{\n\"fields\":{\n\"drug\":[%s],\n\"count\":%d\n},\n\"model\":\"drug_search.word\",\n\"pk\":\"%s\"\n},\n" % (",".join(["\"%s\"" % (drug) for drug in category_map[category]]),len(category_map[category]),category)
    output_str = output_str[:-2] + "\n]" 
    return output_str

def create_gene_score_source_string(phenotype_dict):
    output_str = ""
    skip = False
    for phenotype_source in phenotype_dict:
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.genescoresource\",\n\"pk\":\"%s\"\n},\n" % (phenotype_source)
        if not skip:
            for phenotype in phenotype_dict[phenotype_source]:
                output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.phenotype\",\n\"pk\":\"%s\"\n},\n" % (phenotype)
            skip = True
    output_str = output_str[:-2] + "\n]"
    return output_str

def create_phenotype_string(phenotype_dict):
    output_str = ""
    pk = 0
    allowed_genes = pd.read_csv("Allowed Genes.csv",names=["Gene"])
    for phenotype_source in phenotype_dict:
           for phenotype in phenotype_dict[phenotype_source]:
                for index,row in tqdm.tqdm(phenotype_dict[phenotype_source][phenotype].iterrows()):
                    if row['Gene'] in list(allowed_genes['Gene']):
                        output_str+="{\n\"fields\":{\n\"source\":\"%s\",\n\"gene\":\"%s\",\n\"phenotype\":\"%s\",\n\"p_val\":%f,\n\"log_score\":%f},\n\"model\":\"drug_search.phenotypemap\",\n\"pk\":%d\n},\n" % (phenotype_source,row['Gene'],phenotype,row['Pvalue'],row['log_score'],pk)
                        pk = pk + 1
    output_str = output_str[:-2] + "\n]"
    return output_str

drug_group_order_map = {"approved":0, "investigational":1, "experimental":2,"nutraceutical":3,"withdrawn":4,"illicit":5}
parser = argparse.ArgumentParser(prog="Database Generator",description="This program generates the data for the django database.")
parser.add_argument("-s","--string",help="This argument is used to read in the protein-protein interactions from string database. Args:<File Name>",nargs=1) 
parser.add_argument("-i","--inweb",help="This argument is used to read in protein-protein interactions from the inweb database. Args:<Interaction File Name><Protein id File Name>",nargs=2)
parser.add_argument("-d","--drugbank",help="This argument is used to read in the drug data from drugbank.ca. Args:<File Name>",nargs=1)
parser.add_argument("-e","--ensembl",help="This argument is used to read in the gene information from ensembl.Args<Master Gene File><Sequence File>",nargs="+")
parser.add_argument("-o","--output",help="This argument is used to print out the data in json format. Args:<output folder>",nargs=1)
parser.add_argument("-w","--wordcloud",help="This argument is used to input a list of word cloud categories. Args: <Input file>",nargs=1)
parser.add_argument("-p","--phenotype",help="This argument is used to input a list of gene - phenotype associations. Args: <Input file>",nargs='+')
args = parser.parse_args()
allowed_gene_names = []

if args.ensembl:
    print "Reading From Ensembl"
    ensembl_genes = read_data(args.ensembl[0],sep="\t")
    if len(args.ensembl) > 1:
        ensembl_seq = read_data(args.ensembl[1],sep="\t")
    allowed_gene_names = ensembl_genes["Associated Gene Name"].unique()

if args.drugbank:
    print "Reading From DrugBank"
    drug_id_table = pd.DataFrame([],columns=["Drug Bank Id","Name"])
    drug_group_table = pd.DataFrame([],columns=["Name","Group"])
    drug_gene_table = pd.DataFrame([],columns=["Name","Gene Name","Gene Action"]) 
    drug_indication_table = pd.DataFrame([],columns=["Name","Indication"])
    gene_table = pd.DataFrame([],columns=["Gene Name","Gene Group"])
    for drug,gene in read_drug_bank(ET.parse(args.drugbank[0]).getroot(),allowed_gene_names,drug_group_order_map):
        for gene_name in gene:
            if gene_name not in gene_table["Gene Name"].unique():
                gene_table = gene_table.append(pd.DataFrame([[gene_name,gene[gene_name]]],columns=gene_table.columns),ignore_index=True)
            elif drug_group_order_map[gene_table[gene_table["Gene Name"] == gene_name]["Gene Group"].values[0]] > drug_group_order_map[gene[gene_name]]:
                gene_table.loc[gene_table[gene_table["Gene Name"] == gene_name].index[0],"Gene Group"] = gene[gene_name]
            else:
                pass
        for drug_id in drug["DB_ID"]:
           drug_id_table = drug_id_table.append(pd.DataFrame([[drug_id,drug["name"]]],columns=list(drug_id_table.columns)),ignore_index=True)
        for group in drug["groups"]:
            drug_group_table = drug_group_table.append(pd.DataFrame([[drug["name"],group]],columns=list(drug_group_table.columns)),ignore_index=True)
        for gene in drug["gene"]:
            for gene_action in gene[0]:
                drug_gene_table = drug_gene_table.append(pd.DataFrame([[drug["name"],gene[1],gene_action]],columns=list(drug_gene_table.columns)),ignore_index=True)
        if drug["indication"] != "":
            drug_indication_table = drug_indication_table.append(pd.DataFrame([[drug["name"],drug["indication"]]],columns=list(drug_indication_table.columns)),ignore_index=True)

if args.string:
    print "Reading From String"
    string_interactions = read_data(args.string[0],sep="\t")
    ensembl_gene_map = ensembl_genes[["Ensembl Protein ID","Associated Gene Name"]].drop_duplicates().set_index("Ensembl Protein ID").to_dict()["Associated Gene Name"]
    string_interactions_list = [[ensembl_gene_map[interaction[0][5:]],ensembl_gene_map[interaction[1][5:]]] for interaction in string_interactions[["item_id_a","item_id_b"]].values.tolist() if interaction[0][5:] in ensembl_gene_map and interaction[1][5:] in ensembl_gene_map]

if args.inweb:
    print "Reading From Inweb"
    interactions = read_data(args.inweb[0],sep="\t",header=None)
    gene_ids = read_data(args.inweb[1],sep="\t",header=None)
    gene_ids = pd.merge(gene_ids,pd.DataFrame(allowed_gene_names,columns=["Gene"]),left_index=True,left_on=1,right_on="Gene").set_index(0).to_dict()[1]
    inweb_interaction_list = [[gene_ids[int(interaction[0][:-2])],gene_ids[int(interaction[1][:-2])]] for interaction in interactions.values.tolist() if int(interaction[0][:-2]) in gene_ids and int(interaction[1][:-2]) in gene_ids]

if args.wordcloud:
    print "Reading From WordCloud"
    categories = {}
    with codecs.open(args.wordcloud[0],"r",encoding="utf8") as f:
        categories = {line.strip():{} for line in f}
    for (index,value) in tqdm.tqdm(drug_indication_table.iterrows()):
        indication = value["Indication"]
        name = value["Name"]
        re.sub(r'[\(\)\[\]]+','', indication)
        sentence_tokens = sentence_parser(indication)
        grammar = "NP: {<JJ>*<CD>*(<NN>|<NNS>|<NNP>|<VBZ>|<JJ>)+}<,>*"
        cp = nltk.RegexpParser(grammar)
        tree = cp.parse(sentence_tokens)
        for subtree in tree.subtrees():
            if subtree.label() == "NP":
                keywords = ' '.join(map(lambda leaf: leaf[0], subtree))
                for cat_keys in set(categories.keys()):
                    if cat_keys.lower() in keywords.lower():
                        categories[cat_keys].update({name:keywords})

if args.phenotype:
    print "Reading From Phenotype"
    total_phenotype_dict = {}
    for phenotype_file in args.phenotype:
        pheno_file = read_data(phenotype_file,",")
        file_name = os.path.splitext(os.path.basename(phenotype_file))[0].split("_")
        gene_score_source = file_name[0]
        phenotype = re.sub("[\d]+$","",file_name[1])
        if gene_score_source not in total_phenotype_dict:
            total_phenotype_dict[gene_score_source] = {}
        if phenotype not in total_phenotype_dict[gene_score_source]:
            total_phenotype_dict[gene_score_source][phenotype] = pheno_file[[col for col in pheno_file if col in ["Gene","Pvalue","log_score"]]]

if args.output:
    print "Outputing Files"
    #write group json
    with codecs.open(args.output[0]+"/reporpoise_group.json","w",encoding="utf8") as f:
        f.write("[\n")
        f.write(create_group_string(drug_group_table["Group"].unique()))
    #write gene json
    with codecs.open(args.output[0]+"/reporpoise_gene.json","w",encoding="utf8") as f:
        f.write("[\n")
        f.write(create_gene_string(ensembl_genes[["Ensembl Gene ID","Associated Gene Name"]].drop_duplicates(),gene_table.set_index("Gene Name")))
    #write drug table
    with codecs.open(args.output[0]+"/reporpoise_drug.json","w",encoding="utf8") as f:
        f.write("[\n")
        f.write(create_drug_string(drug_id_table,drug_group_table))
    #write drug target table
    with codecs.open(args.output[0]+"/reporpoise_drug_target.json","w",encoding="utf8") as f:
        f.write("[\n")
        f.write(create_drug_target_string(drug_gene_table))
    #write interacion table
    with codecs.open(args.output[0]+"/reporpoise_protein_interaction.json","w",encoding="utf8") as f:
        f.write("[\n")
        f.write(create_interaction_string(["String","Dapple"],string_interactions_list,inweb_interaction_list))
    #write word cloud
    with codecs.open(args.output[0]+"/reporpoise_word_cloud.json","w",encoding="utf8") as f:
        f.write("[\n")
        f.write(create_wordcloud_string(categories))
    #write phenotype values
    with codecs.open(args.output[0]+"/reporpoise_phenotype_source.json","w",encoding="utf8") as f:
        f.write("[\n")
        f.write(create_gene_score_source_string(total_phenotype_dict))
    with codecs.open(args.output[0]+"/reporpoise_phenotype.json","w",encoding="utf8") as f:
        f.write("[\n")
        f.write(create_phenotype_string(total_phenotype_dict))