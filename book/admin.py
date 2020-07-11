from django.contrib import admin
from .models import Booking,Tables, Waiting
from users.tasks import w_next_user, w_c_user

from django.utils.html import format_html
from django.urls import reverse
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.utils import timezone
import datetime


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    date_heirarchy = (
        '-modified'
    )
    list_display = (
        'id',
        'user',
        'date',
        'time',
        'table',
        'capacity'
    )

    def get_ordering(self, request):
        return ['date']


@admin.register(Waiting)
class WaitingAdmin(admin.ModelAdmin):
    date_heirarchy = (
        '-modified'
    )
    list_display = (
        'id',
        'user',
        'no_people',
        'add_time',
    )

    def get_ordering(self, request):
        return ['add_time']
    
@admin.register(Tables)
class TablesAdmin(admin.ModelAdmin):
    date_heirarchy = (
        '-modified',
    )
    list_display = (
        'id',
        'table_id',
        'capacity',
        'is_avail',
        'user',
        'time',
        'action',
    )
    def get_ordering(self, request):
        return ['time']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<id>.+)/next/$',
                self.admin_site.admin_view(self.next_user),
                name = 'next_user',
            ),
            url(
                r'^(?P<id>.+)/allocate/$',
                self.admin_site.admin_view(self.allocate_table),
                name = 'allocate_table',
            ),
            url(
                r'^(?P<id>.+)/disallocate/$',
                self.admin_site.admin_view(self.disallocate_table),
                name = 'disallocate_table',
            ),
        ]
        return custom_urls + urls
    
    def action(self, obj):
        if Waiting.objects.filter(no_people__lte = obj.capacity).count() == 0:
            if obj.is_avail:
                return format_html(
                    '<a class="button" href="{}">Allocate table</a>',
                    reverse('admin:allocate_table', args = [obj.pk]),
                )   
            else:
                return format_html(
                    '<a class="button" href="{}">Disallocate table</a>',
                    reverse('admin:disallocate_table', args = [obj.pk]),
                )
        else:
            return format_html(
                '<a class="button" href="{}">Call Next User</a>',
                reverse('admin:next_user', args = [obj.pk]),
            )
    action.short_description = 'Action'
    action.allow_tags = True


    def allocate_table(self, request, id, *args, **kwargs):
        table = Tables.objects.get(id = id)
        table.is_avail = False
        table.time = datetime.datetime.now().time()
        table.save()
        url = reverse("admin:book_tables_changelist")
        return HttpResponseRedirect(url)


    def disallocate_table(self, request, id, *args, **kwargs):
        table = Tables.objects.get(id = id)
        table.is_avail = True
        table.time = None
        table.user = None
        table.save()
        url = reverse("admin:book_tables_changelist")
        return HttpResponseRedirect(url)

    def next_user(self, request, id, *args, **kwargs):
        table = Tables.objects.get(id = id)
        no_table = Tables.objects.filter(capacity = table.capacity).count()
        waiting = Waiting.objects.filter(no_people__lte = table.capacity ).order_by('add_time')
        
        if no_table < waiting.count():
            # Mail to Users
            next_user = waiting[0].user
            w_c_user(next_user.id, schedule = timezone.now() )
            w_next_user(waiting[no_table].user.id, r_time = 60, schedule = timezone.now())
            
            # Updating Database
            next_user = waiting[0]
            table.user = next_user.user
            table.time = datetime.datetime.now().time()
            next_user.delete()
            table.save()

        elif waiting[0]:
            next_user = waiting[0]
            w_c_user(next_user.user.id, schedule = timezone.now())
            table.user = next_user.user
            table.time = datetime.datetime.now().time()
            table.save()
            next_user.delete()

        url = reverse("admin:book_tables_changelist")
        return HttpResponseRedirect(url)



