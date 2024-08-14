from django.contrib import admin
from .models import Process,Organization,Task,Activity,Log
from mptt.admin import MPTTModelAdmin,DraggableMPTTAdmin

# Register your models here.

class OrganizationModelAdmin(DraggableMPTTAdmin):
    list_display = ['id','name','parent','created_at','updated_at',]
    list_display_links = list_display
    # specify pixel amount for this ModelAdmin only:
    mptt_level_indent = 20

admin.site.register(Organization, OrganizationModelAdmin)

class ProcessAdmin(admin.ModelAdmin):
    list_display = ['id','name','created_at','updated_at',]
    list_display_links = list_display
admin.site.register(Process,ProcessAdmin)

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id','name','process','percent_completed','completed','created_at','updated_at',]
    list_display_links = list_display
admin.site.register(Task,TaskAdmin)

class ActivityAdmin(admin.ModelAdmin):
    list_display = ['id','name','activity_id','task','created_at','updated_at',]
    list_display_links = list_display
admin.site.register(Activity,ActivityAdmin)


class LogAdmin(admin.ModelAdmin):
    list_display = ['id','activity_name','task_name','created_at']
    list_display_links = list_display
admin.site.register(Log,LogAdmin)

