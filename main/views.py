# Create your views here.
from common.djdecorators import rendersTemplate
from main.models import TopMenuItem, SiteParameters, FooterMenuItem, Page
from django.views.decorators.cache import never_cache
from django.template.loader import render_to_string
from django.template.base import Template
from django.template.context import Context
from main.admin import widget_registry
from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME, logout as auth_logout,\
    authenticate
from django.contrib.admin.forms import ERROR_MESSAGE
from django.contrib.auth import get_user
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User


#===============================================================================
# Utils
#===============================================================================

def render_subheader():
    try:
        return SiteParameters.objects.get(id=1).subheader
    except:
        return '<p style="color:red;">-- subheader text not defined yet --</p>'

def render_footer():
    try:
        return SiteParameters.objects.get(id=1).footer
    except:
        return '<span style="color:red;">-- footer text not defined yet --</span>'

def render_content_template(request, user):
    slug = request.path.replace('/', '')
    pages = Page.objects.filter(slug=slug)
    if len(pages) == 0: return render_to_string('template404.html', {})
    page = pages[0]
    if not page.can_view(user): return render_to_string('template403.html', {})
    template = Template(page.layout.template)
    context = {}
    col_widths = page.column_widths.split('-')
    for w in zip(range(1, len(col_widths) + 1), col_widths):
        context['COLUMN_%s' % w[0]] = 'column%s' % w[1]
    all_widgets = []
    for widget_model in widget_registry:
        all_widgets.extend(widget_model.objects.filter(page=page))
    all_widgets.sort(key=lambda x: x.order)
    for w in zip(range(1, len(all_widgets) + 1), all_widgets):
        context['SLOT_%s' % w[0]] = w[1].render_html(request)
    return template.render(Context(context))

def render_logo():
    try:
        template = SiteParameters.objects.get(pk=1).logo_template
        #path = STATIC_URL + SiteParameters.objects.get(pk=1).logo_image.url.split('/')[-1]
        path = SiteParameters.objects.get(pk=1).logo_image.url
        return Template(template).render(Context({'LOGO_PATH': path}))
    except:
        return '<span style="color:red;">-- logo has not been uploaded yet --</span>'


def filter_items(items, user):
    res = []
    for item in items:
        page = item.page
        if page.can_view(user): res.append(item)
    return res
    

#===============================================================================
# Views
#===============================================================================

@never_cache
@rendersTemplate('base.html')
def process_page(request):
    user = get_user(request)
    LOGO = render_logo()
    SUB_HEADER = render_subheader()
    CONTENT_TEMPLATE = render_content_template(request, user)
    FOOTER = render_footer()
    TOPMENU_ITEMS = filter_items(TopMenuItem.objects.order_by('order'), user)
    FTRMENU_ITEMS = filter_items(FooterMenuItem.objects.order_by('order'), user)
    USER_NAME = user.username
    SLUG = str(request.path.replace('/', ''))
    return locals()



class MyAdminAuthenticationForm(AuthenticationForm):
    this_is_the_login_form = forms.BooleanField(widget=forms.HiddenInput, initial=1,
        error_messages={'required': ugettext_lazy("Please log in again, because your session has expired.")})
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        message = ERROR_MESSAGE

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                if u'@' in username:
                    # Mistakenly entered e-mail address instead of username? Look it up.
                    try:
                        user = User.objects.get(email=username)
                    except (User.DoesNotExist, User.MultipleObjectsReturned):
                        # Nothing to do here, moving along.
                        pass
                    else:
                        if user.check_password(password):
                            message = _("Your e-mail address is not your username."
                                        " Try '%s' instead.") % user.username
                raise forms.ValidationError(message)
            elif not self.user_cache.is_active:
                raise forms.ValidationError(message)
        self.check_for_test_cookie()
        return self.cleaned_data

@never_cache
def my_login(request, extra_context=None):
    from django.contrib.auth.views import login
    context = {
        'title': 'Log in',
        'app_path': request.get_full_path(),
        REDIRECT_FIELD_NAME: get_default_app_path(request),
    }
    context.update(extra_context or {})
    defaults = {
        'extra_context': context,
        'current_app': 'AppName',
        'authentication_form': MyAdminAuthenticationForm,
        'template_name': 'admin/login.html',
    }
    return login(request, **defaults)

@never_cache
def my_logout(request, extra_context=None):
    auth_logout(request)
    return HttpResponseRedirect(get_default_app_path(request))


def get_default_app_path(request):
    slug = SiteParameters.objects.all()[0].default_page_slug
    return '/%s/' % slug

def process_empty_slug(request):
    return HttpResponseRedirect(get_default_app_path(request))








