from django.core.management.base import NoArgsCommand
from polls.models import Document, Vcf

class Command(NoArgsCommand):

    help = 'Deletes all files and instances from file models'

    def handle_noargs(self, **options):
        Document.objects.all().delete()
        Vcf.objects.all().delete()