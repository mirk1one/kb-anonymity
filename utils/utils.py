import sys


def log(content, enabled=True, endl=True):
    """
    Prints a log message.

    :param content: Content of the message.
    :param enabled: If False the message is not printed.
    """

    if enabled:
        if endl:
            print(content)
        else:
            sys.stdout.write('\r' + content)


def debug(content, enabled=False):
    """
    Prints a debug message.

    :param content: Content of the message.
    :param enabled: If False the message is not printed.
    """

    if enabled:
        print(content)


def strToVal(value: str, raise_ex=False):
    """
    Convert string to a value

    :param value:       String of value input.
    :param raise_ex:    If True, I return an exception if it isn't an int or float number
    :return:            The string converted to it value:
                        - if it is a number, return int value;
                        - else if it is a decimal, number return float value;
                        - else return a string value (not converted);
    """

    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            if raise_ex:
                raise ValueError
            else:
                return value


def strTypeVal(value: str):
    """
    Convert string to a value

    :param value:       String of value input.
    :return:            String of type value.
    """

    try:
        int(value)
        return "int"
    except ValueError:
        try:
            float(value)
            return "float"
        except ValueError:
            return "str"
