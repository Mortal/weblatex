import io
import re


class Lyrics:
    def __init__(self, text):
        self.text = text

    def render(self, fp):
        lyrics = re.sub(r'\r+\n?', '\n', self.text)
        lyrics = re.sub(r'^ +| +$', '', lyrics, 0, re.M)
        paragraphs = re.split(r'\n\n+', lyrics)
        for p in paragraphs:
            if p.startswith('[Omk]'):
                p = p[5:].strip()
                kind = 'omkvaed'
            else:
                kind = 'vers'
            p = p.replace('´', '\'')
            p = re.sub(r'(^| )-( |$)',r'\1--\2', p, 0, re.M)
            lines = p.splitlines()
            fp.write(
                '\\begin{%s}%%\n%s\end{%s}%%\n\n' %
                (kind, '\n\\verseend\n'.join(lines), kind))

    def read(self):
        buf = io.StringIO()
        self.render(buf)
        return buf.getvalue()


class Song:
    def __init__(self, name, attribution, filename, twocolumn=False):
        self.name = name
        self.attribution = attribution
        self.filename = filename
        self.twocolumn = twocolumn

    def render(self, fp):
        fp.write('\\begin{sang}{%s}{%s}\n' % (self.name, self.attribution))
        if self.twocolumn:
            fp.write('\\begin{multicols}{2}\\multicolinit\n')
        fp.write('\\input{%s}\n' % self.filename)
        if self.twocolumn:
            fp.write('\\end{multicols}\n')
        fp.write('\\end{sang}\n')


class Rows:
    def __init__(self, children):
        self.children = children

    def render(self, fp):
        for c in self.children:
            c.render(fp)


class Cols:
    def __init__(self, children):
        self.children = children

    def render(self, fp):
        for c in self.children:
            fp.write('\\noindent\\begin{minipage}[t]' +
                     '{%s\\textwidth}%%\n' % (1/len(self.children)))
            c.render(fp)
            fp.write('\\end{minipage}\n')


class Page:
    def __init__(self, child):
        self.child = child

    def render(self, fp):
        self.child.render(fp)
        fp.write('\\clearpage\n')
