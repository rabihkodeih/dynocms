'''
Created on Feb 23, 2012

@author: Rabih Kodeih
'''
from django.shortcuts import render_to_response
from functools import wraps
from django.http import HttpResponse
from django.utils import simplejson
from django.template.context import RequestContext

def rendersTemplate(template):
    '''
    Decorator for template rendering
    '''
    def decorator(func):
        @wraps(func)
        def innerClosure(*args, **kws):
            res = func(*args, **kws)
            request = args[0]
            if res.__class__ == dict:
                return render_to_response(template, res, RequestContext(request))
            return res
        return innerClosure
    return decorator

def ajaxPostRequest(func):
    '''
    Decorator for ajax post request
    '''
    @wraps(func)
    def innerClosure(request):
        if request.is_ajax() and request.method == 'POST':
            return HttpResponse(simplejson.dumps(func(request)), 'application/javascript')
        return {}
    return innerClosure

def apiPostRequest(func):
    '''
    Decorator for normal form-based post request
    '''
    @wraps(func)
    def innerClosure(request):
        if request.method == 'POST':
            return HttpResponse(simplejson.dumps(func(request)), 'application/javascript') 
        return {}
    return innerClosure