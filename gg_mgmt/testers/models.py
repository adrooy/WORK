#-*- coding:utf-8 -*-


from django.db import models


class IplayTesters(models.Model):
     id = models.IntegerField('', max_length=11, primary_key=True)
     imei = models.CharField('imei', max_length=40)
     vendor = models.CharField('', max_length=64) 
     model = models.CharField('', max_length=64) 
     fingerprint = models.CharField('', max_length=255)
     product = models.CharField('', max_length=64)
     sdk = models.IntegerField('', max_length=11)
     mac = models.CharField('', max_length=40)
     widthpixels = models.IntegerField('', max_length=11)
     heightpixels = models.IntegerField('', max_length=11)
     density = models.IntegerField('', max_length=11)
     contact = models.CharField('', max_length=1024) 
     name =  models.CharField('', max_length=1024)
     create_time_ymd = models.CharField('', max_length=8)
     create_time_hms = models.CharField('', max_length=6)    

     class Meta:
         db_table = 'iplay_testers'
         verbose_name_plural = '内测用户管理表'
