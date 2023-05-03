import strawberry


Schema = strawberry.Schema


class ErrorRaisingSchema(strawberry.Schema):
    def process_errors(
        self,
        errors,
        execution_context=None,
    ) -> None:
        super().process_errors(errors, execution_context)

        for error in errors:
            err = getattr(error, "original_error")
            if err:
                raise err
