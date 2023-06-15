import cbmcodecs2
import datetime
import enum


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
            hour=timestamp.hour, minute=timestamp.minute
        )


    @property
    def datetime(self):
        return datetime.datetime(
            year=self.year, month=self.month, day=self.day,
            hour=self.hour, minute=self.minute
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
