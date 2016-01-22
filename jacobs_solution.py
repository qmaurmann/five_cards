"""
Solution by Jacob Liechty.
"""

import itertools as it
from collections import namedtuple

def nth(iterable, n, default=None):
    return next(it.islice(iterable, n, None), default)

def encode_n(sorted_four, n):
    return nth(it.permutations(sorted_four), n)

def decode_n(sorted_four):
    for idx, el in enumerate(sorted(it.permutations(sorted_four))):
        if el == sorted_four:
            return idx

def num_even(n_tuple):
    n = 0
    for i in n_tuple:
        if i % 2 == 0:
            n += 1
    return n

def a_encode(sorted_five):
    card_guess = sorted_five[1 - (num_even(sorted_five) % 2)]
    n_to_encode = card_guess

    for i in sorted_five:
        if i < card_guess:
            n_to_encode -= 1

    n_to_encode = (n_to_encode - n_to_encode % 2) // 2

    return encode_n(tuple(x for x in sorted_five if x != card_guess), n_to_encode)

def b_decode(ordered_four):
    n = decode_n(ordered_four) * 2 + num_even(ordered_four) % 2

    for i in ordered_four:
        if (n >= i):
            n += 1
    return n
