"""
Timothy Salazar
2022-09-16
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

    ansi_re = fr'''(?mxs)   # Sets MULTILINE, VERBOSE, and DOTALL flags
        (
            (?P<fmt>({ctr_seq})+)  # matches one or more control sequences
            |(?=[^\x1b])?   # This lets us skip ahead when the string
        )                   # doesn't begin with a control sequence
        (?P<text>.+?)       # The plaintext
        ({end}              # Either a control sequence ending the string or None
        |(?={ctr_seq}))     # Looks ahead for control sequences not
    '''                     # ending the string
    return ansi_re

class AnsiSubString:
    " A  "
    def __init__(self, match):
        get_group = lambda m, name: m.group(name) if m.group(name) else ''
        self.fmt = get_group(match, 'fmt') + '{}' + get_group(match, 'end')
        self.text = match.group('text')

    def __str__(self):
        return self.fmt.format(self.text)

    def __repr__(self):
        return f'< AnsiSubString: {self.text} >'

class AnsiText():
    """ Class for reading and manipulating ANSI formatted text.

    Reads in text that has had formatting applied using ANSI escape
    sequences (colored foreground, colored background, bold, underline, etc.).
    This isn't really all that useful for composing ANSI formatted text, it's
    more of a utility for easily editing text that already has had ANSI
    formatting applied to it.
    """
    def __init__(self, raw=None):
        self._text = None
        self.groups = []
        if raw:
            self.read(raw)

    def __repr__(self):
        return f'< AnsiText: {self.text} >'

    def __str__(self):
        return ''.join([str(i) for i in self.groups])

    def read(self, raw):
        " reads text, does regex "
        ansi_re = get_regex()
        self.groups = [AnsiSubString(match) 
            for match in re.finditer(ansi_re, raw)]
        # matches = [i for i in re.finditer(tst, raw)]
        # get_group = lambda m, name: m.group(name) if m.group(name) else ''
        # node = None
        # for m in matches:
        #     fmt = get_group(m, 'fmt') + '{}' + get_group(m, 'end')
        #     txt = m.group('text')
        #     if not node:
        #         self.node = SubString(txt, fmt, node)
        #         node = self.node
        #         # first_node = SubString(txt, fmt, node)
        #         # node = first_node
        #         # self.groups.append(node)
        #     else:
                # node = SubString(txt, fmt, node)
                # self.groups.append(node)
        # [for m in matches]

    def __getitem__(self, index):
        return self.groups[index]
        # if self.node:
        #     return self.node[index]

    def __setitem__(self, index, value):
        self.groups[index].text = value
        # if self.node:
        #     self.node[index] = value
        # else:
        #     raise ValueError

    @property
    def text(self):
        " returns the plaintext "
        if self.groups:
            return ''.join([i.text for i in self.groups])
        else:
            return ''

# class AnsiText(MutableSequence):
#     """ Reads in text that has had formatting applied using ANSI escape
#     sequences (colored foreground, colored background, bold, underline, etc.).
#     This isn't really all that useful for composing ANSI formatted text, it's
#     more of a utility for easily editing text that already has had ANSI
#     formatting applied to it.
#     The text can then be accessed and manipulated in a number of ways. For the
#     examples below, assume you have an AnsiText object called 'atext'

#     Reading text into AnsiText object:
#         - If you have a string of text that already has ANSI formatting applied
#           to it, you can read it into an AnsiText object when the AnsiText
#           object is created:
#                 > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
#                 > atext = AnsiText(text)
#           or by using the 'read' method:
#                 > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
#                 > atext.read(text)

#     Reading from AnsiText object:
#         - Operations such as print() or str() which use the __str__() method
#           will receive the formatted text
#                 > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
#                 > atext.read(text)
#                 > str(atext)
#                     '\x1b[38;5;12mANSI formatted text\x1b[0m'
#         - The unformatted text is available as the 'plaintext' attribute
#                 > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
#                 > atext.read(text)
#                 > atext.plaintext
#                     'ANSI formatted text'
#         - The unformatted text can also be accessed through indexing
#                 > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
#                 > atext.read(text)
#                 > atext[:]
#                     'ANSI formatted text'
#                 > atext[5:11]
#                     'format'

#     Writing to AnsiText object:
#         - The text can also be edited using slice assignment:
#                 > text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
#                 > atext.read(text)
#                 > atext[:4] = ':D'
#                 > str(atext)
#                     '\x1b[38;5;12m:D formatted text\x1b[0m'

#     """
#     def __init__(self, raw: str = None):
#         """ things and stuff
#         """
#         self.plaintext = ''
#         self.format_str = ''
#         self.format_dict = dict()
#         self.regex = ''
#         self.regex_stuff()
#         self.start_node = None
#         # self.slice_dict = dict()
#         if raw:
#             self.read(raw)


#     def __getitem__(self, index):
#         return self.plaintext[index]

