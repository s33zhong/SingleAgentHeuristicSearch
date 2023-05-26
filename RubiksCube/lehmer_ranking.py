import math
import numpy as np

"""Implementation of Lehmer Code.

Permutation - an array of integers. For the given interval, the array has to contains all numbers
for the interval and each of the number has to appear only once.

"""


def permutation_is_valid(permutation):
    if len(permutation) == 0:
        return False
    minimum = np.min(permutation)
    maximum = np.max(permutation)

    used = np.zeros(maximum - minimum + 1)
    for i in permutation:
        used[i - minimum] += 1

    if np.min(used) == 1 and np.max(used) == 1:
        return True
    else:
        return False


def count_lesser(i, permutation):
    return sum(item < permutation[i] for item in permutation[i + 1:])


def partial(i, permutation):
    return count_lesser(i, permutation) * math.factorial(len(permutation) - 1 - i)


def lehmer_rank(permutation):
    """
    Return Lehmer Code for the given permutation. Permutation has to contain numbers from 0 to len(permutation)-1.
    This function is based on the algorithm described in the paper:
    "Ranking and Unranking Permutations in Linear Time" by A. Ruskey and J. Sawada.
    """

    if not permutation_is_valid(permutation):
        return False

    return sum(partial(i, permutation) for i in range(0, len(permutation)))


def lehmer_unrank(length, lehmer):
    """Return permutation for the given Lehmer Code and permutation length. Result permutation contains
    number from 0 to length-1.
    """
    result = [(lehmer % math.factorial(length - i)) // math.factorial(length - 1 - i) for i in range(length)]
    used = np.zeros(length, dtype=bool)
    for i in range(length):
        count = 0
        for j in range(length):
            if not used[j]:
                count += 1
            if count == result[i] + 1:
                result[i] = j
                used[j] = True
                break
    return result


def test():
    assert lehmer_rank([]) == 0
    assert lehmer_rank([0]) == 0
    assert lehmer_rank([0, 1]) == 0
    assert lehmer_rank([1, 0]) == 1
    assert lehmer_rank([0, 1, 2, 3]) == 0
    assert lehmer_rank([3, 1, 0, 2]) == 20
    assert lehmer_rank([3, 2, 1, 0]) == 23

    assert lehmer_unrank(1, 0) == [0]
    assert lehmer_unrank(2, 1) == [1, 0]
    assert lehmer_unrank(3, 5) == [2, 1, 0]
    assert lehmer_unrank(4, 0) == [0, 1, 2, 3]
    assert lehmer_unrank(4, 23) == [3, 2, 1, 0]
    assert lehmer_unrank(4, 20) == [3, 1, 0, 2]
    assert lehmer_unrank(4, 23) == [3, 2, 1, 0]
    assert lehmer_unrank(5, 119) == [4, 3, 2, 1, 0]
    assert lehmer_unrank(6, 719) == [5, 4, 3, 2, 1, 0]
    assert lehmer_unrank(7, 5039) == [6, 5, 4, 3, 2, 1, 0]
    assert lehmer_unrank(8, 40319) == [7, 6, 5, 4, 3, 2, 1, 0]
    assert lehmer_unrank(9, 362879) == [8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert lehmer_unrank(10, 3628799) == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert lehmer_unrank(11, 39916799) == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert lehmer_unrank(12, 479001599) == [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]


if __name__ == "__main__":
    test()
    print('all test passed')


#%%
