import cbmcodecs2


LC_CODEC = 'petscii_c64en_lc'
NEWLINE = b'\x0d'


def cbm_readline(buffer):
    s = b''
    while (True):
        v = buffer.read(1)
        if not v or v == NEWLINE:
            return s
        s += v



class ApplicationMenu:

    def __init__(self, menu):
        self.menu = menu


    @property
    def menu(self):
        return self._menu


    @menu.setter
    def menu(self, value):
        self._menu = value


    def _serialize(self, buffer, menu):
        for key, val in menu.items():
            if isinstance(val, dict):
                size = chr(ord('a')-1+len(val))
                buffer.write(f'{key};{size}'.encode(LC_CODEC) + NEWLINE)
                self._serialize(buffer, val)
            else:
                buffer.write(f'{key}:{val}'.encode(LC_CODEC) + NEWLINE)


    def serialize(self, buffer):
        self._serialize(buffer, self.menu)
        buffer.write(NEWLINE)


    @staticmethod
    def deserialize(buffer):
        raise NotImplementedError()


class ApplicationMetadata:

    def __init__(self, name, version, year, author):
        self.name = name
        self.version = version
        self.year = year
        self.author = author


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, value):
        self._name = value


    @property
    def version(self):
        return self._version


    @version.setter
    def version(self, value):
        self._version = value


    @property
    def year(self):
        return self._year


    @year.setter
    def year(self, value):
        self._year = value


    @property
    def author(self):
        return self._author


    @author.setter
    def author(self, value):
        self._author = value


    def serialize(self, buffer):
        buffer.write(self.name.encode(LC_CODEC) + NEWLINE)
        buffer.write(b'\x20' + self.version.encode(LC_CODEC) + NEWLINE)
        buffer.write(str(self.year).encode(LC_CODEC) + NEWLINE)
        buffer.write(self.author.encode(LC_CODEC) + NEWLINE)


    @staticmethod
    def deserialize(buffer):
        name = cbm_readline(buffer).decode(LC_CODEC)
        buffer.read(1)
        version = cbm_readline(buffer).decode(LC_CODEC)
        year_s = cbm_readline(buffer).decode(LC_CODEC)
        year = int(year_s)
        author = cbm_readline(buffer).decode(LC_CODEC)
