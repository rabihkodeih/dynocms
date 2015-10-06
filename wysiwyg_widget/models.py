from django.db import models

class WysiwygWidget(models.Model):
    order           = models.PositiveIntegerField()
    page            = models.ForeignKey('main.Page')
    html_content    = models.TextField()
    def render_html(self, request):
        return self.html_content
    class Meta:
        ordering = ('order',)
