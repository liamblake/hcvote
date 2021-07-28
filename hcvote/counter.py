from __future__ import annotations

from math import ceil
from typing import List

from pandas import DataFrame, read_csv


class InvalidVote(Exception):
    """Exception raised when an invalid vote is passed to a class."""

    pass


class CountingError(Exception):
    """Exception raised when an unexpected error occurs in vote counting"""

    pass


class Position:
    """Class representing a single position with an arbitrary number of candidates
    and vacancies.
    """

    def __init__(
        self,
        name: str,
        no_vac: int,
        candidates: List[str],
        opt_pref: bool = False,
        raise_invalid: bool = False,
    ):
        """
        Constructor of object.

        Arguments are:
            name: title of position, as string
            no_vac: the number of vacancies for that position
            candidates: a list of candidate names, with order providing each a unique index
            opt_pref: option for vote to be optional preferential. If True, incomplete votes are permitted.
                      If False, incomplete votes are treated as invalid.
            raise_invalid: option to raise an exception if an invalid vote is passed. If False, the invalid
                      vote is ignored.

        For example, for a general committee of 10 members, with 15 people running for election
        Position("General Committee Member", 10)
        """

        self.name = name
        self.__opt_pref = opt_pref
        self.__raise_invalid = raise_invalid

        # Create a dictionary storing first preference vote for each candidate
        self.__cand_index = {i: c for i, c in enumerate(candidates)}
        self.__votes = []
        self.__first_prefs = {i: 0 for i in range(len(candidates))}

        self.__no_vac = no_vac
        self.__no_cand = len(candidates)

        self.__elected = []
        self.__elect_open = True

    def __invalid_vote(self, str: str):
        if not self.__raise_invalid:
            return
        else:
            raise InvalidVote(str)

    def add_vote(self, prefs: List[int]):
        # TODO: Deal with optional preferential votes

        # Checking for invalid vote
        if len(prefs) != self.__no_cand:
            # Vote is invalid
            self.__invalid_vote(
                "Preference array passed to add_vote is of invalid length: expected %i, got %i."
                % (self.no_cand, len(prefs))
            )
            return

        # Check each vote individually
        for i in prefs:
            # Ensure vote is an integer
            if not isinstance(i, int):
                self.__invalid_vote(
                    "Preference array passed to add_vote includes invalid type: expected float."
                )
                return

            if i >= self.__no_cand:
                self.__invalid_vote(
                    "Preference array passed to add_vote includes value too large."
                )
                return

        self.__votes.append(prefs)

    def add_votes(self, votes: List[List[int]]):
        for prefs in votes:
            self.add_vote(prefs)

    @property
    def n_votes(self) -> int:
        return len(self.__votes)

    @property
    def quota(self) -> float:
        return ceil((len(self.__votes) + 1) / (self.__no_vac + 1))

    def count_vote(self):
        if not self.__elect_open:
            print("Election has already been counted")
            return

        # Vote backup in case count fails
        self.__vote_bku = self.__votes.copy()

        # Number of first preference votes for each candidate
        first_prefs = [0] * self.__no_cand

        # Calculate the quote
        quota = self.quota

        while self.__no_cand < self.__no_vac:
            # Count first preference votes
            for v in self.__votes:
                first_prefs[v[0]] += 1

            # Check for election
            for c in range(len(self.__no_cand)):
                if first_prefs[c] >= quota:
                    self.__elected.append(c)
                    self.__no_vac -= 1
                    self.__no_cand -= 1

            if self.no_vac < 0:
                raise ValueError()
            elif self.no_vac == 0:
                # Election complete
                break
            else:

                # Calculate transfer values
                no_exclude = False
                transfer = [0] * self.__no_cand

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
                            if v[0] in self.__elected:
                                v.remove[0]

                        except IndexError:
                            # Second preference is already elected candidate
                            pass

                else:
                    exclude = first_prefs.index(min(first_prefs))  # GET INDEX OF MIN
                    for v in self.votes:
                        v.remove(exclude)

        # Check for remaining vacancies
        if self.__no_vac <= self.__no_cand:
            # Elect remaining candidates
            self.__elected.append()
        else:
            raise CountingError()

        self.__elect_open = False

    @property
    def opt_pref(self) -> bool:
        return self.__opt_pref

    @opt_pref.setter
    def opt_pref(self, n_val: bool):
        if not isinstance(n_val, bool):
            raise TypeError("Expected bool type, got %s." % (type(n_val).__name__))

        self.__opt_pref = n_val

    @property
    def raise_invalid(self) -> bool:
        return self.__raise_invalid

    @raise_invalid.setter
    def raise_invalid(self, n_val: bool):
        if not isinstance(n_val, bool):
            raise TypeError("Expected bool type, got %s." % (type(n_val).__name__))

        self.__raise_invalid = n_val

    def get_elected(self):
        if self.__elect_open:
            raise AttributeError(
                "The vote has not been counted for this position yet. Call the count_vote method to do so."
            )

        # Generator of elected candidiates
        return self.__elected  # currently a bit janky
        # for i in self.__elected yield self.__cand_index[i]

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
