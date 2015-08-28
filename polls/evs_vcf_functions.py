import vcf
from django.http import HttpResponse
from django.core.files import File
import xlsxwriter
import os
from .vcf_functions import getBasePath, save_binary, getFilePath, parse_fasta, getEspPath
import subprocess
import collections
from .dictionaries import esp_col_dic


#PYTERA_PATH = str(os.getenv('PYTERA_PATH'))
PYTERA_PATH = '/usr/local/share/applications/pytera'


def evs_xlsx_file(chromo, start, stop, user_profile, columns):
    basePath=getBasePath()
    espPath = getEspPath(chromo)
    
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+espPath+" "+str(chromo)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    
    text = {}
    for key in columns:
        text[esp_col_dic[key][0]] = [esp_col_dic[key][1]]
        
    text[0] = ['CHROM'] 
    text[1] = ['POS'] 
    text[2] = ['ID'] 
    text[3] = ['Type'] #SNP/INDEL
    text[4] = ['REF']
    text[5] = ['ALT']
    
    for record in vcf_reader:
        if record.POS>=start and record.POS<=stop and record.CHROM==chromo:
            text[0].append(str(record.CHROM))
            text[1].append(str(record.POS))
            ID = str(record.ID)
            text[3].append(str(record.var_type))
            text[4].append(str(record.REF))
            text[5].append(str(record.ALT[0]))
            try:
                text[6].append('A='+str(record.INFO['EA_AC'][0])+' / R='+str(record.INFO['EA_AC'][1]))
            except KeyError:
                pass
            try:
                text[7].append('A='+str(record.INFO['AA_AC'][0])+' / R='+str(record.INFO['AA_AC'][1]))
            except KeyError:
                pass
            try:
                text[8].append('A='+str(record.INFO['TAC'][0])+' / R='+str(record.INFO['TAC'][1]))
            except KeyError:
                pass
            try:
                text[9].append(str('EA='+str(record.INFO['MAF'][0])+' / '+'AA='+str(record.INFO['MAF'][1]+' / '+'All='+str(record.INFO['MAF'][2]))))
            except KeyError:
                pass
            try:
                text[10].append(str(record.INFO['GTS'][0])+'='+str(record.INFO['EA_GTC'][0])+' / '+str(record.INFO['GTS'][1])+'='+str(record.INFO['EA_GTC'][1]))
            except KeyError:
                pass
            try:
                text[11].append(str(record.INFO['GTS'][0])+'='+str(record.INFO['AA_GTC'][0])+' / '+str(record.INFO['GTS'][1])+'='+str(record.INFO['AA_GTC'][1]))
            except KeyError:
                pass
            try:
                text[12].append(str(record.INFO['GTS'][0])+'='+str(record.INFO['GTC'][0])+' / '+str(record.INFO['GTS'][1])+'='+str(record.INFO['GTC'][1]))
            except KeyError:
                pass
            try:
                text[13].append(str(record.INFO['DP']))
            except KeyError:
                pass
            FG = str(record.INFO['FG'][0])
            if FG.startswith('NM'):
                GVS = FG.split(':')
                try:
                    text[14].append(GVS[1])
                except KeyError:
                    pass
            else:
                try:
                    text[14].append(FG)
                except KeyError:
                    pass
            try:
                text[15].append(str(record.INFO['CDS_SIZES'][0]))
            except KeyError:
                pass
            gene1 = record.INFO['GL'][0]
            try:
                gene2 = record.INFO['GL'][1]
                try:
                    text[16].append(str(gene1)+'/'+str(gene2))
                except KeyError:
                    pass
            except IndexError:
                try:
                    text[16].append(gene1)
                except KeyError:
                    pass
            try:
                text[17].append(str(record.INFO['GRCh38_POSITION'][0]))
            except KeyError:
                pass

            if ID!='None':
                if ID.startswith('rs'):
                    text[2].append(('http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs='+ID[2:], ID))
                else:
                    text[2].append(ID)
            else:
                text[2].append('None')
        elif record.POS>=stop and record.CHROM==chromo:
            break
    
    text = collections.OrderedDict(sorted(text.items()))
    
    workbook = xlsxwriter.Workbook(basePath+'/excel_esp-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx')
    link_format = workbook.add_format({'color': 'blue', 'underline': 1})
    worksheet = workbook.add_worksheet()
    worksheet.set_column(5, 20, 18)
    worksheet.set_column(0, 0, 8)
    worksheet.set_column(3, 5, 8)
    worksheet.set_column(1, 2, 14)
    
    col = 0
    for key in text.keys():
        row = 0
        if key!=2:
            for par in text[key]:
                worksheet.write(row, col, str(par))
                row = row + 1
        else:
            for par in text[key]:
                if par[1][0:2]=='rs':
                    worksheet.write_url(row, col, str(par[0]), link_format, str(par[1]))
                    row = row + 1
                else:
                    worksheet.write(row, col, str(par))
                    row = row + 1
        col = col + 1
    workbook.close()
    file = 'excel_esp-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx'
    save_binary(file, user_profile)
    os.remove(basePath+'/excel_esp-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx')
    os.remove(basePath+"/subset.vcf")
    
    path = basePath+'/documents/excel_esp-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx'
    with open(path, "rb") as excel:
        data = excel.read()
    response = HttpResponse( data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=' + 'excel_esp-'+str(start)+'-'+str(stop)+'.xlsx'
    return response



# MAF Minor Allele Frequency in percent in the order of EA,AA,All
def filter_vcf(chromo, start, stop, user_profile, ea, aa, total, ea_sign, aa_sign, total_sign):
    basePath=getBasePath()
    espPath = getEspPath(chromo)
    
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+espPath+" "+str(chromo)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=basePath+"/subset.vcf")
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
                        breaks
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
                        breaks
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
                        breaks
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
    
    
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -c -f "+basePath+"/ESP.chr"+str(chromo)+".subset.vcf"+' > '+basePath+"/ESP.chr"+str(chromo)+".subset.vcf.gz", shell=True)
    
    file = "ESP.chr"+str(chromo)+".subset.vcf.gz"
    save_binary(file, user_profile)
    os.remove(basePath+"/ESP.chr"+str(chromo)+".subset.vcf.gz")
    os.remove(basePath+"/ESP.chr"+str(chromo)+".subset.vcf")
    os.remove(basePath+"/subset.vcf")

    path = basePath+"/documents/"+"ESP.chr"+str(chromo)+".subset.vcf.gz"
    with open(path, "rb") as gzip:
        data = gzip.read()
    response = HttpResponse( data, content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=' + "ESP.chr"+str(chromo)+".subset.vcf.gz"
    return response

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



