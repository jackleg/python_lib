# -*- coding: utf8 -*-

"""utility 모음"""

import itertools

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
