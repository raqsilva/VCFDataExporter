import os
import subprocess


subprocess.call('tar xzf ESP6500SI-V2-SSA137.GRCh38-liftover.snps_indels.vcf.tar.gz', shell=True)

os.remove('ESP6500SI-V2-SSA137.GRCh38-liftover.snps_indels.vcf.tar.gz')

names = os.listdir('.')

for old_name in names:
    if old_name.endswith('.vcf'):
        subprocess.call('/../../tabix/bgzip -c -f '+old_name+' > '+'ESP.'+old_name.split('.')[2]+'.vcf.gz', shell=True)
        os.remove(old_name)

names = os.listdir('.')

for gzipped in names:
    if gzipped.endswith('.vcf.gz'):
        subprocess.call('/../../tabix/tabix -f -p vcf '+gzipped, shell=True)



