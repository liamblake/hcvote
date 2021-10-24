"""Testing of methods of loading positions and votes directly from CSV files."""
import pytest

from hcvote import Position
from hcvote.from_files import multiple_from_csv

# TODO: Need examples with more than one vacancy per position


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
            header=True,
            # There should be no invalid votes in the CSV
            raise_invalid=True,
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


class TestMultipleFromCSV:
    """Follows the example data in `google_full.csv`, which contains multiple positions
    with optional preferential voting.
    """

    @pytest.fixture
    def csv_file(self):
        yield "tests/data/google_full.csv"

    @pytest.fixture
    def metadata(self):
        yield [
            (1, ["Platypus", "Wombat"]),
            (1, ["Platypus", "Koala", "Wombat"]),
            (1, ["Wombat", "Kangaroo"]),
            (1, ["Platypus", "Possum", "Kangaroo", "Emu"]),
            (1, ["Kangaroo", "Cassowary", "Emu"]),
            (1, ["Cassowary", "Emu"]),
        ]

    @pytest.fixture
    def expected_elected(self):
        yield [["Wombat"], ["Platypus"]]

    @pytest.fixture
    def expected_elected_exclude(self):
        yield [["Wombat"], ["Koala"], ["Kangaroo"], [], [], [""]]

    def test_loading_no_count(self, csv_file, metadata):
        """
        GIVEN: A CSV file containing votes for multiple, prespecified positions with
            corresponding metadat.
        WHEN: Loading the data with `multiple_from_csv`, without automatically counting.
        THEN:
            - The number of positions matches the expected number.
            - Each position has votes.
        """

        positions = multiple_from_csv(
            csv_file, metadata, auto_count=False, exclude_elected=False, verbose=True
        )

        assert len(positions) == len(metadata)
        for pos in positions:
            assert pos.n_votes > 0

    @pytest.mark.parametrize(
        "exclude_elected,expected_fixture",
        [(False, "expected_elected"), (True, "expected_elected_exclude")],
    )
    def test_loading_with_count(
        self, csv_file, metadata, exclude_elected, expected_fixture, request
    ):
        """
        GIVEN:
        WHEN:
        THEN:
        """
        positions = multiple_from_csv(
            csv_file,
            metadata,
            auto_count=True,
            exclude_elected=exclude_elected,
            verbose=True,
        )

        assert len(positions) == len(metadata)
        for pos in positions:
            assert pos._counted
            assert pos.elected == request.getfixturevalue(expected_fixture)
