from ftplib import FTP
import os 
from os.path import expanduser
import vcf
import collections
from .dictionaries import ftp_dic, pop_sex, pop_samples
from django.http import HttpResponse
from Bio import SeqIO
from .models import Document, Plot
from django.core.files import File
import subprocess

#PYTERA_PATH = str(os.getenv('PYTERA_PATH'))
PYTERA_PATH = '/usr/local/share/applications/pytera'


def getBasePath():
    return PYTERA_PATH+'/static/downloads'

def getBaseFileName(name):
    return PYTERA_PATH+'/static/downloads/chr'+str(name)+'.vcf.gz'

def getFilePath(filename):
    return PYTERA_PATH+'/static/downloads/documents/'+str(filename)


def save(filename, user_profile):
    basePath=getBasePath()
    file=open(basePath+"/"+filename,"r")
    django_file_1 = File(file)
    doc = Document(docfile = django_file_1, user_profile = user_profile)
    #doc = Document()
    #doc.docfile.save(filename, django_file_1, save=True)
    doc.save()
    django_file_1.close()
    file.close()


def save_excel(filename, user_profile):
    basePath=getBasePath()
    file=open(basePath+"/"+filename,"rb")#read binary 
    django_file_1 = File(file)
    doc = Document(docfile = django_file_1, user_profile = user_profile)
    doc.save()
    django_file_1.close()
    file.close()


def save_pdf(filename, user_profile):
    basePath=getBasePath()
    file=open(basePath+"/"+filename,"rb")
    django_file_1 = File(file)
    doc = Plot(pdf = django_file_1, user_profile = user_profile)
    doc.save()
    django_file_1.close()
    file.close()



def FTP_teste(chromossome):
    baseName=getBaseFileName(chromossome)
    
    ftp = FTP("ftp.1000genomes.ebi.ac.uk")
    ftp.login()
    ftp.cwd('/vol1/ftp/release/20130502')
    fhandle = open(baseName, 'wb')
    readme=ftp.retrbinary('RETR '+ftp_dic[str(chromossome)],fhandle.write)
    fhandle.close()
    ftp.quit()

    
    
def MySamples(pop_list):# pop_list is a list with the picked populations returned by pop_picker
    dic=pop_samples #its a dictionary with populations as key and a list of samples
    samples=[]
    for pop in pop_list:
        samples.extend(dic[pop])
    samples=sorted(samples)
    return samples # return only the list with the samples of the populations chosen



def ped_teste(chromossome, start, stop, list_samples):
    baseName=getBaseFileName(chromossome)

    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+" "+str(chromossome)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    dic_a={}
    snp=[]
    if list_samples[0]=="all":
        list_samples=vcf_reader.samples
    for sample in list_samples:
        dic_a[sample]=[]
    for record in vcf_reader:
        if record.is_snp:
            if record.POS>=start and record.POS<=stop:
                for sample in list_samples:
                    call=record.genotype(str(sample))
                    base=call.gt_bases
                    dic_a[sample].extend((str(base[0]),str(base[2])))
                ID=record.ID
                chrom=record.CHROM
                pos=record.POS
                zero=0
                snp.append((chrom,ID,zero,pos))
            elif record.POS>=stop:
                break
    dic_a = collections.OrderedDict(sorted(dic_a.items()))
    os.remove(PYTERA_PATH+"/static/downloads/subset.vcf")
    
    return dic_a, snp



