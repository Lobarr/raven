from cerberus import Validator
from pydash import omit, omit_by, is_none, merge
from typing import Optional
from api.event import event_schema

class EventDTO:
    def __init__(self):
        self.id: Optional[str] = None
        self.circuit_breaker_id: Optional[str] = None
        self.target: Optional[str] = None
        self.body: Optional[dict] = None
        self.headers: Optional[dict] = None
    
        self.__schema = event_schema
        self.__validator = Validator(self.__schema)

    def to_dict(self) -> dict:
        transformed_data = merge(
            omit(self.__dict__, '_CircuitBreakerDTO__schema', '_CircuitBreakerDTO__validator', 'id'),
            {'_id': self.id},
        )

        return omit_by(transformed_data, lambda v: is_none(v))

    def is_valid(self) -> bool:
        return self.__validator.validate(self.to_dict())

    def get_validation_errors(self) -> list:
        return self.__validator.errors
