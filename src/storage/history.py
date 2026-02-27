import os
import json

class HistoryManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._history_set = set()
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history_set = set(data)
            except json.JSONDecodeError:
                self._history_set = set()
        else:
            self._history_set = set()

    def _save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(list(self._history_set), f, ensure_ascii=False)

    def is_exists(self, item_id: str) -> bool:
        return item_id in self._history_set

    def add(self, item_id: str):
        if item_id not in self._history_set:
            self._history_set.add(item_id)
            self._save()
