import pytest

from hcvote import Position


@pytest.fixture(scope="class")
def position():
    p = Position(3, ["Platypus", "Wombat", "Kangaroo", "Koala"])
    yield p


class TestCounterSimple:
    """Modified from the Wikipedia example:
    https://en.wikipedia.org/wiki/Hare%E2%80%93Clark_electoral_system#Counting_method_with_example
    """

    @pytest.fixture
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

        assert position.n_votes == 10000
        assert position.quota == 2501

    @pytest.mark.order(2)
    def test_full_count(self, position):
        """
        GIVEN: A position and votes.
        WHEN: Performing the vote count.
        THEN: The correct candidates are elected.
        """
        position.count_vote()
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
        p = Position(n_vac=5, candidates=candidates)
        p.add_votes([[0, 1], [1, 0]])

        p.count_vote()
        assert p.elected == candidates
