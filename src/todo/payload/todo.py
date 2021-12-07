import json

from uuid import UUID, uuid4


class Todo(object):
    def __init__(self, text: str, _id: UUID = None, status: str = None):
        self._id = _id
        self._text = text
        self._status = status

    def assing_default_values(self):
        # Generate a new UUID if a value isn't supplied.
        self._id = self._id if self._id is not None else uuid4()
        # Assign a default value for status if one isn't supplied.
        # Defaults to N (for Not Done).
        self._status = self._status if self._status is not None else 'N'

    def get_id(self) -> UUID:
        return self._id

    def get_text(self) -> str:
        return self._text

    def get_status(self) -> str:
        return self._status

    def to_dict(self) -> dict:
        return {
            'id': self._id,
            'text': self._text,
            'status': self._status
        }

    @classmethod
    def from_dict(cls, todo_dict: dict):
        return cls(todo_dict.get('text'), todo_dict.get('id'), todo_dict.get('status'))

    @classmethod
    def from_json(cls, in_json: str):
        return cls.from_dict(json.loads(in_json))
