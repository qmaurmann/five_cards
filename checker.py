def check(a_encode, b_decode):
    from itertools import combinations
    problem_message = "five_cards={} (case {} of 2598960)"
    for i, five_cards in enumerate(combinations(range(52), 5)):
        if i % 10000 == 0:
            print "Progress: {} of 2598960 cases checked. Current case: {}".format(i, five_cards)
        four_cards = a_encode(five_cards)
        assert len(set(four_cards)) == 4, problem_message.format(five_cards, i)
        assert all(c in five_cards for c in four_cards), problem_message.format(five_cards, i)
        guess = b_decode(four_cards)
        assert tuple(sorted(four_cards + (guess,))) == five_cards, problem_message.format(five_cards, i)
    print "All cases pass!"

if __name__ == "__main__":
    from solution import a_encode, b_decode
    check(a_encode, b_decode)
