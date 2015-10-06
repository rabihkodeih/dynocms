from django.contrib import admin
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect


class SingletonModelAdmin(admin.ModelAdmin):

    change_form_template = "admin/singleton_models/change_form.html"
    
    def has_add_permission(self, request):
        """ Singleton pattern: prevent addition of new objects """
        return False
    
    def has_delete_permission(self, request, obj=None):
        """ Singleton pattern: hide deletion button in singleton form """
        return False
     
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(SingletonModelAdmin, self).get_urls()

        # _meta.model_name only exists on Django>=1.6 -
        # on earlier versions, use module_name.lower()
        try:
            model_name = self.model._meta.model_name
        except AttributeError:
            model_name = self.model._meta.module_name.lower()

        self.model._meta.verbose_name_plural = self.model._meta.verbose_name
        url_name_prefix = '%(app_name)s_%(model_name)s' % {
            'app_name': self.model._meta.app_label,
            'model_name': model_name,
        }
        custom_urls = patterns('',
            url(r'^history/$',
                self.admin_site.admin_view(self.history_view),
                {'object_id': '1'},
                name='%s_history' % url_name_prefix),
            url(r'^$',
                self.admin_site.admin_view(self.change_view),
                {'object_id': '1'},
                name='%s_change' % url_name_prefix),
        )
        # By inserting the custom URLs first, we overwrite the standard URLs.
        return custom_urls + urls    
  
        
    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        opts = obj._meta #@UnusedVariable

        msg = _('%(obj)s was changed successfully.') % {'obj': force_unicode(obj)}
        if request.POST.has_key("_continue"):
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            return HttpResponseRedirect("../../")
            
    def change_view(self, request, object_id, extra_context=None):
        if object_id=='1':
            self.model.objects.get_or_create(pk=1)
        return super(SingletonModelAdmin, self).change_view(
            request,
            object_id,
            extra_context=extra_context,
        )

