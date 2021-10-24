from __future__ import annotations

import csv
from math import ceil
from typing import Dict, List, Optional, Union


class Position:
    """Class representing a single position with an arbitrary number of candidates
    and vacancies.

    Args:
        no_vac: the number of vacancies for that position.
        candidates: a list of candidate names.
        opt_pref: option for vote to be optional preferential. If True, incomplete votes are permitted.
                    If False, incomplete votes are treated as invalid.
        raise_invalid: option to raise an exception if an invalid vote is passed. If False, the invalid
                    vote is ignored.
    """

    def __init__(
        self,
        n_vac: int,
        candidates: List[str],
        opt_pref: bool = False,
        raise_invalid: bool = False,
    ):
        self._n_vac = n_vac
        self._candidates = candidates
        self._opt_pref = opt_pref
        self._raise_invalid = raise_invalid

        self._votes: List[List[str]] = []
        self._elected: List[str] = []
        self._counted = False

    #
    # Properties enforcing attribute access
    #

    @property
    def n_vac(self) -> int:
        return self._n_vac

    @property
    def candidates(self) -> List[str]:
        return self._candidates

    @property
    def votes(self) -> List[List[str]]:
        return self._votes

    @property
    def n_votes(self) -> int:
        return len(self._votes)

    @property
    def n_candidates(self) -> int:
        return len(self._candidates)

    @property
    def quota(self) -> float:
        """Calculate the quota of votes required for election"""
        return ceil(len(self._votes) / (self._n_vac + 1) + 1)

    @property
    def opt_pref(self) -> bool:
        return self._opt_pref

    @opt_pref.setter
    def opt_pref(self, val: bool):
        if not isinstance(val, bool):
            raise TypeError(f"Expected bool, got {type(val)}")

        self._opt_pref = val

    @property
    def raise_invalid(self) -> bool:
        return self._raise_invalid

    @raise_invalid.setter
    def raise_invalid(self, val: bool):
        if not isinstance(val, bool):
            raise TypeError(f"Expected bool, got {type(val)}")

        self._raise_invalid = val

    @property
    def elected(self) -> List[str]:
        if not self._counted:
            raise AttributeError(
                "The vote has not been counted for this position yet. Call the count_vote method first."
            )

        return self._elected

    #
    # Methods for adding and validating votes
    #

    def _invalid_vote(self, error_str: str):
        """Only raise a ValueError if raise_invalid is specified."""
        if self._raise_invalid:
            raise ValueError(error_str)

    def add_vote(self, prefs: List[Union[int, str]]):
        # TODO: Deal with optional preferential votes

        # Checking for invalid vote
        if not self._opt_pref and len(prefs) != self.n_candidates:
            # Vote is invalid
            self._invalid_vote(
                f"Preference array passed to add_vote is of invalid length: expected {self.n_candidates}, got {len(prefs)}."
            )
            return

        # Check each preference individually
        for i, val in enumerate(prefs):
            if isinstance(val, int):
                val = prefs[i] = self._candidates[val - 1]
            # Vote is invalid if not a string or integer
            elif not isinstance(val, str):
                self._invalid_vote(
                    f"Preference array passed to add_vote includes invalid type: expected int or str but found {type(val)}."
                )
                return

            if val not in self.candidates:
                self._invalid_vote(
                    f"Preference array passed to add_vote includes a name who is not a candidate, found {val}."
                )
                return

        # TODO: The above logic is confusing mypy
        self._votes.append(prefs)  # type: ignore

    def add_votes(self, votes: List[List[Union[str, int]]]):
        for prefs in votes:
            self.add_vote(prefs)

    #
    # Methods for counting votes
    #

    def _distribute_and_remove(
        self,
        count: Dict[str, float],
        cand: str,
        remaining: List[str],
        transfer_value: float,
    ) -> Dict[str, float]:
        for v in self._votes:
            if v[0] == cand:
                # The first candidate still remaining recieves the transferred vote.
                for i in range(1, len(v)):
                    next_cand = v[i]
                    if next_cand in remaining:
                        count[next_cand] += transfer_value
                        break

        del count[cand]
        return count

    def count_vote(
        self, exclude_cands: Optional[List[str]] = None, verbose: bool = False
    ) -> List[str]:
        """Perform the count, using all votes added to the class via the get_vote(s)
        methods.

        Args:
            exclude_cands: Any candidates to immediately remove from consideration. Their
                votes are redistributed prior to starting the counting loop. This is useful
                if counting for multiple positions with shared candidates, but each candidate
                can only be elected to one position.
            verbose: Whether to print results as the counting loop happens. Defaults to
                false.

        Returns:
            A list of the elected candidates.

        Raises:
            RuntimeError: If this method has already been called before.
            ValueError: If no votes have been added to the class, so no count can happen.

        """
        if self._counted:
            raise RuntimeError("Election has already been counted")

        if self.n_votes == 0:
            raise ValueError("No votes have been added, so count cannot be performed.")

        if exclude_cands is None:
            exclude_cands = []

        # Count the initial number of first preference votes
        first_prefs: Dict[str, float] = {cand: 0 for cand in self._candidates}
        for v in self._votes:
            first_prefs[v[0]] += 1
        remaining = self._candidates

        # Exclude any specified candidates and redistribute votes
        for cand in exclude_cands:
            # Ignore any names specified in exclude_cands who are not candidates for this
            # position.
            if cand in self._candidates:
                self._distribute_and_remove(
                    count=first_prefs, cand=cand, remaining=remaining, transfer_value=1
                )
                remaining.remove(cand)

        # If there are less candidates than positions, all are elected by default
        if len(remaining) < self.n_vac:
            self._elected = self._candidates
            self._counted = True
            return self._elected

        # Iterate until all positions are filled
        # The break condition is manually checked after electing candidates
        # Sometimes you just wish you could use a do while loop :(
        while True:
            elected_this_loop = False

            # Elect any candidates with more first preference votes than the quota
            new_first_prefs = first_prefs
            for cand in remaining:
                cand_first_prefs = first_prefs[cand]
                if cand_first_prefs > self.quota:
                    self._elected.append(cand)
                    remaining.remove(cand)
                    elected_this_loop = True

                    if verbose:
                        print(
                            f"{cand} has more votes than the quota and was elected!\nThere are {self._n_vac - len(self._elected)} vacancies and {len(remaining)} candidates remaining."
                        )

                    # Transfer the votes of the elected candidate
                    transfer_value = (cand_first_prefs - self.quota) / cand_first_prefs

                    # For every vote with the elected candidate as the first
                    # preference, their first preference votes are distributed to the
                    # second preference, at a reduced value according to the transfer
                    # value.
                    new_first_prefs = self._distribute_and_remove(
                        count=new_first_prefs,
                        cand=cand,
                        remaining=remaining,
                        transfer_value=transfer_value,
                    )
            first_prefs = new_first_prefs

            # Check if all positions have been filled
            if len(self._elected) == self._n_vac:
                self._counted = True
                break

            elif len(remaining) <= self._n_vac - len(self._elected):
                # Fill the remaining positions
                self._elected.extend(remaining)
                self._counted = True
                break

            elif not elected_this_loop:
                # If no one was elected this loop, then exclude the candidate with the least votes
                # TODO(typing): SupportsLessThan???
                excluded = min(first_prefs, key=first_prefs.get)  # type: ignore
                # Their votes are redistributed to second preferences
                first_prefs = self._distribute_and_remove(
                    count=first_prefs,
                    cand=excluded,
                    remaining=remaining,
                    transfer_value=1,
                )
                remaining.remove(excluded)

                if verbose:
                    print(f"{excluded} had too few votes and was excluded.")

        return self._elected

    #
    # Constructors from votes in other data formats.
    #

    @classmethod
    def from_csv(
        cls,
        filename: str,
        n_vac: int,
        candidates: List[str],
        header: bool = False,
        opt_pref: bool = False,
        raise_invalid: bool = False,
    ) -> Position:
        """Reads a CSV file containing candidates and preferences.

        Arguments:
            filename: directory of CSV file to be read.
            header: Whether the CSV file includes a header, which will be ignored.

        The following arguments are passed directly to the Position constructor. See the
        class documentation for more detail.
            n_vac: The number of vacancies.
            candidates: A list of candidate names.
            opt_pref: Whether the vote is optional preferential.
            raise_invalid: Whether to raise an exception on invalid votes.

        """
        # Create the position using the provided metadata
        pos = Position(
            n_vac=n_vac,
            candidates=candidates,
            opt_pref=opt_pref,
            raise_invalid=raise_invalid,
        )

        # Read the CSV file and load votes into the position
        with open(filename, "r") as read_obj:
            votes = list(csv.reader(read_obj))

            if header:
                votes = votes[1:]

            # TODO: mypy does not understand the above line
            pos.add_votes(votes)  # type: ignore

        return pos
