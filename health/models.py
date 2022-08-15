import datetime
from multiprocessing.sharedctypes import Value
from django.db import models

# Create your models here.


class Weight(models.Model):
    date = models.DateField('日付', default=datetime.datetime.now().date())
    weight = models.FloatField('体重')
    body_fat = models.FloatField('体脂肪率', default=0)
    bmi = models.FloatField('BMI', default=0)


class Detail(models.Model):
    GENDER_CHOICES = (
        (1, '男性'),
        (2, '女性'),
    )
    height = models.FloatField('身長')
    gender = models.IntegerField(
        verbose_name='性別', choices=GENDER_CHOICES, blank=True, null=True)
    age = models.IntegerField('年齢')
