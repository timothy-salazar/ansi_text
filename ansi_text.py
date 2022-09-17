""" 
Timothy Salazar
2022-09-16
"""
from collections.abc import Sequence
import re


class AnsiText(Sequence):
    """ Ansi text thing
    """
    def __init__(self):
        """ things and stuff
        """
        self.text = ''
        self.format_str = ''
        self.format_dict = dict()
        self.raw = ''

    def __getitem__(self, index):
        return self.text[index]

    def __len__(self):
        return len(self.text)
    
    def __str__(self):
        return self.raw

    def read(self, raw):
        """
        """
        get_char_expression = r'''
        \x1b\[          # This begins the escape sequence
        (?:[0-9]{1,3};)+? # semicolon-separated parameters
        [0-9]{1,3}m     # final parameter
        (?P<char>.+?)     # the printable character
        (?=\x1b\[0m)        # resets everything back
        '''
        r = re.compile(get_char_expression, re.VERBOSE)
        r.findall(raw)
        self.raw = raw
        self.text = ''.join(r.findall(raw))


    # def __str__(self):
    #     print(self.text)