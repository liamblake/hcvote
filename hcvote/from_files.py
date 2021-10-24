"""More complex methods for automatically counting votes from files."""
import csv
from typing import List, Tuple

from .position import Position


# TODO: This use case is quite specific, so needs better documentation.
def multiple_from_csv(
    filename: str,
    metadata: List[Tuple[List[str], int]],
    auto_count: bool = False,
    exclude_elected: bool = False,
    verbose: bool = False,
    **kwargs,
) -> List[Position]:
    """Load multiple positions and votes from a single CSV file.

    The expected format of the CSV file is:
        TODO
    which can be the response format of a Google Form.

    Args:
        filename: The name of the CSV file to load.
        metadata: A list of 2-tuples corresponding to each position, containing
            information which cannot be distinguished from the CSV file alone. The first
            element of each tuple is the number of vacancies, and the second is a list of
            candidate names.
        auto_count: Whether to count each position before returning.
        exclude_elected: If auto_count is True, exclude any previously elected candidates
            when counting each position.
        verbose: If auto_count is True, whether to pass verbose=True to the count method
            on each position.
        **kwargs: Additional keyword arguments to pass to each `Position` constructor.

    Returns:
        A list of Positions inferred from the metadata and CSV.

    """
    positions: List[Position] = []

    # Read the csv as a single object
    with open(filename, "r") as read_obj:
        raw = list(csv.reader(read_obj))

        # Check that the CSV data is compatible with the metadata
        if len(raw[0]) != sum([len(item[1]) for item in metadata]):
            raise ValueError(
                "The total number of candidates across all positions does not match the number of rows in the CSV."
            )
        # TODO: More checks here, to prevent harder-to-diagnose issues later on.

        # Create the positions and assign votes
        rolling_idx = 0
        for pos_data in metadata:
            pos = Position(n_vac=pos_data[0], candidates=pos_data[1], **kwargs)
            pos.add_votes(
                row[rolling_idx : (rolling_idx + pos.n_candidates)] for row in raw[1:]  # type: ignore
            )
            rolling_idx += pos.n_candidates

    all_elected: List[str] = []
    if auto_count:
        for pos in positions:
            pos.count_vote(
                exclude_cands=all_elected if exclude_elected else None, verbose=verbose
            )
            all_elected.extend(pos.elected)

    return positions
