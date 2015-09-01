from django.shortcuts import render, redirect
from .forms import *
from django.http import HttpResponse
from .vcf_functions import *
from .upload_vcf_functions import *
from .evs_vcf_functions import *
from .exac_functions import *
from .models import Document, UserProfile, Vcf
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import os
from django.utils.datastructures import MultiValueDictKeyError
import mimetypes
from django.contrib import messages
import subprocess


#PYTERA_PATH = str(os.getenv('PYTERA_PATH'))
PYTERA_PATH = '/usr/local/share/applications/pytera'


#CHROMOSSOME = "Name"
#@login_required
def index(request):
    return render(request, 'polls/index.html')


def authentication(request):
    return render(request, 'polls/authentication.html')


#@login_required
def result(request):
    if request.user.is_authenticated():
        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
        vcf_files = Vcf.objects.filter(user_profile=request.user.userprofile).all()
    else:
        return redirect('/authentication/')
    return render(request, 'polls/result.html', {'documents': documents, 'vcf_files':vcf_files})



def clear(request):
    Document.objects.filter(user_profile=request.user.userprofile).all().delete()
    #Document.objects.all().delete()
    return redirect('/documents/')


def clear_vcf(request):
    Vcf.objects.filter(user_profile=request.user.userprofile).all().delete()
    return redirect('/documents/')



def validate_file(f):
    filename = f.name
    mime = f.content_type #application/x-gzip text/directory
    allowed_mimes = ['application/x-gzip', 'text/directory', 'text/x-vcard']
    with open(PYTERA_PATH+'/static/downloads/name.vcf', 'wb+') as destination:
        n = 0
        for chunk in f.chunks(chunk_size=4000):
            if n<1:
                destination.write(chunk)
                n = n+1
    try:
        fileformat = str(open(PYTERA_PATH+'/static/downloads/name.vcf', 'r').readline()[0:13])
    except UnicodeDecodeError:
        os.remove(PYTERA_PATH+"/static/downloads/name.vcf")
        return 1
    mime_type = mimetypes.guess_type(PYTERA_PATH+'/static/downloads/name.vcf')
    if mime in allowed_mimes and mime_type[0]=='text/x-vcard':
        pass
    else:
        os.remove(PYTERA_PATH+"/static/downloads/name.vcf")
        return 1
    
    if fileformat=='##fileformat=':
        pass
    else:
        os.remove(PYTERA_PATH+"/static/downloads/name.vcf")
        return 2
    os.remove(PYTERA_PATH+"/static/downloads/name.vcf")
        



def exac_view(request):
    if request.user.is_authenticated():
        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
        vcf_files = Vcf.objects.filter(user_profile=request.user.userprofile).all()
        
        if request.method == 'POST':
            form = information(request.POST)
            region = region_form(request.POST)
            exac_excel_columns = exac_columns(request.POST)
            exac_form = exac_format(request.POST)
            
            if form.is_valid() and region.is_valid() and exac_excel_columns.is_valid() and exac_form.is_valid():
                chromo = form.cleaned_data.get('chromosome')
                start = region.cleaned_data.get('start')
                stop = region.cleaned_data.get('stop')
                exac_cols = exac_excel_columns.cleaned_data.get('exac_col')
                format_exac = exac_form.cleaned_data.get('exac_form')
                
                user_profile = request.user.userprofile

                if format_exac=='xlsx':
                    return exac_xlsx_file(str(chromo), int(start), int(stop), user_profile, list(exac_cols))
                
                return redirect('/documents/')
                
        else:
            form = information()
            region = region_form()
            exac_excel_columns = exac_columns()
            exac_form = exac_format()
    else:
        return redirect('/authentication/')
    return render(request, 'polls/exac.html', {'form':form, 'region':region, 'documents': documents, 'vcf_files':vcf_files,
                                               'exac_cols':exac_excel_columns, 'exac_form':exac_form}) 


def esp_view(request):
    if request.user.is_authenticated():
        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
        vcf_files = Vcf.objects.filter(user_profile=request.user.userprofile).all()
        
        if request.method == 'POST':
            form = information(request.POST)
            region = region_form(request.POST)
            evs_form = evs_format(request.POST)
            maf = maf_form(request.POST)
            esp_excel_columns = excel_columns(request.POST)
            
            if form.is_valid() and region.is_valid() and evs_form.is_valid() and maf.is_valid() and esp_excel_columns.is_valid():
                chromo = form.cleaned_data.get('chromosome')
                start = region.cleaned_data.get('start')
                stop = region.cleaned_data.get('stop')
                format_evs = evs_form.cleaned_data.get('esp_format')
                ea = maf.cleaned_data.get('EA')
                aa = maf.cleaned_data.get('AA')
                total = maf.cleaned_data.get('All')
                ea_sign = maf.cleaned_data.get('ea_char')
                aa_sign = maf.cleaned_data.get('aa_char')
                total_sign = maf.cleaned_data.get('all_char')
                esp_columns = esp_excel_columns.cleaned_data.get('columns')

                user_profile = request.user.userprofile
                
                if format_evs=="vcf":
                    return filter_vcf(str(chromo), int(start), int(stop), user_profile, ea, aa, total, ea_sign, aa_sign, total_sign)
                elif format_evs=="xlsx":
                    return evs_xlsx_file(str(chromo), int(start), int(stop), user_profile, list(esp_columns))
                    
                return redirect('/documents/')
                
        else:
            form = information()
            region = region_form()
            evs_form = evs_format()
            maf = maf_form()
            esp_excel_columns = excel_columns()
            
    else:
        return redirect('/authentication/')
    return render(request, 'polls/esp.html', {'form':form, 'region':region, 'documents': documents, 'vcf_files':vcf_files,
                                               'evs_form':evs_form, 'maf':maf, 'esp_columns':esp_excel_columns,}) 



