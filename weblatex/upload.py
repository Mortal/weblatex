import re

from django.core.exceptions import ValidationError

from weblatex.models import Song


def parse(f):
    if isinstance(f, bytes):
        try:
            s = f.decode('utf8')
        except UnicodeDecodeError as e:
            if f[e.start] in 'æøåÆØÅ'.encode('latin1'):
                s = f.decode('latin1')
            else:
                raise ValidationError(
                    'Filen skal være i UTF-8-kodning')
        f = s

    if not f:
        raise ValidationError("file is empty")

    patterns = (
        ('sang', r'\\begin{sang}{(?P<name>[^}]+)}{(?P<attr>[^}]+)}'),
        ('spal', r'\\spal(?:{\d+}|\d+)'),
        ('laps', r'\\laps'),
        ('begin', r'\\begin{(?P<begink>vers|omkvaed)}'),
        ('end', r'\\end{(?P<endk>vers|omkvaed)}'),
        ('endsang', r'\\end{sang}'),
        ('comment', r'%.*'),
    )
    pattern = (
        '(?:%s)' %
        '|'.join('(?P<%s>%s)' % o for o in patterns))

    name = attribution = None
    song = []
    text = ''
    i = 0
    extra = []
    for mo in re.finditer(pattern, f, flags=re.M):
        k = mo.lastgroup
        # v = mo.group(k)

        j = mo.start(0)
        text += f[i:j]
        i = mo.end(0)

        if k == 'sang':
            extra.append(text)
            text = ''
            name = mo.group('name')
            print(name)
            attribution = mo.group('attr')
        elif k == 'spal':
            extra.append(text)
            text = ''
        elif k == 'laps':
            extra.append(text)
            text = ''
        elif k == 'begin':
            extra.append(text)
            text = ''
        elif k == 'end':
            kind = mo.group('endk')
            lines = '\n'.join(
                line.strip() for line in text.splitlines()
                if line.strip())
            if kind == 'omkvaed':
                lines = '[Omk] %s' % lines
            song.append(lines)
            text = ''
        elif k == 'endsang':
            extra.append(text)
            text = ''
        elif k == 'comment':
            pass
        else:
            raise AssertionError("Unknown lastgroup %s" % k)

    extra = [e.strip() for e in extra if e.strip()]
    if extra:
        raise ValidationError("Unknown extra text: %s" % (extra,))

    lyrics = '\n\n'.join(song)

    if name is None:
        raise ValidationError("No song name")

    return Song(name=name, attribution=attribution, lyrics=lyrics)
