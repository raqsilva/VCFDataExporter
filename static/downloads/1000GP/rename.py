import os

names = os.listdir('.')

for old_name in names:
    if old_name.endswith('.vcf.gz'):
        os.rename(old_name, old_name.split('.')[1]+'.vcf.gz')
    elif old_name.endswith('.vcf.gz.tbi'):
        os.rename(old_name, old_name.split('.')[1]+'.vcf.gz.tbi')
