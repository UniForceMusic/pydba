"""Escape helpers for string manipulation."""


def escape_ansi(string: str, chars: str) -> str:
    """Double-escape certain characters in a string.

    Replaces each occurrence of a character in ``chars`` with itself doubled.

    Args:
        string: The input string to process.
        chars: A string containing the characters to double-escape.

    Returns:
        The string with matching characters doubled.

    Example:
        >>> escape_ansi('hello "world"', '"')
        'hello ""world""'
    """
    return string.translate(str.maketrans(chars, chars * 2))


def escape_backslash(string: str, chars: str) -> str:
    """Backslash-escape certain characters in a string.

    Prefixes each occurrence of a character in ``chars`` with a backslash.

    Args:
        string: The input string to process.
        chars: A string containing the characters to escape.

    Returns:
        The string with matching characters prefixed by a backslash.

    Example:
        >>> escape_backslash("it's", "'")
        "it\\'s"
    """
    return string.translate(str.maketrans(chars, "\\" + chars))
