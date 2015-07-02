import xml.etree.ElementTree as ET
import sys 
import getopt
import time
import pickle
import pdb
import codecs
import tqdm
#dependencies (Need drugbank.xml, InWeb3_HC_NonRed.txt, IWtoHugo)
#I discovered the beauty of json :D

def fill_data_inweb(file_name):
    with open(file_name, "r") as f:
        pass
def fill_data_string(file_name):
    with open(file_name, "r") as f:
        pass
def fill_data_DGIdb(file_name):
    with open(file_name, "r") as f:
        pass
def fill_data_drug_bank(tree_root, drug_dict,gene_dict,gene_set):
    gene_data = []
    for drug in tree_root:
        for child in drug:
            if "{http://www.drugbank.ca}drugbank-id" in child.tag:
                drug_dict["DB_ID"].append(child.text)
            elif "{http://www.drugbank.ca}groups" in child.tag:
                for group_child in child:
                    if "{http://www.drugbank.ca}group" in group_child.tag:
                        drug_dict["groups"].append(group_child.text)
            elif "{http://www.drugbank.ca}name" in child.tag:
                drug_dict["name"] = child.text
            elif "{http://www.drugbank.ca}targets" in child.tag:
                for sub_child in child:
                    if "{http://www.drugbank.ca}target" in sub_child.tag:
                        for sub_sub_child in sub_child: #in side target
                            if "{http://www.drugbank.ca}id" in sub_sub_child.tag:
                                gene_dict.update({sub_sub_child.text:[]})
                                gene_id = sub_sub_child.text
                            elif "{http://www.drugbank.ca}name" in sub_sub_child.tag:
                                #gene_dict[gene_id]["name"] = sub_sub_child.text
                                name = sub_sub_child.text
                            elif "{http://www.drugbank.ca}actions" in sub_sub_child.tag:
                                if len(list(sub_sub_child)) == 0:
                                    gene_data.append("unknown")
                                else:
                                    for sub_sub_sub_child in sub_sub_child: #inside action
                                        if "{http://www.drugbank.ca}action" in sub_sub_sub_child.tag:
                                            gene_data.append(sub_sub_sub_child.text)
                            elif "{http://www.drugbank.ca}polypeptide" in sub_sub_child.tag:
                                #gene_dict[gene_id]["Uniprot_ID"] = sub_sub_child.attrib["id"]
                                Uniprot_ID = sub_sub_child.attrib["id"]
                                for sub_sub_sub_child in sub_sub_child:
                                    if "{http://www.drugbank.ca}gene-name" in sub_sub_sub_child.tag:
                                        gene_set.add(sub_sub_sub_child.text)
                                        gene_dict[gene_id].append({"Gene_ID":gene_id,"name":name,"Uniprot_ID":Uniprot_ID,"Gene_name":sub_sub_sub_child.text})
                                        drug_dict["gene"].append((gene_data,sub_sub_sub_child.text))
                                #gene.append(dict(gene_dict))
                            else:
                                pass
                        gene_data = []
        yield (drug_dict,gene_dict)
        drug_dict = {"DB_ID":[],"groups":[],"gene":[]}
        gene_dict = {}

