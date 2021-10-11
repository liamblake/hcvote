from contextlib import ExitStack

import pytest

from hcvote import Position


@pytest.fixture(scope="class")
def position():
    p = Position(3, ["Platypus", "Wombat", "Kangaroo", "Koala"])
    yield p


@pytest.mark.parametrize(
    "transfer_value,exp_count",
    [(0, {"B": 5, "C": 1}), (0.2, {"B": 5.4, "C": 1.2}), (1, {"B": 7, "C": 2})],
)
def test_distribute_and_remove(transfer_value, exp_count):
    """
    GIVEN: A Position, corresponding votes, first preference counts for candidates and a
        transfer value.
    WHEN: Distributing and removing a candidate from the preference counts with
        Position._distribute_and_remove.
    THEN:
        - The candidate has been removed from the counts distribution.
        - The votes have been distributed correctly.
    """
    count = {"A": 2, "B": 5, "C": 1}
    votes = [["A", "B", "C"], ["A", "C", "B"], ["A", "B", "C"]]
    p = Position(n_vac=1, candidates=["A", "B", "C"])
    p.add_votes(votes)

    updated_count = p._distribute_and_remove(
        count, cand="A", transfer_value=transfer_value
    )

    assert "A" not in updated_count.keys()
    assert updated_count == exp_count


class TestCounterSimple:
    """Modified from the Wikipedia example:
    https://en.wikipedia.org/wiki/Hare%E2%80%93Clark_electoral_system#Counting_method_with_example
    """

    @pytest.fixture(scope="class")
    def votes(self):
        # 3000 votes in total
        votes = (
            # 1000 first preference votes for Platypus with Wombat as second
            [["Platypus", "Wombat", "Kangaroo", "Koala"] for _ in range(1000)]
            # 2000 first preference votes for Platypus without Wombat as second
            + [["Platypus", "Kangaroo", "Wombat", "Koala"] for _ in range(2000)]
        )

        yield votes

    @pytest.mark.order(1)
    def test_loading_votes(self, position, votes):
        """
        GIVEN: A position and votes.
        WHEN: Adding the votes to the position
        THEN:
            - The votes are added correctly.
            - The quota is calculated correctly.
        """
        position.add_votes(votes)

        assert position.n_votes == 3000
        assert position.quota == 2501

    @pytest.mark.order(2)
    def test_full_count(self, position):
        """
        GIVEN: A position and votes.
        WHEN: Performing the vote count.
        THEN:
            - The internal _counted flag is set to True.
            - The correct candidates are elected.
        """
        position.count_vote()

        assert position._counted
        assert position.elected == ["Platypus", "Wombat", "Kangaroo"]

    @pytest.mark.order(3)
    def test_count_again(self, position):
        """
        GIVEN: A position which has already been elected.
        WHEN: Attempting to perform the count again.
        THEN: A RuntimeError is raised.
        """
        with pytest.raises(RuntimeError):
            position.count_vote()


class TestSpecialCountCases:
    """Tests of special cases in which the HC algorithm is not used"""

    def test_no_votes(self, position):
        """
        GIVEN: A position without any votes.
        WHEN: Attempting to count votes.
        THEN: A ValueError is raised.
        """
        with pytest.raises(ValueError):
            position.count_vote()

    def test_less_candidates(self):
        """
        GIVEN: A position with less candidates than vacancies.
        WHEN: Performing the vote count.
        THEN: All the candidates are elected.
        """
        candidates = ["Koala", "Kangaroo"]
        p = Position(n_vac=5, candidates=candidates, raise_invalid=True)
        p.add_votes([[1, 2], [2, 1]])

        p.count_vote()
        assert p._counted
        assert p.elected == candidates


@pytest.mark.parametrize("raise_invalid", [False, True])
@pytest.mark.parametrize(
    "vote",
    [[1, 2], [1, 2, 3, 4, 5], ["Platypus", "Emu", "Koala", "Kangaroo"], [1, 2, 0.5, 3]],
)
def test_invalid_vote(position, raise_invalid, vote):
    """
    GIVEN: A Position and a invalid vote.
    WHEN: Adding the vote to the Position.
    THEN:
        - If raise_invalid is set on the position, then a ValueError is raised when
            trying to add the vote to the position. Otherwise, no exception is raised.
        - The vote is not added to the position.
    """
    position.raise_invalid = raise_invalid
    assert position.raise_invalid == raise_invalid

    # This allows us to only enter the pytest.raises(...) context if raise_invalid and
    # invalid is True. So we test that the exception is only raised when the raise_invalid
    # flag is set to True on the Position and the vote is invalid.
    # Described by this SE answer: https://stackoverflow.com/a/34798330
    # Yes, tests should be straightforward, but this is also pretty cool.
    with ExitStack() as stack:
        if raise_invalid:
            stack.enter_context(pytest.raises(ValueError))

        position.add_vote(vote)

    assert len(position.votes) == 0
