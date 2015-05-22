#-*- coding:utf-8 -*-


from django.db import models


class GameDeveloper(models.Model):
    id = models.IntegerField('pk', max_length=11, primary_key=True)
    developer = models.CharField('开发商', max_length=200)
    icon_url = models.CharField('icon', max_length=200)
    manual_num = models.IntegerField('排列序号', max_length=11)
    is_top = models.IntegerField('顶级厂商', max_length=1)

    class Meta:
        db_table = 'iplay_game_developer'
        verbose_name_plural = '游戏开发商列表'

class GameOperation(models.Model):
    id = models.IntegerField('pk', max_length=11, primary_key=True)
    user_id = models.IntegerField('操作人ＩＤ', max_length=11)
    user_name = models.CharField('操作人姓名', max_length=45)
    page = models.CharField('操作页面', max_length=45)
    goal = models.CharField('操作目标ＩＤ', max_length=45)
    action = models.CharField('操作行为', max_length=45)
    operation_time = models.IntegerField('操作时间', max_length=11)
    operation_date = models.CharField('操作日期', max_length=45)

    class Meta:
        db_table = 'iplay_operation_record'
        verbose_name_plural = '后台管理操作记录'

class TestImei(models.Model):
     imei = models.CharField('imei', max_length=45, primary_key=True)
     user_name = models.CharField('使用人的名字', max_length=45)

     class Meta:
         db_table = 'iplay_test_imei'
         verbose_name_plural = '测试机imei'
   

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
