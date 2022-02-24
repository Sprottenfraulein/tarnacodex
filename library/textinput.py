# Accepts keys and returns changed text
from library import logfun


def do_edit(char_unicode, orig_string, maxlen, letters=True, numbers=True, log=True):

    logfun.put(char_unicode, log)

    if ((letters and numbers and char_unicode.isalnum())
            or (letters and not numbers and char_unicode.isalpha())
            or (not letters and numbers and char_unicode.isdigit())):
        orig_string += char_unicode
        if maxlen > -1:
            orig_string = orig_string[:maxlen]
    elif char_unicode == '\u0008' and len(orig_string) > 0:
        orig_string = orig_string[:-1]
    return orig_string
