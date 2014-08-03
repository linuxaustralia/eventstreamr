import string


#
# Quote a string for the shell, if necessary.
#
def shellquote(s, quote="'"):
    if s == "":
        if quote == '"':
            return '""'
        return "''"
    if not s[0] in SHELLQUOTE_1ST:
        if not " " in s.translate(SHELLQUOTE_TRANS):
            return s
    if quote == "'":
        s = quote + s.replace(quote, quote + "\\" + quote + quote) + quote
    elif quote == '"':
        s = s.replace("\\", "\\\\").replace(quote, "\\" + quote)
        s = s.replace("$", "\\$")
        s = quote + s + quote
    else:
        for c in SHELLQUOTE_MAGIC:
            s = s.replace(c, "\\" + c)
        if s[0] in SHELLQUOTE_1ST:
            s = "\\" + s
    return s
SHELLQUOTE_MAGIC = "\\'\" \n\t`$&*{}()[]|;<>?"
SHELLQUOTE_1ST = "~!#%"
SHELLQUOTE_TRANS = len(SHELLQUOTE_MAGIC)
SHELLQUOTE_TRANS = string.maketrans(SHELLQUOTE_MAGIC, " " * SHELLQUOTE_TRANS)
