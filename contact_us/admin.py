'''
Created on Oct 17, 2012

@author: Rabih Kodeih
'''

from django.contrib import admin
from contact_us.models import ContactUsWidget, ContactUsField
from main.admin import register_widget


#===============================================================================
# Admin Classes
#===============================================================================

class ContactUsFieldInline(admin.TabularInline):
    model = ContactUsField
    extra = 0
    prepopulated_fields = {'name': ('title',)}

class ContactUsWidgetInline(admin.TabularInline):
    model = ContactUsWidget
    extra = 0
    def settings(self, obj):
        if obj.id:
            return '<a style="font-weight:bold; color:red;" href="/admin/contact_us/contactuswidget/%s/">edit settings ...</a>' % obj.id
        return '(none)'
    settings.allow_tags = True
    fields = ('order', 'settings')
    readonly_fields = ('settings',)
    

class ContactUsWidgetAdmin(admin.ModelAdmin):
    inlines = [ContactUsFieldInline,]
    fieldsets = (
        (None, {
            'fields': ('order', 'page', 'textbox_rows', 'textbox_cols', 'short_input_width', 'long_input_width',
                       'success_slug')
        }),
        ('Email Settings', {
            'classes': ('collapse',),
            'fields': ('subject', 'sender_email', 'sender_password')
        }),
        ('Template', {
            'classes': ('collapse',),
            'fields': ('template',)
        }),
    )


#===============================================================================
# Widget Registration
#===============================================================================
register_widget(ContactUsWidget, ContactUsWidgetInline)


#===============================================================================
# Admin Registration
#===============================================================================
admin.site.register(ContactUsWidget, ContactUsWidgetAdmin)

