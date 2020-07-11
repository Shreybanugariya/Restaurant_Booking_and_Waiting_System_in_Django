from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail


import datetime
from django.utils import timezone

from .tasks import notify_user, update_user, w_next_user
from .models import User
from .forms import UserForm, BookingForm
from book.models import Booking, Tables, Waiting


# Book is home page of website
class Book(CreateView):
    model = Booking
    template_name = 'users/index.html'
    form_class = BookingForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Welcome to RWS"
        context['message'] = "Testing for message"
        context['total_waitings'] = Waiting.objects.all().count()
        context['total_table'] = Tables.objects.all().count()
        context['avail_table'] = Tables.objects.filter(is_avail = True).count()
        context['total_bookings'] = Booking.objects.filter(date = datetime.datetime.today()).count()
        context['avail_4_table'] = Tables.objects.filter(capacity = 4).filter(is_avail = True).count()
        context['avail_6_table'] = Tables.objects.filter(capacity = 6).filter(is_avail = True).count()
        context['total_4_waitings'] = Waiting.objects.filter(no_people__lte = 4).count()
        context['total_6_waitings'] = Waiting.objects.filter(no_people__gte = 4).count()
        context['is_waiting'] = False if ( context['avail_4_table'] and context['avail_6_table'] ) else True
        return context
    
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            inst = form.save(commit=False)
            inst.user = self.request.user
            inst.save()
            notify_user(user_id = self.request.user.id ,schedule=timezone.now())
            time = datetime.datetime.strptime(str(inst.time), "%H:%M:%S") - datetime.timedelta(hours=1)
            dt = str(inst.date) + " " + str(time.time())
            update_user(user_id = self.request.user.id , schedule = datetime.datetime.strptime(dt, "%Y-%m-%d  %H:%M:%S"))
            return super().form_valid(form)
        else:
            return redirect('login')



# It is View for Ajax call to get available table for Booking 
def load_table(request):
    u_date = request.GET.get('date')
    u_time = request.GET.get('time') 
    no_people = int(request.GET.get('capacity'))
    capacity = 0

    if no_people <= 4:
        endtime = datetime.timedelta(hours=1)    
        e_time = datetime.datetime.strptime(u_time,"%H:%M") - endtime
        e1_time = datetime.datetime.strptime(u_time,"%H:%M") + endtime
        Booked_table = Booking.objects.filter(capacity__lte = 4).filter(date = u_date).filter(time__lte = e1_time).filter(time__gte = e_time ).values_list('table_id', flat=True)
        table = Tables.objects.exclude(id__in = Booked_table).exclude(capacity = 6)

    elif no_people <= 6:
        print("success \n \n ")
        endtime = datetime.timedelta(hours=1, minutes = 30)    
        e_time = datetime.datetime.strptime(u_time,"%H:%M") - endtime
        Booked_table = Booking.objects.filter(capacity__gte = 4).filter(date = u_date).filter(time__lte = u_time).filter(time__gte = e_time ).values_list('table_id', flat=True)
        table = Tables.objects.exclude(id__in = Booked_table).exclude(capacity = 4)
    
    else :
        capacity = 0
        table = None
    return render(request, 'users/table_list.html',{'table':table})

#Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

# Menu View
def menu(request):
    context = {'menu_page':'active','title':'Menu'}
    return render(request,'users/menu.html', context)


# Contact-Us Page
def contact(request):
    if request.method == "POST":
        message_name = request.POST['message-name']
        message_email = request.POST['message-email']
        message_subject = request.POST['message-subject']
        message = request.POST['message']


        #Send Email
        send_mail(
            message_subject, #subject
            message, #message
            message_email, #from Email
            ['170120107010@git.org.in', '170120107033@git.org.in'], #to Email
        )
        return render(request, 'users/contact.html', {'message_name':message_name})

    else:
        context = {'contact_page':'active','title':'Contact-us'}
        return render(request, 'users/contact.html', context)

class Login(UserPassesTestMixin, LoginView):
    template_name = 'users/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_page"] = "active"
        context["title"] = "Login"
        return context
    
    def test_func(self):
        if self.request.user.is_authenticated:
            return False
        return True


# Registration Form 
class Registration(UserPassesTestMixin,CreateView):
    model = User
    form_class = UserForm
    template_name = 'users/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['register_page'] = 'active'
        context["title"] = "Register"
        return context

    def form_valid(self, form):
        user = form.save()
        return redirect('login')

    def test_func(self):
        if self.request.user.is_authenticated:
            return False
        return True


class WaitingCreateView(UserPassesTestMixin, CreateView):
    model = Waiting
    template_name = 'users/form.html'
    fields = ['no_people']
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Waiting List"
        return context

    def form_valid(self, form):
        inst = form.save(commit=False)
        inst.user = self.request.user
        capacity = 4 if inst.no_people <= 4 else 6 
        wait_no = Waiting.objects.all().count()
        table = Tables.objects.filter(capacity = capacity).order_by('time')
        if wait_no < table.count() :
            t1 = datetime.datetime.now()
            t2 = datetime.datetime.combine(datetime.datetime.today(),table[wait_no].time)
            if t1 < t2 :
                r_time = 10
            r_time = (t1 - t2)
            r_time = int(r_time.total_seconds()/60)
            w_next_user(user_id = self.request.user.id, r_time = r_time, schedule=timezone.now()) 
        inst.save()
        return super().form_valid(form)
    
    def test_func(self):
        avail_4_table = Tables.objects.filter(capacity = 4).filter(is_avail = True).count()
        avail_6_table = Tables.objects.filter(capacity = 6).filter(is_avail = True).count()
        if self.request.user.is_authenticated and (avail_4_table == 0 or avail_6_table == 0):
            return True
        else:
            return False

@login_required()
def notification(request):
    booking = Booking.objects.filter(user=request.user)  
    waiting = Waiting.objects.filter(user=request.user)
    if waiting:
        capacity = 4 if waiting[0].no_people <= 4 else 6
        qs = Waiting.objects.filter(no_people__lte = capacity)
        your_waiting = list(qs.values_list('id', flat=True)).index(waiting[0].id)
        your_waiting += 1
        total_waiting = qs.count()
        
        context = {'notification':'active', 'title':'Status', 'Booking':booking, 'waiting':waiting[0],'total_waiting':total_waiting, 'your_waiting':your_waiting}
        return render(request, 'users/notification.html', context)
    else:
        context = {'notification':'active', 'title':'Status', 'Booking':booking, 'waiting':waiting}
        return render(request, 'users/notification.html', context)
  