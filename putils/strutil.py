# -*- coding: utf8 -*-

"""string 관련 처리 모듈."""

import re
import itertools


# constants
HANGUL_SYLLABLE_BASE=0xAC00 # == '가'
HANGUL_CHOSEONG_BASE=0x1100
HANGUL_JUNGSEONG_BASE=0x1161
HANGUL_JONGSEONG_BASE=0x11A7


def str_join(data_list, sep="\t"):
    """data_list들을 하나의 문자열로 만든다.

    str.join()과 유사하게 동작한다.
    단, data_list가 str이 아닌 경우에도 사용 가능하다.
    
    :param data_list: join해서 하나로 만들 데이터 리스트.
    :param sep: data_list의 element들을 join할 때 사용할 glue str.
    :return: sep로 data_list를 붙인 하나의 str.
    """

    if not data_list: return ""

    str_list = map(convert_to_str, data_list)
    return sep.join(str_list)


def has_hangul(haystack, encoding="utf8"):
    """주어진 string 안에 한글이 존재하는지 여부를 판단.

    :param hayatack: 검사할 string.
    :param encoding: haystack이 unicode가 아닌 경우 사용된 encoding.
    :return: haystack string안에 한글 자모, 혹은 글자가 존재하면 True, 없으면 False
    """

    hangul = re.compile(u'[ㄱ-ㅎㅏ-ㅣ가-힣]')
   
    if isinstance(haystack, str):
        haystack = haystack.decode(encoding)
    elif isinstance(haystack, unicode):
        pass
    else: # 문자열이 아닌 값이 들어온 경우
        raise TypeError("haystack must be str, or unicode. (%s)[%s] received." % (haystack, type(haystack)))

    return (hangul.search(haystack) is not None)


def is_hangul_syllable(needle, encoding="utf8"):
    """주어진 글자가 한글인지 아닌지 판단.

    :param needle: 검사할 글자
    :param encoding: needle이 unicode가 아닌 경우 사용된 encoding.
    :return: needle이 한글 자모 혹은 하나의 음절이면 True, 아니면 False.
    """

    if isinstance(needle, str):
        needle = needle.decode(encoding)
    elif isinstance(needle, unicode):
        pass
    else:
        raise TypeError("needle must be str or unicode. (%s)[%s] received." % (needle, type(needle)))

    return u'가' <= needle and needle <= u'힣'


def expand_syllable_to_jamo(needle, encoding="utf8"):
    """주어진 글자를 자모로 분리한다.

    주어진 글자가 한글의 온전한 음절인 경우, 해당 글자를 자모로 분리한 리스트를 반환한다.
    그렇지 않은 경우 자모 분리를 하지 않고 글자 그대로 리스트에 담아서 반환한다.

    :param needle: 분석 대상 글자
    :param encoding: needle이 unicode가 아닌 경우 사용된 encoding.
    :return: needle이 자모로 분석된 글자들의 리스트. needle이 한글이 아닌 경우 글자가 그대로 들어가 있다.
    """

    if isinstance(needle, str):
        needle = needle.decode(encoding)
    elif isinstance(needle, unicode):
        pass
    else:
        raise TypeError("needle must be str or unicode. (%s)[%s] received." % (needle, type(needle)))

    if is_hangul_syllable(needle):
        needle_index = ord(needle) - HANGUL_SYLLABLE_BASE
        jongseong_index = needle_index % 28
        jungseong_index = ((needle_index - jongseong_index) / 28) % 21
        choseong_index = (((needle_index - jongseong_index) / 28) - jungseong_index) / 21

        if jongseong_index == 0:
            return [unichr(choseong_index + HANGUL_CHOSEONG_BASE), unichr(jungseong_index + HANGUL_JUNGSEONG_BASE)]
        else:
            return [unichr(choseong_index + HANGUL_CHOSEONG_BASE),
                    unichr(jungseong_index + HANGUL_JUNGSEONG_BASE),
                    unichr(jongseong_index + HANGUL_JONGSEONG_BASE)]
    else:
        return [needle]
        

def expand_string_to_jamo(haystack, encoding="utf8"):
    """haystack에 한글이 포함된 경우에 자모로 분리한다.

    haystack에 한글이 있는 경우에는 한글을 자모로 분리하고,
    그 외의 글자들은 그대로 유지한다.

    :param haystack: 분석 대상 string
    :param encoding: haystack이 unicode가 아닌 경우 사용된 encoding.
    :return: haystack의 한글이 자모로 분석된 글자들의 리스트. 한글이 아닌 글자는 변형되지 않는다.
    """

    if isinstance(haystack, str):
        haystack = haystack.decode(encoding)
    elif isinstance(haystack, unicode):
        pass
    else:
        raise TypeError("haystack must be str or unicode. (%s)[%s] received." % (haystack, type(haystack)))

    expanded_list = map(expand_syllable_to_jamo, haystack)
    merged_list = list(itertools.chain.from_iterable(expanded_list))

    return merged_list


def convert_to_str(may_unicode, encoding="utf8"):
    """주어진 string을 str로 바꿔준다.
    
    :param may_unicode: str로 바꿀 스트링.
    :param encoding: 사용할 encoding.
    :return: may_unicode를 encoding으로 encoding한 str.
    """

    if isinstance(may_unicode, unicode):
        return may_unicode.encode(encoding)
    else:
        return str(may_unicode)


def get_json_value(json_obj, element_name):
    """json_obj에서 element_name의 value를 가져온다.

    기본적으로 json_obj[element_name] 값을 반환한다.
    이 때, element_name이 "/"로 나뉘어져 있으면, 하위 element name으로 생각한다.
    즉, "parent/child" 로 이름이 들어왔으면, json_obj["parent"]["child"]를 반환한다.

    :param json_obj: 살펴볼 json object.
    :param element_name: 값을 가져올 element name. '/'는 parent/child 구분자로 사용한다.
    :return: json_obj에서 element_name의 value. element_name이 없다면 KeyError.
    """
    if json_obj is None: return ""

    name_tokens = element_name.split("/", 1)

    target_obj = None
    name_token = name_tokens[0]

    # json_obj가 list형이라면, [{"name1": {}}, {"name2": {}}, ..., ] 인 경우로 가정하고 해당 dictionary를 구한다.
    try:
        if isinstance(json_obj, list):
            for item in json_obj:
                if name_token in item:
                    target_obj = item[name_token]
        elif isinstance(json_obj, dict):
            target_obj = json_obj[name_token]

        if len(name_tokens) == 1:
            return target_obj
        else:
            return get_json_value(target_obj, name_tokens[1])
    # 주어진 데이터가 없는 경우.
    except KeyError:
        return ""


