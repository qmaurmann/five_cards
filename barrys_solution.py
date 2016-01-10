"""
Solution communicated by Barry Weng.

Actually use the suits and ranks in a natural way: of the five cards, there
must be some suit represented at least twice. Alice picks any two cards of
same suit, orders them by rank to minimize their difference mod 13 (so the
difference from Queen to 2 is 3 rather than 10), which must be between 1 and 6.
Alice passes the first card to indicate suit and a small range of ranks for the
other card, which she keeps. The ramaining three cards can be permuted to
encode a number between 1 and 6.
"""

import itertools as it
from collections import defaultdict

from solution import apply_permutation, get_permutation

PERMS_3 = tuple(it.permutations((0, 1, 2)))
PERM_3_TO_INDEX = {p: i for i, p in enumerate(PERMS_3)}

def suit_and_rank(cardnum):
    """
    >>> suit_and_rank(0)
    (0, 0)
    >>> suit_and_rank(12)
    (0, 12)
    >>> suit_and_rank(13)
    (1, 0)
    >>> suit_and_rank(30)
    (2, 4)
    >>> suit_and_rank(51)
    (3, 12)
    """
    suit = cardnum // 13
    rank = cardnum % 13
    return (suit, rank)

def reconstruct_from_suit_rank(suit, rank):
    """
    Defining property:
    >>> all(c == reconstruct_from_suit_rank(*suit_and_rank(c)) for c in range(52))
    True
    """
    return suit * 13 + rank

def group_by_suit(sr_cards):
    d = defaultdict(list)
    for suit, rank in sr_cards:
        d[suit].append(rank)
    return d

def sort_and_diff(rank1, rank2):
    """
    Given two ranks (mod 13), one of them is "at most six lower" than the
    other, allowing for wraparound. Put them in that order and report the
    difference. Examples:
    >>> sort_and_diff(2, 7) # 2 is lower with 2 + 5 == 7
    (2, 7, 5)
    >>> sort_and_diff(3, 11) # 11 is lower with (11 + 5) % 13 == 3
    (11, 3, 5)

    Important properties:
    >>> max(sort_and_diff(r1, r2)[2] for r1 in range(13) for r2 in range(13))
    6
    >>> min(sort_and_diff(r1, r2)[2] for r1 in range(13) for r2 in range(13) if r1 != r2)
    1
    """
    dist_1_to_2 = (rank2 - rank1) % 13
    dist_2_to_1 = (rank1 - rank2) % 13
    if dist_1_to_2 <= dist_2_to_1:
        return (rank1, rank2, dist_1_to_2)
    else:
        return (rank2, rank1, dist_2_to_1)

def a_encode(sorted_five):
    sr_sorted_five = map(suit_and_rank, sorted_five)
    ranks_by_suit = group_by_suit(sr_sorted_five)
    common_suit, ranks_of_common_suit = max(ranks_by_suit.items(), key=lambda (k, v): len(v))
    lower_cs, higher_cs, diff_cs = sort_and_diff(*ranks_of_common_suit[:2])
    first_card = reconstruct_from_suit_rank(common_suit, lower_cs)
    dropped_card = reconstruct_from_suit_rank(common_suit, higher_cs)
    sorted_three = tuple(c for c in sorted_five if c != first_card and c != dropped_card)
    perm = PERMS_3[diff_cs - 1] # index should be 0-5, not 1-6
    ordered_three = apply_permutation(sorted_three, perm)
    return (first_card,) + ordered_three

def b_decode(ordered_four):
    first_card = ordered_four[0]
    first_suit, first_rank = suit_and_rank(first_card)
    ordered_three = ordered_four[1:]
    perm = get_permutation(ordered_three)
    diff = PERM_3_TO_INDEX[perm] + 1
    return reconstruct_from_suit_rank(first_suit, (first_rank + diff) % 13)
