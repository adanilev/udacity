dprint_level = 4


def dprint(level, text):
    """Helper to print depending on level passed. dprint_level is:
    1 = Error
    2 = Warning
    3 = Info
    4 = Debug"""
    prefix = ''
    if level == 1:
        prefix = '[ ERROR ] '
    elif level == 2:
        prefix = '[ WARNING ] '
    elif level == 3:
        prefix = '[ INFO ] '
    elif level == 4:
        prefix = '[ DEBUG ] '

    if level <= dprint_level:
        print prefix + text
