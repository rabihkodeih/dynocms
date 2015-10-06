'''
Created on Nov 8, 2011

@author: Rabih Kodeih
'''

from django.contrib import admin
#from main.models import ToolBox, Plier, Hammer, Nail

from main.models import Page, TopMenuItem, GenericWidget,\
    SiteParameters, TopMenu, FooterMenuItem, FooterMenu, PageLayout, File, Macro
from singleton_models.admin import SingletonModelAdmin
from dynocms.custom.custom_widgets import AdminImageWidgetAdmin


#===============================================================================
# Utils
#===============================================================================
def imagify_layout_pair(url, filep, height):
    return '<img src="%s" alt="%s" style="max-height:%s;">' % (url, filep, height)    

def imagify_layout(obj, height="100px"):
    try:
        return imagify_layout_pair(obj.url, obj.file, height)
    except Exception as ex:
        try:
            return imagify_layout_pair(obj.url, '', height)
        except:
            return str(ex)

def imagify_file(obj):
    return '<img src="%s" style="max-height:100px;">' % obj.url    


#===============================================================================
# Admin Classes
#===============================================================================
    
class GenericWidgetInline(admin.TabularInline):
    model = GenericWidget
    extra = 0

class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = []
    list_display = ('title',)
    def layout_image(self, obj):
        return imagify_layout(obj.layout.image)  
    layout_image.short_description = 'Layout image'
    layout_image.allow_tags = True
    readonly_fields = ('layout_image',)
    search_fields = ('slug', 'title')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'layout', 'column_widths', 'layout_image')
        }),
        ('Viewing Permissions', {
            'classes': ('collapse',),
            'fields': ('user_viewers', 'group_viewers')
        }),
    )

class TopMenuItemInline(admin.TabularInline):
    model = TopMenuItem
    extra = 0

class TopMenuAdmin(SingletonModelAdmin):
    inlines = [TopMenuItemInline,]

class FooterMenuItemInline(admin.TabularInline):
    model = FooterMenuItem
    extra = 0
    
class FooterMenuAdmin(SingletonModelAdmin):
    inlines = [FooterMenuItemInline,]

class PageLayoutAdmin(AdminImageWidgetAdmin):
    def image_img(self, obj):
        return imagify_layout(obj.image, "50px")
    image_img.short_description = 'Layout'
    image_img.allow_tags = True
    list_display = ('name', 'image_img',)

class FileAdmin(AdminImageWidgetAdmin):
    def preview(self, obj):
        return imagify_file(obj.file)
    preview.allow_tags = True
    def name(self, obj):
        return str(obj.file).split('/')[-1]
    name.allow_tags = True
    list_display = ('name', 'preview')
    search_fields = ('file',)

class SiteParametersAdmin(SingletonModelAdmin, AdminImageWidgetAdmin):
    fieldsets = (
        (None, {
            'fields': ('subheader', 'logo_image', 'logo_template', 'footer', 'default_page_slug')
        }),
        ('Theme html', {
            'classes': ('collapse',),
            'fields': ('theme_html',)
        }),
        ('Theme css', {
            'classes': ('collapse',),
            'fields': ('theme_css',)
        }),
    )

#===============================================================================
# Widget Registry
#===============================================================================
widget_registry = []

def register_widget(widget_model, widget_admin_inline):
    widget_registry.append(widget_model) 
    PageAdmin.inlines.append(widget_admin_inline)

register_widget(GenericWidget, GenericWidgetInline)


#===============================================================================
# Admin Registration
#===============================================================================
admin.site.register(Page, PageAdmin)
admin.site.register(SiteParameters, SiteParametersAdmin)
admin.site.register(TopMenu, TopMenuAdmin)
admin.site.register(FooterMenu, FooterMenuAdmin)
admin.site.register(PageLayout, PageLayoutAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Macro)








