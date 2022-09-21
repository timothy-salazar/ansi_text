""" 
Timothy Salazar
2022-09-16
"""
from collections.abc import MutableSequence
import re

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


class SubString:
    def __init__(self, text, fmt, prev=None,):
        self.text = text
        self.fmt = fmt
        self.prev = prev
        self.next = None
        if prev:
            prev.next = self
            self.index = prev.index + 1
        else:
            self.index = 0

    def __getitem__(self, index):
        if index == self.index:
            return self
        elif self.next:
            return self.next.__getitem__(index)
        else:
            raise IndexError('SubString index out of range')

    def __setitem__(self, index, text):
        if not isinstance(index, int):
            raise ValueError('''
            Type SubString does not support slices for item assignment''')
        if index == self.index:
            self.text = text
        elif self.next:
            return self.next.__setitem__(index, text)
        else:
            raise IndexError('SubString index out of range')

class SliceThing():
    """ a slice thing
    """
    def __init__(self, text=None, prev=None, format_str=None):
        self.next = None
        self.prev = prev
        if prev:
            prev.next = self
            self.first = prev.first
            self.prev.last = self
            self.index = prev.index + len(text)
            # self.format_str = format_str
            # self._text = text
        else:
            self.index = 0
            self.first = self
            self.last = self
            # self.read(text)
        self.format_str = format_str
        self._text = text

    # def __repr__(self):
    #     return 

    def __str__(self):
        if self.next:
            return self.format_str.format(self._text) + str(self.next)
        return self.format_str.format(self._text)

    def read(self, raw):
        " reads text, does regex "
        matches = [i for i in re.finditer(tst, raw)]
        get_group = lambda m, name: m.group(name) if m.group(name) else ''
        node = None
        for m in matches:
            fmt = get_group(m, 'fmt') + '{}' + get_group(m, 'end')
            txt = m.group('text')
            if not node:
                self.format_str = fmt
                self._text = txt
                node = self
            else:
                node = SliceThing(text=txt, prev=node, format_str=fmt)

    def __getitem__(self, index):
        return self.text[index]

    def __setitem__(self, index, value):
        if isinstance(index, int):
            first_part = slice(None, index)
            last_part = slice(index+1, None) if (index != -1) else slice(-1, -1)
        elif isinstance(index, slice):
            if index.step:
                raise ValueError(
                    '''Slicing SliceThing objects with a step argument is not
                    currently supported''')
            first_part = slice(None, index.start) if index.start else slice(0, 0)
            last_part = slice(index.stop, None) if index.stop else slice(-1, -1)
        else:
            raise ValueError(f'''
                Unexpected value passed as index to SliceThing object:
                {index}''')
        self.text = self.text[first_part] + value + self.text[last_part]

    @property
    def last(self):
        " the last node in the list "
        return self._last

    @last.setter
    def last(self, value):
        self._last = value
        if self.prev:
            self.prev.last = value

    @property
    def text(self):
        " returns he plaintext "
        if self.next:
            return self._text + self.next.text
        return self._text

    @text.setter
    def text(self, text):
        if not text:
            return
        text_len = len(self._text)
        if self.next:
            self._text = text[:text_len]
            self.next.text = text[text_len:]
        else:
            self._text = text

    @text.deleter
    def text(self):
        del self._text


    @property
    def groups(self):
        """ Input:
                index: int - the index of the group
        """
        return [self]

    #     inc = value - self.stop
    #     self._stop = value
    #     current_slice = self.next
    #     while True:
    #         if not current_slice:
    #             break
    #         current_slice.inc_start(inc)
    #         current_slice.inc_stop(inc)
    #         current_slice = current_slice.next

    # def overwrite(self, text: str):
    #     ''' Input:
    #             text: str - the text which we want to replace self.text with.

    #     Takes 'text' and overwrites self.text with it.
    #     If 'text' is longer than self.text, then the remainder is passed to
    #     self.next, and the process repeats.
    #     The length of self.text will be the same before and after this operation
    #     unless:
    #         - 'text' is shorter than self.text
    #         - self.next does not exist
    #     In both cases, self.text will be set to equal 'text', causing the length
    #     of self.text to decrease in the first case, and causing it to either
    #     decrease or increase in the second case (assuming they have different
    #     lengths, obviously).
    #     '''
    #     if not text:
    #         return
    #     l = len(self.text)
    #     if self.next:
    #         self.text = text[:l]
    #         self.next.overwrite(text[l:])
    #     else:
    #         self.text = text

    # def inc_start(self, val):
    #     "add val to the start index"
    #     self.start += val

    # def inc_stop(self, val):
    #     "add val to the stop index"
    #     self._stop += val

    # @property
    # def stop(self):
    #     " The index at which this slice ends "
    #     return self._stop

    # @stop.setter
    # def stop(self, value):
    #     inc = value - self.stop
    #     self._stop = value
    #     current_slice = self.next
    #     while True:
    #         if not current_slice:
    #             break
    #         current_slice.inc_start(inc)
    #         current_slice.inc_stop(inc)
    #         current_slice = current_slice.next

    ## This isn't needed, so removing it
    # @property
    # def start(self):
    #     " The index at which this slice begins "
    #     return self._start

    # @start.setter
    # def start(self, value):
    #     inc = value - self.start
    #     self._start = value
    #     current_slice = self.prev
    #     while True:
    #         if not current_slice:
    #             break
    #         current_slice.inc_start(inc)
    #         current_slice.inc_stop(inc)
    #         current_slice = current_slice.prev




