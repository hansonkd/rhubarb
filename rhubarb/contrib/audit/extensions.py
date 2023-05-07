from psycopg import Rollback
from strawberry.extensions import SchemaExtension
from strawberry.types.graphql import OperationType

from rhubarb.contrib.audit.models import log_gql_event


class AuditingExtension(SchemaExtension):
    async def on_execute(self):
        kwargs = {}
        if user := self.execution_context.context.get("user"):
            kwargs["user_id"] = user.id

        if request := self.execution_context.context.get("request"):
            kwargs["impersonator_id"] = request.sessions.get("impersonator_id")
            kwargs["session_id"] = request.sessions.get("session_id")
            kwargs["ip"] = request.client.host

        try:
            yield
        finally:
            await log_gql_event(
                conn=self.execution_context.context.get("audit_conn"),
                raw_query=self.execution_context.query,
                variables=self.execution_context.variables,
                operation_type=self.execution_context.operation_type,
                event_name=self.execution_context.operation_name,
                **kwargs,
            )


class TransactionalMutationExtension(SchemaExtension):
    async def on_execute(self):
        if self.execution_context.operation_type == OperationType.MUTATION:
            async with self.execution_context.context["conn"].transaction() as txn:
                yield
                result = self.execution_context.result
                if result and result.errors:
                    raise Rollback(txn)
        else:
            yield
