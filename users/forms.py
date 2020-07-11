from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from book.models import Booking,Tables
from django.db import transaction
import datetime




class UserForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'input-class'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'input-class'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'input-class'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'input-class'}))
    password1 = forms.CharField(label = 'Password' ,widget=forms.PasswordInput(attrs={'class':'input-class'}))
    password2 = forms.CharField(label = 'Confirm Password' ,widget=forms.PasswordInput(attrs={'class':'input-class'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class':'input-class','rows':10}))
    contact = forms.RegexField(regex=r'^\+?1?\d{9,11}$', widget=forms.NumberInput(attrs={'class':'input-class'}),error_messages={'invalid': 'Phone number must be entered in the format: +999999999. Up to 11 digits allowed'})

    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password1','password2','contact','address']


class BookingForm(forms.ModelForm):
  capacity = forms.IntegerField(widget = forms.NumberInput(attrs={'class':'form-control capacity','placeholder':'Number of People'}))
  date = forms.DateField(widget = forms.DateInput(attrs={'class':"form-control datepicker",'type':'date', "placeholder":"Date"}))
  time = forms.TimeField(widget = forms.TimeInput(attrs={'class':'form-control timepicker','type':'time'}))
  table = forms.ModelChoiceField(queryset=Tables.objects.none(),
                                empty_label = 'Select Table ID ',
                                widget=forms.Select(
                                attrs={'class':'form-control','id':'id_table', 'placeholder':'Table Number'}
                                ))
  class Meta:
    model = Booking
    fields = ['capacity', 'date', 'time','table']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['table'].queryset = Tables.objects.none()
    if 'date' in self.data and 'time' in self.data :
      try:
        date = self.data.get('date')
        time = self.data.get('time')
        endtime = datetime.timedelta(hours=1)
        e_time = datetime.datetime.strptime(time,"%H:%M") - endtime
        Booked_table = Booking.objects.filter(date = date).filter(time__lte = time).filter(time__gte = e_time ).values_list('table_id', flat=True)
        self.fields['table'].queryset =  Tables.objects.exclude(id__in = Booked_table)
      except (ValueError, TypeError):
        pass
    elif self.instance.pk:
      self.fields['table'].queryset =  Tables.objects.none()


  