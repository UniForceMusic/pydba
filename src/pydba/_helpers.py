def escape_ansi(string: str, chars: str) -> str:
    return string.translate(str.maketrans(chars, chars * 2))

def escape_backslash(string: str, chars: str) -> str:
    return string.translate(str.maketrans(chars, "\\" + chars))
