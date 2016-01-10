def check(a_encode, b_decode):
    """
    Exhaustively check whether a pair of encode/decode functions solve the
    problem.
    """
    from itertools import combinations
    problem_message = "Problem at sorted_five={} (case {} of 2598960)"
    for i, sorted_five in enumerate(combinations(range(52), 5)):
        if i % 10000 == 0:
            print "Progress: {} of 2598960 cases checked. Current case: {}".format(i, sorted_five)
        ordered_four = a_encode(sorted_five)
        assert len(set(ordered_four)) == 4, problem_message.format(sorted_five, i)
        assert all(c in sorted_five for c in ordered_four), problem_message.format(sorted_five, i)
        guess = b_decode(ordered_four)
        assert tuple(sorted(ordered_four + (guess,))) == sorted_five, problem_message.format(sorted_five, i)
    print "All cases pass!"

def main():
    from solution import a_encode, b_decode
    check(a_encode, b_decode)

if __name__ == "__main__":
    main()
