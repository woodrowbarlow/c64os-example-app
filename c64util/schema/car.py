import cbmcodecs2
import datetime
import enum
import os


CAR_MAGIC = 'C64Archive'
CAR_VERSION = 2
LC_CODEC = 'petscii_c64en_lc'


class CarArchiveType(enum.Enum):

    GENERAL = 0
    RESTORE = 1
    INSTALL = 2


class CarCompressionType(enum.Enum):

    NONE = 0
    RLE = 1
    LZ = 2


class CarRecordType(enum.Enum):

    FILE = 'F'
    DIRECTORY = 'D'


class CarRecord:

    def __init__(self, record_type, compression_type, name, buffer):
        self.record_type = record_type
        self.compression_type = compression_type
        self.name = name
        self.buffer = buffer


    @property
    def record_type(self):
        return self._record_type


    @record_type.setter
    def record_type(self, value):
        self._record_type = value


    @property
    def compression_type(self):
        return self._compression_type


    @compression_type.setter
    def compression_type(self, value):
        self._compression_type = value


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, value):
        self._name = value


    @property
    def buffer(self):
        return self._buffer


    @buffer.setter
    def buffer(self, value):
        self._buffer = value


    def serialize(self, buffer):
        raise NotImplementedError()


    @staticmethod
    def deserialize(buffer):
        raise NotImplementedError()


class CarFileRecord(CarRecord):

    def __init__(self, compression_type, name, buffer):
        super().__init__(
            CarRecordType.FILE,
            compression_type,
            name, buffer
        )


class CarDirectoryRecord(CarRecord):

    def __init__(self, name):
        super().__init__(
            CarRecordType.DIRECTORY,
            CarCompressionType.NONE,
            name, None
        )


class CarTimestamp:

    def __init__(self, year=1900, month=0, day=0, hour=0, minute=0):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute


    @staticmethod
    def from_datetime(timestamp):
        return CarTimestamp(
            year=timestamp.year, month=timestamp.month, day=timestamp.day,
            hour=timestamp.hour, minute=timestamp.minute,
        )


    @property
    def datetime(self):
        return datetime.datetime(
            year=self.year, month=self.month, day=self.day,
            hour=self.hour, minute=self.minute,
        )


    @property
    def year(self):
        return self._year
    

    @year.setter
    def year(self, value):
        assert value >= 1900
        self._year = value


    @property
    def month(self):
        return self._month
    
    @month.setter
    def month(self, value):
        self._month = value


    @property
    def day(self):
        return self._day


    @day.setter
    def day(self, value):
        self._day = value


    @property
    def hour(self):
        return self._hour


    @hour.setter
    def hour(self, value):
        self._hour = value


    @property
    def minute(self):
        return self._minute


    @minute.setter
    def minute(self, value):
        self._minute = value


    def serialize(self, buffer):
        values = [ self.year - 1900, self.month, self.day, self.hour, self.minute ]
        for value in values:
            buffer.write(value.to_bytes(1, 'little'))


    @staticmethod
    def deserialize(buffer):
        fields = ['year', 'month', 'day', 'hour', 'minute']
        values = buffer.read(len(fields))
        d = dict(zip(fields, values))
        d['year'] += 1900
        return CarTimestamp(**d)


class CarHeader:

    MAX_NOTE_SIZE = 31


    def __init__(self, archive_type=CarArchiveType.GENERAL, timestamp=datetime.datetime.utcnow(), note=''):
        assert len(note) <= CarHeader.MAX_NOTE_SIZE
        self.archive_type = archive_type
        self._timestamp = CarTimestamp.from_datetime(timestamp)
        self.note = note


    @property
    def archive_type(self):
        return self._archive_type


    @archive_type.setter
    def archive_type(self, value):
        self._archive_type = value


    @property
    def note(self):
        return self._note


    @note.setter
    def note(self, value):
        self._note = value


    @property
    def timestamp(self):
        return self._timestamp


    def serialize(self, buffer):
        buffer.write(self.archive_type.value.to_bytes(1, 'little'))
        buffer.write(CAR_MAGIC.encode(LC_CODEC))
        buffer.write(CAR_VERSION.to_bytes(1, 'little'))
        self.timestamp.serialize(buffer)
        buffer.write(self.note.encode(LC_CODEC).ljust(CarHeader.MAX_NOTE_SIZE))


    @staticmethod
    def deserialize(buffer):
        a_type = int.from_bytes(buffer.read(1), 'little')
        archive_type = CarArchiveType(a_type)
        magic = buffer.read(10).decode(LC_CODEC)
        version = int.from_bytes(buffer.read(1), 'little')
        timestamp = CarTimestamp.deserialize(buffer)
        note_buff = buffer.read(CarHeader.MAX_NOTE_SIZE)
        note = note_buff.rstrip(b'\0').decode(LC_CODEC)
        assert magic == CAR_MAGIC
        assert version == CAR_VERSION
        return CarHeader(archive_type=archive_type, timestamp=timestamp, note=note)


class CarRecords:

    def __init__(
        self, manifest={}
    ):
        raise NotImplementedError()


    def serialize(self, buffer):
        raise NotImplementedError()


    @staticmethod
    def deserialize(buffer):
        raise NotImplementedError()


class CarArchive:

    def __init__(
        self, manifest={},
        archive_type=CarArchiveType.GENERAL,
        timestamp=datetime.datetime.utcnow(),
        note='',
    ):
        self._header = CarHeader(
            archive_type=archive_type,
            timestamp=timestamp,
            note=note,
        )
        self._records = CarRecords(manifest, compression_type)


    @property
    def header(self):
        return self._header


    @property
    def records(self):
        return self._records


    def serialize(self, buffer):
        raise NotImplementedError()


    @staticmethod
    def deserialize(buffer):
        raise NotImplementedError()


def _add_path_to_manifest(manifest, full_path, partial_path):
    parts = partial_path.split(os.sep)
    head = parts[0]
    if len(parts) < 2:
        manifest[head] = full_path
    else:
        tail_path = os.sep.join(parts[1:])
        if head not in manifest:
            manifest[head] = {}
        _add_path_to_manifest(manifest[head], full_path, tail_path)


def _add_paths_to_manifest(manifest, base, paths):
    for path in paths:
        if os.path.isdir(path):
            nested_paths = glob.glob(os.path.join(path, '*'))
            _add_paths_to_manifest(manifest, nested_paths)
        else:
            _add_path_to_manifest(manifest, os.path.join(base, path), path)


def build_manifest(*paths, relative_to=None, prefix='', compression_type=CarCompressionType.NONE):
    if relative_to is None:
        relative_to = os.getcwd()
    manifest = {
        'contents': {},
        'attributes': {},
    }
    prefix = os.path.normpath(prefix)
    assert not prefix.startswith('/')
    contents = manifest['contents']
    for prefix_part in prefix.split(os.sep):
        contents[prefix_part] = {}
        contents = contents[prefix_part]
    sanitized_paths = []
    for path in paths:
        path = os.path.relpath(path, start=relative_to)
        path = os.path.normpath(path)
        assert not path.startswith('..')
        assert os.path.exists(path)
        sanitized_paths.append(path)
    _add_paths_to_manifest(contents, relative_to, sanitized_paths)
    for path in sanitized_paths:
        full_path = os.path.join(relative_to, path)
        manifest['attributes'][full_path] = {
            'compression': compression_type.name.lower(),
        }
    return manifest
