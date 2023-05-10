import dataclasses
import importlib
from datetime import timedelta, datetime
from typing import Optional, Union, Any, Callable

from arq.typing import WorkerCoroutine, SecondsTimedelta
from arq.worker import Function, func as arq_func

from rhubarb.config import init_rhubarb, config

registry = {}


class RhubarbFunction(Function):
    async def enqueue_job(self,
                          *args: Any,
                          _job_id: str | None = None,
                          _queue_name: str | None = None,
                          _defer_until: datetime | None = None,
                          _defer_by: None | int | float | timedelta = None,
                          _expires: None | int | float | timedelta = None,
                          _job_try: int | None = None,
                          **kwargs: Any):
        arq_pool = await config().arq.get_pool()
        return await arq_pool.enqueue_job(self.name, *args, _job_id=_job_id, _queue_name=_queue_name, _defer_until=_defer_until, _defer_by=_defer_by, _expires=_expires, _job_try=_job_try, **kwargs)


def task(
    coroutine: Union[str, Function, WorkerCoroutine] = None,
    *,
    name: Optional[str] = None,
    keep_result: Optional[SecondsTimedelta] = None,
    timeout: Optional[SecondsTimedelta] = None,
    keep_result_forever: Optional[bool] = None,
    max_tries: Optional[int] = None,
) -> Function | Callable[[WorkerCoroutine], Function]:
    def wrap(coroutine):
        f = arq_func(coroutine, name=name, keep_result=keep_result, timeout=timeout,
                     keep_result_forever=keep_result_forever, max_tries=max_tries)
        rf = RhubarbFunction(**dataclasses.asdict(f))

        registry[rf.name] = rf
        return rf

    if coroutine is not None:
        return wrap(coroutine)
    else:
        return wrap



async def startup(ctx):
    pass


async def shutdown(ctx):
    pass


def functions_gen():
    init_rhubarb()
    conf = config().arq
    for mod in conf.task_modules:
        importlib.import_module(mod)
    yield from registry.values()


class _WorkerSettings:
    on_startup = startup
    on_shutdown = shutdown
    functions = functions_gen()

    def __init__(self):
        self._func = None

    def __call__(self, *args, **kwargs):
        return self


WorkerSettings = _WorkerSettings
