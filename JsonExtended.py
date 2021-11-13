import json
from typing import get_type_hints

def dumps(obj):
    to_dict = getattr(obj, 'to_dict', None)
    if callable(to_dict):
        return json.dumps(to_dict())
    return json.dumps(obj)

def loads(obj, type=None):
    if type is not None:
        from_dict = getattr(type, 'from_dict', None)
        if callable(from_dict):
            t = type()
            t.from_dict(json.loads(obj))
            return t
    return json.loads(obj)
    