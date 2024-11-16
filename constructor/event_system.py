import logging
from typing import Callable


class EventSystem:
    def __init__(self):
        self.__events = {}

    def emit(self, event_name, *args):
        if event_name not in self.__events:
            logging.warning(f'{self.__class__.__name__}.emit({event_name}, {args}) -> Event name not found.')
            return

        for handler in self.__events[event_name]:
            try:
                handler(*args)
            except Exception as e:
                logging.warning(f'{self.__class__.__name__}.emit({event_name}, {args}) -> {e.__class__.__name__}: {e}')

    def subscribe(self, event_name, handler: Callable) -> None:
        if event_name not in self.__events:
            self.__events[event_name] = []

        self.__events[event_name].append(handler)
