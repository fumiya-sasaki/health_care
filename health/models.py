from multiprocessing.sharedctypes import Value
from django.db import models

# Create your models here.

class Weight(models.Model):
  date = models.DateField('日付')
  weight = models.FloatField('体重')
  body_fat = models.FloatField('体脂肪率',default=0)