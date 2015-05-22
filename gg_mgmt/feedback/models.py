#-*- coding:utf-8 -*-


from django.db import models


class Feedback(models.Model):
    id = models.IntegerField('', max_length=8, primary_key=True)
    imei = models.CharField('', max_length=40)
    vendor = models.CharField('', max_length=40) 
    model = models.CharField('', max_length=40) 
    fingerprint = models.CharField('', max_length=40)
    product = models.CharField('', max_length=40)
    sdk = models.IntegerField('', max_length=11)
    mac = models.CharField('', max_length=40)
    widthpixels = models.IntegerField('', max_length=11)
    heightpixels = models.IntegerField('', max_length=11)
    density = models.IntegerField('', max_length=11)
    pkg_name = models.CharField('', max_length=40)
    ver_code = models.IntegerField('', max_length=11)
    signature = models.CharField('', max_length=40)
    channel = models.CharField('', max_length=40)
    options = models.IntegerField('', max_length=11)
    game_id = models.CharField('', max_length=40)
    apk_id = models.CharField('', max_length=40)
    content = models.CharField('', max_length=5000)
    attachment = models.CharField('', max_length=255)
    create_time_ymd = models.CharField('', max_length=40)
    create_time_hms = models.CharField('', max_length=40)    
 
#    class Meta:
#        db_table = ''
