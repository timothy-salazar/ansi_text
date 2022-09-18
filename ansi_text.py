""" 
Timothy Salazar
2022-09-16
"""
from collections.abc import MutableSequence
import re


class AnsiText(MutableSequence):
    """ Reads in text that has had formatting applied using ANSI escape
    sequences (colored foreground, colored background, bold, underline, etc.).
    The text can then be accessed and manipulated in a number of ways.
        - The characters of the unformatted text can be 
    """
    def __init__(self):
        """ things and stuff
        """
        self.plaintext = []
        self.format_str = ''
        self.format_dict = dict()
        # self.raw = ''
        self.regex = ''
        self.regex_stuff()
        self.slice_dict = dict()

    def __getitem__(self, index):
        return self.plaintext[index]

    def __setitem__(self, index, value):
        # temp = list(self.plaintext)
        # temp[index] = value
        # self.plaintext = ''.join(temp)
        self.plaintext = self.plaintext[:index] + value + self.plaintext[index+1:]

    def __delitem__(self, index):
        # del self.plaintext[index]
        pass

    def insert(self, index, value):
        # self.plaintext.insert(index, value)
        pass

    def __len__(self):
        return len(self.plaintext)

    def __str__(self):
        # return ''.join(self.format_dict.values())
        # return self.raw
        return self.format_str.format(*[
            ''.join(self.plaintext[v])
            for v in self.format_dict.values()])

    def read(self, raw):
        """ 
        """
        # self.raw = raw
        matches = [i for i in re.finditer(self.regex, raw)]
        # self.plaintext = ''.join([m.group('text') for m in matches])

        get_group = lambda m, name: m.group(name) if m.group(name) else ''
        self.format_str = ''.join(
            [get_group(m, 'fmt') + f'{{{v}}}' + get_group(m, 'end')
             for v, m in enumerate(matches)])
        # self.format_dict = {v:m.group('text') for v, m in enumerate(matches)}
        # self.format_dict = {v:m.group('text') for v, m in enumerate(matches)}

        # self.slice_dict = {v:slice(m.start('text'), m.end('text')) for v,m in enumerate(matches)}

        s = ''
        for v, m in enumerate(matches):
            # t = list(m.group('text'))
            t = m.group('text')
            self.format_dict[v] = slice(len(s), len(s)+len(t))
            s += t
        self.plaintext = s

    def regex_stuff(self):
        """ Builds the regular expression we'll use to process our text.
        I put it down here to keep things tidy.
        """

        ctr_seq = r'''
            \x1b\[          # This marks the start of a control sequence
            ([0-9]{1,3};)*? # semicolon-separated parameters
            [0-9]{1,3}m     # final parameter
        '''
        end = fr'''
          (?P<end>      # group name
              {ctr_seq} # matches a control sequence
           )*\Z         # This makes it so we'll always match the end, even if
        '''             #   the string doesn't end with a control sequence

        tst = fr'''(?mxs)       # Sets MULTILINE, VERBOSE, and DOTALL flags
            (
                (?P<fmt>({ctr_seq})+)  # matches one or more control sequences
                |(?=[^\x1b])?   # This lets us skip ahead when the string 
            )                   # doesn't begin with a control sequence
            (?P<text>.+?)       # The plaintext
            ({end}              # Either a control sequence ending the string or None
            |(?={ctr_seq}))     # Looks ahead for control sequences not 
        '''                     # ending the string
        self.regex = tst
