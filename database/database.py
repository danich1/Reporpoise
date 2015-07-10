import xml.etree.cElementTree as ET
import sys 
import getopt
import time
import codecs
import tqdm
#dependencies (Need drugbank.xml, InWeb3_HC_NonRed.txt, IWtoHugo, need string human data files)
#I discovered the beauty of json :D
def fill_data_master_list(file_name):
    gene_protein_map = {}
    with open(file_name, "r") as f:
        header = f.readline().strip().split(",")
        header_map = {header_field:index for header_field,index in zip(header,range(len(header)))}
        gene_entries = [line.strip().split(",") for line in f]
        #filter out the non coding transcripts
        gene_entries = filter(lambda x: x[2] != "", gene_entries)
        #create a gene protein id mapping
        for gene_entry in gene_entries:
            if gene_entry[header_map["Associated Gene Name"]] not in gene_protein_map:
                gene_protein_map.update({gene_entry[header_map["Ensembl Protein ID"]]:""})
            gene_protein_map[gene_entry[header_map["Ensembl Protein ID"]]] = gene_entry[header_map["Associated Gene Name"]]
        #create a dictionary with the remaining data in order to use it later in drug bank section
        gene_entries = {gene_entry[header_map["Associated Gene Name"]]:[gene_entry[header_map["Ensembl Gene ID"]],gene_entry[header_map["Gene Start (bp)"]],gene_entry[header_map["Gene End (bp)"]]] for gene_entry in gene_entries}
    return (gene_entries,gene_protein_map)
#@profile
def fill_data_inweb(interaction_file_name, gene_name_file_name):
    gene_id_map = {}
    with open(interaction_file_name, "r") as f:
        with open(gene_name_file_name, "r") as g:
            for lines in g:
                lines = lines.strip()
                line = lines.split("\t")
                gene_id_map.update({line[0]:line[1]})
        lines = [line.strip().split("\t") for line in f]
        interactions = map(lambda x: [gene_id_map[x[0][:-2]],gene_id_map[x[1][:-2]]], lines)
    return (interactions,gene_id_map)

#@profile
def fill_data_string(file_name, interaction_set,gene_protein_map,iteration,allowed_gene_names):
    alias_source = ""
    alias_target = ""
    already_seen_interaction = set({})
    with open(file_name, "r") as f:
        #write the json information unless it was already found above
        throw_away = f.readline()
        #i don't like string and their redundant interaction list
        for interaction in [line.split("\t") for line in f]:
            if interaction[0][5:] in gene_protein_map:
                alias_source = gene_protein_map[interaction[0][5:]]
            if interaction[1][5:] in gene_protein_map:
                alias_target = gene_protein_map[interaction[1][5:]]
            if  alias_source in allowed_gene_names and alias_target in allowed_gene_names:
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
    return interaction_set
#@profile
def fill_data_DGIdb(file_name):
    with open(file_name,"r") as f:
       throw_away = f.readline()
       genes = [line.split("\t") for line in f]
       genes = filter(lambda x: x[3].strip() == "DRUGGABLE GENOME", genes)
    return set([gene[0] for gene in genes])

#@profile
def fill_data_drug_bank(tree_root, drug_dict,allowed_gene_names):
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
            elif "{http://www.drugbank.ca}name" in child.tag:
                drug_dict["name"] = child.text
            elif "{http://www.drugbank.ca}targets" in child.tag:
                for sub_child in child:
                    if len(sub_child) > 0:
                        skip = False
                        if "{http://www.drugbank.ca}target" in sub_child.tag:
                            for sub_sub_child in sub_child: #in side target
                                if "{http://www.drugbank.ca}name" in sub_sub_child.tag:
                                    name = sub_sub_child.text
                                elif "{http://www.drugbank.ca}actions" in sub_sub_child.tag:
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
        drug_dict = {"DB_ID":[],"groups":[],"gene":[]}
        gene_dict = {}
        gene_group_map = {}