class AnsiText(MutableSequence):
    """ Reads in text that has had formatting applied using ANSI escape
    sequences (colored foreground, colored background, bold, underline, etc.).
    This isn't really all that useful for composing ANSI formatted text, it's
    more of a utility for easily editing text that already has had ANSI
    formatting applied to it.
    The text can then be accessed and manipulated in a number of ways. For the
    examples below, assume you have an AnsiText object called 'atext'

    Reading text into AnsiText object:
        - If you have a string of text that already has ANSI formatting applied
          to it, you can read it into an AnsiText object when the AnsiText
          object is created:
                > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
                > atext = AnsiText(text)
          or by using the 'read' method:
                > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
                > atext.read(text)

    Reading from AnsiText object:
        - Operations such as print() or str() which use the __str__() method
          will receive the formatted text
                > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
                > atext.read(text)
                > str(atext)
                    '\x1b[38;5;12mANSI formatted text\x1b[0m'
        - The unformatted text is available as the 'plaintext' attribute
                > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
                > atext.read(text)
                > atext.plaintext
                    'ANSI formatted text'
        - The unformatted text can also be accessed through indexing
                > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
                > atext.read(text)
                > atext[:]
                    'ANSI formatted text'
                > atext[5:11]
                    'format'

    Writing to AnsiText object:
        - The text can also be edited using slice assignment:
                > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
                > atext.read(text)
                > atext[:4] = ':D'
                > str(atext)
                    '\x1b[38;5;12m:D formatted text\x1b[0m'

    """
    def __init__(self, raw: str = None):
        """ things and stuff
        """
        self.plaintext = ''
        self.format_str = ''
        self.format_dict = dict()
        self.regex = ''
        self.regex_stuff()
        self.start_node = None
        # self.slice_dict = dict()
        if raw:
            self.read(raw)
        

    def __getitem__(self, index):
        return self.plaintext[index]

    def __setitem__(self, index, value):
        # print('Index:', index)
        # print('Value:', value)
        # print('Plaintext start:', self.plaintext)
        if isinstance(index, int):
            # print('piece_1:', self.plaintext[:index])
            # print('piece_2:', self.plaintext[index:])
            # self.plaintext = self.plaintext[:index] + \
            #     value + self.plaintext[index:]
            first_part = slice(None, index)
            last_part = slice(index+1, None) if (index != -1) else slice(-1, -1)
        elif isinstance(index, slice):
            if index.step:
                raise ValueError(
                    '''Slicing AnsiText objects with a step argument is not
                    currently supported''')
            first_part = slice(None, index.start) if index.start else slice(0, 0)
            last_part = slice(index.stop, None) if index.stop else slice(-1, -1)
        else:
            raise ValueError(f'''
                Unexpected value passed as index to AnsiText object:
                {index}''')
            # self.plaintext = self.plaintext[:index.start if index.start else 0]\
            #     + value + (self.plaintext[index.stop:]  if index.stop else '')
        # print('first slice:', first_part)
        # print('-->', self.plaintext[first_part])
        # print('last slice:', last_part)
        # print('-->', self.plaintext[last_part])
        self.plaintext = self.plaintext[first_part] \
            + value + self.plaintext[last_part]
        # print('Plaintext end:', self.plaintext)

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
            t = m.group('text')
            self.format_dict[v] = slice(len(s), len(s)+len(t))
            s += t
        self.plaintext = s

        # # This will make extra text added to 'plaintext' later unformatted
        # self.format_dict[len(matches)] = slice(len(s), None)
        # self.format_str += f'{{{len(matches)}}}'

        node = None
        for v, m in enumerate(matches):
            fmt = get_group(m, 'fmt') + '{}' + get_group(m, 'end')
            txt = m.group('text')
            
            if not node:
                self.start_node = SliceThing(text=txt, format_str=fmt)
                node = self.start_node
            else:
                node = SliceThing(text=txt, prev=node, format_str=fmt)



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
