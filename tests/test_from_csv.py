"""Testing of methods of loading positions and votes directly from CSV files."""
import pytest

from hcvote import Position


class TestSinglePositionFromCSV:
    """A single position loaded from a CSV file."""

    @pytest.fixture
    def position(self):
        # This example consists of anonymised votes from an actual election using the
        # Hare-Clark system, which was counted manually.
        # The winner should be Wombat.
        yield Position.from_csv(
            filename="tests/data/single.csv",
            n_vac=1,
            candidates=["Platypus", "Wombat", "Koala"],
        )

    def test_position_load(self, position):
        """
        GIVEN: Votes for a single position stored in a CSV file.
        WHEN: Loading a Position class from the CSV.
        THEN:
            - The metadata has been set correctly.
            - The quota is calculated correctly.
            - The count has not occured yet.
        """
        assert position.n_vac == 1
        assert position.candidates == ["Platypus", "Wombat", "Koala"]
        assert position.n_votes == 46

        assert position.quota == 24

        assert not position._counted
        with pytest.raises(AttributeError):
            position.elected

    def test_full_count(self, position):
        """
        GIVEN: A Position class loaded from a CSV file.
        WHEN: Counting the vote for the class.
        THEN: The correct candidate (Koala) is elected.
        """
        position.count_vote()
        assert position._counted
        assert position.elected == ["Koala"]
