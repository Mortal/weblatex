import re

from django.db import models


class Song(models.Model):
    name = models.CharField(max_length=100)
    lyrics = models.TextField()

    def __str__(self):
        return self.name

    def as_tex(self):
        lyrics = self.lyrics
        lyrics = re.sub(r'\r+\n?', '\n', lyrics)
        result = []
        paragraphs = re.split(r'\n\n+', lyrics)
        result.append(r'\chapter{%s}' % self.name)
        result.append(r'\begin{enumerate}')
        for p in paragraphs:
            lines = p.splitlines()
            result.append(r'\item %s' % '\\\\\n'.join(lines))
        result.append(r'\end{enumerate}')
        return ''.join('%s\n' % l for l in result)
