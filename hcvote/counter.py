from __future__ import annotations

import csv
from math import ceil
from typing import Dict, List, Union


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
        self._opt_pref = opt_pref
        self._raise_invalid = raise_invalid
        self._candidates = candidates

        self._votes = []

        self._n_vac = n_vac

        self._elected = []
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
        return ceil((len(self._votes) + 1) / (self._n_vac + 1))

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
        if len(prefs) != self.n_candidates:
            # Vote is invalid
            self._invalid_vote(
                f"Preference array passed to add_vote is of invalid length: expected {self.n_candidates}, got {len(prefs)}."
            )
            return

        # Check each vote individually
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

        self._votes.append(prefs)

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
    ) -> Dict[str, int]:
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

    def count_vote(self):
        if self._counted:
            raise RuntimeError("Election has already been counted")

        if self.n_votes == 0:
            raise ValueError("No votes have been added, so count cannot be performed.")

        # If there are less candidates than positions, all are elected by default
        if self.n_candidates < self.n_vac:
            self._elected = self._candidates
            self._counted = True
            return

        remaining = self._candidates

        # Count the initial number of first preference votes
        first_prefs = {cand: 0 for cand in self._candidates}
        for v in self._votes:
            first_prefs[v[0]] += 1

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
                return

            elif len(remaining) <= self._n_vac - len(self._elected):
                # Fill the remaining positions
                # TODO: This should not happen in practice
                self._elected.extend(remaining)
                self._counted = True
                return

            elif not elected_this_loop:
                # If no one was elected this loop, then exclude the candidate with the least votes
                exclude_cand = min(first_prefs, key=first_prefs.get)
                # Their votes are redistributed to second preferences
                first_prefs = self._distribute_and_remove(
                    count=first_prefs,
                    cand=exclude_cand,
                    remaining=remaining,
                    transfer_value=1,
                )
                remaining.remove(exclude_cand)

    #
    # Constructors from votes in other data formats.
    #

    @classmethod
    def from_csv(
        cls,
        filename: str,
        n_vac: int,
        candidates: List[str],
        opt_pref: bool = False,
        raise_invalid: bool = False,
    ) -> Position:
        """Reads a .csv file containing candidates and preferences.

        Arguments:
            filename: directory of .csv file to be read.
            See df_to_position docstring for remaining arguments

        Note that there are strong requirements on the format of the .csv file
        to ensure correct behaviour:
            -
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
            pos.add_votes(votes)

        return pos
