from __future__ import division, absolute_import, unicode_literals

import re
import os.path
import tempfile
import textwrap
import subprocess

from django.http import HttpResponse


class TexException(Exception):
    def __str__(self):
        raw = self.args[0]
        mo = re.search(r'^! (.*)\n(?:l\.\d+ )(.*)', raw, re.M)
        if mo:
            return '%s %s' % (mo.group(1), mo.group(2))
        else:
            return 'Unknown TeX error. %s' % raw


def pdflatex(data):
    source = textwrap.dedent(r"""
    \documentclass[article,oneside,a4paper]{memoir}
    \usepackage[sc]{mathpazo}
    \usepackage[final]{microtype}
    \usepackage{multicol}
    \usepackage[utf8]{inputenc}
    \usepackage{amsmath}
    \catcode`<=\active
    \def<#1>{${}^{\text{#1}}$}
    \def\b{${}^\mathrm{b}$}
    \begin{document}
    \tableofcontents*
    \clearpage
    %s
    \end{document}
    """.strip()) % (data,)
    with tempfile.TemporaryDirectory() as directory:
        tex_filename = os.path.join(directory, 'document.tex')
        pdf_filename = os.path.join(directory, 'document.pdf')
        with open(tex_filename, 'w') as fp:
            fp.write(source)
        pp = subprocess.Popen(
            ['latexmk', '-pdf', '-latexoption=-interaction nonstopmode',
             'document.tex'],
            cwd=directory, universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with pp:
            result = pp.stdout.read()
            exitcode = pp.wait()
        if exitcode != 0:
            raise TexException(result)
        with open(pdf_filename, 'rb') as fp:
            return fp.read()


def render_pdf(data):
    try:
        pdf_contents = pdflatex(data)
        return HttpResponse(pdf_contents, content_type='application/pdf')
    except TexException as e:
        return HttpResponse(
            e.args[0], content_type='text/plain', status=500)
