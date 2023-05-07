import time

from strawberry.extensions import SchemaExtension

from rhubarb.config import config
from rhubarb.contrib.audit.models import log_gql_event


class AuditingExtension(SchemaExtension):
    async def on_execute(self):
        conn = None
        if config().audit.reuse_conn_in_extension:
            conn = self.execution_context.context.get("conn")

        kwargs = {}
        if user := self.execution_context.context.get("user"):
            kwargs["user_id"] = user.id

        if request := self.execution_context.context.get("request"):
            kwargs["impersonator_id"] = request.sessions.get("impersonator_id")
            kwargs["session_id"] = request.sessions.get("session_id")
            kwargs["ip"] = request.client.host

        start = time.perf_counter_ns()

        try:
            yield
        finally:
            end = time.perf_counter_ns()
            await log_gql_event(
                conn=conn,
                raw_query=self.execution_context.query,
                variables=self.execution_context.variables,
                operation_type=self.execution_context.operation_type,
                event_name=self.execution_context.operation_name,
                duration_ns=end - start,
                **kwargs,
            )
