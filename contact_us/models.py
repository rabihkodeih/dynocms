'''
Created on Oct 17, 2012

@author: Rabih Kodeih
'''

from django.db import models
from dynocms.custom.custom_fields import models_TextField
from django.template.base import Template
from django.template.context import Context


DEFAULT_TEMPLATE =\
'''
<style>
.contact {
/*     width:90%; */
    margin-top: 15px;
    margin-left: auto;
    margin-right: auto;
    color: #666;
}
.contact .form {
    font-size: 95%;
}
.contact .form .redstar {
    color: red;
    font-size: 118%;
}
.contact .form .short_input {
    width: {{ CIW }};
}
.contact .form .long_input {
    width: {{ LIW }};
}
</style>

<div class="contact">
    <div class="form">
        <span class="redstar">{{ERROR_MESSAGE}}</span>
        <form name="contact-form" action="/contactpost/" method="post">
            {% for field in FIELDS %}
                {% if field.type = 'short input' %}
                    <p>{{ field.title }}: {% if field.is_required %}<span class="redstar">* {{ field.error }}{% endif %}</span><br><input type="text"
                        class="short_input" name="{{ field.name }}" value="{{ field.value }}"/></p>
                {% elif field.type = 'long input' %}
                    <p>{{ field.title }}: {% if field.is_required %}<span class="redstar">* {{ field.error }}{% endif %}</span><br><input type="text"
                        class="long_input" name="{{ field.name }}" value="{{ field.value }}"/></p>
                {% elif field.type = 'text box' %}
                    <p>{{ field.title }}: {% if field.is_required %}<span class="redstar">* {{ field.error }}{% endif %}</span><br><textarea name="{{ field.name }}"
                        rows="{{ TB_ROWS }}" cols="{{ TB_COLS }}">{{ field.value }}</textarea></p>
                {% endif %}
            {% endfor %}
            <input type="submit" value="Send"/> <input type="reset" value="Reset">
            <input type="hidden" value="{{ CUW_ID }}" name="_cu_widget_id_">
        </form>
        <br>        
    </div>
</div>
'''

class ContactUsWidget(models.Model):
    order               = models.PositiveIntegerField()
    page                = models.ForeignKey('main.Page')
    textbox_rows        = models.CharField(max_length=10, default='12')
    textbox_cols        = models.CharField(max_length=10, default='60')
    short_input_width   = models.CharField(max_length=100, default='200px')
    long_input_width    = models.CharField(max_length=100, default='350px')
    success_slug        = models.CharField(max_length=100, default='home')
    subject             = models.CharField(max_length=100, default='Customer Inquiry')
    sender_email        = models.CharField(max_length=100)
    sender_password     = models.CharField(max_length=100)
    template            = models_TextField(rows=30, cols=140, default=DEFAULT_TEMPLATE)
    def render_fields(self, request, is_post=False):
        data = request.GET if not is_post else request.REQUEST
        fields = self.fields.all().order_by('order')
        for f in fields:
            f.value = data[f.name] if f.name in data else ''
            f.error = f.error_message if f.value == '' and f.is_required and ('_success_' in data or is_post) else '' 
        return fields
    def render_html(self, request):
        data = request.GET
        fields = self.render_fields(request)
        template = Template(self.template)
        context_map = {'ERROR_MESSAGE': data['_success_'] if '_success_' in data else '',
                       'FIELDS': fields,
                       'TB_ROWS': self.textbox_rows, 'TB_COLS': self.textbox_cols,
                       'CIW': self.short_input_width, 'LIW':self.long_input_width,
                       'CUW_ID': self.id}
        return template.render(Context(context_map))
#        return render_to_string('contact_us.html', context_map)
    class Meta:
        ordering = ('order',)
    def __unicode__(self):
        return 'Contact Us Widget %d in page "%s"' % (self.id, self.page.title)
        
        
type_choices = (('short input', 'short input'), ('long input','long input'), ('text box', 'text box'))

class ContactUsField(models.Model):
    order               = models.PositiveIntegerField()
    contact_us_widget   = models.ForeignKey('ContactUsWidget', related_name='fields')
    title               = models.CharField(max_length=100)
    name                = models.SlugField(max_length=100, unique=True)
    is_required         = models.BooleanField(default=True)
    error_message       = models.CharField(max_length=300, default='this value is required')
    type                = models.CharField(max_length=20, choices=type_choices, default='short input')
    class Meta:
        ordering = ('order',)







