from __future__ import division, absolute_import, unicode_literals

import os.path
import tempfile
import textwrap
import subprocess

from django.views.generic import TemplateView, View, FormView
from django.http import HttpResponse

from weblatex.forms import BookletForm


class Booklet(FormView):
    form_class = BookletForm
    template_name = 'weblatex/booklet.html'

    def form_valid(self, form):
        data = '\n'.join(song.as_tex() for song in form.cleaned_data['songs'])
        source = textwrap.dedent(r"""
        \documentclass[article,oneside,a4paper]{memoir}
        \usepackage[sc]{mathpazo}
        \usepackage[final]{microtype}
        \usepackage[utf8]{inputenc}
        \begin{document}
        \tableofcontents*
        %s
        \end{document}
        """.strip()) % (data,)
        return render_pdf(source)


class InputView(TemplateView):
    template_name = 'weblatex/input.html'


class TexException(Exception):
    pass


def pdflatex(source):
    with tempfile.TemporaryDirectory() as directory:
        tex_filename = os.path.join(directory, 'document.tex')
        pdf_filename = os.path.join(directory, 'document.pdf')
        with open(tex_filename, 'w') as fp:
            fp.write(source)
        with subprocess.Popen(['latexmk', '-pdf',
            '-latexoption=-interaction nonstopmode', 'document.tex'],
            cwd=directory, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT) as pp:
            result = pp.stdout.read()
            exitcode = pp.wait()
        if exitcode != 0:
            raise TexException(result)
        with open(pdf_filename, 'rb') as fp:
            return fp.read()


def render_pdf(source):
    try:
        pdf_contents = pdflatex(source)
        return HttpResponse(pdf_contents, content_type='application/pdf')
    except TexException as e:
        return HttpResponse(
            e.args[0], content_type='text/plain', status=500)


class RenderView(View):
    def post(self, request):
        self.request = request

        data = request.POST['data']

        source = """
        \\documentclass[article,oneside,a4paper]{memoir}
        \\usepackage[sc]{mathpazo}
        \\usepackage[final]{microtype}
        \\begin{document}
        %s
        \\end{document}
        """ % data

        return render_pdf(source)
