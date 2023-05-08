from enum import Enum
from typing import NewType

import bcrypt
from strawberry import scalar

from rhubarb import RhubarbException
from rhubarb.object_set import SqlType


class PasswordHashers(Enum):
    BCRYPT = "bcrypt"


class PasswordHash(object):
    def __init__(self, hash_: bytes):
        self.hash = hash_
        split = self.hash.split(b"$")
        self.algo = PasswordHashers[split[0].decode().upper()]
        self.rounds = int(split[2].decode())
        self.real_hash = b"$" + b"$".join(split[1:])

    @staticmethod
    def __sql_type__():
        return SqlType.from_python(bytes)

    def __eq__(self, candidate):
        if isinstance(candidate, str):
            candidate = candidate.encode()
            return bcrypt.checkpw(candidate, self.real_hash)
        return False

    def __repr__(self):
        return "<{}>".format(type(self).__name__)

    def check(self, candidate: str):
        if self.algo == PasswordHashers.BCRYPT:
            return bcrypt.checkpw(candidate.encode(), self.real_hash)
        raise RhubarbException("Unknown algorithm")

    @classmethod
    def new(cls, password, algo=PasswordHashers.BCRYPT, rounds=12):
        if isinstance(password, str):
            password = password.encode("utf8")
        # rounds = rounds or (datetime.date.today().year - 2000)
        if algo == PasswordHashers.BCRYPT:
            new_hash = bcrypt.hashpw(password, bcrypt.gensalt(rounds))
        else:
            raise RhubarbException("Unknown algorithm")
        return cls(algo.value.encode() + new_hash)


Password = scalar(
    NewType("Password", PasswordHash),
    serialize=lambda v: v.hash,
    parse_value=PasswordHash,
)
