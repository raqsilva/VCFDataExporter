import vcf
from django.http import HttpResponse
from django.core.files import File
import xlsxwriter
import os
from .vcf_functions import getBasePath, save, getFilePath, save_pdf, save_excel, parse_fasta
import subprocess
import collections

#PYTERA_PATH = str(os.getenv('PYTERA_PATH'))
PYTERA_PATH = '/usr/local/share/applications/pytera'


def evs_xlsx_file(chromo, start, stop, named_file, user_profile, pop, columns):
    baseName=getFilePath(named_file)
    basePath=getBasePath()
    
    ##### add all ESP files provided### change subprocess ### change path
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -c -f "+baseName+' > '+baseName+'.gz', shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf "+baseName+".gz", shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+".gz"+" "+str(chromo)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    
    column_dic = {
        'EA_AC':(6, 'European American Allele Count'), 'AA_AC':(7, 'African American Allele Count'), 'TAC':(8, 'Total Allele Count'), 'MAF':(9, 'Minor Allele Frequency'),
        'EA_GTC':(10, 'European American Genotype Counts'), 'AA_GTC':(11, 'African American Genotype Count'), 'GTC':(12, 'Total Genotype Count'),
        'DP':(13, 'Average Sample Read Depth'), 'FG':(14, 'Function GVS'), 'CDS_SIZES':(15, 'Coding DNA Sizes'), 'GL':(16, 'Genes'), 'GRCh38_POSITION':(17, 'GRCh38_POSITION')
                  }
    
    text = {}
    for key in columns:
        text[column_dic[key][0]] = [column_dic[key][1]]
        
    text[0] = ['CHROM'] 
    text[1] = ['POS'] 
    text[2] = ['ID'] 
    text[3] = ['Type'] #SNP/INDEL
    text[4] = ['REF']
    text[5] = ['ALT']
    if pop=='EA':
        text[6] = ['European American Allele Count'] #European American Allele Count
    elif pop=='AA':
        text[7] = ['African American Allele Count'] #African American Allele Count
    else:
        text[6] = ['European American Allele Count'] #European American Allele Count
        text[7] = ['African American Allele Count'] #African American Allele Count
    text[8] = ['Total Allele Count'] #Total Allele Count
    if pop=='EA':
        text[9] = ['European American Genotype Counts'] #European American Genotype Counts in the order of listed GTS
    elif pop=='AA':
        text[10] = ['African American Genotype Counts'] #African American Genotype Counts in the order of listed GTS
    else:
        text[9] = ['European American Genotype Counts'] #European American Genotype Counts in the order of listed GTS
        text[10] = ['African American Genotype Counts'] #African American Genotype Counts in the order of listed GTS
    text[11] = ['Total Genotype Counts'] #Total Genotype Counts in the order of listed GTS
    text[12] = ['Genes'] 
    text[13] = ['GRCh38_POSITION'] 
    text[14] = ['GVS Function']
    
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
            text[8].append('A='+str(record.INFO['TAC'][0])+' / R='+str(record.INFO['TAC'][1]))
            try:
                text[9].append(str(record.INFO['GTS'][0])+'='+str(record.INFO['EA_GTC'][0])+' / '+str(record.INFO['GTS'][1])+'='+str(record.INFO['EA_GTC'][1]))
            except KeyError:
                pass
            try:
                text[10].append(str(record.INFO['GTS'][0])+'='+str(record.INFO['AA_GTC'][0])+' / '+str(record.INFO['GTS'][1])+'='+str(record.INFO['AA_GTC'][1]))
            except KeyError:
                pass
            text[11].append(str(record.INFO['GTS'][0])+'='+str(record.INFO['GTC'][0])+' / '+str(record.INFO['GTS'][1])+'='+str(record.INFO['GTC'][1]))
            gene1 = record.INFO['GL'][0]
            try:
                gene2 = record.INFO['GL'][1]
                text[12].append(gene2)
            except IndexError:
                text[12].append(gene1)
            text[13].append(str(record.INFO['GRCh38_POSITION'][0]))
            FG = str(record.INFO['FG'][0])
            if FG.startswith('NM'):
                GVS = FG.split(':')
                text[14].append(GVS[1])
            else:
                text[14].append(FG)
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
    
    workbook = xlsxwriter.Workbook(basePath+'/excel_doc-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx')
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
    file = 'excel_doc-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx'
    save_excel(file, user_profile)
    os.remove(basePath+'/excel_doc-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx')
    os.remove(basePath+"/subset.vcf")
    os.remove(baseName+".gz")
    os.remove(baseName+".gz.tbi")
    
    path = basePath+'/documents/excel_doc-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx'
    with open(path, "rb") as excel:
        data = excel.read()
    response = HttpResponse( data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=' + 'excel_doc-'+str(start)+'-'+str(stop)+'.xlsx'
    return response



# MAF Minor Allele Frequency in percent in the order of EA,AA,All
def filter_vcf(chromo, start, stop, named_file, user_profile, ea, aa, total, ea_sign, aa_sign, total_sign):
    baseName=getFilePath(named_file)
    basePath=getBasePath()

    ##### add all ESP files provided### change subprocess ### change path
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -c -f "+baseName+' > '+baseName+'.gz', shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf "+baseName+".gz", shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+".gz"+" "+str(chromo)+":"+str(start)+"-"+str(stop)+" > "+basePath+"/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=basePath+"/subset.vcf")
    vcf_writer = vcf.Writer(open(basePath+"/"+ named_file.split('.')[0] +".subset.vcf", 'w'), vcf_reader)
    
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
    
    
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -c -f "+basePath+"/"+named_file.split('.')[0] +".subset.vcf"+' > '+basePath+"/"+named_file.split('.')[0] +".subset.vcf.gz", shell=True)
    
    file = named_file.split('.')[0] +".subset.vcf.gz"
    save_excel(file, user_profile)
    os.remove(basePath+"/"+named_file.split('.')[0] +".subset.vcf.gz")
    os.remove(basePath+"/"+named_file.split('.')[0] +".subset.vcf")
    os.remove(basePath+"/subset.vcf")
    os.remove(baseName+".gz")
    os.remove(baseName+".gz.tbi")
    
    path = basePath+"/documents/"+named_file.split('.')[0] +".subset.vcf.gz"
    with open(path, "rb") as gzip:
        data = gzip.read()
    response = HttpResponse( data, content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=' + named_file.split('.')[0] +".subset.vcf.gz"
    return response

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



