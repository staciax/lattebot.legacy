# Standard 
import datetime
import os

class plural:
    def __init__(self, value):
        self.value = value
    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'

def human_join(seq, delim=', ', final='or'):
    size = len(seq)
    if size == 0:
        return ''

    if size == 1:
        return seq[0]

    if size == 2:
        return f'{seq[0]} {final} {seq[1]}'

    return delim.join(seq[:-1]) + f' {final} {seq[-1]}'

class TabularData:
    def __init__(self):
        self._widths = []
        self._columns = []
        self._rows = []

    def set_columns(self, columns):
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row):
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 2
            if width > self._widths[index]:
                self._widths[index] = width

    def add_rows(self, rows) -> None:
        for row in rows:
            self.add_row(row)

    def render(self) -> str:
        """Renders a table in rST format.
        Example:
        +-------+-----+
        | Name  | Age |
        +-------+-----+
        | Alice | 24  |
        |  Bob  | 19  |
        +-------+-----+
        """

        sep = '+'.join('-' * w for w in self._widths)
        sep = f'+{sep}+'

        to_draw = [sep]

        def get_entry(d):
            elem = '|'.join(f'{e:^{self._widths[i]}}' for i, e in enumerate(d))
            return f'|{elem}|'

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return '\n'.join(to_draw)

def format_dt(dt: datetime.datetime, style: str=None) -> str: #style 'R' or 'd'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    if style is None:
        return f'<t:{int(dt.timestamp())}>'
    return f'<t:{int(dt.timestamp())}:{style}>'

def format_relative(dt: datetime.datetime) -> str:
    return format_dt(dt, 'R')

def timestamp_utc() -> datetime.datetime:
    return datetime.datetime.timestamp(datetime.datetime.utcnow())

#thanks for stella_bot
def reading_recursive(root: str, /) -> int:
    for x in os.listdir(root):
        if os.path.isdir(x):
            yield from reading_recursive(root + "/" + x) 
            # for y in os.listdir(root + "/" + x):
            #     if os.path.isdir(root + "/" + x + "/" + y):
            #         yield from reading_recursive(root + "/" + x + "/" + y)  
        else:
            if x.endswith((".py")) and not root.startswith('./.test'):
                # print(root + "/" + x)
                with open(f"{root}/{x}" , encoding="utf-8") as r:
                    yield len(r.readlines())

def count_python(root: str) -> int:
    return sum(reading_recursive(root))

def deltaconv(s: int) -> str:
    hours = s // 3600
    s = s - (hours * 3600)
    minutes = s // 60
    seconds = s - (minutes * 60)
    if hours > 0:
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    return '{:02}:{:02}'.format(int(minutes), int(seconds))

fancy_text = {
    '0':'𝟶',
    '1':'𝟷',
    '2':'𝟸',
    '3':'𝟹',
    '4':'𝟺',
    '5':'𝟻',
    '6':'𝟼',
    '7':'𝟽',
    '8':'𝟾',
    '9':'𝟿',
    'a':'ᴀ',
    'b':'ʙ',
    'c':'ᴄ',
    'd':'ᴅ',
    'e':'ᴇ',
    'f':'ꜰ',
    'g':'ɢ',
    'h':'ʜ',
    'i':'ɪ',
    'j':'ᴊ',
    'k':'ᴋ',
    'l':'ʟ',
    'm':'ᴍ',
    'n':'ɴ',
    'o':'ᴏ',
    'p':'ᴘ',
    'q':'ǫ',
    'r':'ʀ',
    's':'ꜱ',
    't':'ᴛ',
    'u':'ᴜ',
    'v':'ᴠ',
    'w':'ᴡ',
    'x':'x',
    'y':'ʏ',
    'z':'ᴢ',
    ' ': ' '
}    

def get_fancy_text(text: str) -> str:
    def split(word):
        return list(word)

    text_list = split(text.lower())
    output = ''
    for x in text_list:
        try:
            output += fancy_text[x]
        except:
            output += x
    
    return output