from typing import Type
from pydantic import BaseModel


def dual_body_openapi(schema: Type[BaseModel], required: bool = True) -> dict:
    schema_dict = schema.model_json_schema()
    return {
        "requestBody": {
            "required": required,
            "content": {
                "application/json": {"schema": schema_dict},
                "application/x-www-form-urlencoded": {"schema": schema_dict},
            },
        }
    }