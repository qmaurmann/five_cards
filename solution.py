"""
Solution (in progress) to the riddle:

* Adversary gives A five unordered cards out of a deck of 52
* A chooses four cards out of the five, puts them in any order, and gives them
    to B.
* B must name A's remaining card
* Find a strategy for A and B that always allows them to do this.

The basic idea (in progress) is this:
* Represent cards by numbers between 0 and 51
* There are 24 permutations of four cards. When A passes B four cards, B has
    to distinguish between 48 remaining cards. That is, independent of the four
    cards selected by A, the ordering is enough to transmit all but ONE bit of
    information needed by B.
* The remaining task is to encode one bit of information in the selection task.
    A has five choices here, but encoding one bit of information in a uniform
    way across all (52 choose 5) is subtle.
* Outline... TODO

Run doc tests on command line with:
    python -m doctest -v solution.py
"""

import itertools as it
import funcy
from collections import namedtuple

# Represent cards by the numbers 0 to 51 inclusive

# Represent permutations as rearrangements of indices (0, 1, 2, 3), just as it itertools
PERMS_4 = tuple(it.permutations((0, 1, 2, 3)))
PERM_4_TO_INDEX = {p: i for i, p in enumerate(PERMS_4)}

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

def find_gaps(sorted_cards):
    """
    Find "gaps mod 52" between a sorted sequence of cards. Example:
    >>> find_gaps((3, 4, 8, 12, 47))
    (0, 3, 3, 34, 7)

    The last gap (7 in this case) "wraps around" from the last to first card.
    """
    n = len(sorted_cards)
    data = [sorted_cards[i+1] - sorted_cards[i] - 1 for i in range(n-1)]
    data.append(52 + sorted_cards[0] - sorted_cards[-1] - 1)
    return tuple(data)

GAP_PARITY_5_CASES = (
    (0, 0, 0, 0, 1),
    (0, 0, 1, 1, 1),
    (0, 1, 0, 1, 1),
    (1, 1, 1, 1, 1)
)

GAP_PARITY_4_CASES = (
    (0, 0, 1, 1),
    (0, 1, 0, 1),
    (1, 1, 1, 1)
)

def parities(nums):
    return tuple(n % 2 for n in nums)

def rotate(sequence, step=1):
    return sequence[step:] + sequence[:step]

CaseAndRot = namedtuple("CaseAndRot", "par_case rot_num")

def find_gap_parity_case(sorted_cards):
    """
    Find which gap parity case is represented, as well as how many rotations
    are needed to align the hand to the canonical representative of that case.
    Examples:
    >>> find_gap_parity_case((3, 4, 8, 12, 47))
    CaseAndRot(par_case=(0, 1, 0, 1, 1), rot_num=3)
    >>> find_gap_parity_case((3, 4, 12, 47))
    CaseAndRot(par_case=(0, 1, 0, 1), rot_num=0)
    """
    n = len(sorted_cards)
    if n == 4:
        gap_parity_cases = GAP_PARITY_4_CASES
    elif n == 5:
        gap_parity_cases = GAP_PARITY_5_CASES
    else:
        raise ValueError("Expected sequence of length 4 or 5; got {}".format(sorted_cards))
    gaps = find_gaps(sorted_cards)
    parity_rotations = funcy.take(n, funcy.iterate(rotate, parities(gaps)))
    for rot_num, par_case in enumerate(parity_rotations):
        if par_case in gap_parity_cases:
            return CaseAndRot(par_case=par_case, rot_num=rot_num)
    raise ValueError("Could not align {} with any gap parity case".format(sorted_cards))

# Encoding cases!

def possible_cards_between(start, end, odd_offset=True):
    if end < start:
        end += 52
    real_start = start + 2 if odd_offset else start + 1
    return [x % 52 for x in range(real_start, end, 2)]

def possible_cards_0101(sorted_four):
    """
    >>> possible_cards_0101((3, 4, 12, 47))
    [6, 8, 10, 49, 51, 1]
    """
    s = sorted_four
    gap_parities = parities(find_gaps(s))
    if gap_parities == (0, 1, 0, 1):
        return possible_cards_between(s[1], s[2]) + possible_cards_between(s[3], s[0])
    elif gap_parities == (1, 0, 1, 0):
        return possible_cards_between(s[0], s[1]) + possible_cards_between(s[2], s[3])
    else:
        raise ValueError("Bad gaps for 0101")

def a_encode_01011(five_cards, rot_num=None): # TODO: what do I want to do about rot_num parameter?
    if rot_num is None:
        rot_num = find_gap_parity_case(five_cards).rot_num
    rotated_hand = rotate(five_cards, rot_num)
    drop_one = rotated_hand[-1] # merges the two odd gaps
    select_four = rotated_hand[:-1]
    sorted_four = tuple(sorted(select_four))
    poss = possible_cards(sorted_four)
    i = poss.index(drop_one)
    return apply_permutation(sorted_four, PERMS_4[i])

def drop_select(seq, index):
    drop = seq[index]
    select = seq[:index] + seq[index+1:]
    return (drop, select)

def a_encode(five_cards):
    par_case, rot_num = find_gap_parity_case(five_cards)
    rotated_hand = rotate(five_cards, rot_num)
    if par_case == (0, 1, 0, 1, 1): # merge odd gaps at end
        drop_index = 4
    elif par_case == (1, 1, 1, 1, 1): # merge odd gaps at beginning
        drop_index = 1
    elif par_case == (0, 0, 0, 0, 1): # merge *even* gaps before odd
        drop_index = 3
    elif par_case == (0, 0, 1, 1, 1): # merge odd gaps at end
        drop_index = 4
    else:
        raise ValueError("Unrecognized par_case {}".format(par_case))
    drop_one, select_four = drop_select(rotated_hand, drop_index)
    sorted_four = tuple(sorted(select_four))
    poss = possible_cards(sorted_four)
    i = poss.index(drop_one)
    return apply_permutation(sorted_four, PERMS_4[i])

def possible_cards(sorted_four):
    """
    >>> possible_cards((3, 4, 12, 47)) # case 0101
    [6, 8, 10, 49, 51, 1]
    >>> possible_cards((6, 10, 20, 47)) # case 0011
    [7, 9, 12, 14, 16, 18]
    """
    par_case, rot_num = find_gap_parity_case(sorted_four)
    r = rotate(sorted_four, step=rot_num)
    if par_case == (0, 1, 0, 1):
        return possible_cards_between(r[1], r[2]) + possible_cards_between(r[3], r[0])
    if par_case == (0, 0, 1, 1):
        return possible_cards_between(r[2], r[3], odd_offset=False) + possible_cards_between(r[3], r[0])
    if par_case == (1, 1, 1, 1):
        return possible_cards_between(r[0], r[1])
    else:
        raise ValueError("Problem with input {}. par_case={}, rot_num={}".format(sorted_four, par_case, rot_num))


def b_decode(four_cards):
    """
    >>> a_encode_01011((3, 4, 8, 12, 47), 3) # (kinda annoying to provide num_rot=3)
    (3, 4, 47, 12)
    >>> b_decode(_)
    8
    """
    perm = get_permutation(four_cards)
    i = PERM_4_TO_INDEX[perm]
    sorted_four = tuple(sorted(four_cards))
    cards = possible_cards(sorted_four)
    return cards[i]
