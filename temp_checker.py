from collections import defaultdict

import solution


def check(a_encode, b_decode):
    from itertools import combinations
    problem_message = "five_cards={} (case {} of 2598960)"
    counts = defaultdict(int)
    for i, five_cards in enumerate(combinations(range(52), 5)):
        par_case, rot_num = solution.find_gap_parity_case(five_cards)
        if True:
            four_cards = a_encode(five_cards)
            assert len(set(four_cards)) == 4, problem_message.format(five_cards, i)
            assert all(c in five_cards for c in four_cards), problem_message.format(five_cards, i)
            guess = b_decode(four_cards)
            assert tuple(sorted(four_cards + (guess,))) == five_cards, problem_message.format(five_cards, i)
            counts[par_case] += 1
        if i % 10000 == 0:
            print "checking in: i={}, five_cards={}".format(i, five_cards)
    print "OK so far! counts: {}".format(counts)

if __name__ == "__main__":
    check(solution.a_encode, solution.b_decode)
