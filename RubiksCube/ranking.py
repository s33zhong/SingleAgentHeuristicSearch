import math
import numpy as np


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


def lehmer_rank_corner(permutation):
    """
    Return Lehmer Code for the given permutation. Permutation has to contain numbers from 0 to len(permutation)-1.
    This function is based on the algorithm described in the paper:
    "Ranking and Unranking Permutations in Linear Time" by A. Ruskey and J. Sawada.
    """

    if not permutation_is_valid(permutation):
        return False

    return sum(partial(i, permutation) for i in range(0, len(permutation)))


def lehmer_unrank_corner(length, lehmer):
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


def convert_from_dec(num, base):
    """
    Convert a number from one base to another
    :param num:  int, base-10 number to be converted
    :param base: int, base to be converted to
    :return:     int, number converted to the new base
    """
    if num == 0:
        return 0
    if base == 10:
        return num
    digits = np.zeros(7)
    for i in range(7):
        digits[i] = num % base
        num //= base
    return digits[::-1]  # reverse the order of the digits


def convert_to_dec(arr, base):
    """
    Convert a number from one base to base 10
    :param arr:  list of int, number to be converted
    :param base: int, base of the number
    :return:     int, number converted to base 10
    """
    if base == 10:
        return arr
    n = len(arr)
    result = 0
    for i in range(n):
        result += arr[i] * base ** i
    return result


rank_constant = 3**7  # 2187 to ensure that the rank is unique


def rank_corner(position, rotation):
    """
    Rank a position and rotation of corner cubies
    :param position:  list of 8 int, each integer is the position of the corner cubie
    :param rotation:  list of 7 int, each integer is the rotation of the corner cubie
    :return:          int, rank of the position and rotation
    """
    position_rank = lehmer_rank_corner(position)
    rotation_rank = convert_to_dec(rotation[:-1], 3)
    result = np.int32(position_rank * rank_constant + rotation_rank)
    return result


def unrank_corner(rank):
    """
    Unrank a position and rotation of corner cubies
    :param rank: int, rank of the position and rotation
    :return:     tuple of list of 8 int and list of 7 int, position and rotation of the corner cubies
    """
    position = lehmer_unrank_corner(8, rank // rank_constant)
    rotation = convert_from_dec(rank % rank_constant, 3)
    return position, rotation
