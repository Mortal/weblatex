from __future__ import division, absolute_import, unicode_literals

import os.path
import tempfile
import subprocess

from django.views.generic import TemplateView, View
from django.http import HttpResponse


class InputView(TemplateView):
    template_name = 'weblatex/input.html'


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
                return HttpResponse(result, content_type='text/plain', status=500)
            with open(pdf_filename, 'rb') as fp:
                pdf_contents = fp.read()
            return HttpResponse(pdf_contents, content_type='application/pdf')
