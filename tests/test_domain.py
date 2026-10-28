from app.domain.events import IndividualCreated, IndividualRenamed
from app.domain.individual import Individual
def test_event_history_rehydrates():
    person = Individual.create("Ana Silva"); person.rename("Ana Souza")
    assert person.version == 2 and person.name == "Ana Souza"
    assert isinstance(person.pending_events[0], IndividualCreated)
    assert isinstance(person.pending_events[1], IndividualRenamed)
    restored = Individual.rehydrate(list(person.pending_events))
    assert restored.id == person.id and restored.name == "Ana Souza" and restored.version == 2
    assert restored.pending_events == ()
