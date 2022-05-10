from unicodedata import name
from django.db import models
# from django.db.models import Model
# Create your models here.

class FileDetails(models.Model):
	file_id = models.AutoField(primary_key=True)
	file_name = models.CharField(max_length=100,null=False)
	file_field = models.FileField(upload_to ="store/",max_length=200,null=True,default=None)
	class Meta:
		db_table='file_details'


class ExtractionItems(models.Model):
	extracted_id = models.AutoField(primary_key=True)
	job_number=models.IntegerField()
	task_item_number=models.CharField(max_length=20)
	task_quantity=models.IntegerField()

	class Meta:
		db_table='po_extract'