import time

from strawberry.extensions import SchemaExtension

from rhubarb.pkg.audit.models import log_gql_event, audit_connection


class AuditingExtension(SchemaExtension):
    async def on_execute(self):
        async with audit_connection() as conn:
            kwargs = {}
            if request := self.execution_context.context.get("request"):
                kwargs["request"] = request

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
