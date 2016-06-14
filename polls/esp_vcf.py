import vcf
from django.http import HttpResponse
from django.core.files import File
import xlsxwriter
import os
from .vcf_functions import getBasePath, save_binary, getFilePath, parse_fasta, getEspPath
import subprocess
import collections
from .dictionaries import esp_col_dic
from pytera.settings import BASE_DIR


#PYTERA_PATH = str(os.getenv('PYTERA_PATH'))
PYTERA_PATH = BASE_DIR

# MAF Minor Allele Frequency in percent in the order of EA,AA,All
def filter_vcf(chromo, start, stop, user_profile, ea, aa, total, ea_sign, aa_sign, total_sign):
    basePath = getBasePath()
    espPath = getEspPath(chromo)
    
    subprocess.call(PYTERA_PATH + "/static/tabix/tabix -f -p vcf -h " + espPath + " " + str(chromo) + ":" + str(start) + "-" + str(stop) + " > " + PYTERA_PATH + "/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename = basePath + "/subset.vcf")
    vcf_writer = vcf.Writer(open(basePath+"/ESP.chr"+str(chromo)+".subset.vcf", 'w'), vcf_reader)
    
    if ea_sign=='<':
        if aa_sign=='<':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea and float(record.INFO['MAF'][1]) < aa and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea and float(record.INFO['MAF'][1]) < aa and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea and float(record.INFO['MAF'][1]) < aa:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
        elif aa_sign=='>':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea and float(record.INFO['MAF'][1]) > aa and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea and float(record.INFO['MAF'][1]) > aa and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea and float(record.INFO['MAF'][1]) > aa:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
        elif aa_sign=='':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) < ea :
                        vcf_writer.write_record(record)
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
##################################
    elif ea_sign=='>':
        if aa_sign=='<':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea and float(record.INFO['MAF'][1]) < aa and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea and float(record.INFO['MAF'][1]) < aa and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea and float(record.INFO['MAF'][1]) < aa:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
        elif aa_sign=='>':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea and float(record.INFO['MAF'][1]) > aa and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea and float(record.INFO['MAF'][1]) > aa and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea and float(record.INFO['MAF'][1]) > aa:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
        elif aa_sign=='':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][0]) > ea :
                        vcf_writer.write_record(record)
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
#########################################
    elif ea_sign=='':
        if aa_sign=='<':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][1]) < aa and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][1]) < aa and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][1]) < aa:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
        elif aa_sign=='>':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][1]) > aa and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][1]) > aa and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][1]) > aa:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
        elif aa_sign=='':
            if total_sign=='<':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][2]) < total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break                
            elif total_sign=='>':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo and float(record.INFO['MAF'][2]) > total:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break
            elif total_sign=='':
                for record in vcf_reader:
                    maf = record.INFO['MAF']
                    if record.POS>=start and record.POS<=stop and record.CHROM==chromo:
                        vcf_writer.write_record(record)  
                    elif record.POS>=stop and record.CHROM==chromo:
                        break   

    vcf_writer.close()
    subprocess.call(PYTERA_PATH+"/static/tabix/bgzip -c -f "+basePath+"/ESP.chr"+str(chromo)+".subset.vcf"+' > '+basePath+"/ESP.chr"+str(chromo)+".subset.vcf.gz", shell=True)
    
    file = "ESP.chr"+str(chromo)+".subset.vcf.gz"
    name = save_binary(file, user_profile)
    os.remove(basePath+"/ESP.chr"+str(chromo)+".subset.vcf.gz")
    os.remove(basePath+"/ESP.chr"+str(chromo)+".subset.vcf")
    os.remove(basePath+"/subset.vcf")

    path = basePath+'/'+name
    with open(path, "rb") as gzip:
        data = gzip.read()
    response = HttpResponse( data, content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=' + name.split('/')[1]
    return response
