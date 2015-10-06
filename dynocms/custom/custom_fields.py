'''
Created on Oct 20, 2012

@author: Rabih Kodeih
'''
from django.db import models
from django.forms.widgets import Textarea

class models_TextField(models.TextField):
    description = "A normal text field with modifyable rows and columns."
    __metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        self.rows = kwargs.get('rows', 10)
        self.cols = kwargs.get('cols', 85) 
        if 'rows' in kwargs: kwargs.pop('rows')
        if 'cols' in kwargs: kwargs.pop('cols')
        return super(models_TextField, self).__init__(*args, **kwargs)
    
    def formfield(self, **kwargs):
        kwargs.update({"widget": Textarea(attrs={'rows':self.rows, 'cols':self.cols})})
        return super(models_TextField, self).formfield(**kwargs)



class models_FileEditorField(models_TextField):
    description = "A text field which keeps its content synchronized to a file specified in a path."
    __metaclass__ = models.SubfieldBase
    def __init__(self, *args, **kwargs):
        self.path = kwargs.get('path', '/')
        if 'path' in kwargs: kwargs.pop('path')
        kwargs['null']=True
        kwargs['blank']=True
        return super(models_FileEditorField, self).__init__(*args, **kwargs)

    def value_from_object(self, obj):
        return open(self.path).read()

    def save_form_data(self, instance, data):
        f = open(self.path, 'wb')
        f.write(data)



