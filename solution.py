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

A more detailed outline of encoding via selection:

* View the cards as points on a circle mod 52, with "gaps" between them.
* Invariant: for any set of five cards, the gaps sum to 47, and in particular
    this sum is odd.
* Ignoring rotation, there are only four possible cases for a sequence of five
    gaps on a circle summing to an odd number:
    - 1. all five odd (11111)
    - 2. just one odd (00001)
    - 3. three odd with the two even gaps adjacent to each other (00111)
    - 4. three odd with the two even gaps separated from one another (01011)
* If a card between two gaps of the same parity is removed, then these two gaps
    merge to form an odd gap (the card itself adds one).
* Beyond these facts, our choices are largely arbitrary, but here's one set of
    choices that works:
    - A will always merge gaps of the same parity, and will merge odd gaps when
        possible (every case but 2 above).
    - 1. B sees gap se...


    I think there may be a much simpler way to do this actually, where A always
    merges an odd gap and something after, so we just know the offset is odd
    (going around the circle in "increasing" order).


Run doc tests on command line with:
    python -m doctest -v solution.py
"""

import itertools as it
from collections import namedtuple

# Represent cards by the numbers 0 to 51 inclusive

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

def rotations(sequence):
    curr = sequence
    yield curr
    for _ in range(len(sequence)-1):
        curr = rotate(curr)
        yield curr

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
    parity_rotations = rotations(parities(gaps))
    for rot_num, par_case in enumerate(parity_rotations):
        if par_case in gap_parity_cases:
            return CaseAndRot(par_case=par_case, rot_num=rot_num)
    raise ValueError("Could not align {} with any gap parity case".format(sorted_cards))

# Encoding cases!

PAR_5_CASE_TO_DROP_INDEX = {
    (0, 1, 0, 1, 1): 4, # merge odd gaps at end
    (1, 1, 1, 1, 1): 1, # merge odd gaps at beginning
    (0, 0, 0, 0, 1): 3, # merge EVEN gaps before odd
    (0, 0, 1, 1, 1): 4  # merge odd gaps at end
}

def drop_select(seq, index):
    drop = seq[index]
    select = seq[:index] + seq[index+1:]
    return (drop, select)

def a_encode(sorted_five):
    """
    A's main encoding function.
    """
    par_case, rot_num = find_gap_parity_case(sorted_five)
    rotated_hand = rotate(sorted_five, rot_num)
    drop_one, select_four = drop_select(rotated_hand, PAR_5_CASE_TO_DROP_INDEX[par_case])
    sorted_four = tuple(sorted(select_four))
    poss = possible_cards(sorted_four)
    i = poss.index(drop_one)
    return apply_permutation(sorted_four, PERMS_4[i])

def possible_cards_between(start, end, odd_offset=True):
    if end < start:
        end += 52
    real_start = start + 2 if odd_offset else start + 1
    return [x % 52 for x in range(real_start, end, 2)]

def possible_cards(sorted_four):
    """
    A list of the possible cards (in order) that a selection of four cards
    could represent.
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
