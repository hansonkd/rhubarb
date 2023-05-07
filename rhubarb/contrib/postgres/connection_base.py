import dataclasses
import logging
from collections import deque
from contextlib import contextmanager
from typing import Optional, Protocol, ContextManager

import phonenumbers
from psycopg import AsyncConnection, AsyncCursor, postgres
from psycopg.abc import Query, Params
from psycopg.pq import Format
from psycopg.rows import Row
import time

from psycopg.types.string import StrBinaryDumper


class QueryListener(Protocol):
    def new_query(self, query: Query, params: Optional[Params], duration_ns):
        pass


@dataclasses.dataclass(slots=True)
class TrackedQuery:
    query: Query
    params: Optional[Params]
    duration_ns: int


class QueryTracker(QueryListener):
    def __init__(self):
        self.queries: deque[TrackedQuery] = deque(maxlen=500)

    def new_query(self, query: Query, params: Optional[Params], duration_ns):
        self.queries.append(TrackedQuery(query, params, duration_ns))


class LocalQueryListeners:
    listeners: dict[int, QueryListener]

    def __init__(self):
        self.listeners: dict[int, QueryListener] = {}

    def register(self, listener_id: int, listener: QueryListener):
        self.listeners[listener_id] = listener

    def unregister(self, listener_id: int):
        del self.listeners[listener_id]

    def new_query(self, query, params, duration_ns):
        logging.debug(f"[QUERY] {query}")
        for listener in self.listeners.values():
            listener.new_query(query, params, duration_ns)


local_queries = LocalQueryListeners()


@contextmanager
def track_queries() -> ContextManager[QueryTracker]:
    tracker = QueryTracker()
    tracker_id = time.monotonic_ns()
    local_queries.register(tracker_id, tracker)
    try:
        yield tracker
    finally:
        local_queries.unregister(tracker_id)


class AsyncConnectionWithStats(AsyncConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_factory = AsyncCursorWithStats
        self.adapters.register_dumper(phonenumbers.PhoneNumber, PhoneNumberDumper)


class AsyncCursorWithStats(AsyncCursor):
    async def execute(
        self,
        query: Query,
        params: Optional[Params] = None,
        *,
        prepare: Optional[bool] = None,
        binary: bool = False,
    ) -> AsyncCursor[Row]:
        start_ns = time.perf_counter_ns()
        result = await super().execute(query, params, prepare=prepare, binary=binary)
        end_ns = time.perf_counter_ns()
        local_queries.new_query(query, params, end_ns - start_ns)
        return result


class PhoneNumberDumper(StrBinaryDumper):
    format = Format.TEXT
    oid = postgres.types["text"].oid

    def dump(self, obj):
        return super().dump(str(obj))
