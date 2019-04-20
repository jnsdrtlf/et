from enum import Enum
from aenum import MultiValueEnum


class Weekday(Enum):
    """Weekdays

    Used to identify weekly repeating lessons. Starting with `monday`
    according to the python documentation (see `date.weekday()`) 
    """
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6

    @staticmethod
    def to_list():
        return list(map(lambda c: c.value, Weekday))


class Role(Enum):
    """User roles
    none:       default, no priviledges
    admin:      highest privileges
    editor:     maintainer for a specific school
    tutor:      student or tutor
                has to be approved (see `Status`)
    student:    student (can only access one school)
    """
    none = 'none'
    admin = 'admin'
    editor = 'editor'
    tutor = 'tutor'
    student = 'student'


class Status(Enum):
    """Status for approval of users
    pending:    has to be approved
    accepted:   approved
    rejected:   not eligible for teaching. No reason given
    """
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'


class Locale(MultiValueEnum):
    """Supported locale settings
    default: 'de'

    A multi value enum is used for different formats. Some browser 
    (e.g. Safari) use the long format (e.g. `en_US`) while others use a
    smaller format (such as `de`).
    """
    de = 'de_DE', 'de'
    en = 'en_US', 'en'

    @staticmethod
    def to_list():
        return list(map(lambda c: c.value, Locale))

    @staticmethod
    def to_short_list():
        return list(map(lambda c: c.value[:2], Locale))

    @staticmethod
    def default():
        return Locale.de
