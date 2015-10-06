'''
Created on Oct 17, 2012

@author: Rabih Kodeih
'''
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
import urllib
from contact_us.models import ContactUsWidget
from django.conf import settings


#===============================================================================
# Views
#===============================================================================

def contactpost(request):
    source_page = '/%s/' % request.META['HTTP_REFERER'].split('/')[-2]
    data = request.REQUEST
    cuw = ContactUsWidget.objects.get(pk=data['_cu_widget_id_'])
    fields = cuw.render_fields(request, True)
    success = len([f.error for f in fields if f.error != '']) == 0
    if not success:
        d = {}
        d.update(request.REQUEST)
        d['_success_'] = 'Not all input values were supplied. Please input all required values.'
        return HttpResponseRedirect('%s?%s' % (source_page,urllib.urlencode(d)))
    _subject = 'Customer Inquiry'
    _message = '----------------------------------------------\n'
    for f in fields:
        _message += '%s :\n %s' % (f.title, f.value)
        _message += '\n\n----------------------------------------------\n'
    try:
        if settings.PRODUCTION:
            send_mail(subject=_subject,
                      message=_message,
                      from_email=cuw.sender_email,
                      recipient_list=[cuw.sender_email],
                      fail_silently=False,
                      auth_user=cuw.sender_email,
                      auth_password=cuw.sender_password)
    except:
        d = {}
        d.update(request.REQUEST)
        d['_success_'] = 'No email could be sent due to an internal server error. Please contact your system administrator.'
        return HttpResponseRedirect('%s?%s' % (source_page,urllib.urlencode(d)))
    return HttpResponseRedirect('/%s/' % cuw.success_slug)