def main(argv=sys.argv):
    system_options = dict(getopt.getopt(argv[1:], '',['drugbank=', 'inweb=', 'string=', 'dgidb=','output=','genefile='])[0])
    output_str = ""
    total_time = 0
    drugable_genes = set({})
    gene_set = set({})
    interaction_set = {}
    if "--dgidb" in system_options:
        print "Opening the DGIdb files and parsing them....."
        start = time.time()
        with open(system_options["--dgidb"],"r") as f:
           throw_away = f.readline()
           genes = [line.split("\t") for line in f]
           genes = filter(lambda x: x[3].strip() == "DRUGGABLE GENOME", genes)
           drugable_genes = set([gene[0] for gene in genes])
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.genecategory\",\n\"pk\":\"Drugable\"\n},\n"
        end = time.time()
        print "Done Time: %.5f" % (end-start)
        total_time += (end-start)
    if "--drugbank" in system_options:
        #keep track of each drug group to prevent duplicates
        group_tracker = set({})
        primary_target_id = 1
        print "Opening the Drugbank database in element tree...."
        start = time.time()
        tree = ET.parse(system_options["--drugbank"])
        end = time.time()
        total_time += (end-start)
        print "Finished... Time: %.5fs" % (end-start)
        print "Now parsing the data"
        start = time.time()
        for drug_dict, gene_dict in fill_data_drug_bank(tree.getroot(),{"DB_ID":[],"groups":[],"gene":[]},{},gene_set):
            #write out group json
            for drug_group in drug_dict["groups"]:
                if drug_group not in group_tracker:
                    output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.group\",\"pk\":\"%s\"\n},\n" % (drug_group)
                    group_tracker.add(drug_group)

            #write out gene json
            #only add a gene to the table if a drug targets it otherwise don't worry about it
            for gene_key in gene_dict:
                for gene in gene_dict[gene_key]:
                    if "Uniprot_ID" in gene:
                        if gene["Gene_name"] in drugable_genes:
                            #this chopped up line writes out the json for the gene table
                            output_str+="{\n\"fields\":{\n\"category\":[\"Drugable\"],\n\"uniprot_id\":\"%s\",\n\"name\":\"%s\",\n\"gene_id\":\"%s\"\n},\n\"model\":\"drug_search.gene\",\n\"pk\":\"%s\"\n},\n" % (gene["Uniprot_ID"], gene["name"],
                                gene["Gene_ID"],gene["Gene_name"])
                        else:
                            #this chopped up line writes out the json for the gene table
                            output_str+="{\n\"fields\":{\n\"category\":[],\n\"uniprot_id\":\"%s\",\n\"name\":\"%s\",\n\"gene_id\":\"%s\"\n},\n\"model\":\"drug_search.gene\",\n\"pk\":\"%s\"\n},\n" % (gene["Uniprot_ID"], gene["name"],
                                gene["Gene_ID"],gene["Gene_name"])
            #only include a drug if it has a gene target
            if(len(drug_dict["gene"]) > 0):
                #write out drug json
                output_str+="{\n\"fields\":{\n\"group\":["
                for group in drug_dict["groups"]:
                    output_str+= "\""+ group + "\",\n"
                output_str = output_str[:-2]
                output_str+="]\n},\n\"model\":\"drug_search.drug\",\n\"pk\":\"%s\"\n},\n" % (drug_dict["name"])
                #write out drug_id json
                for drugid in drug_dict["DB_ID"]:
                    output_str+="{\n\"fields\":{\n\"name\":\"%s\"\n},\n\"model\":\"drug_search.drugid\",\n\"pk\":\"%s\"\n},\n" % (drug_dict["name"],drugid)
                #write out targets json
                for actions, gene in drug_dict["gene"]:
                    for action in actions:
                        output_str+="{\n\"fields\":{\n\"action\":\"%s\",\n\"gene\":\"%s\",\n\"drug\":\"%s\"\n},\n\"model\":\"drug_search.targets\",\n\"pk\":%d\n},\n" % (
                            action, gene, drug_dict["name"],primary_target_id)
                        primary_target_id = primary_target_id + 1
        end = time.time()
        with codecs.open("gene_list.txt", "w",encoding="utf8") as f:
            gene_set = filter(lambda x: x != None, list(gene_set))
            f.write("\n".join(gene_set))
        total_time += (end-start)
        print "Done Time: %.5fs" % (end-start)
    if "--inweb" in system_options:
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.source\",\n\"pk\":\"Dapple\"\n},\n"
        iteration = 1
        gene_id_map = {}
        files = system_options["--inweb"].split(",")
        print "Opening the Dapple Files and parsing them....."
        start = time.time()
        if "--genefile" in system_options:
            with open(system_options["--genefile"],"r") as f:
                gene_set = set([line.strip() for line in f])
        with open(files[0], "r") as f:
            with open(files[1], "r") as g:
                for lines in g:
                    lines = lines.strip()
                    line = lines.split("\t")
                    gene_id_map.update({line[0]:line[1]})
            lines = [line.strip().split("\t") for line in f]
            interactions = map(lambda x: [gene_id_map[x[0][:-2]],gene_id_map[x[1][:-2]]], lines)
        for interaction in interactions:
            #only include interaction if both genes are in drug_bank
            if interaction[0] in gene_set and interaction[1] in gene_set:
                interaction_string = interaction[0]+"_"+interaction[1]
                if interaction_string not in interaction_set:
                    interaction_set.update({interaction_string:{"source":[]}})
                interaction_set[interaction_string]["source"].append("Dapple")
                interaction_set[interaction_string]["pk"]= iteration
                iteration = iteration + 1
        end = time.time()
        print "Done Time: %.5f" % (end-start)
        total_time+= (end-start)
    if "--string" in system_options:
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.source\",\n\"pk\":\"String\"\n},\n"
        if len(interaction_set) == 0:
            iteration = 1
        alias_source = ""
        alias_target = ""
        gene_alias_map = {}
        already_seen_interaction = set({})
        files = system_options["--string"].split(",")
        print "Opening the String database files and parsing them...."
        start = time.time()
        if "--genefile" in system_options:
            with open(system_options["--genefile"],"r") as f:
                gene_set = set([line.strip() for line in f])
        with open(files[0], "r") as f:
            with open(files[1], "r") as g:
                throw_away=g.readline()
                for alias in  [line.split("\t") for line in g]:
                    if alias[1] in gene_set:
                        gene_alias_map[alias[0]] = alias[1]
            #write the json information unless it was already found above
            throw_away = f.readline()
            #i don't like string and their redundant interaction list
            for interaction in [line.split("\t") for line in f]:
                if interaction[0] in gene_alias_map:
                    alias_source = gene_alias_map[interaction[0]]
                if interaction[1] in gene_alias_map:
                    alias_target = gene_alias_map[interaction[1]]
                if  alias_source in gene_set and alias_target in gene_set:
                    interaction_string = alias_source+"_"+alias_target
                    reverse_interaction_string = alias_target+"_"+alias_source
                    #there are a lot of duplicates in the string database so filter out to make life easier
                    if interaction_string not in already_seen_interaction and reverse_interaction_string not in already_seen_interaction:
                        if reverse_interaction_string not in interaction_set:
                            if interaction_string not in interaction_set:
                                interaction_set.update({interaction_string:{"source":[]}})
                                interaction_set[interaction_string]["pk"] = iteration
                                iteration = iteration + 1
                            interaction_set[interaction_string]["source"].append("String")
                            already_seen_interaction.add(interaction_string)
                        else:
                            interaction_set[reverse_interaction_string]["source"].append("String")
                            already_seen_interaction.add(reverse_interaction_string)
        end = time.time()
        print "Done Time: %.5f" % (end-start)
        total_time+= (end-start)
    #since interactions can have multiple sources I have to put this block here
    #this takes about 3 hours holy mother of magical words I need to cut some interactions out 
    if "--string" in system_options or "--inweb" in system_options:
        print "Parsing the Gene interaction list....."
        start = time.time()
        for interaction_key in tqdm.tqdm(interaction_set):
            gene_source, gene_target = interaction_key.split("_")
            output_str+="{\n\"fields\":\n{\n\"source\":["
            for source_str in interaction_set[interaction_key]["source"]:
                output_str+="\""+source_str+"\","
            #cut out the last , characters
            output_str = output_str[:-1] + "],\n\"gene_source\":\"%s\",\n\"gene_target\":\"%s\"\n},\n\"model\":\"drug_search.interactions\",\n\"pk\":%d\n},\n" % (gene_source, gene_target,interaction_set[interaction_key]["pk"])
        end = time.time()
        print "Done Time: %.5f" % (end-start)
        total_time+=(end-start)
    if "--output" in system_options:
        file_obj = codecs.open(system_options["--output"], "w",encoding="utf8")
    else:
        file_obj = codecs.open("repurpose_data.json", "w",encoding="utf8")
    print "Writting Everything to file...."
    start = time.time()
    #begin the json option with a square open bracket
    file_obj.write("[\n")
    output_str = output_str[:-2]+"\n"
    file_obj.write(output_str)
    #end the json object with a closing square bracket
    file_obj.write("]")
    file_obj.close()
    end = time.time()
    total_time += (end-start)
    print "Done Time: %.5fs" % (end-start)
    print "Total Time Taken: %.5fs" % (total_time)
    return 0
if __name__ == "__main__":
    sys.exit(main())