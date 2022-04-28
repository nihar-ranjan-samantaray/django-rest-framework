from django.db import models
# from django.db.models import Model
# Create your models here.

class FileSave(models.Model):
	file_field = models.FileField(upload_to ="store/",max_length=200,null=True,default=None)

