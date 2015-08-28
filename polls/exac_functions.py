import vcf
from django.http import HttpResponse
from django.core.files import File
import xlsxwriter
import os
from .vcf_functions import getBasePath, save_binary, getFilePath, save_pdf, parse_fasta
import subprocess
import collections
from .dictionaries import exac_col_dic


#PYTERA_PATH = str(os.getenv('PYTERA_PATH'))
PYTERA_PATH = '/usr/local/share/applications/pytera'
    

def exac_xlsx_file(chromo, start, stop, named_file, user_profile, columns):
    baseName=getFilePath(named_file)
    basePath=getBasePath()
    
    ##### add all ESP files provided### change subprocess ### change path
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -c -f "+baseName+' > '+baseName+'.gz', shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf "+baseName+".gz", shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+".gz"+" "+str(chromo)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    
    text = {}
    for key in columns:
        text[exac_col_dic[key][0]] = [exac_col_dic[key][1]]
        
    text[0] = ['CHROM'] 
    text[1] = ['POS'] 
    text[2] = ['ID'] 
    text[3] = ['Type'] #SNP/INDEL
    text[4] = ['REF']
    text[5] = ['ALT']
    text[6] = ['QUAL']
    
    for record in vcf_reader:
        if record.POS>=start and record.POS<=stop and record.CHROM==chromo:
            text[0].append(str(record.CHROM))
            text[1].append(str(record.POS))
            ID = str(record.ID)
            text[3].append(str(record.var_type))
            text[4].append(str(record.REF))
            text[5].append(str(record.ALT[0]))
            text[6].append(str(record.QUAL))
            if ID!='None':
                if ID.startswith('rs'):
                    text[2].append(('http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs='+ID[2:], ID))
                else:
                    text[2].append(ID)
            else:
                text[2].append('None')
            
            def append_data(dic_key, dic, nr):
                try:
                    key = list(record.INFO[dic_key])
                    if len(key)==2:
                        try:
                            dic[nr].append(str(key[0])+'/'+str(key[1]))
                        except KeyError:
                            pass
                    elif len(key)==3:
                        try:
                            dic[nr].append(str(key[0])+'/'+str(key[1])+'/'+str(key[2]))
                        except KeyError:
                            pass
                    elif len(key)==1:
                        try:
                            dic[nr].append(str(key[0]))
                        except KeyError:
                            pass
                    else:
                        try:
                            dic[nr].append(str(key))
                        except KeyError:
                            pass
                except KeyError:
                    pass
            
            def append_to_dic(dic_key, dic, nr):
                try:
                    dic[nr].append(record.INFO[dic_key])
                except KeyError:
                    pass

            append_data('AC', text, 7)
            append_data('AC_AFR', text, 8)
            append_data('AC_AMR', text, 9)
            append_data('AC_Adj', text, 10)
            append_data('AC_EAS', text, 11)
            append_data('AC_FIN', text, 12)
            append_data('AC_Het', text, 13)
            append_data('AC_Hom', text, 14)
            append_data('AC_NFE', text, 15)
            append_data('AC_OTH', text, 16)
            append_data('AC_SAS', text, 17)
            append_data('AF', text, 18)
            
            append_to_dic('AN', text, 19)
            append_to_dic('AN_AFR', text, 20)
            append_to_dic('AN_AMR', text, 21)
            append_to_dic('AN_Adj', text, 22)
            append_to_dic('AN_EAS', text, 23)
            append_to_dic('AN_FIN', text, 24)
            append_to_dic('AN_NFE', text, 25)
            append_to_dic('AN_OTH', text, 26)
            append_to_dic('AN_SAS', text, 27)
            append_to_dic('GQ_MEAN', text, 28)
            append_to_dic('GQ_STDDEV', text, 29)
            
            append_data('Hemi_AFR', text, 30)
            append_data('Hemi_AMR', text, 31)
            append_data('Hemi_EAS', text, 32)
            append_data('Hemi_FIN', text, 33)
            append_data('Hemi_NFE', text, 34)
            append_data('Hemi_OTH', text, 35)
            append_data('Hemi_SAS', text, 36)
            append_data('Het_AFR', text, 37)
            append_data('Het_AMR', text, 38)
            append_data('Het_EAS', text, 39)
            append_data('Het_FIN', text, 40)
            append_data('Het_NFE', text, 41)
            append_data('Het_OTH', text, 42)
            append_data('Het_SAS', text, 43)
            append_data('Hom_AFR', text, 44)
            append_data('Hom_AMR', text, 45)
            append_data('Hom_EAS', text, 46)
            append_data('Hom_FIN', text, 47)
            append_data('Hom_NFE', text, 48)
            append_data('Hom_OTH', text, 49)
            append_data('Hom_SAS', text, 50)
            
        elif record.POS>=stop and record.CHROM==chromo:
            break
    
    text = collections.OrderedDict(sorted(text.items()))
    
    workbook = xlsxwriter.Workbook(basePath+'/excel_exac-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx')
    link_format = workbook.add_format({'color': 'blue', 'underline': 1})
    worksheet = workbook.add_worksheet()
    worksheet.set_column(5, 40, 15)
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
    file = 'excel_exac-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx'
    save_binary(file, user_profile)
    os.remove(basePath+'/excel_exac-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx')
    os.remove(basePath+"/subset.vcf")
    os.remove(baseName+".gz")
    os.remove(baseName+".gz.tbi")
    
    path = basePath+'/documents/excel_exac-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx'
    with open(path, "rb") as excel:
        data = excel.read()
    response = HttpResponse( data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=' + 'excel_exac-'+str(start)+'-'+str(stop)+'.xlsx'
    return response





