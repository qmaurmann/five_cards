"""
Solution to the riddle:

* Adversary gives Player A five cards out of a deck of 52.
* A selects four cards out of the five, puts them in any order, and gives them
    to B.
* B must name A's remaining card.
* (Find a strategy for A and B that always allows them to do this.)

-------------------------------------------------------------------------------
This module defines functions a_encode and b_decode implementing our solution,
which can be verified correct in all (52 choose 5) cases with:
    python checker.py.

To run the unit tests in this module's docstrings:
    python -m doctest -v solution.py
-------------------------------------------------------------------------------

Our basic idea is this:

* Represent cards by numbers between 0 and 51 (suits and face values are
    incidental).
* There are 24 permutations of four cards. When A passes B four cards, B has
    to distinguish between 48 remaining cards. That is, the ordering alone is
    enough to transmit all but ONE bit of information needed by B.
* Then the remaining task is to encode one independent bit of information in
    the selection task. A has five choices here, but encoding one bit of
    information in a uniform way across all (52 choose 5) possibilities is
    subtle.

An outline of encoding via selection:

* View the cards as points on a circle mod 52, with "gaps" between them.
* Invariant: for any set of five cards, the gaps sum to 47. In particular this
    sum is odd, so there must be at least one odd gap.
* A will drop the card immediately after the first odd gap (starting at 0,
    traveling in the direction of increasing numbers), so B can know that the
    missing card occurs an odd number of steps after one of the shown cards.
    This cuts the search space in half, as needed.

(This solution is much simplified from the one in commit 9fd83d1)
"""

import itertools as it
from collections import namedtuple

# Represent permutations as rearrangements of indices (0, 1, 2, 3), just as it itertools
PERMS_4 = tuple(it.permutations((0, 1, 2, 3)))
PERM_4_TO_INDEX = {p: i for i, p in enumerate(PERMS_4)}

def get_permutation(ordered_cards):
    """
    Return permutation caputuring the order of the cards. Examples:
    >>> get_permutation((5, 6, 7, 8))
    (0, 1, 2, 3)
    >>> get_permutation((8, 7, 6, 5))
    (3, 2, 1, 0)
    >>> get_permutation((21, 34, 8, 4))
    (2, 3, 1, 0)
    """
    p = [None] * len(ordered_cards)
    for i, c in enumerate(sorted(ordered_cards)):
        p[ordered_cards.index(c)] = i
    return tuple(p)

def apply_permutation(sorted_cards, perm):
    """
    Apply a permutation to a tuple of cards. Example / property:
    >>> cards = (21, 34, 8, 4)
    >>> apply_permutation(sorted(cards), get_permutation(cards)) == cards
    True
    """
    return tuple(sorted_cards[i] for i in perm)

def find_gaps(sorted_cards):
    """
    Find "gaps mod 52" between a sorted sequence of cards. Example:
    >>> find_gaps((3, 4, 8, 12, 47))
    (0, 3, 3, 34, 7)

    The last gap (7 in this case) "wraps around" from the last to first card.
    """
    n = len(sorted_cards)
    diffs = [sorted_cards[(i+1) % n] - sorted_cards[i] - 1 for i in range(n)]
    return tuple(d % 52 for d in diffs)

def parities(nums):
    """
    >>> parities((0, 3, 3, 34, 7))
    (0, 1, 1, 0, 1)
    """
    return tuple(n % 2 for n in nums)

def first_odd_gap_index(sorted_five):
    """
    >>> first_odd_gap_index((3, 4, 8, 12, 47))
    1
    """
    return parities(find_gaps(sorted_five)).index(1)

def drop_select(seq, index):
    """
    >>> drop_select(('a', 'b', 'c', 'd'), 2)
    ('c', ('a', 'b', 'd'))
    """
    drop = seq[index]
    select = seq[:index] + seq[index+1:]
    return (drop, select)

def possible_cards_between(start, end):
    """
    List the cards strictly between start and end that would make an odd gap
    with start.
    >>> possible_cards_between(8, 19)
    [10, 12, 14, 16, 18]
    >>> possible_cards_between(8, 20)
    [10, 12, 14, 16, 18]
    """
    if end < start:
        end += 52
    return [x % 52 for x in range(start+2, end, 2)]

def possible_cards(sorted_four):
    """
    List the <= 24 cards that A and B agree are compatible with the four.
    Important property:
    >>> max(len(possible_cards(s)) for s in it.combinations(range(52), 4))
    24
    """
    return list(it.chain(*(possible_cards_between(sorted_four[i], sorted_four[(i+1) % 4]) for i in range(4))))

def a_encode(sorted_five):
    """
    A's main encoding function.
    """
    drop_index = (first_odd_gap_index(sorted_five) + 1) % 5 # merge the first odd gap into whatever is next
    drop_one, sorted_four = drop_select(sorted_five, drop_index)
    poss = possible_cards(sorted_four)
    i = poss.index(drop_one)
    return apply_permutation(sorted_four, PERMS_4[i])

def b_decode(ordered_four):
    """
    B's main decoding funcion.
    >>> a_encode((3, 4, 8, 12, 47))
    (3, 4, 47, 12)
    >>> b_decode(_)
    8
    """
    perm = get_permutation(ordered_four)
    i = PERM_4_TO_INDEX[perm]
    sorted_four = tuple(sorted(ordered_four))
    cards = possible_cards(sorted_four)
    return cards[i]
