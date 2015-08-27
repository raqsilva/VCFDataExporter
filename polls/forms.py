from django import forms
from .models import Document
from django.forms import ModelForm



class information(forms.Form):
    OPTIONS =(
        ("1","1"),("2","2"),("3","3"),("4","4"),("5","5"),("6","6"),("7","7"),
        ("8","8"),("9","9"),("10","10"),("11","11"),("12","12"),("13","13"),("14","14"),("15","15"),
        ("16","16"),("17","17"),("18","18"),("19","19"),("20","20"),("21","21"),("22","22"),("X","X"),
        ("Y","Y"),
        )
    chromosome = forms.ChoiceField(choices=OPTIONS, required = True) 



class fetch_info(forms.Form):
    CHOICES = (
        ('European Ancestry (EUR)',(('GBR','GBR'),('FIN','FIN'),('IBS','IBS'),('TSI','TSI'),
        ('CEU','CEU'))),
        
        ('Americas Ancestry (AMR)',(('CLM','CLM'),('MXL','MXL'),('PEL','PEL'),('PUR','PUR'))),
        
        ('South Asian Ancestry (SAS)', (('BEB','BEB'),('GIH','GIH'),('ITU','ITU'),('PJL','PJL'),
        ('STU','STU'))),
        
        ('East Asian Ancestry (EAS)',(('CDX','CDX'),('CHB','CHB'),('JPT','JPT'),('KHV','KHV'),
        ('CHS','CHS'))),
        
        ('African Ancestry (AFR)',(('ASW','ASW'),('ACB','ACB'),('ESN','ESN'),('GWD','GWD'),('LWK','LWK'),
        ('MSL','MSL'),('YRI','YRI'))),
        
        )
    populations = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple(), required = False)
    


class region_form(forms.Form):
    start = forms.CharField(label='Start', max_length=20, required = True)
    stop = forms.CharField(label='Stop', max_length=20, required = True)



class file_format_form(forms.Form):
    OPTIONS =(
        ("",""),("rdf","RDF"),("ped","PED/MAP/INFO"),("nexus", "NEXUS"),("fasta", "FASTA"),
        )
    file_format = forms.ChoiceField(choices=OPTIONS, required = False)

 

class ProfileForm(forms.ModelForm):   
    class Meta:
        model = Document
        fields = ['docfile']
        #exclude = ['activation_key', 'key_expires', 'user']
        
    

class format_form_uploaded(forms.Form):
    OPTIONS =(
        ("",""),("stats","Stats"),("xlsx","Excel(.xlsx)"),("fasta_up", "FASTA"),
        )
    format_output = forms.ChoiceField(choices=OPTIONS, required = False)
    


class file_uploaded_form(forms.Form):
    file_uploaded = forms.CharField(label='File Name', max_length=30, required = False)



class sample_form(forms.Form):
    samples = forms.CharField(label='Samples', max_length=200, required = False)  


class evs_pop(forms.Form):
    OPTIONS =(
        ("all","Both"), ("EA","European American"), ("AA","African American"), 
        )
    pop = forms.ChoiceField(choices=OPTIONS, required = False) 


class evs_format(forms.Form):
    OPTIONS =(
        ("",""), ("xlsx","Excel(.xlsx)"), ("vcf", "VCF"),
        )
    esp_format = forms.ChoiceField(label='Format', choices=OPTIONS, required = False)


class maf_form(forms.Form):# Minor Allele Frequency in percent
    OPTIONS =(
        ("",""), (">",">"), ("<","<"), 
        )
    ea_char = forms.ChoiceField(label='European American Sign', choices=OPTIONS, required = False)
    EA = forms.FloatField(label='European American', max_value=100, min_value=0, required = False, help_text = 'Ex: 0.023, leave blank if you dont want to filter this parameter')
    OPTIONS =(
        ("",""), (">",">"), ("<","<"), 
        )
    aa_char = forms.ChoiceField(label='African American Sign', choices=OPTIONS, required = False)
    AA = forms.FloatField(label='African American', max_value=100, min_value=0, required = False, help_text = 'Ex: 0.2, leave blank if you dont want to filter this parameter')
    OPTIONS =(
        ("",""), (">",">"), ("<","<"), 
        )
    all_char = forms.ChoiceField(label='All Sign', choices=OPTIONS, required = False)
    All = forms.FloatField(label='All', max_value=100, min_value=0, required = False, help_text = 'Ex: 0.35, leave blank if you dont want to filter this parameter')  
    


class excel_columns(forms.Form):
    CHOICES = (
        ('EA_AC','EA Allele Count'),('AA_AC','AA Allele Count'),('TAC','Total Allele Count'),('MAF','Minor Allele Frequency'),
        ('GRCh38_POSITION','GRCh38 Position'), ('EA_GTC','EA Genotype Count'), ('AA_GTC','AA Genotype Count'),
        ('GTC','Total Genotype Count'), ('DP','Average Sample Read Depth'), ('FG','Function GVS'),
        ('CDS_SIZES','Coding DNA Sizes'), ('GL','Genes'), 
        )
    columns = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple(), required = False)











