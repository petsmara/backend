from django.db import models

class User(models.Model):
    email        = models.EmailField(max_length      = 250, unique = True)
    password     = models.CharField(max_length       = 300)
    nickname     = models.CharField(max_length       = 300)
    phone_number = models.CharField(max_length       = 300)
    has_cat      = models.NullBooleanField(default = False)
    has_dog      = models.NullBooleanField(default = False)
    created_at   = models.DateTimeField(auto_now_add = True)
    updated_at   = models.DateTimeField(auto_now     = True)

    class Meta:
        db_table = 'users'

