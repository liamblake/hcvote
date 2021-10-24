[![PyPI](https://img.shields.io/pypi/v/hcvote)](https://pypi.org/project/hcvote)
[![codecov](https://codecov.io/gh/liamblake/hcvote/branch/main/graph/badge.svg?token=AJ9GO0Q7DC)](https://codecov.io/gh/liamblake/hcvote)
[![Unit tests](https://github.com/LiamBlake/Hare-Clark-VoteCounter/actions/workflows/test.yml/badge.svg)](https://github.com/LiamBlake/Hare-Clark-VoteCounter/actions/workflows/test.yml)
[![Code style checks](https://github.com/LiamBlake/Hare-Clark-VoteCounter/actions/workflows/lint.yml/badge.svg)](https://github.com/LiamBlake/Hare-Clark-VoteCounter/actions/workflows/lint.yml)

# The Hare-Clark electoral system in Python

The [Hare-Clark electoral system](https://en.wikipedia.org/wiki/Hare%E2%80%93Clark_electoral_system) is a preferential voting system used for elections in Tasmania and the Australian Capital Territory. This small Python package provides an implementation of this system, with the ability to load votes from a range of sources and formats.

## Table of Contents

1. [The voting system](#the-voting-system)
2. [Installation](#installation)
3. [Usage](#usage)
   1. [The `Position` class](#the-position-class)
   2. [Vote validation](#vote-validation)
   3. [Loading from other sources](#loading-from-other-sources)

## The voting system

TODO

## Installation

This package is available on PyPI, and can be installed with pip;

```shell
pip install hcvote
```

Alternatively, you can clone the repository and install it directly with pip;

```shell
git clone git@github.com:LiamBlake/hcvote.git
cd hcvote
pip install .
```

To install the development and testing tools, run

```shell
pip install -e .[dev,test]
```

## Usage

### The `Position` class

The main functionality is contained by the `Position` class, which represents a position with one or more vacancies:

```python
from hcvote import Position

# The names of the candidates
names = ["Platypus", "Wombat", "Kangaroo", "Koala"]

# Create a position with 2 available places
p = Position(no_vac=2, candidates=names)
```

Votes can be added via the `add_votes` method, which accepts a list of lists, where each sublist corresponds to a vote. Each vote is an ordered list of either the candidate names or corresponding (one-based) indices matching the order originally passed to `candidates` when constructing the `Position`;

```python
votes = []

# This vote has Wombat as the first preference, Platypus as the second, etc.
votes[0] = ["Wombat", "Platypus", "Koala", "Wombat"]

# Alternatively, (one-based) indices can be used.
# This vote has Koala as the first preference, Wombat as the second, etc.
votes[1] = [4, 2, 1, 3]

# Add the votes to the Position
p.add_votes(votes)
```

To perform the count once all votes have been added, call the `count_vote` method:

```python
p.count_vote()
```

The elected candidates are then available from the `elected` property:

```python
p.elected
```

which returns as list of the elected candidates.

### Vote Validation

TODO

### Loading votes from other sources

TODO
