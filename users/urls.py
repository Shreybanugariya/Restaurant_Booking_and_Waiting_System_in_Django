from django.urls import path
from .views import Book, Registration, logout_view, Login, menu, contact, load_table, WaitingCreateView, notification

urlpatterns = [
    path('',Book.as_view(),name='home'),
    path('contact/',contact,name='contact'),
    path('register/', Registration.as_view(), name='register'),
    path('login/',Login.as_view(),name='login'),
    path('logout/', logout_view, name='logout'),
    path('menu/',menu,name='menu'),
    path('ajax/load_table/', load_table, name='ajax_load_table'),
    path('WaitingForm/', WaitingCreateView.as_view(), name="waiting"),
    path('notification/',notification, name='notification'),
]