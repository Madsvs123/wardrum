"""Commands leave the queue only on their own tick, in seq order."""

from __future__ import annotations

import pytest

from wardrum.commands import Command, CommandQueue, move


def test_commands_are_frozen():
    command = move(0, 1, "solo", 1, 0)
    with pytest.raises(AttributeError):
        command.tick = 3  # type: ignore[misc]


def test_due_commands_follow_seq_not_insertion_order():
    queue = CommandQueue()
    later = move(4, 2, "solo", 0, 1)
    earlier = move(4, 1, "solo", 1, 0)
    queue.enqueue(later)
    queue.enqueue(earlier)
    released = queue.pop_due(4)
    assert [command.seq for command in released] == [1, 2]
    assert released[0] is earlier
    assert len(queue) == 0


def test_equal_seq_keeps_insertion_order():
    queue = CommandQueue()
    first = Command(1, 5, "move", "solo", (("dx", 1), ("dy", 0)))
    second = Command(1, 5, "move", "solo", (("dx", 0), ("dy", 1)))
    queue.enqueue(first)
    queue.enqueue(second)
    assert queue.pop_due(1) == [first, second]


def test_future_tick_waits_through_earlier_boundaries():
    queue = CommandQueue()
    waiting = move(5, 1, "solo", 1, 0)
    queue.enqueue(waiting)
    assert queue.pop_due(4) == []
    assert len(queue) == 1
    assert queue.pop_due(5) == [waiting]
    assert len(queue) == 0


def test_past_tick_is_not_released_on_a_later_boundary():
    queue = CommandQueue()
    stale = move(3, 1, "solo", 1, 0)
    queue.enqueue(stale)
    assert queue.pop_due(4) == []
    assert len(queue) == 1


def test_negative_tick_is_rejected():
    with pytest.raises(ValueError):
        Command(-1, 0, "move", "solo", ())


def test_payload_map_reads_pairs():
    command = move(0, 0, "solo", -1, 0)
    assert command.payload_map() == {"dx": -1, "dy": 0}