#     def __setitem__(self, index, value):
#         # print('Index:', index)
#         # print('Value:', value)
#         # print('Plaintext start:', self.plaintext)
#         if isinstance(index, int):
#             # print('piece_1:', self.plaintext[:index])
#             # print('piece_2:', self.plaintext[index:])
#             # self.plaintext = self.plaintext[:index] + \
#             #     value + self.plaintext[index:]
#             first_part = slice(None, index)
#             last_part = slice(index+1, None) if (index != -1) else slice(-1, -1)
#         elif isinstance(index, slice):
#             if index.step:
#                 raise ValueError(
#                     '''Slicing AnsiText objects with a step argument is not
#                     currently supported''')
#             first_part = slice(None, index.start) if index.start else slice(0, 0)
#             last_part = slice(index.stop, None) if index.stop else slice(-1, -1)
#         else:
#             raise ValueError(f'''
#                 Unexpected value passed as index to AnsiText object:
#                 {index}''')
#             # self.plaintext = self.plaintext[:index.start if index.start else 0]\
#             #     + value + (self.plaintext[index.stop:]  if index.stop else '')
#         # print('first slice:', first_part)
#         # print('-->', self.plaintext[first_part])
#         # print('last slice:', last_part)
#         # print('-->', self.plaintext[last_part])
#         self.plaintext = self.plaintext[first_part] \
#             + value + self.plaintext[last_part]
#         # print('Plaintext end:', self.plaintext)

#     def __delitem__(self, index):
#         # del self.plaintext[index]
#         pass

#     def insert(self, index, value):
#         # self.plaintext.insert(index, value)
#         pass

#     def __len__(self):
#         return len(self.plaintext)

#     def __str__(self):
#         # return ''.join(self.format_dict.values())
#         # return self.raw
#         return self.format_str.format(*[
#             ''.join(self.plaintext[v])
#             for v in self.format_dict.values()])

#     def read(self, raw):
#         """
#         """
#         # self.raw = raw
#         matches = [i for i in re.finditer(self.regex, raw)]
#         # self.plaintext = ''.join([m.group('text') for m in matches])

#         get_group = lambda m, name: m.group(name) if m.group(name) else ''
#         self.format_str = ''.join(
#             [get_group(m, 'fmt') + f'{{{v}}}' + get_group(m, 'end')
#              for v, m in enumerate(matches)])
#         # self.format_dict = {v:m.group('text') for v, m in enumerate(matches)}
#         # self.format_dict = {v:m.group('text') for v, m in enumerate(matches)}

#         # self.slice_dict = {v:slice(m.start('text'), m.end('text')) for v,m in enumerate(matches)}


#         s = ''
#         for v, m in enumerate(matches):
#             t = m.group('text')
#             self.format_dict[v] = slice(len(s), len(s)+len(t))
#             s += t
#         self.plaintext = s

#         # # This will make extra text added to 'plaintext' later unformatted
#         # self.format_dict[len(matches)] = slice(len(s), None)
#         # self.format_str += f'{{{len(matches)}}}'

#         node = None
#         for v, m in enumerate(matches):
#             fmt = get_group(m, 'fmt') + '{}' + get_group(m, 'end')
#             txt = m.group('text')

#             if not node:
#                 self.start_node = SliceThing(text=txt, format_str=fmt)
#                 node = self.start_node
#             else:
#                 node = SliceThing(text=txt, prev=node, format_str=fmt)



#     def regex_stuff(self):
#         """ Builds the regular expression we'll use to process our text.
#         I put it down here to keep things tidy.
#         """

#         ctr_seq = r'''
#             \x1b\[          # This marks the start of a control sequence
#             ([0-9]{1,3};)*? # semicolon-separated parameters
#             [0-9]{1,3}m     # final parameter
#         '''
#         end = fr'''
#           (?P<end>      # group name
#               {ctr_seq} # matches a control sequence
#            )*\Z         # This makes it so we'll always match the end, even if
#         '''             #   the string doesn't end with a control sequence

#         tst = fr'''(?mxs)       # Sets MULTILINE, VERBOSE, and DOTALL flags
#             (
#                 (?P<fmt>({ctr_seq})+)  # matches one or more control sequences
#                 |(?=[^\x1b])?   # This lets us skip ahead when the string
#             )                   # doesn't begin with a control sequence
#             (?P<text>.+?)       # The plaintext
#             ({end}              # Either a control sequence ending the string or None
#             |(?={ctr_seq}))     # Looks ahead for control sequences not
#         '''                     # ending the string
#         self.regex = tst
# class SubString:
#     """ like an ansi string, but bite sized :) """
#     def __init__(self, text, fmt, prev=None,):
#         self.text = text
#         self.fmt = fmt
#         # self.prev = prev
#         self.next = None
#         if prev:
#             prev.next = self
#             self.index = prev.index + 1
#         else:
#             self.index = 0

#     def __repr__(self):
#         return f'< SubString: {self.text} >'

#     def __str__(self):
#         return self.fmt.format(self.text)

#     def __getitem__(self, index):
#         if isinstance(index, slice):
#             within_lower_bound = (not index.start) or (index.start <= self.index)
#             within_upper_bound = (not index.stop) or (index.stop >= self.index)
#             if within_lower_bound and within_upper_bound:
#                 if self.next:
#                     return self.text + self.next.__getitem__(index)
#                 else:
#                     return self.text
#             if not within_lower_bound:
#                 if self.next:
#                     return self.next.__getitem__(index)
#                 else:
#                     IndexError('SubString index out of range')
#             if not within_upper_bound:
#                 return

#         if index == self.index:
#             return self
#         elif self.next:
#             return self.next.__getitem__(index)
#         else:
#             raise IndexError('SubString index out of range')

#     def __setitem__(self, index, text):
#         if not isinstance(index, int):
#             raise ValueError('''
#             Type SubString does not support slices for item assignment''')
#         if index == self.index:
#             self.text = text
#         elif self.next:
#             return self.next.__setitem__(index, text)
#         else:
#             raise IndexError('SubString index out of range')

#     def get_text(self):
#         "gets the formatted text for this and all child nodes"
#         formatted_text = self.fmt.format(self.text)
#         if self.next:
#             return formatted_text + self.next.get_text()
#         else:
#             return formatted_text