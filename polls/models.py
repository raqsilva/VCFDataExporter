from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
import datetime



class UserProfile(models.Model):
    user = models.OneToOneField(User)
    #docfile = models.FileField(upload_to='documents')
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField(default=datetime.date.today())
  
    
class Document(models.Model):
    docfile = models.FileField(upload_to = 'documents', blank = True)
    user_profile = models.ForeignKey(UserProfile)

@receiver(pre_delete, sender=Document)
def document_delete(sender, instance, **kwargs):
    instance.docfile.delete(False)


class Plot(models.Model):
    pdf = models.FileField(upload_to = 'documents', blank = True)
    user_profile = models.ForeignKey(UserProfile)

@receiver(pre_delete, sender=Plot)
def image_delete(sender, instance, **kwargs):
    instance.pdf.delete(False)
