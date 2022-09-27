""" Tools to make it easier to read and edit ANSI formatted text
"""
import re

def get_regex():
    """ Input:
            None
        Output:
            ansi_re: raw string

    This just builds the regular expression we use separate any ANSI formatting
    from the associated text.
    I made it a function rather than a method to:
        - keep things tidy
        - make it easier to import elsewhere, if needed
    """
    # This matches control sequences
    ctr_seq = r'''
        \x1b\[          # This marks the start of a control sequence
        ([0-9]{1,3};)*? # semicolon-separated parameters
        [0-9]{1,3}m     # final parameter
    '''

    # This matches either any control sequences that occur at the end of the
    # string, or an empty string if the string doesn't have any control
    # sequences at the end
    end = fr'''
        (?P<end>        # group name
            {ctr_seq}   # matches control sequences
        )*\Z            # <- Always match the end, even if the string doesn't  
    '''                 # end with a control sequence

    ansi_re = fr'''(?mxs)   # Sets MULTILINE, VERBOSE, and DOTALL flags
        (
            (?P<fmt>({ctr_seq})+)  # Matches one or more control sequences
            |(?=[^\x1b])?   # This lets us skip ahead when the string
        )                   # doesn't begin with a control sequence
        (?P<text>.+?)       # The p slaintext
        ({end}              # Either a control sequence ending the string or None
        |(?={ctr_seq}))     # Looks ahead for control sequences not
    '''                     # ending the string
    return ansi_re

class AnsiSubString:
    """ Contains text, along with any ANSI formatting which has been applied to
    it.

    The formatted text can be accessed by the __str__ method (i.e., calling
    str() or print() on it). The plaintext can be accessed through the 'text'
    attribute. If self.text is replaced, the new text will have the
    same formatting applied to it.
    """
    def __init__(self, match: re.Match):
        get_group = lambda m, name: m.group(name) if m.group(name) else ''
        self.fmt = get_group(match, 'fmt') + '{}' + get_group(match, 'end')
        self._text = list(match.group('text'))

    def __str__(self):
        return self.fmt.format(self.text)

    def __repr__(self):
        return f'< AnsiSubString: {self.text!r} >'

    def __len__(self):
        return len(self._text)

    def __getitem__(self, index):
        return ''.join(self._text[index])

    def __setitem__(self, index, value):
        self._text[index] = value

    @property
    def text(self):
        "the plaintext for this substring"
        return ''.join(self._text)

    @text.setter
    def text(self, value):
        self._text = list(value)

class AnsiText():
    """ Class for reading and manipulating ANSI formatted text.

    Reads in text that has had formatting applied using ANSI escape
    sequences (colored foreground, colored background, bold, underline, etc.).
    This isn't really all that useful for composing ANSI formatted text, it's
    more of a utility for easily editing text that already has had ANSI
    formatting applied to it.
    """
    def __init__(self, raw=None, groups=None, index_groups=True):
        self.index_groups = index_groups
        if groups:
            self.groups = groups
        else:
            self.groups = []
        if raw:
            self.read(raw)

    def __repr__(self):
        return f'< AnsiText: {self.text!r} >'

    def __str__(self):
        " This returns the ANSI formatted text in its entirity "
        return ''.join([str(i) for i in self.groups])

    def read(self, raw):
        """ Input:
                raw: str - the raw text we want to process

        Reads in text and uses a regular expression to find matches, which are
        then used to create AnsiSubString objects. These contain the unformatted
        text along with the ANSI formatting information.
        """
        ansi_re = get_regex()
        self.groups = [AnsiSubString(match)
                       for match in re.finditer(ansi_re, raw)]

    def __getitem__(self, index):
        if self.index_groups:
            return self.groups[index]
        else:
            return self.text[index]

    def __setitem__(self, index, value):
        # This is the EASY way to do things
        if self.index_groups:
            self.groups[index].text = value
            return
        # This is a little messier, but better than anything else I came up
        # with. Also: kinda sad we have to copy this list
        text_list = [text for group in self.groups for text in group._text]
        text_list[index] = value
        for group in self.groups:
            text_len = len(group)
            group._text = text_list[:text_len]
            text_list = text_list[text_len:]

    def __delitem__(self, index):
        if self.index_groups:
            del self.groups[index]

    def __add__(self, other):
        return AnsiText(groups=(self.groups + other.groups))

    def __len__(self):
        return len(self.text)

    @property
    def text(self):
        " Returns the plaintext for all groups "
        return ''.join([i.text for i in self.groups])

    @property
    def fmt(self):
        """ Returns a list of formattable strings.
        They have the form:
            "<ANSI formatting>{}<more ANSI formatting>"
        where the <ANSI formatting> chunks are optional.
        """
        return [i.fmt for i in self.groups]