def ped_file(chromossome, start, stop, list_samples, user_profile):
    basePath=getBasePath()
    
    dic_sex=pop_sex    
    ped, snp=ped_teste(chromossome, start, stop, list_samples)
    file=open(basePath+"/PED-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".ped","w")
    file_info=open(basePath+"/INFO-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".info", "w")
    file_snp=open(basePath+"/MAP-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".map","w")
    for i in ped.keys():
        samp,gt=ped.popitem(last=False)
        sex=dic_sex[i]
        if sex[2]=="male":
            file.write(str(samp)+"\t"+str(samp)+"\t0\t0\t1")
        elif sex[2]=="female":
            file.write(str(samp)+"\t"+str(samp)+"\t0\t0\t2")
        s="\t".join(gt)
        file.write("\t0\t"+str(s)+"\n")
    for tuplo in snp:        
        file_snp.write(str(tuplo[0])+"\t"+str(tuplo[1])+"\t"+str(tuplo[2])+"\t"+str(tuplo[3])+"\n")
        file_info.write(str(tuplo[1])+"\t"+str(tuplo[3])+"\n")
    file.close()
    file_info.close()
    file_snp.close()
    file1 = "PED-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".ped"
    file2 = "INFO-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".info"
    file3 = "MAP-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".map"
    save(file1, user_profile)
    save(file2, user_profile)
    save(file3, user_profile)
    os.remove(basePath+"/PED-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".ped")
    os.remove(basePath+"/INFO-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".info")
    os.remove(basePath+"/MAP-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".map")
    


def rdf_teste(chromossome, start, stop, list_samples):
    baseName=getBaseFileName(chromossome)

    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+" "+str(chromossome)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    if list_samples[0]=="all":
        list_samples=vcf_reader.samples
    dic_pop=pop_sex
    snp=[]
    headline_a=[]
    headline_b=[]
    dic_a={}
    dic_b={}
    snp_ID=[]
    for sample in list_samples:
        tuplo=dic_pop[sample]
        dic_a[sample]=[]
        dic_b[sample]=[]
        headline_a.append(">"+str(sample)+"a"+";1;"+str(tuplo[0])+";;;;;")
        headline_b.append(">"+str(sample)+"b"+";1;"+str(tuplo[0])+";;;;;")
    for record in vcf_reader:
        if record.POS>=start and record.POS<=stop and record.is_snp and record.var_subtype!="unknown":
            snp.append(record.is_snp)
            snp_ID.append(record.ID)
            for sample in list_samples:
                gt=record.genotype(str(sample))['GT']
                dic_a[sample].append(str(gt[0])+";")
                dic_b[sample].append(str(gt[2])+";")
        elif record.POS>=start and record.POS<=stop and record.is_snp and record.var_subtype=="unknown":
                snp.extend((record.is_snp,record.is_snp))
                snp_ID.extend((record.ID+"a",record.ID+"b"))
                for sample in list_samples:
                    gt=record.genotype(str(sample))['GT']
                    if str(gt[0])=="0" and str(gt[2])=="0":
                        dic_a[sample].extend(("0;","0;"))
                        dic_b[sample].extend(("0;","0;"))                     
                    elif str(gt[0])=="0" and str(gt[2])=="1":
                        dic_a[sample].extend(("0;","0;"))
                        dic_b[sample].extend(("1;","0;"))   
                    elif str(gt[0])=="1" and str(gt[2])=="0":
                        dic_a[sample].extend(("1;","0;"))
                        dic_b[sample].extend(("0;","0;"))   
                    elif str(gt[0])=="1" and str(gt[2])=="1":
                        dic_a[sample].extend(("1;","0;"))
                        dic_b[sample].extend(("1;","0;"))   
                    elif str(gt[0])=="2" and str(gt[2])=="0":
                        dic_a[sample].extend(("0;","1;"))
                        dic_b[sample].extend(("0;","0;"))   
                    elif str(gt[0])=="0" and str(gt[2])=="2":
                        dic_a[sample].extend(("0;","0;"))
                        dic_b[sample].extend(("0;","1;"))   
                    elif str(gt[0])=="2" and str(gt[2])=="2":
                        dic_a[sample].extend(("0;","1;"))
                        dic_b[sample].extend(("0;","1;"))   
                    elif str(gt[0])=="2" and str(gt[2])=="1":
                        dic_a[sample].extend(("0;","1;"))
                        dic_b[sample].extend(("1;","0;"))   
                    elif str(gt[0])=="1" and str(gt[2])=="2":
                        dic_a[sample].extend(("1;","0;"))
                        dic_b[sample].extend(("0;","1;"))    
        elif record.POS>=stop:
            break
    
    dic_a = collections.OrderedDict(sorted(dic_a.items()))
    dic_b = collections.OrderedDict(sorted(dic_b.items()))
    os.remove(PYTERA_PATH+"/static/downloads/subset.vcf")
              
    return dic_a, dic_b, snp, headline_a, headline_b, snp_ID



def rdf_file_multi_allelic(chromossome, start, stop, list_samples, user_profile):
    basePath=getBasePath()

    info=rdf_teste(chromossome, start, stop, list_samples)# rdf_multi_allelic
    file=open(basePath+"/RDF-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".rdf","w")
    file_snp=open(basePath+"/snp-ID-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".txt","w")
    
    file.write("  ;1.0\n")
    snp_ID=info[5]
    for i in range(1,len(info[2])+1):
        file.write(str(i)+";")
        file_snp.write(str(i)+" -> "+str(snp_ID[i-1])+"\n")
    file.write("\n")
    for i in range(len(info[2])):
        file.write("10;")
    file.write("\n")
    GT_a=info[0]
    GT_b=info[1]
    headline_a=info[3]
    headline_b=info[4]
    for i in range(len(info[3])):
        file.write(headline_a[i]+"\n")        
        tuplo=GT_a.popitem(last=False)
        for g in tuplo[1]:
            value=g
            file.write(str(value))
        file.write("\n"+headline_b[i]+"\n")
        tuplob=GT_b.popitem(last=False)
        for g in tuplob[1]:
            value=g
            file.write(str(value))
        file.write("\n")
    file.close()
    file_snp.close()
    file1 = "RDF-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".rdf"
    file2 = "snp-ID-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".txt"
    save(file1, user_profile)
    save(file2, user_profile)
    os.remove(basePath+"/RDF-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".rdf")
    os.remove(basePath+"/snp-ID-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".txt")



def nexus_teste(chromossome, start, stop, list_samples):
    baseName=getBaseFileName(chromossome)

    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+" "+str(chromossome)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)

    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    if list_samples[0]=="all":
        list_samples=vcf_reader.samples
    dic_a={}
    dic_b={}

    for sample in list_samples:
        dic_a[sample]=[]
        dic_b[sample]=[]
    for record in vcf_reader:
        if record.is_snp:
            if record.POS>=start and record.POS<=stop:
                for sample in list_samples:
                    call=record.genotype(str(sample))
                    base=call.gt_bases
                    dic_a[sample].append(str(base[0]))
                    dic_b[sample].append(str(base[2]))
            elif record.POS>=stop:
                break
    
    dic_a = collections.OrderedDict(sorted(dic_a.items()))
    dic_b = collections.OrderedDict(sorted(dic_b.items()))
    os.remove(PYTERA_PATH+"/static/downloads/subset.vcf")
    
    return dic_a, dic_b



def nexus_file(chromossome, start, stop, list_populations, list_samples, user_profile):
    basePath=getBasePath()

    nexus_a, nexus_b=nexus_teste(chromossome, start, stop, list_samples)
    if list_populations[0]=="all":
        dic=pop_samples
    else:
        dic={}
        for p in list_populations:
            dic[p]=pop_samples[p]#dictionary with populations as key and a list of samples
    nex_keys=nexus_a.keys()
    file=open(basePath+"/NEXUS-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".nex","w")
    tax=len(nexus_a)+len(nexus_b)
    for i in nex_keys:
        key=i
        break
    char=len(nexus_a[key])
    string="#nexus\nbegin data;\ndimensions ntax=%d nchar=%d;" % (tax, char)
    string2="\nformat datatype=dna gap=- missing=?;\nmatrix\n"
    s="".join([string, string2])
    file.write(s)
    lines=[]
    new_dic={}
    for popul in dic:
        lines.append(popul)
        new_dic[popul]=0
        for j in nex_keys:
            if j in dic[popul]:
                new_dic[popul]+=2
                seq_a="".join(nexus_a[j])## j is sample, nexus_a[j] gives the list with bases
                seq2_a="\t".join([j+"a", seq_a])### sample-> tab-> sequence
                seq_b="".join(nexus_b[j])
                seq2_b="\t".join([j+"b", seq_b])
                file.write(seq2_a+"\n"+seq2_b+"\n")
    file.write(";\nend;\n\nbegin sets;\n")
    before=1
    after=0
    for pop in lines:
        after=before-1+new_dic[pop]
        file.write("TaxSet "+str(pop)+" = "+str(before)+"-"+str(after)+";\n")
        before=after+1
    file.write("end;")
    file.close()
    file1 = "NEXUS-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".nex"
    save(file1, user_profile)
    os.remove(basePath+"/NEXUS-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".nex")




def parse_fasta(chromossome, start, stop):
    basePath=getBasePath()
    for record in SeqIO.parse(basePath+"/chr"+str(chromossome)+".fasta", "fasta"):
        my_seq=record.seq
        region=my_seq[start:stop]
    return region, start, stop



def fasta_teste(chromossome, start, stop, list_samples):
    baseName=getBaseFileName(chromossome)
    
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+" "+str(chromossome)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    if list_samples[0]=="all":
        list_samples=vcf_reader.samples
    dic_a={}
    dic_b={}
    for sample in list_samples:
        dic_a[sample]=[]
        dic_b[sample]=[]
    for record in vcf_reader:
        if record.is_snp:
            if record.POS>=start and record.POS<=stop:
                for sample in list_samples:
                    call=record.genotype(str(sample))
                    base=call.gt_bases
                    dic_a[sample].append((str(base[0]), int(record.POS)))
                    dic_b[sample].append((str(base[2]), int(record.POS)))
            elif record.POS>=stop:
                break
    
    dic_a = collections.OrderedDict(sorted(dic_a.items()))
    dic_b = collections.OrderedDict(sorted(dic_b.items()))

    return dic_a, dic_b



def fasta_file(chromossome, start, stop, list_samples, user_profile):
    basePath=getBasePath()
    
    file=open(basePath+"/FASTA-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".fasta","w")
    region, pos1, pos2 = parse_fasta(chromossome, start, stop)
    dic_a, dic_b = fasta_teste(chromossome, start, stop, list_samples)
    for sample in dic_a.keys():
        reg_a=region
        reg_b=region
        for i in range(len(dic_a[sample])):
            base_a, pos_a = dic_a[sample][i]
            base_b, pos_b = dic_b[sample][i]
            pos_resa=pos_a-pos1
            pos_resb=pos_b-pos1
            reg_a=reg_a[0:pos_resa]+str(base_a)+reg_a[pos_resa+1:pos2]
            reg_b=reg_b[0:pos_resb]+str(base_b)+reg_a[pos_resb+1:pos2]
            
        file.write(">"+str(sample)+"a"+"\n")
        file.write(str(reg_a)+"\n")
        file.write(">"+str(sample)+"b"+"\n")
        file.write(str(reg_b)+"\n")
    file.close()
    file1 = "FASTA-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".fasta"
    save(file1, user_profile)
    os.remove(basePath+"/FASTA-"+str(chromossome)+"-"+str(start)+"-"+str(stop)+".fasta")
    os.remove(PYTERA_PATH+"/static/downloads/subset.vcf")
    
    









                






