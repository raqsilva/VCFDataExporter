from django.shortcuts import render, redirect
from .forms import *
from django.http import HttpResponse
from .vcf_functions import *
from .upload_vcf_functions import *
from .evs_vcf_functions import *
from .models import Document, UserProfile, Plot
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import os
from django.utils.datastructures import MultiValueDictKeyError
import mimetypes
from django.contrib import messages

#PYTERA_PATH = str(os.getenv('PYTERA_PATH'))
PYTERA_PATH = '/usr/local/share/applications/pytera'


#CHROMOSSOME = "Name"
#@login_required
def index(request):
    return render(request, 'polls/index.html')


def authentication(request):
    return render(request, 'polls/authentication.html')


#@login_required
def info(request):
    if request.method == 'POST':
        form = information(request.POST)
        picker = fetch_info(request.POST)
        region = region_form(request.POST)
        frmt = file_format_form(request.POST)
        if form.is_valid() and picker.is_valid() and region.is_valid() and frmt.is_valid() :
            chromo = form.cleaned_data.get('chromosome')
            populations = picker.cleaned_data.get('populations')
            start = region.cleaned_data.get('start')
            stop = region.cleaned_data.get('stop')
            file_format = frmt.cleaned_data.get('file_format')
            
            if list(populations)[0]!="all":
                samples=MySamples(list(populations))
            else:
                samples=list(populations)
                
            if file_format=="ped":
                ped_file(str(chromo), int(start), int(stop), list(samples))
            elif file_format=="rdf":
                rdf_file_multi_allelic(str(chromo), int(start), int(stop), list(samples))
            elif file_format=="nexus":
                nexus_file(str(chromo), int(start), int(stop), list(populations), list(samples))
            elif file_format=="fasta":
                fasta_file(str(chromo), int(start), int(stop), list(samples))
            
            #return HttpResponse('Check Download Folder')
            return redirect('/result/')
            #return HttpResponse(str(samples))
    else:
        form = information()
        picker = fetch_info()
        region = region_form()
        frmt = file_format_form()
    return render(request, 'polls/info.html', {'form':form, 'picker':picker, 'region':region, 'frmt':frmt})


#@login_required
def result(request):
    if request.user.is_authenticated():
        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
        plots = Plot.objects.filter(user_profile=request.user.userprofile).all()
    else:
        return redirect('/authentication/')
    return render(request, 'polls/result.html', {'documents': documents, 'plots':plots})



def clear(request):
    Document.objects.filter(user_profile=request.user.userprofile).all().delete()
    #Document.objects.all().delete()
    return redirect('/documents/')


def clear_images(request):
    Plot.objects.filter(user_profile=request.user.userprofile).all().delete()
    return redirect('/documents/')



def validate_file(f):
    filename = f.name
    mime = f.content_type #application/x-gzip text/directory
    allowed_mimes = ['application/x-gzip', 'text/directory', 'text/x-vcard']
    # if filename.endswith('.vcf') or filename.endswith('.gz'):
    #     pass
    # else:
    #     raise ValidationError("File is not a VCF or gzipped VCF file. Please try again")
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
        

    
def upload_view(request):
    if request.method == 'POST':
        upload_file = ProfileForm(request.POST, request.FILES)
        if upload_file.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'], user_profile = request.user.userprofile)
            newdoc.save()
    else:
        upload_file = ProfileForm(instance=request.user.userprofile)
    documents = Document.objects.filter(user_profile=request.user.userprofile).all()
    return render(request, 'polls/upload.html', {'upload_file':upload_file, 'documents': documents})



