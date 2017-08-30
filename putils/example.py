#!/usr/bin/env python
# -*- coding: utf8 -*-

import strutil


def test_expand_string_to_jamo():
	eng_str = """Make an iterator that returns elements from the first iterable until it is exhausted,
				 then proceeds to the next iterable, until all of the iterables are exhausted.
				 Used for treating consecutive sequences as a single sequence. Roughly equivalent to:"""

	han_str = """다시 들어도 좋은 송민호x태양 '겁'♪ (ft.진한 여운)
				 동영상 FAQ
				 등록일2017. 08. 26 원본영상 아는 형님 90회 다시보기 홈페이지 바로가기"""

	print "original:\t", eng_str
	print "expanded:\t", strutil.expand_string_to_jamo(eng_str)
	print
	print "original:\t", han_str
	print "expanded:\t", strutil.expand_string_to_jamo(han_str)


if __name__ == "__main__":
	test_expand_string_to_jamo()
