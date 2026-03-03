import time
from typing import Optional, Any

class SimpleTTLCache:
    def __init__(self, default_ttl: int = 15):
        self._store: dict[str, dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        if time.time() - item.get('ts', 0) > item.get('ttl', self.default_ttl):
            # Expirado
            self._store.pop(key, None)
            return None
        return item.get('val')

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._store[key] = {
            'val': value,
            'ts': time.time(),
            'ttl': ttl if ttl is not None else self.default_ttl,
        }