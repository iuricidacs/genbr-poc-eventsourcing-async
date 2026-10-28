from uuid import UUID

from eventsourcing.domain import Aggregate, event

class Individual(Aggregate):

    _name: str

    @event("Created")
    def __init__(self, id: UUID, name: str):
        self._name = name


    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @event("NameChanged")
    def name(self, value: str) -> None:
        self._name = value

# from datetime import datetime, timezone
# from uuid import UUID, uuid4
# from eventsourcing.domain import Aggregate, event
# from app.domain.events import IndividualCreated, IndividualRenamed
# Event = IndividualCreated | IndividualRenamed
#
# def utcnow(): return datetime.now(timezone.utc)
#
#
# class Individual(Aggregate):
#
#     @event("Created")
#     def __init__(self, individual_id: UUID, name: str, version: int = 0):
#         self.id, self.name, self.version = individual_id, name, version
#         self._pending_events: list[Event] = []
#
#     @classmethod
#     def create(cls, name: str):
#         name = name.strip()
#         if not name: raise ValueError("O nome não pode ser vazio")
#         obj = cls(uuid4(), name)
#         event = IndividualCreated(obj.id, name, utcnow())
#         obj._apply(event); obj._pending_events.append(event)
#         return obj
#     def rename(self, new_name: str):
#         new_name = new_name.strip()
#         if not new_name: raise ValueError("O nome não pode ser vazio")
#         if new_name == self.name: return
#         event = IndividualRenamed(self.id, self.name, new_name, utcnow())
#         self._apply(event); self._pending_events.append(event)
#     def _apply(self, event: Event):
#         if isinstance(event, IndividualCreated): self.name = event.name
#         else: self.name = event.new_name
#         self.version += 1
#     @classmethod
#     def rehydrate(cls, events: list[Event]):
#         if not events or not isinstance(events[0], IndividualCreated):
#             raise ValueError("Histórico inválido: IndividualCreated deve ser o primeiro evento")
#         first = events[0]; obj = cls(first.individual_id, first.name)
#         for event in events: obj._apply(event)
#         obj._pending_events.clear()
#         return obj
#     @property
#     def pending_events(self): return tuple(self._pending_events)
#     def mark_events_committed(self): self._pending_events.clear()
