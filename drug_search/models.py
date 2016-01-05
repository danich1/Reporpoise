from django.db import models

#This is the source table which holds the values Dapple or String database. It keeps reference where the interactions came from
class InteractionSource(models.Model):
    source = models.CharField(max_length=100, primary_key=True, default='unknown')

    def __str__(self):
        return self.source
#This is the source for gene scores
class GeneScoreSource(models.Model):
    source = models.CharField(max_length=100, primary_key=True, default='unknown')

    def __str__(self):
        return self.source

#This is the Drug Group Model that represents which drug group a given Drug belongs
class Group(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name

#class SNP(models.Model):
#    chrom = models.CharField(max_length=2)
#    rs_id = models.CharField(max_length=200,primary_key=True,default='unknown')
#    r_sq = models.ManyToManyField('self',through='R_Squared',symmetrical=False)
#    position = models.IntegerField()

#    def __str__(self):
#        return "%s" % (self.rs_id)

#class R_Squared(models.Model):
#    snp_A = model.ForeignKey(SNP)
#    snp_B = model.ForeignKey(SNP,related_name='snp_B')
#    val = models.FloatField()

#    def __str__(self):
#        return "%s,%s: %f" % (self.snp_A,self.snp_B,val)

# This is the gene model that represents a given Gene
class Gene(models.Model):
    gene_name = models.CharField(max_length=100,primary_key=True, default='unknown')
    gene_id = models.CharField(max_length=100, default='unknown')
    interact = models.ManyToManyField('self', through='Interactions',symmetrical=False)
    category = models.ManyToManyField(Group)
    #start = models.IntegerField()
    #end = models.IntegerField()
    #strand = models.BooleanField(default=True)
    #chrom = models.CharField(max_length=2)

    def __str__(self):
        return self.gene_name

#This is a test table
class Interactions(models.Model):
    gene_source = models.ForeignKey(Gene)
    gene_target = models.ForeignKey(Gene,related_name='gene_targets')
    source = models.ManyToManyField(InteractionSource)

#This is the Drug model that represents a given Drug
class Drug(models.Model):
    name = models.CharField(max_length=300,primary_key=True)
    target = models.ManyToManyField(Gene, through='Targets')
    group = models.ManyToManyField(Group)
    def __str__(self):
        return self.name

#This is the DrugID model that represents each Drug Bank ID for a given Drug
class DrugID(models.Model):
    name = models.ForeignKey(Drug)
    drug_id = models.CharField(max_length=100,primary_key=True)

    def __str__(self):
        return "Drug: %s, ID: %s" % (str(self.name), self.drug_id)

#This is the Target model that represents each gene a given drug targets and the drug's action (inhibit, inducer, etc.) 
class Targets(models.Model):
    gene = models.ForeignKey(Gene)
    drug = models.ForeignKey(Drug)
    action = models.CharField(max_length=300)
    def __str__(self):
        return "Drug: %s, Gene: %s, Action:%s" % (str(self.drug), str(self.gene), self.action)

#This is the Word model that represents each key indication phrase for a given drug
class Word(models.Model):
    label = models.CharField(max_length=200, primary_key=True)
    drug = models.ManyToManyField(Drug)
    count = models.IntegerField()
    def __str__(self):
        return "Label:%s, Count:%d" % (str(self.label), int(self.count))

#This is the Phenotype model that represents a phenotype that a gene is associated with
class Phenotype(models.Model):
    gene = models.ManyToManyField(Gene,through='PhenotypeMap')
    name = models.CharField(max_length=400, primary_key=True)
    def __str__(self):
        return "%s" % (str(self.name))

#This is the Phenotype Map model where it maps a gene to a phenotype and provides a given Z-score 
class PhenotypeMap(models.Model):
    gene = models.ForeignKey(Gene)
    phenotype = models.ForeignKey(Phenotype)
    p_val = models.FloatField()
    log_score = models.FloatField()
    source = models.ForeignKey(GeneScoreSource)
    def __str__(self):
        return "Gene:%s, Phenotype:%s, Log score:%.2f Source:%s" % (str(self.gene), str(self.phenotype), self.log_score,str(self.source))
