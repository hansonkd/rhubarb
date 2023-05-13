import dataclasses
import datetime
import uuid

from rhubarb.core import SqlModel, Serial
from rhubarb.object_set import column, BUILTINS


@dataclasses.dataclass
class BaseModel(SqlModel):
    __schema__ = "public"
    __pk__ = "id"
    id: uuid.UUID = column(sql_default=BUILTINS.UUID_GENERATE_V4)


@dataclasses.dataclass
class BaseUpdatedAtModel(BaseModel):
    created: datetime.datetime = column(insert_default=BUILTINS.NOW)
    updated: datetime.datetime = column(update_default=BUILTINS.NOW)


@dataclasses.dataclass
class BaseIntModel(BaseModel):
    id: Serial = column()


@dataclasses.dataclass
class BaseIntUpdatedAtModel(BaseIntModel):
    created: datetime.datetime = column(insert_default=BUILTINS.NOW)
    updated: datetime.datetime = column(update_default=BUILTINS.NOW)
