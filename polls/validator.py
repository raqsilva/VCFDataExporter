import vcf
from django.http import HttpResponse
from django.core.files import File
import os
from .vcf_functions import getBasePath, save_binary, getFilePath, parse_fasta
import subprocess


PYTERA_PATH = '/usr/local/share/applications/pytera'


def validate_vcf(named_file, user_profile):
    baseName=getFilePath(named_file)
    basePath=getBasePath()
    
    subprocess.call(PYTERA_PATH + '/static/vcftools_0.1.12b/bin/vcf-validator -u '+ baseName
                    +' 2>&1 | tee ' + PYTERA_PATH + '/static/downloads/output_unfilter.txt',
                    shell=True, env={'PERL5LIB': PYTERA_PATH + '/static/vcftools_0.1.12b/perl'})

    new_out = open(PYTERA_PATH + '/static/downloads/output.txt', 'w')
    with open(PYTERA_PATH + '/static/downloads/output_unfilter.txt', 'r') as out:
        x = out.readlines()
        for elem in x:
            if PYTERA_PATH+'/static/' or PYTERA_PATH in elem:
                elem = elem.replace("/usr/local/share/applications/pytera/static/", "")
                elem = elem.replace('/usr/local/share/applications/pytera', '')
            new_out.write(elem)

    new_out.close()
    out.close()
    file = 'output.txt'
    name = save_binary(file, user_profile)
    os.remove(PYTERA_PATH + '/static/downloads/output.txt')
    os.remove(PYTERA_PATH + '/static/downloads/output_unfilter.txt')
    
    path = PYTERA_PATH+'/static/downloads/' + name
    with open(path, "rb") as text:
        data = text.read()
    response = HttpResponse( data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=' + name.split('/')[1]
    return response


