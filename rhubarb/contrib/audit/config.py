import dataclasses

from rhubarb.contrib.postgres.config import PostgresConfig, load_postgres_config


@dataclasses.dataclass(frozen=True)
class AuditConfig:
    audit_mutations: bool = True
    audit_queries: bool = False
    audit_subscriptions: bool = False
    reuse_conn: bool = False
    postgres: PostgresConfig = dataclasses.field(
        default_factory=lambda: load_postgres_config("PG_AUDIT_URI")
    )
