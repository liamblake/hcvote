import pytest
from hcvote import Position


class TestCounterSimple:
    """Follows the Wikipedia example:
    https://en.wikipedia.org/wiki/Hare%E2%80%93Clark_electoral_system#Counting_method_with_example
    """

    @pytest.fixture
    def position(self):
        p = Position("Position", 3, ["Platypus", "Wombat", "Kangaroo", "Koala"])
        yield p

    @pytest.fixture
    def votes(self):
        # 1000 first preference votes for Platypus with Wombat as second
        # 2000 first preference votes for Platypus without Wombat as second
        # 7000 other votes
        # 500 invalid votes
        votes = (
            [[0, 1, 2, 3] for _ in range(1000)]
            + [[0, 2, 1, 3] for _ in range(2000)]
            + [[3, 2, 0, 1] for _ in range(7000)]
            + [[4, 5, 6, 7] for _ in range(500)]
        )

        yield votes

    def test_loading_votes(self, position, votes):
        position.add_votes(votes)

        assert position.n_votes == 10000
        assert position.quota == 2501
