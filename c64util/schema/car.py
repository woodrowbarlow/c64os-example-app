import abc
import cbmcodecs2
import copy
import collections
import datetime
import enum
import os


# this is originally based on gillham's excellent uncar.py
# https://github.com/gillham/C64/blob/main/C64OS/uncar/uncar.py


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

    PRGFILE = 0x50
    SEQFILE = 0xAC
    DIRECTORY = 0x44


    def to_class(self):
        if self == CarRecordType.PRGFILE:
            return CarPrgFileRecord
        if self == CarRecordType.SEQFILE:
            return CarSeqFileRecord
        if self == CarRecordType.DIRECTORY:
            return CarDirectoryRecord
        raise NotImplementedError()


class CarRecord(abc.ABC):

    MAX_NAME_SIZE = 15


    @property
    @abc.abstractmethod
    def size(self):
        raise NotImplementedError()


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
        assert len(name) <= CarRecord.MAX_NAME_SIZE
        self._name = value


    @staticmethod
    @abc.abstractmethod
    def _deserialize(buffer, size, record_type, compression_type, base_dir, name):
        raise NotImplementedError()


    def _serialize(self, buffer):
        record_type_bytes = self.record_type.value.to_bytes(1, 'little')
        buffer.write(record_type_bytes)
        buffer.write(b'\0') # lock byte?
        size_bytes = self.size.to_bytes(3, 'little')
        buffer.write(size_bytes)
        name_bytes = self.name.encode(LC_CODEC).ljust(CarRecord.MAX_NAME_SIZE, b'\xA0')
        buffer.write(name_bytes)
        buffer.write(b'\0') # ???
        compression_type = self.compression_type.value
        compression_bytes = compression_type.to_bytes(1, 'little')
        buffer.write(compression_bytes)


    @abc.abstractmethod
    def serialize(self, buffer):
        raise NotImplementedError()


    @staticmethod
    def deserialize(buffer, base_dir=None):
        if base_dir is None:
            base_dir = os.getcwd()
        record_type_bytes = buffer.read(1)
        record_type_val = int.from_bytes(record_type_bytes, 'little')
        buffer.read(1) # lock byte?
        size_bytes = buffer.read(3)
        size = int.from_bytes(size_bytes, 'little')
        name_bytes = buffer.read(CarRecord.MAX_NAME_SIZE)
        name = name_bytes.rstrip(b'\xA0').decode(LC_CODEC)
        buffer.read(1) # ???
        compression_bytes = buffer.read(1)
        compression_val = int.from_bytes(compression_bytes, 'little')
        print(f'"{base_dir}/{name}" ({size} {record_type_val} {compression_val})')
        record_type = CarRecordType(record_type_val)
        compression_type = CarCompressionType(compression_val)
        return record_type.to_class()._deserialize(
            buffer, size, record_type, compression_type, base_dir, name
        )


# TODO this should be abstract
class CarFileRecord(CarRecord):

    @property
    def size(self):
        return os.path.getsize(self.path)


    @property
    def path(self):
        return self._path


    @path.setter
    def path(self, value):
        self._path = value


    def to_dict(self):
        return {
            self.name: self.path
        }


    def __eq__(self, other):
        if other is None:
            return False
        if self.record_type != other.record_type:
            return False
        if self.name != other.name:
            return False
        if self.path != other.path:
            return False
        if self.compression_type != other.compression_type:
            return False
        return True


    def serialize(self, buffer, base_dir=None, follow_symlinks=False):
        # TODO symlinks
        assert follow_symlinks == False
        # TODO compression
        assert self.compression_type == CarCompressionType.NONE
        if base_dir is None:
            base_dir = os.getcwd()
        super()._serialize(buffer)
        full_path = os.path.join(base_dir, self.name)
        with open(full_path, 'rb') as f:
            while True:
                chunk = f.read(64)
                if not chunk:
                    break
                buffer.write(chunk)


    @staticmethod
    def _deserialize(buffer, size, record_type, compression_type, base_dir, name):
        # TODO compression
        assert compression_type == CarCompressionType.NONE
        full_path = os.path.join(base_dir, name)
        with open(full_path, 'wb') as f:
            while size:
                chunk = buffer.read(min(64, size))
                if not chunk:
                    raise ValueError()
                f.write(chunk)
                size -= len(chunk)
        return record_type.to_class()(
            compression_type=compression_type,
            name=name, path=full_path
        )


