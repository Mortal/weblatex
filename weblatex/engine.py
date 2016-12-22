from __future__ import division, absolute_import, unicode_literals

import re
import os.path
import tempfile
import textwrap
import subprocess

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe


class TexException(Exception):
    def __str__(self):
        raw = self.args[0]
        mo = re.search(r'^! (.*)\n(?:l\.\d+ )(.*)', raw, re.M)
        if mo:
            return '%s %s' % (mo.group(1), mo.group(2))
        else:
            return 'Unknown TeX error. %s' % raw


def render_tex(data, page_size=None, chords=False, font_size=None):
    context = dict(
        document=mark_safe(data),
        page_size=page_size,
        chords=chords,
        font_size=font_size,
    )
    template = get_template('weblatex/booklet.tex')
    source = template.render(context)
    return source


def pdflatex(source, files):
    with tempfile.TemporaryDirectory() as directory:
        tex_filename = os.path.join(directory, 'document.tex')
        pdf_filename = os.path.join(directory, 'document.pdf')
        with open(tex_filename, 'w') as fp:
            fp.write(source)
        for filename, f in files:
            with open(os.path.join(directory, filename), 'wb') as fp:
                f.open('rb')
                fp.write(f.read())
        pp = subprocess.Popen(['latexmk', '-pdf', 'document.tex'],
            cwd=directory, universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with pp:
            result = pp.stdout.read()
            exitcode = pp.wait()
        if exitcode != 0:
            raise TexException(result)
        with open(pdf_filename, 'rb') as fp:
            return fp.read()


def render_pdf(*args, **kwargs):
    files = kwargs.pop('files', ())
    try:
        source = render_tex(*args, **kwargs)
        pdf_contents = pdflatex(source, files)
        return HttpResponse(pdf_contents, content_type='application/pdf')
    except TexException as e:
        return HttpResponse(
            e.args[0], content_type='text/plain', status=500)
