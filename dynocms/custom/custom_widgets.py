from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
import os
from django.db.models.fields.files import ImageField, FileField
from django.conf import settings

class AdminImageWidgetAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if type(db_field) == ImageField or type(db_field) == FileField:
            request = kwargs.pop("request", None) #@UnusedVariable
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(AdminImageWidgetAdmin,self).formfield_for_dbfield(db_field, **kwargs)

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            path_name = str(value)
            file_name = path_name.split('/')[-1]
            image_url = os.path.join(settings.MEDIA_URL, path_name)
            output.append(u'<img src="%s" alt="%s" /><br><br>' % (image_url, file_name))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


# class FileAdmin(AdminImageWidgetAdmin):
#     def preview(self, obj):
#         return imagify_file(obj.file)
#     preview.allow_tags = True
#     def name(self, obj):
#         return str(obj.file).split('/')[-1]
#     name.allow_tags = True
#     list_display = ('name', 'preview')
#     search_fields = ('file',)
# 
# class File(models.Model):
#     file            = models.FileField('File', upload_to='uploaded_files/')
#     def __unicode__(self):
#         return self.file.path