class CarSeqFileRecord(CarFileRecord):

    def __init__(self, compression_type=CarCompressionType.NONE, name='', path=''):
        self._record_type = CarRecordType.SEQFILE
        self._compression_type = compression_type
        self._name = name
        self._path = path



class CarPrgFileRecord(CarFileRecord):

    def __init__(self, compression_type=CarCompressionType.NONE, name='', path=''):
        self._record_type = CarRecordType.PRGFILE
        self._compression_type = compression_type
        self._name = name
        self._path = path



class CarDirectoryRecord(CarRecord):

    def __init__(self, name='', children=[]):
        self._record_type = CarRecordType.DIRECTORY
        self._compression_type = CarCompressionType.NONE
        self._name = name
        self._children = []
        self.add_children(children)


    @property
    def size(self):
        return len(self.children)


    @property
    def children(self):
        return self._children


    def get_child(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None


    def add_child(self, record):
        self.children.append(record)


    def add_children(self, records):
        for record in records:
            self.add_child(record)


    def merge(self, other):
        if other.name != self.name:
            raise ValueError()
        for other_child in other.children:
            child = self.get_child(other_child.name)
            if not child:
                self.add_child(other_child)
            elif child.record_type != other_child.record_type:
                raise ValueError()
            elif child.record_type == CarRecordType.DIRECTORY:
                child.merge(other_child)
            elif child != other_child:
                raise ValueError()


    def to_dict(self):
        d = collections.OrderedDict()
        for child in self.children:
            d.update(child.to_dict())
        return {
            self.name: d
        }


    def serialize(self, buffer, base_dir=None, follow_symlinks=False):
        # TODO symlinks
        assert follow_symlinks == False
        if base_dir is None:
            base_dir = os.getcwd()
        super()._serialize(buffer)
        full_path = os.path.join(base_dir, self.name)
        for child in self.children:
            child.serialize(buffer, base_dir=full_path, follow_symlinks=False)


    @staticmethod
    def _deserialize(buffer, size, record_type, compression_type, base_dir, name):
        full_path = os.path.join(base_dir, name)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        children = []
        for _ in range(size):
            child = CarRecord.deserialize(buffer, base_dir=full_path)
            children.append(child)
        return CarDirectoryRecord(name=name, children=children)



class CarManifest:

    def __init__(self, root=None):
        self._root = root


    def __init__(self, *paths, prefix='/', compression_type=CarCompressionType.NONE):
        self._root = None
        for path in paths:
            self.add_file(path, prefix=prefix, compression_type=compression_type)


    @property
    def root(self):
        return self._root


    @root.setter
    def root(self, value):
        self._root = value


    def add_file(self, path, prefix='/', compression_type=CarCompressionType.NONE):
        path = os.path.normpath(path)
        prefix_parts = [ part for part in prefix.split('/') if part ]
        path_parts = [ part for part in path.split(os.sep) if part ]
        name = '/'.join(prefix_parts, path_parts)
        record = _build_record(name, path, compression_type=compression_type)
        self.root = self.merge_record(record)


    def get_record(self, name):
        parts = [ part for part in name.split('/') if part ]
        assert self.root is not None
        assert self.root.name == parts[0]
        return self._get_record(parts[1:], self.root)


    def merge_record(self, record):
        if record is None:
            return
        if self.root is None:
            self.root = record
            return
        if self.root.record_type != record.record_type:
            raise ValueError()
        if record.record_type == CarRecordType.DIRECTORY:
            self.root.merge(record)
        elif self.root != record:
            raise ValueError()


    def _get_record(self, parts, parent):
        if not parts:
            return parent
        child = parent.get_child(parts[0])
        if not child:
            raise KeyError()
        return _get_record(parts[1:], child)


    def iterate_records(self, filter_fn=None):
        if self.root is not None:
            yield from self._iterate_records(self.root, filter_fn)


    def iterate_files(self, filter_fn=None):

        def file_filter_fn(n):
            if n.record_type != CarRecordType.DIRECTORY:
                return False
            if filter_fn and not filter_fn(n):
                return False
            return True

        if self.root is not None:
            yield from self._iterate_records(self.root, filter_fn=file_filter_fn)


    def _iterate_records(self, node, filter_fn):
        if filter_fn is not None and filter_fn(node):
            yield node
        if node.record_type == CarRecordType.DIRECTORY:
            for child in node.children:
                yield from self._iterate_records(child, filter_fn)


    def get_file(self, path):
        for file in self.iterate_files():
            if file.path == path:
                return file
        return None


    def set_file_compression(self, path, compression_type):
        file = self.get_file(path)
        file.compression_type = compression_type


    def to_dict(self):
        manifest = collections.OrderedDict()
        manifest['contents'] = {}
        manifest['attributes'] = {}
        if self.root:
            manifest['contents'] = self.root.to_dict()
        for file in self.iterate_files():
            manifest['attributes'][file.path] = {
                'compression': file.compression_type.name.lower(),
            }
        return manifest


    def serialize(self, buffer, base_dir=None, follow_symlinks=False):
        self.root.serialize(buffer, base_dir=base_dir, follow_symlinks=follow_symlinks)


    @staticmethod
    def deserialize(buffer, base_dir=None):
        root = CarRecord.deserialize(buffer, base_dir=base_dir)
        return CarManifest(root=root)


class CarTimestamp:

    def __init__(self, year=1900, month=0, day=0, hour=0, minute=0):
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute


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
        self._archive_type = archive_type
        self._timestamp = CarTimestamp.from_datetime(timestamp)
        self._note = note


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
        assert len(note) <= CarHeader.MAX_NOTE_SIZE
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


class CarArchive:

    def __init__(self, header, manifest):
        self._header = header
        self._manifest = manifest


    def __init__(
        self,
        archive_type=CarArchiveType.GENERAL,
        timestamp=datetime.datetime.utcnow(),
        note='',
    ):
        self._header = CarHeader(
            archive_type=archive_type,
            timestamp=timestamp,
            note=note,
        )
        self._manifest = CarManifest()


    def __init__(
        self, *paths, prefix=None,
        compression_type=CarCompressionType.NONE,
        archive_type=CarArchiveType.GENERAL,
        timestamp=datetime.datetime.utcnow(),
        note='',
    ):
        self._header = CarHeader(
            archive_type=archive_type,
            timestamp=timestamp,
            note=note,
        )
        self._manifest = CarManifest(
            *paths, prefix=prefix, compression_type=compression_type
        )


    @property
    def header(self):
        return self._header


    @property
    def manifest(self):
        return self._manifest


    def serialize(self, buffer, base_dir=None, follow_symlinks=False):
        self.header.serialize(buffer)
        self.manifest.serialize(buffer, base_dir=base_dir, follow_symlinks=follow_symlinks)


    @staticmethod
    def deserialize(buffer, base_dir=None):
        header = CarHeader.deserialize(buffer)
        manifest = CarManifest.deserialize(buffer, base_dir=base_dir)
        return CarArchive(header, manifest)


def _build_record(name, path, compression_type=CarCompressionType.NONE):
    parts = [ part for part in name.split('/') if part ]
    head = parts[0]
    parts = parts[1:]
    name = '/'.join(parts)
    if not name:
        return CarPrgFileRecord(name=head, path=path, compression_type=compression_type)
    child = _build_record(name, path, compression_type=compression_type)
    return CarDirectoryRecord(name=head, children=[child])
