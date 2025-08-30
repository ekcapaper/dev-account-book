
# schemas/base.py
from pydantic import BaseModel, ConfigDict

from devaccountbook_backend.utils.case_util import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,  # snake_case -> camelCase
        populate_by_name=True      # snake_case로도 입력 받기 허용
    )
