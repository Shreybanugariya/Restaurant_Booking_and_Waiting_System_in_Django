from django.db import models
from users.models import User
from django.core.exceptions import ValidationError
import datetime

def valid_time(value):
  if value < datetime.time(17,0,0) or value > datetime.time(22,0,0):
    raise ValidationError('Enter time between 5pm to 10pm')
  else:
    return value

def capacity_validation(value):
  if value > 6:
    raise ValidationError('Our Capacity is up to 6 person please Enter valid number')
  else:
    return value

def waiting_validation(value):
  avail_4_table = Tables.objects.filter(capacity = 4).filter(is_avail = True).count()
  avail_6_table = Tables.objects.filter(capacity = 6).filter(is_avail = True).count()
  if(avail_4_table == 0 and avail_6_table):
    if value >= 4 :
      raise ValidationError('Table for ' + str(value) + ' is available')
    else:
      return value

  elif(avail_6_table == 0 and avail_4_table):
    if value <= 4 :
      raise ValidationError('Table for ' + str(value) + ' is available')
    else:
      return value

  else:
    return value


# Create your models here.
class Tables(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True, null = True)
    capacity = models.IntegerField(null = False)
    is_avail = models.BooleanField(default = True)
    table_id = models.IntegerField(null = False, unique = True)
    time = models.TimeField(null = True,blank=True)

    def __str__(self):
        return str(self.table_id)

class Waiting(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  no_people = models.IntegerField(null = False, validators=[capacity_validation,waiting_validation])
  #table = models.ForeignKey(Tables , on_delete=models.CASCADE, blank=True, null = True)
  add_time = models.TimeField(null = False, default = datetime.datetime.now().time() )

  def __str__(self):
    return str(self.id) + " " + self.user.username

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    table = models.ForeignKey(Tables, on_delete = models.CASCADE)
    date = models.DateField()
    time = models.TimeField(validators=[valid_time])
    capacity = models.IntegerField()

    def __str__(self):
      return self.user.first_name + " " + str(self.table.table_id)