def file_frmt_view_up(request):
    if request.user.is_authenticated():
        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
        plots = Plot.objects.filter(user_profile=request.user.userprofile).all()
        
        if request.method == 'POST':
            form = information(request.POST)
            picker = fetch_info(request.POST)
            region = region_form(request.POST)
            frmt = file_format_form(request.POST)
            form_up = format_form_uploaded(request.POST)
            upload_file = ProfileForm(request.POST, request.FILES)
            upload_name = file_uploaded_form(request.POST)
            sample_up = sample_form(request.POST)
            evs = evs_pop(request.POST)
            evs_form = evs_format(request.POST)
            maf = maf_form(request.POST)
            esp_excel_columns = excel_columns(request.POST)
            
            if form.is_valid() and picker.is_valid() and region.is_valid() and frmt.is_valid() and form_up.is_valid() and upload_file.is_valid() and upload_name.is_valid() and sample_up.is_valid() and evs.is_valid() and evs_form.is_valid() and maf.is_valid() and esp_excel_columns.is_valid():
                chromo = form.cleaned_data.get('chromosome')
                populations = picker.cleaned_data.get('populations')
                start = region.cleaned_data.get('start')
                stop = region.cleaned_data.get('stop')
                file_format = frmt.cleaned_data.get('file_format')
                format_form = form_up.cleaned_data.get('format_output')
                spec_samples = sample_up.cleaned_data.get('samples')
                pop_evs = evs.cleaned_data.get('pop')
                format_evs = evs_form.cleaned_data.get('esp_format')
                ea = maf.cleaned_data.get('EA')
                aa = maf.cleaned_data.get('AA')
                total = maf.cleaned_data.get('All')
                ea_sign = maf.cleaned_data.get('ea_char')
                aa_sign = maf.cleaned_data.get('aa_char')
                total_sign = maf.cleaned_data.get('all_char')
                esp_columns = esp_excel_columns.cleaned_data.get('columns')
                
                #return HttpResponse(str(esp_columns))
                
                #return HttpResponse(str(request.FILES['docfile'].content_type)) #application/x-gzip text/directory
                
                user_profile = request.user.userprofile
                try:
                    resp = validate_file(request.FILES['docfile'])
                    if resp == 1:
                        messages.add_message(request, messages.ERROR, 'The uploaded file is not a VCF or Gizipped file, please provide a new file')
                        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
                        plots = Plot.objects.filter(user_profile=request.user.userprofile).all()
                        return render(request, 'polls/tool.html', {'form':form, 'picker':picker, 'region':region, 'frmt':frmt,
                                                                   'form_up':form_up, 'upload_file':upload_file, 'upload_name':upload_name,
                                                                   'documents': documents, 'sample_up':sample_up, 'plots':plots, 'evs':evs, 'evs_form':evs_form, 'esp_columns':esp_excel_columns}) 
                    elif resp==2:
                        messages.add_message(request, messages.ERROR, 'The uploaded file is not a VCF file format, please provide a new file')
                        documents = Document.objects.filter(user_profile=request.user.userprofile).all()
                        plots = Plot.objects.filter(user_profile=request.user.userprofile).all()
                        return render(request, 'polls/tool.html', {'form':form, 'picker':picker, 'region':region, 'frmt':frmt,
                                                                   'form_up':form_up, 'upload_file':upload_file, 'upload_name':upload_name,
                                                                   'documents': documents,'sample_up':sample_up, 'plots':plots, 'evs':evs, 'evs_form':evs_form, 'esp_columns':esp_excel_columns}) 
                    else:
                        pass
                    newdoc = Document(docfile = request.FILES['docfile'], user_profile = user_profile)
                    doc = request.FILES['docfile']
                    doc_name = str(doc.name)
                    newdoc.save()
                except MultiValueDictKeyError:
                    pass
                
                if upload_name.cleaned_data.get('file_uploaded')!='':
                    doc_name = upload_name.cleaned_data.get('file_uploaded')
                else:
                    pass
                
                try:
                    samples=MySamples(populations)
                except IndexError:
                    pass
                
                if file_format=="ped":
                    ped_file(str(chromo), int(start), int(stop), list(samples), user_profile)
                elif file_format=="rdf":
                    rdf_file_multi_allelic(str(chromo), int(start), int(stop), list(samples), user_profile)
                elif file_format=="nexus":
                    nexus_file(str(chromo), int(start), int(stop), list(populations), list(samples), user_profile)
                elif file_format=="fasta":
                    fasta_file(str(chromo), int(start), int(stop), list(samples), user_profile)
                elif format_form=="xlsx":
                    return xlsx_file(str(chromo), int(start), int(stop), doc_name, user_profile)
                elif format_form=="stats":
                    return plot_stats(str(chromo), int(start), int(stop), doc_name, user_profile)
                elif format_form=="fasta_up":
                    return get_fasta(str(chromo), int(start), int(stop), doc_name, user_profile, spec_samples)
                elif format_evs=="vcf":
                    return filter_vcf(str(chromo), int(start), int(stop), doc_name, user_profile, ea, aa, total, ea_sign, aa_sign, total_sign)
                elif format_evs=="xlsx":
                    return evs_xlsx_file(str(chromo), int(start), int(stop), doc_name, user_profile, pop_evs, esp_columns)
                    
                return redirect('/documents/')
                #return HttpResponse(str(samples))
                
        else:
            form = information()
            picker = fetch_info()
            region = region_form()
            frmt = file_format_form()
            form_up = format_form_uploaded()
            upload_file = ProfileForm(instance=request.user.userprofile)
            upload_name = file_uploaded_form()
            sample_up = sample_form()
            evs = evs_pop()
            evs_form = evs_format()
            maf = maf_form()
            esp_excel_columns = excel_columns()
            
    else:
        return redirect('/authentication/')
    return render(request, 'polls/tool.html', {'form':form, 'picker':picker, 'region':region, 'frmt':frmt, 'form_up':form_up,
                                               'upload_file':upload_file, 'upload_name':upload_name, 'sample_up':sample_up,
                                               'documents': documents, 'plots':plots, 'evs':evs, 'evs_form':evs_form, 'maf':maf, 'esp_columns':esp_excel_columns}) 