#@profile
def main(argv=sys.argv):
    system_options = dict(getopt.getopt(argv[1:], '',['drugbank=', 'inweb=', 'string=', 'dgidb=','output=','masterlist='])[0])
    output_str = ""
    total_time = 0
    drugable_genes = set({})
    gene_tracker = set({})
    interaction_set = {}
    if "--dgidb" in system_options:
        print "Opening the DGIdb file and parsing it....."
        start = time.time()
        drugable_genes = fill_data_DGIdb(system_options["--dgidb"])
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.group\",\n\"pk\":\"Drugable\"\n},\n"
        end = time.time()
        print "Done Time: %.5f" % (end-start)
        total_time += (end-start)
    if "--masterlist" in system_options:
        print "Opening the Master Gene file and parsing it....."
        start = time.time()
        gene_entries,gene_protein_map = fill_data_master_list(system_options["--masterlist"])
        allowed_gene_names = set(gene_protein_map.values())
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
        for drug_dict,gene_group_map in fill_data_drug_bank(tree.getroot(),{"DB_ID":[],"groups":[],"gene":[]},allowed_gene_names):
            #write out group json
            for drug_group in drug_dict["groups"]:
                if drug_group not in group_tracker:
                    output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.group\",\"pk\":\"%s\"\n},\n" % (drug_group)
                    group_tracker.add(drug_group)
            for gene in gene_group_map:
                output_str+="{\n\"fields\":{\n\"category\":[\""+gene_group_map[gene]+"\"],\n\"gene_id\":\"%s\"\n},\n\"model\":\"drug_search.gene\",\n\"pk\":\"%s\"\n},\n" % (gene_entries[gene][0],gene)
                gene_tracker.add(gene)
            #write out drug json
            output_str+="{\n\"fields\":{\n\"group\":["+",\n".join(["\""+group+"\"" for group in drug_dict["groups"]])+"]\n},\n\"model\":\"drug_search.drug\",\n\"pk\":\"%s\"\n},\n" % (drug_dict["name"])
            #write out drug_id json
            for drugid in drug_dict["DB_ID"]:
                output_str+="{\n\"fields\":{\n\"name\":\"%s\"\n},\n\"model\":\"drug_search.drugid\",\n\"pk\":\"%s\"\n},\n" % (drug_dict["name"],drugid)
            #write out targets json
            for actions, gene in drug_dict["gene"]:
                for action in actions:
                    output_str+="{\n\"fields\":{\n\"action\":\"%s\",\n\"gene\":\"%s\",\n\"drug\":\"%s\"\n},\n\"model\":\"drug_search.targets\",\n\"pk\":%d\n},\n" % (action, gene, drug_dict["name"],primary_target_id)
                    primary_target_id = primary_target_id + 1
        #for the rest of the genes that are not in drugbank 
        for gene in filter(lambda x: x not in gene_tracker,gene_entries.keys()):
            if gene in drugable_genes:
                output_str+="{\n\"fields\":{\n\"category\":[\"Drugable\"],\n\"gene_id\":\"%s\"\n},\n\"model\":\"drug_search.gene\",\n\"pk\":\"%s\"\n},\n" % (gene_entries[gene][0],gene)
            else:
                output_str+="{\n\"fields\":{\n\"category\":[],\n\"gene_id\":\"%s\"\n},\n\"model\":\"drug_search.gene\",\n\"pk\":\"%s\"\n},\n" % (gene_entries[gene][0],gene)
        end = time.time()
        print "Done Time: %.5fs" % (end-start)
        total_time += (end-start)
    if "--inweb" in system_options:
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.source\",\n\"pk\":\"Dapple\"\n},\n"
        iteration = 1
        gene_id_map = {}
        files = system_options["--inweb"].split(",")
        print "Opening the Dapple Files and parsing them....."
        start = time.time()
        interactions,gene_id_map = fill_data_inweb(files[0], files[1])
        for interaction in interactions:
            #only include interaction if both genes are in drug_bank
            if interaction[0] in allowed_gene_names and interaction[1] in allowed_gene_names:
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
        if len(interaction_set) == 0:
            iteration = 1
        output_str+="{\n\"fields\":{},\n\"model\":\"drug_search.source\",\n\"pk\":\"String\"\n},\n"
        print "Opening the String database files and parsing them...."
        start = time.time()
        interaction_set = fill_data_string(system_options["--string"], interaction_set, gene_protein_map, iteration,allowed_gene_names)
        end = time.time()
        print "Done Time: %.5f" % (end-start)
        total_time+= (end-start)
    #since interactions can have multiple sources I have to put this block here
    #this takes about 3 hours holy mother of magical words I need to cut some interactions out 
    if "--string" in system_options or "--inweb" in system_options:
        print "Parsing the Gene interaction list....."
        start = time.time()
        for interaction_key,interaction_values in tqdm.tqdm(interaction_set.iteritems()):
            gene_source, gene_target = interaction_key.split("_")
            output_str+="{\n\"fields\":\n{\n\"source\":[" + ",".join(["\""+ source_str + "\"" for source_str in interaction_values["source"]]) + "],\n\"gene_source\":\"%s\",\n\"gene_target\":\"%s\"\n},\n\"model\":\"drug_search.interactions\",\n\"pk\":%d\n},\n" % (gene_source, gene_target,interaction_values["pk"])
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