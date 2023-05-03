import dataclasses
import datetime
import uuid

from rhubarb.core import SupportsSqlModel
from rhubarb.object_set import column


@dataclasses.dataclass
class BaseModel(SupportsSqlModel):
    __schema__ = "public"
    __pk__ = "id"
    id: uuid.UUID = column(sql_default="uuid_generate_v4()")


@dataclasses.dataclass
class BaseUpdatedAtModel(BaseModel):
    created_at: datetime.datetime = column(insert_default="now()")
    updated_at: datetime.datetime = column(update_default="now()")


@dataclasses.dataclass
class BaseIntModel(BaseModel):
    id: uuid.UUID = column(sql_default="uuid_generate_v4()")
