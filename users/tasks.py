from background_task import background
from .models import User
from django.core.mail import EmailMessage

@background(schedule = 60)
def notify_user(user_id):
    user = User.objects.get(pk=user_id)
    subject = 'Booking Successful.' 
    message = "Dear Customer, \nWelcome to Mohit and Shrey's Restaurant. We are happy to serve you! Your Booking was Successful! Waiting to see you on time. Don't forget to give us feedback about your booking experience. Call our manager for any queries and information related to your booking. We are available for inquiries from 5:00 pm to 11:00 pm every day except Wednesday. We will inform you one hour prior to the time of booking so that you can reach on time. Happy Eating!!! \nRegards MOHIT AND SHREY'S RESTAURANT"
    user.email_user(subject, message)

@background(schedule = 60)
def update_user(user_id):
    user = User.objects.get(pk=user_id)
    subject = ' One hour to go for your delicious meal.'
    message = "Dear Customer, We are waiting for you. This is to remind you that one hour is left for your delicious cuisine. We will appreciate your punctuality. Contact our manager @ 999****** for any queries. Come Soon! \n WE WILL WAIT FOR 35 MINUTES SUBSEQUENT THE TIME OF BOOKING IF YOU FAIL TO REACH OR CONTACT US THE BOOKING WILL BE CANCELED AUTOMATICALLY.\n Regards MOHIT AND SHREY'S RESTAURANT"
    user.email_user(subject, message)
    
@background(schedule = 60)
def w_next_user(user_id, r_time):
        user = User.objects.get(pk=user_id)
        subject = 'You are next,'
        message = "Dear Customer,  Your turn is next. Please reach the restaurant in " + str(r_time) +"Minutes. We appreciate your patience. We are waiting for you. Thank you for your cooperation. For any queries regarding your waiting feel free to contact us at @999******. or reply to us through this mail. We will respond to you shortly.  Thank you. Happy Eating!!!. \nRegards MOHIT AND SHREY'S RESTAURANT  " 
        user.email_user(subject, message)

@background(schedule = 60)
def w_c_user(user_id):
        user = User.objects.get(pk=user_id)
        subject = "It's Your Turn....YAYYY"
        message = "Dear customer, It is your turn, Your table is already arranged and we are waiting for your order.  Enjoy the delicious meal and don't forget to give us your valuable feedback. Your opinion matters. \nRegards MOHIT AND SHREY'S RESTAURANT"
        user.email_user(subject, message)