def GP_view(request):
    if request.user.is_authenticated():
        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
        vcf_files = Vcf.objects.filter(user_profile=request.user.userprofile).all()
        
        if request.method == 'POST':
            form = information(request.POST)
            picker = fetch_info(request.POST)
            region = region_form(request.POST)
            frmt = file_format_form(request.POST)
            
            if form.is_valid() and picker.is_valid() and region.is_valid() and frmt.is_valid():
                chromo = form.cleaned_data.get('chromosome')
                populations = picker.cleaned_data.get('populations')
                start = region.cleaned_data.get('start')
                stop = region.cleaned_data.get('stop')
                file_format = frmt.cleaned_data.get('file_format')
                
                user_profile = request.user.userprofile
                try:
                    samples=MySamples(populations)
                except IndexError:
                    pass
                
                if file_format=="ped":
                    return ped_file(str(chromo), int(start), int(stop), list(samples), user_profile)
                elif file_format=="rdf":
                    return rdf_file_multi_allelic(str(chromo), int(start), int(stop), list(samples), user_profile)
                elif file_format=="nexus":
                    return nexus_file(str(chromo), int(start), int(stop), list(populations), list(samples), user_profile)
                elif file_format=="fasta":
                    return fasta_file(str(chromo), int(start), int(stop), list(samples), user_profile)
                    
                return redirect('/documents/')
                #return HttpResponse(str(samples))
                
        else:
            form = information()
            picker = fetch_info()
            region = region_form()
            frmt = file_format_form()
            
    else:
        return redirect('/authentication/')
    return render(request, 'polls/1000GP.html', {'form':form, 'picker':picker, 'region':region, 'frmt':frmt,
                                               'documents': documents, 'vcf_files':vcf_files}) 




def upload_view(request):
    if request.user.is_authenticated():
        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
        vcf_files = Vcf.objects.filter(user_profile=request.user.userprofile).all()
        
        if request.method == 'POST':
            form = information(request.POST)
            region = region_form(request.POST)
            form_up = format_form_uploaded(request.POST)
            upload_file = ProfileForm(request.POST, request.FILES)
            upload_name = file_uploaded_form(request.POST)
            sample_up = sample_form(request.POST)
            
            if form.is_valid() and region.is_valid() and form_up.is_valid() and upload_file.is_valid() and upload_name.is_valid() and sample_up.is_valid():
                chromo = form.cleaned_data.get('chromosome')
                start = region.cleaned_data.get('start')
                stop = region.cleaned_data.get('stop')
                format_form = form_up.cleaned_data.get('format_output')
                spec_samples = sample_up.cleaned_data.get('samples')
                
                user_profile = request.user.userprofile
                try:
                    resp = validate_file(request.FILES['docfile'])
                    if resp == 1:
                        messages.add_message(request, messages.ERROR, 'The uploaded file is not a VCF or Gizipped file, please provide a new file')
                        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
                        vcf_files = Vcf.objects.filter(user_profile=request.user.userprofile).all()
                        return render(request, 'polls/upload.html', {'form':form, 'region':region, 'form_up':form_up,
                                                                    'upload_file':upload_file, 'upload_name':upload_name, 'sample_up':sample_up,
                                                                    'documents': documents, 'vcf_files':vcf_files}) 
                    elif resp==2:
                        messages.add_message(request, messages.ERROR, 'The uploaded file is not a VCF file format, please provide a new file')
                        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
                        vcf_files = Vcf.objects.filter(user_profile=request.user.userprofile).all()
                        return render(request, 'polls/upload.html', {'form':form, 'region':region, 'form_up':form_up,
                                                                    'upload_file':upload_file, 'upload_name':upload_name, 'sample_up':sample_up,
                                                                    'documents': documents, 'vcf_files':vcf_files}) 
                    else:
                        pass
                    newdoc = Vcf(vcf_file = request.FILES['docfile'], user_profile = user_profile)
                    doc = request.FILES['docfile']
                    doc_name = str(doc.name)
                    newdoc.save()

                except MultiValueDictKeyError:
                    pass
                
                if upload_name.cleaned_data.get('file_uploaded')!='':
                    doc_name = upload_name.cleaned_data.get('file_uploaded')
                else:
                    pass
                
                if format_form=="xlsx":
                    return xlsx_file(str(chromo), int(start), int(stop), doc_name, user_profile)
                elif format_form=="stats":
                    return plot_stats(str(chromo), int(start), int(stop), doc_name, user_profile)
                elif format_form=="fasta_up":
                    return get_fasta(str(chromo), int(start), int(stop), doc_name, user_profile, spec_samples)
                    
                return redirect('/documents/')
                
        else:
            form = information()
            region = region_form()
            form_up = format_form_uploaded()
            upload_file = ProfileForm(instance=request.user.userprofile)
            upload_name = file_uploaded_form()
            sample_up = sample_form()
            
    else:
        return redirect('/authentication/')
    return render(request, 'polls/upload.html', {'form':form, 'region':region, 'form_up':form_up,
                                                'upload_file':upload_file, 'upload_name':upload_name, 'sample_up':sample_up,
                                                'documents': documents, 'vcf_files':vcf_files}) 