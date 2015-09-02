import vcf
from django.http import HttpResponse
from django.core.files import File
import xlsxwriter
import os
from .vcf_functions import getBasePath, save_binary, getFilePath, parse_fasta
import subprocess
import collections


#PYTERA_PATH = str(os.getenv('PYTERA_PATH'))
PYTERA_PATH = '/usr/local/share/applications/pytera'


def xlsx_file(chromo, start, stop, named_file, user_profile):
    baseName=getFilePath(named_file)

    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -c -f "+baseName+' > '+baseName+'.gz', shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf "+baseName+".gz", shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+".gz"+" "+str(chromo)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    
    basePath=getBasePath()

    text = {}
    text[0] = ['CHROM'] #CHROM
    text[1] = ['POS'] #POS
    text[2] = ['ID'] #ID
    text[3] = ['Type'] #SNP/INDEL
    for sample in vcf_reader.samples:
        text[sample] = [str(sample)]
        
    for record in vcf_reader:
        if record.POS>=start and record.POS<=stop and record.CHROM==chromo:
            text[0].append(str(record.CHROM))
            text[1].append(str(record.POS))
            ID = str(record.ID)
            text[3].append(str(record.var_type))
            if ID!='None':
                if ID.startswith('rs'):
                    text[2].append(('http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs='+ID[2:], ID))
                else:
                    text[2].append(ID)
            else:
                text[2].append('None')
            for sample in vcf_reader.samples:
                call=record.genotype(str(sample))
                text[sample].append(str(call.gt_bases))
        elif record.POS>=stop and record.CHROM==chromo:
            break
    workbook = xlsxwriter.Workbook(basePath+'/excel_doc-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx')
    link_format = workbook.add_format({'color': 'blue', 'underline': 1})
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, 20, 12)
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
    name = save_binary(file, user_profile)
    os.remove(basePath+'/excel_doc-'+str(chromo)+'-'+str(start)+'-'+str(stop)+'.xlsx')
    os.remove(PYTERA_PATH+"/static/downloads/subset.vcf")
    os.remove(baseName+".gz")
    os.remove(baseName+".gz.tbi")
    
    path = PYTERA_PATH+'/static/downloads/documents/' + name
    with open(path, "rb") as excel:
        data = excel.read()
    response = HttpResponse( data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=' + name.split('/')[1]
    return response
        
    
    
def plot_stats(chromo, start, stop, named_file, user_profile):
    baseName=getFilePath(named_file)
    basePath = getBasePath()
    
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -c -f "+baseName+' > '+baseName+'.gz', shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf "+baseName+".gz", shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+".gz"+" "+str(chromo)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    subprocess.call(PYTERA_PATH+"/static/bcftools-1.2/bcftools stats "+PYTERA_PATH+"/static/downloads/subset.vcf > "+PYTERA_PATH+"/static/downloads/plots/file.vchk", shell=True)
    subprocess.call(PYTERA_PATH+"/static/bcftools-1.2/plot-vcfstats "+PYTERA_PATH+"/static/downloads/plots/file.vchk -p "+PYTERA_PATH+"/static/downloads/plots/plots", shell=True)
    files_path = ''
    try:
        file1 = 'plots/plots-indels.0.pdf'
        files_path = files_path + str(' '+file1)
    except FileNotFoundError:
        pass
    try:
        file2 = 'plots/plots-substitutions.0.pdf'
        files_path = files_path + str(' '+file2)
    except FileNotFoundError:
        pass
    try:
        file3 = 'plots/plots-tstv_by_qual.0.pdf'
        files_path = files_path + str(' '+file3)
    except FileNotFoundError:
        pass
    try:
        file4 = 'plots/plots-counts_by_af.snps.pdf'
        files_path = files_path + str(' '+file4)
    except FileNotFoundError:
        pass
    try:
        file5 = 'plots/plots-counts_by_af.indels.pdf'
        files_path = files_path + str(' '+file5)
    except FileNotFoundError:
        pass
    try:
        file6 = 'plots/plots-tstv_by_af.0.pdf'
        files_path = files_path + str(' '+file6)
    except FileNotFoundError:
        pass
    
    subprocess.call('tar -cvf'+basePath+'/plots/'+'plots.tar -C '+basePath+'/'+files_path, shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -f "+basePath+'/plots/'+'plots.tar', shell=True)
    name = save_binary('plots/plots.tar.gz', user_profile)
 
    for file_name in os.listdir(PYTERA_PATH+"/static/downloads/plots"):
        os.remove(PYTERA_PATH+"/static/downloads/plots/"+file_name)
    os.remove(PYTERA_PATH+"/static/downloads/subset.vcf")
    os.remove(baseName+".gz")
    os.remove(baseName+".gz.tbi")
    
    path = PYTERA_PATH+'/static/downloads/' + name
    with open(path, "rb") as zip_plots:
        data = zip_plots.read()
    response = HttpResponse( data, content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=' + name.split('/')[1]
    return response
    
    
    
def get_fasta(chromo, start, stop, named_file, user_profile, spec_samples):
    baseName=getFilePath(named_file)
    basePath=getBasePath()

    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/bgzip -c -f "+baseName+' > '+baseName+'.gz', shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf "+baseName+".gz", shell=True)
    subprocess.call(PYTERA_PATH+"/static/tabix-0.2.6/tabix -f -p vcf -h "+baseName+".gz"+" "+str(chromo)+":"+str(start)+"-"+str(stop)+" > "+PYTERA_PATH+"/static/downloads/subset.vcf", shell=True)
    
    vcf_reader = vcf.Reader(filename=PYTERA_PATH+"/static/downloads/subset.vcf")
    if spec_samples=='':
        list_samples=vcf_reader.samples
    else:
        x = spec_samples.split(' ')
        a = []
        for elem in x:
            for b in elem.split(','):
                a.append(b)
        list_samples = []
        for elem in a:
            if elem != '':
                list_samples.append(elem)
    dic_a={}
    dic_b={}
    for sample in list_samples:
        dic_a[sample]=[]
        dic_b[sample]=[]
    for record in vcf_reader:
        if record.POS>=start and record.POS<=stop and record.CHROM==chromo:
            for sample in list_samples:
                call=record.genotype(str(sample))
                base = call.gt_bases
                dic_a[sample].append((str(base[0]), int(record.POS)))
                dic_b[sample].append((str(base[2]), int(record.POS)))
        elif record.POS>=stop and record.CHROM==chromo:
            break      
    dic_a = collections.OrderedDict(sorted(dic_a.items()))
    dic_b = collections.OrderedDict(sorted(dic_b.items()))

    region, pos1, pos2 = parse_fasta(chromo, start, stop)
    
    file=open(basePath+"/FASTA-"+str(chromo)+"-"+str(start)+"-"+str(stop)+".fasta","w")
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
    file1 = "FASTA-"+str(chromo)+"-"+str(start)+"-"+str(stop)+".fasta"
    name = save_binary(file1, user_profile)
    os.remove(basePath+"/FASTA-"+str(chromo)+"-"+str(start)+"-"+str(stop)+".fasta")
    os.remove(PYTERA_PATH+"/static/downloads/subset.vcf")
    os.remove(baseName+".gz")
    os.remove(baseName+".gz.tbi")
    
    path = PYTERA_PATH+'/static/downloads/'+name
    with open(path, "rb") as fa:
        data = fa.read()
    response = HttpResponse( data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=' + name.split('/')[1]
    return response
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    