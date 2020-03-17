from cerberus import Validator
from typing import Optional, List
from enum import Enum
from pydash import merge, omit, omit_by, is_empty

from api.circuit_breaker.validate import circuit_breaker_schema

class CircuitBreakerStatus(Enum):
    ON = 'ON'
    OFF = 'OFF'

class CircuitBreakerDTO:
    def __init__(self):
        self.id: Optional[str] = None
        self.status: Optional[CircuitBreakerStatus] = None
        self.service_id: Optional[str] = None
        self.cooldown: Optional[int] = None
        self.status_codes: Optional[List[int]] = None
        self.methods: Optional[str] = None
        self.threshold: Optional[float] = None
        self.period: Optional[int] = None
        self.tripped_count: Optional[int] = None

        self.__schema = circuit_breaker_schema
        self.__validator = Validator(self.__schema)

    def to_dict(self) -> dict:
        transformed_data = merge(
            omit(self.__dict__, '_CircuitBreakerDTO__schema', '_CircuitBreakerDTO__validator', 'id'),
            {'_id': self.id}
        )

        return omit_by(transformed_data, lambda v: is_empty(v))

    def is_valid(self) -> bool:
        return self.__validator.validate(self.to_dict())

    def get_validation_errors(self) -> list:
        return self.__validator.errors

    def normalize(self, ctx: dict) -> dict:
        return self.__validator.normalized(ctx)

