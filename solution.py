"""
Solution (in progress) to the riddle:

* Adversary gives A five unordered cards out of a deck of 52
* A gives B four ordered cards out of the five
* B names A's remaining card
* Find a strategy for A and B that always allows them to do this.

The basic idea (in progress) is this:
* Represent cards by numbers between 0 and 51
* There are 24 permutations of four cards. When A passes B four cards, B has
    to select between 48 remaining cards; thus A's task of selecting four cards
    out of five only needs to transmit a single bit of information to B.
* Use gaps sizes between the cards (as numbers mod 52) to locate the missing
    card. Original idea was that A arranges that the largest gap of size <= 19
    contains the missing card. Does not work if original cards have a gap of
    size 19, but something like this might be workable.

Run doc tests on command line with:
    python -m doctest -v solution.py
"""

import itertools

# Represent cards by the numbers 0 to 51 inclusive

# Represent permutations as rearrangements of indices (0, 1, 2, 3), just as it itertools
PERMUTATIONS = tuple(itertools.permutations((0, 1, 2, 3)))
PERM_TO_INDEX = {p: i for i, p in enumerate(PERMUTATIONS)}

def get_permutation(cards):
    """
    Return permutation caputuring the order of the cards. Examples:
    >>> get_permutation((5, 6, 7, 8))
    (0, 1, 2, 3)
    >>> get_permutation((8, 7, 6, 5))
    (3, 2, 1, 0)
    >>> get_permutation((21, 34, 8, 4))
    (2, 3, 1, 0)
    """
    p = [None] * len(cards)
    for i, c in enumerate(sorted(cards)):
        p[cards.index(c)] = i
    return tuple(p)

def apply_permutation(cards, perm):
    """
    Apply a permutation to a tuple of cards. Example / property:
    >>> cards = (21, 34, 8, 4)
    >>> apply_permutation(sorted(cards), get_permutation(cards)) == cards
    True
    """
    return tuple(cards[i] for i in perm)

def get_gaps(sorted_cards):
    """
    Find "gaps mod 52" between a sorted sequence of cards. Example:
    >>> get_gaps((3, 4, 8, 12, 47))
    (0, 3, 3, 34, 7)

    The last gap (4 in this case) "wraps around" from the last to first card.
    """
    n = len(sorted_cards)
    data = [sorted_cards[i+1] - sorted_cards[i] - 1 for i in range(n-1)]
    data.append(52 + sorted_cards[0] - sorted_cards[-1] - 1)
    return tuple(data)

MAX_GAP = 19

def index_of_largest_gap(gaps):
    """
    Find (index of) largest gap of size <= MAX_GAP (i.e. 19)
    >>> index_of_largest_gap((0, 3, 3, 34, 7))
    4
    """
    for i, gap in sorted(enumerate(gaps), key=lambda x: x[-1], reverse=True):
        if gap <= MAX_GAP:
            return i
    raise ValueError("No gap of size <= MAX_GAP")

def decode(four_cards):
    """
    B's strategy for decoding A's sequence of four ordered cards:
    * sort the cards into their natural order
    * find largest gap of size <= MAX_GAP
    * the missing card is in this gap
    * use the number of the original permutation to determine which card
    TODO: test
    """
    perm = get_permutation(four_cards)
    sorted_cards = sorted(four_cards)
    gaps = get_gaps(sorted_cards)
    gap_start_index = index_of_largest_gap(gaps)
    card_start = sorted_cards[gap_start_index]
    perm_num = PERM_TO_INDEX[perm]
    return (card_start + 1 + perm_num) % 52
