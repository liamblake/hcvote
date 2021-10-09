from __future__ import annotations

from math import ceil
from typing import List, Union

from pandas import DataFrame, read_csv


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

    For example, for a general committee of 10 members, with 15 people running for election;
    >>> Position("General Committee Member", 10)
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
        if self._counted:
            raise AttributeError(
                "The vote has not been counted for this position yet. Call the count_vote method first."
            )

        return self._elected

    #
    # Methods for adding and validating votes
    #

    def _invalid_vote(self, error_str: str):
        """Only raise a ValueError is raise_invalid is specified."""
        if self._raise_invalid:
            raise ValueError(str)

    def add_vote(self, prefs: Union[List[int], List[str]]):
        # TODO: Deal with optional preferential votes

        # Checking for invalid vote
        if len(prefs) != self.n_candidates:
            # Vote is invalid
            self._invalid_vote(
                "Preference array passed to add_vote is of invalid length: expected %i, got %i."
                % (self.no_cand, len(prefs))
            )
            return

        # Check each vote individually
        for i in prefs:
            # Ensure vote is an integer
            if not isinstance(i, int):
                self._invalid_vote(
                    f"Preference array passed to add_vote includes invalid type: expected int or str but found {type(i)}."
                )
                return

            if i >= self.no_cand:
                self._invalid_vote(
                    "Preference array passed to add_vote includes value too large."
                )
                return

        self.__votes.append(prefs)

    def add_votes(self, votes: List[List[int]]):
        for prefs in votes:
            self.add_vote(prefs)

    #
    # Methods for counting votes
    #

    def _count_loop(
        self,
        first_prefs,
        quota: float,
    ):
        # Count first preference votes
        for v in self._votes:
            first_prefs[v[0]] += 1

        # Check for election
        for c in range(len(self._n_cand)):
            if first_prefs[c] >= quota:
                self._elected.append(c)
                self.n_vac -= 1
                self.n_candidates -= 1

        if self.no_vac < 0:
            raise ValueError()
        elif self.n_vac == 0:
            # Election complete
            return
        else:

            # Calculate transfer values
            no_exclude = False
            transfer = [0] * self.n_candidates

            for e in self.__elected:
                surplus = first_prefs[e] - quota
                if surplus > 0:
                    no_exclude = True
                    transfer[e] = surplus / first_prefs[e]

                # Remove from consideration
                first_prefs.remove(e)

            # Transfer surplus votes
            if no_exclude:
                for v in self.votes:
                    try:
                        first_prefs[v[1]] += transfer[v[0]]
                        if v[0] in self._elected:
                            v.remove[0]

                    except IndexError:
                        # Second preference is already elected candidate
                        pass

            else:
                exclude = first_prefs.index(min(first_prefs))  # GET INDEX OF MIN
                for v in self.votes:
                    v.remove(exclude)

        return first_prefs

    def count_vote(self):
        if self._counted:
            raise RuntimeError("Election has already been counted")
            return

        if self.n_votes == 0:
            raise ValueError("No votes have been added, so count cannot be performed.")

        # If there are less candidates than positions, all are elected by default
        if self.n_candidates < self.n_vac:
            self._elected = self._cand

        # Vote backup in case count fails
        self._vote_bku = self._votes.copy()

        # Number of first preference votes for each candidate
        first_prefs = [0] * self.n_candidates

        # Calculate the quote
        quota = self.quota

        # Iterate until all positions are
        while self._n_candidates < self._n_vac:
            self._count_loop(first_prefs, quota)

        self._counted = True

    #
    # Constructors from votes in other data formats.
    #

    @classmethod
    def from_df(
        cls,
        df: DataFrame,
        name: str,
        no_vac: int,
        opt_pref: bool = False,
        raise_invalid: bool = False,
    ) -> Position:
        """Returns a position from a pandas DataFrame of candidates and votes

        Arguments
            name: title of position
            no_vac: number of available vacancies in position
            opt_pref: see Position.__init__ docstring
            raise_invalid: see Position.__init__ docstring

        Note that there are strong requirements on the format of the DataFrame
        to ensure correct behaviour:
            -
        """
        cands = df.columns
        output = cls(name, len(cands), cands, opt_pref, raise_invalid)

        # Parse each vote
        for index, row in df.iterrows():
            output.add_vote(row.values)

        return output

    @classmethod
    def from_csv(
        cls,
        filename: str,
        name: str,
        no_vac: int,
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

        votes = read_csv(filename)
        return cls.from_df(votes, name, no_vac, opt_pref, raise_invalid)
