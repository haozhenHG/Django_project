from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(verbose_name="用户名",max_length=30,unique=True)

    password = models.CharField('密码',max_length=32)

    created_time = models.DateTimeField('创建时间',auto_now_add = True) # 第一次被创建时自动设置为当前日期和时间

    updated_time = models.DateTimeField('更新时间',auto_now = True) # 在模型的任何 save() 操作时自动设置为当前日期和时间

    def __str__(self):
        return 'username %s' % (self.username)


