# coding=utf-8

def str_to_bool(s):
    """
    Get inpunt string True/False and transform it into boolean
    :param s: String with True or False
    :return: Boolen correpondent for the string
    """

    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError