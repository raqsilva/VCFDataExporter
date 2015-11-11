import os 
from os.path import expanduser
import vcf
import collections
from .dictionaries import ftp_dic, pop_sex, pop_samples
from django.http import HttpResponse
from Bio import SeqIO
from .models import Document, Vcf
from django.core.files import File
import subprocess
from pytera.settings import BASE_DIR

PYTERA_PATH = BASE_DIR