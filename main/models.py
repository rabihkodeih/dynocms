from django.db import models
from singleton_models.models import SingletonModel
from django.db.models import signals
from django.contrib.admin import models as admin_models
from django.template.loader import render_to_string
from contact_us.models import ContactUsWidget, ContactUsField
from dynocms.custom.custom_fields import models_TextField, models_FileEditorField
import os
from django.conf import settings
from django.template.base import Template
from django.template.context import Context
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete
from django.contrib.auth.models import User, Group


#===============================================================================
# Models
#===============================================================================

class OrderedModel(models.Model):
    order           = models.PositiveIntegerField()
    class Meta:
        ordering = ('order',)

theme_paths = {
    'css' : os.path.join(os.path.dirname(__file__), 'static/css/main.css').replace(os.sep,'/'),
    'html': os.path.join(os.path.dirname(__file__), 'templates/base.html').replace(os.sep,'/')
}
 
class SiteParameters(SingletonModel):
    subheader           = models_TextField(rows=3, cols=100)
    footer              = models_TextField(rows=3, cols=100)
    logo_image          = models.ImageField('Logo Image', upload_to='uploaded_files/')
    logo_template       = models_TextField(rows=3, cols=100)
    default_page_slug   = models.CharField(max_length=100, default='home')
    
    theme_html          = models_FileEditorField(path=theme_paths['html'], rows=100, cols=125)
    theme_css           = models_FileEditorField(path=theme_paths['css'], rows=100, cols=125)
    
    def __unicode__(self):
        return u'Site parameters'

    def save(self, *args, **kwargs):
        if settings.PRODUCTION:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dynocms.settings")
            from django.core.management import execute_from_command_line
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        super(SiteParameters, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Site parameters"
        verbose_name_plural = "Site parameters"
          
            
class PageLayout(models.Model):
    name            = models.CharField(max_length=100, unique=True)
    image           = models.ImageField('Layout', upload_to='layout_images/')
    template        = models_TextField(rows=25, cols=100)
    def __unicode__(self):
        return self.name



class Page(models.Model):
    title           = models.CharField(max_length=100)
    slug            = models.SlugField(max_length=100, unique=True)
    layout          = models.ForeignKey('PageLayout')
    column_widths   = models.CharField(max_length=100)
    user_viewers    = models.ManyToManyField(User, blank=True, null=True)
    group_viewers   = models.ManyToManyField(Group, blank=True, null=True)
    def __unicode__(self):
        return self.title
    def can_view(self, user):
        ok_users = self.user_viewers.all()
        if user in ok_users: return True
        ok_groups = self.group_viewers.all()
        groups = user.groups.all()
        for group in ok_groups:
            if group.name == "Everyone": return True
            if group in groups: return True
        return False



class TopMenu(SingletonModel):
    def __unicode__(self):
        return 'Top menu'
    class Meta:
        verbose_name = 'Top menu'
        verbose_name_plural = 'Top menu'


class TopMenuItem(OrderedModel):
    page            = models.ForeignKey('Page')
    menu            = models.ForeignKey('TopMenu')


# class FooterMenu(models.Model):
#     def __unicode__(self):
#         return 'Footer menu'
#     class Meta:
#         verbose_name = 'Footer menu'
#         verbose_name_plural = 'Footer menu'
class FooterMenu(SingletonModel):
    def __unicode__(self):
        return 'Footer menu'
    class Meta:
        verbose_name = 'Footer menu'
        verbose_name_plural = 'Footer menu'


class FooterMenuItem(OrderedModel):
    page            = models.ForeignKey('Page')
    menu            = models.ForeignKey('FooterMenu')

class File(models.Model):
    file            = models.FileField('File', upload_to='uploaded_files/')
    def __unicode__(self):
        return self.file.path

@receiver(pre_delete, sender=File)
def _File_delete(sender, instance, **kwargs):
    try:
        os.remove(instance.file.path)
    except:
        pass

class Macro(models.Model):
    name            = models.CharField(max_length=100)
    definition      = models_TextField(default="{% macro <PART NAME> <ARGUMENTS> %}\n<MACRO DEFINITION>\n{% endmacro %}")
    def __unicode__(self):
        return self.name

class GenericWidget(OrderedModel):
    page            = models.ForeignKey('Page')
    html_content    = models_TextField(rows=10, cols=110)
    def render_html(self, request):
        macros = Macro.objects.all()
        res = '\n'
        for m in macros:
            res += m.definition + '\n'
        template_str = '{% load macros %}\n' + res + self.html_content
        return Template(template_str).render(Context({'MEDIA': '%s/uploaded_files/' % settings.MEDIA_URL}))
    

#===============================================================================
# Post Syncdb Signal
#===============================================================================

def model_init_handler(sender, **kwargs):
    if sender != admin_models: return
    layouts = PageLayout.objects.all()
    if len(layouts) != 0: return
    print '\n\n ** initializing built-in layouts ** \n\n'
    values =\
        ('One_Column',           
         'Three_Columns',        
         'Three_Rows',           
         'Two_Columns',          
         'Two_Rows',             
         'Two_Columns_Two_Rows', 
         'Left_Column_Two_Rows', 
         'Right_Column_Two_Rows',
         'Bottom_Row_Two_Columns')
    bi_template_tags = {'%s_%s' % (token, i) :'{{ %s_%s%s }}' % (token, i, '|safe' if token == 'SLOT' else '')
                        for i in range(1, 51) for token in ('COLUMN', 'SLOT')}
    for value in values:
        layout = PageLayout()
        layout.name = value.replace('_', ' ')
        layout.template = render_to_string('builtin_layouts/%s.html' % value.lower(), bi_template_tags)
        layout.image = "layout_images/%s.png" % value.lower()
        layout.save()

    print '\n\n ** creating default users and groups ** \n\n'
    User.objects.create_user('rabih', 'rabih@idlts.com', 'rabih')
    everyone = Group(name="Everyone")
    everyone.save()
    Group(name="Employees").save()

    print '\n\n ** initializing built-in pages ** \n\n'
    topmenu = TopMenu.objects.get_or_create(pk=1)[0]
    footermenu = FooterMenu.objects.get_or_create(pk=1)[0]
    order=1
    pages = ('Home', 'About-Us', 'Our-Services', 'Our-Products',
             'Customer-Assistance', 'Our-Policies', 'Job-Vacancies', 'Contact-Us')
    for p in pages:
        page = Page()
        page.title = p.replace('-', ' ')
        page.slug = p.lower()
        if page.title == 'About Us':
            page.layout = PageLayout.objects.get(name='Left Column Two Rows') 
            page.column_widths = '30-70'
            page.save()
            GenericWidget(order=1, html_content=render_to_string('default_content/slot_1.html'), page=page).save()
            GenericWidget(order=2, html_content=render_to_string('default_content/slot_2.html'), page=page).save()
            GenericWidget(order=3, html_content=render_to_string('default_content/slot_3.html'), page=page).save()
        elif page.title == 'Home':
            page.layout = PageLayout.objects.get(name='Bottom Row Two Columns')
            page.column_widths = '40-60-100'
            page.save()
            GenericWidget(order=1, html_content=render_to_string('default_content/slot_def.html'), page=page).save()
            GenericWidget(order=2, html_content=render_to_string('default_content/slot_def.html'), page=page).save()
            GenericWidget(order=3, html_content=render_to_string('default_content/slot_def.html'), page=page).save()
        elif page.title == 'Contact Us':
            page.layout = PageLayout.objects.get(name='Three Rows') 
            page.column_widths = '100'
            page.save()
            GenericWidget(order=1, html_content=render_to_string('default_content/cu_slot_1.html',
                        context_instance=Context({'MEDIA': '{{ MEDIA }}',
                                                  'MACRO': '{% usemacro image "trademarks.png" width="650px;" %}'})),
                          page=page).save()
            GenericWidget(order=3, html_content=render_to_string('default_content/cu_slot_3.html'), page=page).save()
            widget2 = ContactUsWidget(order=2, page=page, success_slug="contact-success",
                                      sender_email="akodeih@idlts.com", sender_password='password')
            widget2.save()
            ContactUsField(order=1, contact_us_widget=widget2, title='First Name', name='first-name', type='short input').save()
            ContactUsField(order=2, contact_us_widget=widget2, title='Last Name', name='last-name', type='short input').save()
            ContactUsField(order=3, contact_us_widget=widget2, title='Company Name', name='company-name',type='long input').save()
            ContactUsField(order=4, contact_us_widget=widget2, title='Address', name='address',type='long input').save()
            ContactUsField(order=5, contact_us_widget=widget2, title='City', name='city',type='short input').save()
            ContactUsField(order=6, contact_us_widget=widget2, title='Phone Number', name='phone-number',type='short input').save()
            ContactUsField(order=7, contact_us_widget=widget2, title='Mobile Number', name='mobile-number',type='short input').save()
            ContactUsField(order=8, contact_us_widget=widget2, title='Email', name='email',type='long input').save()
            ContactUsField(order=9, contact_us_widget=widget2, title='Message', name='message',type='text box').save()
        else:
            page.layout = PageLayout.objects.get(name='One Column') 
            page.column_widths = '35'
            page.save()
            GenericWidget(order=1, html_content=render_to_string('default_content/slot_def.html'), page=page).save()
        page.group_viewers.add(everyone)
        page.save()
        tm_item = TopMenuItem(page=page, menu=topmenu, order=order)
        tm_item.save()
        fm_item = FooterMenuItem(page=page, menu=footermenu, order=order)
        fm_item.save()
        order += 1

    page = Page()
    p = 'Contact-Success'
    page.title = p.replace('-', ' ')
    page.slug = p.lower()
    page.layout = PageLayout.objects.get(name='One Column') 
    page.column_widths = '100'
    page.save()
    GenericWidget(order=1, html_content=render_to_string('default_content/cu_success.html'), page=page).save()
    
    File(file="uploaded_files/trademarks.png").save()
    Macro(name="Image", definition='{% macro image filename width="auto" height="auto" %}\n<img src="{{ MEDIA }}{{ filename }}" width={{ width }} height={{ height }} border="1px;">\n{% endmacro %}').save()

    params = SiteParameters.objects.get_or_create(pk=1)[0]
    params.subheader = '<p class="subheader">Metering Systems and Solutions</p>'
    params.footer = '<span style="font-size: 12px;">&copy;</span> 2012 Ideal Technical Solutions Co. Ltd. - All rights reserved'
    params.logo_image = "uploaded_files/logo.png"
    params.logo_template = '<img src="{{ LOGO_PATH }}" height="100" border="0">'
    params.save()

signals.post_syncdb.connect(model_init_handler)

    
# NOTE: think of some nice little design of a news feed widget (which has its own template and some javascript embedded as well)




