from __future__ import division, absolute_import, unicode_literals

import re

from django.core.exceptions import ValidationError
from django import forms

class PageField(forms.CharField):
    @staticmethod
    def static_prepare_value(value):
        if isinstance(value, tuple):
            page, position = value
            return '%s%s' % (page, position)
        else:
            return value

    def prepare_value(self, value):
        return self.static_prepare_value(value)

    def clean(self, value):
        value = super(PageField, self).clean(value)
        if not value:
            return value
        mo = re.match(r'(\d+)(.*)')
        if not mo:
            raise ValidationError(
                'Sidetal skal være et heltal')
        page, position = int(mo.group(1)), mo.group(2)
