'''
Created on Oct 23, 2012

@author: Rabih Kodeih
'''
from django.contrib import admin
from wysiwyg_widget.models import WysiwygWidget
from main.admin import register_widget

class WysiwygWidgetInline(admin.TabularInline):
    model = WysiwygWidget
    extra = 0
    def settings(self, obj):
        if obj.id:
            return '<a style="font-weight:bold; color:red;" href="/admin/wysiwyg_widget/wysiwygwidget/%s/">edit content ...</a>' % obj.id
        return '(none)'
    settings.allow_tags = True
    fields = ('order', 'settings')
    readonly_fields = ('settings',)

class WysiwygWidgetAdmin(admin.ModelAdmin):
    change_form_template = 'admin/change_form_custom.html'


#===============================================================================
# Widget Registration
#===============================================================================
register_widget(WysiwygWidget, WysiwygWidgetInline)


#===============================================================================
# Admin Registration
#===============================================================================
admin.site.register(WysiwygWidget, WysiwygWidgetAdmin)

