# -*- coding: utf8 -*-

"""utility 모음"""

import itertools
import collections
import numpy as np


def split_list(crowd, count=1):
    """crowd를 최대한 동일한 사이즈로 count 개수만큼 나누어, 리스트의 리스트를 만든다.

    :param crowd: 나눌 리스트
    :param count: 나눌 개수.
    :return: count 개수만큼 나뉜 리스트의 리스트.
    """

    if count == 1:
        return [crowd[:]]

    chunk_size = len(crowd) / count
    if chunk_size == 0: chunk_size = 1

    # list를 split할 시작 index의 리스트
    # 예를 들어, 10개짜리 list를 두개로 나누는 경우라면, [0, 5]가 된다.
    index = [i * chunk_size for i in range(count)]
   
    splitted = [crowd[start:end] for start, end in itertools.izip_longest(index, index[1:])]

    return splitted


def edit_distance(seq1, seq2, method='levenshtein'):
    """두 iterable sequence의 edit distance를 반환한다.
    
    iterable seq1, seq2 사이의 edit distance를 반환한다.
    seq1, seq2가 동일 object이거나 값이 같다면 0을 반환한다.
    현재 method는 levenshtein만 지원한다.
    
    :param Iterable seq1: edit distance를 구할 iterable
    :param Iterable seq2: edit distance를 구할 iterable
    :param str method: edit distance를 구할 method. 현재는 levenshtein만 지원.
    :return: seq1과 seq2의 edit distance. seq1, 혹은 seq2가 None이면 -1.
    :raises ValueError: seq1, seq2 둘 중의 하나가 iterable이 아니거나, method가 올바른 값이 아닌 경우.
    """

	if seq1 is None or seq2 is None:
		return -1

    if not isinstance(seq1, collections.Iterable) or not isinstance(seq2, collections.Iterable):
        raise ValueError("arguments should be iterable.")
        
    if method != "levenshtein":
        raise ValueError("unknown method: %s" % method)

    if seq1 is seq2 or seq1 == seq2:
        return 0
    
    if method == 'levenshtein':
        return _levenshtein(seq1, seq2)

    
def _levenshtein(seq1, seq2):
    """levenshtein method로 구한 seq1과 seq2의 edit distance"""
    if len(seq1) < len(seq2):
        return _levenshtein(seq2, seq1)

    # So now we have len(seq1) >= len(seq2).
    if len(seq2) == 0:
        return len(seq1)

    # "abc" 같은 string인 경우 ['a', 'b', 'c']로 만들어야 하므로 tuple로 한번 감싸야 한다.
    seq1 = np.array(tuple(seq1))
    seq2 = np.array(tuple(seq2))

    previous_row = np.arange(len(seq2) + 1)
    for s in seq1:
        # d[i, j] = d[i-1, j] + 1
        current_row = previous_row + 1

        # d[i, j] = min(previous current row, d[i-1, j-1] + 1 or 0)
        # seq2 != s이면 seq1[i] != seq2[j] 인 상태임.
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], seq2 != s))

        # d[i, j] = d[i, j-1] + 1
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    # return d[i, j]
    return previous_row[-1]
