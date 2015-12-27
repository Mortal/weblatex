from __future__ import division, absolute_import, unicode_literals

import re

from django.core.exceptions import ValidationError
from django import forms


class PageField(forms.CharField):
    @staticmethod
    def position_to_str(coordinate):
        return ''.join(('v%s' % x1 if x1 else '') +
                       ('h%s' % x2 if x2 else '')
                       for x1, x2 in coordinate)

    @staticmethod
    def static_prepare_value(value):
        if isinstance(value, tuple):
            page, coordinate = value
            if isinstance(coordinate, str):
                s = coordinate
            else:
                s = self.position_to_str(coordinate)
            return '%s%s' % (page, s)
        else:
            return value

    def prepare_value(self, value):
        return self.static_prepare_value(value)

    def clean(self, value):
        value = super(PageField, self).clean(value)
        if not value:
            return value
        mo = re.match(r'(\d+)(.*)', value)
        if not mo:
            raise ValidationError(
                'Sidetal skal være et heltal')
        page, position = int(mo.group(1)), mo.group(2)
        pattern = r'(v\d+)?(h\d+)?'
        p2 = r'^(%s)+$' % pattern
        if not re.match(p2, position):
            raise ValidationError(
                'Sidetal skal være et heltal')
        coordinate = []
        if position:
            for mo in re.finditer(pattern, position):
                x1 = int(mo.group(1)[1:]) if mo.group(1) else None
                x2 = int(mo.group(2)[1:]) if mo.group(2) else None
                coordinate.append((x1, x2))
        return (page, tuple(coordinate))
