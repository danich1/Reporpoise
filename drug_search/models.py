from django.db import models

#This model is suppose to show if a gene is drugable or not. I left it open in case Ben wants more details
class GeneCategory(models.Model):
    category = models.CharField(max_length=100, primary_key=True, default='unknown')

    def __str__(self):
        return self.category

# This is the gene model that represents a given Gene
class Gene(models.Model):
    gene_name = models.CharField(max_length=100,primary_key=True, default='unknown')
    gene_id = models.CharField(max_length=100, default='unknown')
    interact = models.ManyToManyField('self', through='Interactions',symmetrical=False)
    category = models.ManyToManyField(GeneCategory)

    def __str__(self):
        return self.gene_name

#This is the source table which holds the values Dapple or String database. It keeps reference where the interactions came from
class Source(models.Model):
    source = models.CharField(max_length=100, primary_key=True, default='unknown')

    def __str__(self):
        return self.source

#This is a test table
class Interactions(models.Model):
    gene_source = models.ForeignKey(Gene)
    gene_target = models.ForeignKey(Gene,related_name='gene_targets')
    source = models.ManyToManyField(Source)

#This is the Drug Group Model that represents which drug group a given Drug belongs
class Group(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name

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

#This is the Phenotype model that represents a phenotype that a drug is associated with
class Phenotype(models.Model):
    gene = models.ManyToManyField(Gene,through='PhenotypeMap')
    name = models.CharField(max_length=400, primary_key=True)
    def __str__(self):
        return "Type:%s" % (str(name))

#This is the Phenotype Map model where it maps a gene to a phenotype and provides a given Z-score 
class PhenotypeMap(models.Model):
    gene = models.ForeignKey(Gene)
    phenotype = models.ForeignKey(Phenotype)
    z_score = models.FloatField()
    def __str__(self):
        return "Gene:%s, Phenotype:%s, Z-score:%.2f" % (str(self.gene), str(self.phenotype), z_score)