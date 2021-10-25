"""More complex methods for automatically counting votes from files."""
import csv
from typing import Any, Dict, List, Optional, Tuple, Union

from .position import Position


# TODO: This use case is quite specific, so needs better documentation.
def multiple_from_csv(
    filename: str,
    metadata: List[Union[Tuple[int, List[str]], Tuple[int, List[str], str]]],
    auto_count: bool = False,
    exclude_elected: bool = False,
    ignore_cols: Optional[List[int]] = None,
    id_col: Optional[int] = None,
    verbose: bool = False,
    opt_pref: bool = True,
    **kwargs,
) -> List[Position]:
    """Load multiple positions and votes from a single CSV file.

    The expected format of the CSV file is:
        TODO
    which can be the response format of a Google Form.

    Args:
        filename: The name of the CSV file to load.
        metadata: A list of 2-tuples or 3-tuples corresponding to each position,
            containing information which cannot be distinguished from the CSV file alone.
            The first  by element of each tuple is the number of vacancies, and the
            second is a list of candidate names. The third element is optional and
            corresponds to a name for each Position.
        auto_count: Whether to count each position before returning.
        exclude_elected: If auto_count is True, exclude any previously elected candidates
            when counting each position.
        ignore_cols: Optionally, a list of (0-based) indices indicating which columns in
            the CSV to ignore.
        id_col: Optionally, a (0-based) index corresponding to the column in the CSV
            which gives some form of identification for each vote (row). If this is set,
            then duplicates are checked and the most recent (closest to the bottom of the
            CSV) vote is used.
        opt_pref: Whether the votes are optional preferential, i.e. preferences can be
            missing.
        **kwargs: Additional keyword arguments to pass to each `Position` constructor.

    Returns:
        A list of Positions inferred from the metadata and CSV.

    """
    if ignore_cols is None:
        ignore_cols = []

    # Ensure the ID column is also ignored, if specified
    if id_col is not None:
        ignore_cols.append(id_col)

    positions: List[Position] = []

    # Read the csv as a single object
    with open(filename, "r") as read_obj:
        raw = list(csv.reader(read_obj))

        # TODO: Check that the CSV data is compatible with the metadata

        # Create the positions and assign votes
        # Start the rolling index at the first column which isn't ignored
        for i in range(len(raw[1])):
            if i not in ignore_cols:
                rolling_idx = i
                break
        else:
            raise ValueError("Unable to find a column which is not ignored.")
        print(rolling_idx)
        for pos_data in metadata:
            pos = Position(
                n_vac=pos_data[0],
                candidates=pos_data[1],
                name=pos_data[2] if len(pos_data) > 2 else "",  # type: ignore
                opt_pref=opt_pref,
                **kwargs,
            )
            # For tracking duplicates, save each row alongside the ID column, if specified.
            row_by_id: Dict[Any, int] = {}
            votes: List[List[Union[str, int]]] = []
            for i, row in enumerate(raw[1:]):
                # Only get the votes corresponding to the current position, ignoring any
                # specifed columns as required.
                vote = [
                    row[j]
                    for j in range(
                        rolling_idx, min(rolling_idx + pos.n_candidates, len(row))
                    )
                    if j not in ignore_cols
                ]
                if opt_pref:
                    # Remove any gaps in preferences, e.g. if a vote has specifed a first
                    # and third preference, but no second, then the third preference is
                    # moved to the second.
                    try:
                        vote.remove("")
                    # A ValueError is raised if "" is not found in the list. This is
                    # fine, as it means the vote is not missing any values.
                    except ValueError:
                        pass

                if id_col is not None:
                    vote_id = row[id_col]
                    if vote_id in row_by_id.keys():
                        # Delete the old vote
                        del votes[row_by_id[vote_id]]
                    row_by_id[vote_id] = i

                votes.append(vote)  # type: ignore

            pos.add_votes(votes)
            positions.append(pos)
            rolling_idx += pos.n_candidates + len(
                [
                    i
                    for i in ignore_cols
                    if rolling_idx <= i <= (rolling_idx + pos.n_candidates)
                ]
            )

    all_elected: List[str] = []
    if auto_count:
        for pos in positions:
            pos.count_vote(
                exclude_cands=all_elected if exclude_elected else None, verbose=verbose
            )
            all_elected.extend(pos.elected)
    return positions
