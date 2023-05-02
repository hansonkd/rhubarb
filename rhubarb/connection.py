import dataclasses
from collections import deque
from contextlib import asynccontextmanager, contextmanager
from typing import Optional, Protocol, ContextManager

from psycopg import AsyncConnection, AsyncCursor
from psycopg.abc import Query, Params
from psycopg.rows import Row
from asgiref.local import Local
import time


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
    listeners: dict[str, QueryListener]

    def __init__(self):
        self.listeners: dict[str, QueryListener] = {}

    def register(self, listener_id, listener: QueryListener):
        self.listeners[listener_id] = listener

    def unregister(self, listener_id):
        del self.listeners[listener_id]

    def new_query(self, query, params, duration_ns):
        for listener in self.listeners.values():
            listener.new_query(query, params, duration_ns)


local_queries = LocalQueryListeners()



@contextmanager
def track_queries() -> ContextManager[QueryTracker]:
    tracker = QueryTracker()
    tracker_id = str(time.monotonic_ns())
    local_queries.register(tracker_id, tracker)
    try:
        yield tracker
    finally:
        local_queries.unregister(tracker_id)


class AsyncConnectionWithStats(AsyncConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._executed_queries = deque(maxlen=500)
        self.cursor_factory = AsyncCursorWithStats

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


@asynccontextmanager
async def connection(*args, **kwds):
    async with await AsyncConnectionWithStats.connect(
            host="localhost", dbname="debug", password="debug", user="debug"
    ) as conn:
        yield conn
