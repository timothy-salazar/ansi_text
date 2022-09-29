""" Tests for pytest """
import re
import textwrap
from ansi_text.ansi_text import AnsiText, get_regex, AnsiSubString


CLEAR = '\x1b[0m'

class TestRead:
    """ Basic test cases where we provide AnsiText with input
    and examine the output
    """
    def test_empty(self):
        "empty string"
        raw = ''
        ansi_text = AnsiText(raw)
        assert str(ansi_text) == raw
        assert ansi_text.text == raw
        assert ansi_text.groups == []
        assert ansi_text.fmt == []

    def test_basic(self):
        "Most basic test case"
        raw = 'some basic text'
        ansi_text = AnsiText(raw)
        assert str(ansi_text) == raw
        assert ansi_text.text == raw
        assert len(ansi_text.groups) == 1
        assert ansi_text.fmt == ['{}']

    def test_one_color_foreground(self):
        "Tests string with one type of formatting applied throughout"
        raw = '\x1b[38;5;12mstuff\x1b[0m'
        ansi_text = AnsiText(raw)
        assert str(ansi_text) == raw
        assert ansi_text.text == 'stuff'
        assert ansi_text.fmt == ['\x1b[38;5;12m{}\x1b[0m']

    def test_one_color_no_end(self):
        "Tests string with one type of formatting, no end"
        raw = '\x1b[38;5;12mstuff'
        ansi_text = AnsiText(raw)
        assert str(ansi_text) == raw
        assert ansi_text.text == 'stuff'
        assert ansi_text.fmt == ['\x1b[38;5;12m{}']

    def test_one_color_partway_through(self):
        "Tests string with one type of formatting, no end"
        raw = 'things and\x1b[38;5;12mstuff\x1b[0m'
        ansi_text = AnsiText(raw)
        assert str(ansi_text) == raw
        assert ansi_text.text == 'things andstuff'
        assert ansi_text.fmt == ['{}', '\x1b[38;5;12m{}\x1b[0m']

    def test_one_color_partway_through_no_end(self):
        "Tests string with one type of formatting, no end"
        raw = 'things and\x1b[38;5;12mstuff'
        ansi_text = AnsiText(raw)
        assert str(ansi_text) == raw
        assert ansi_text.text == 'things andstuff'
        assert ansi_text.fmt == ['{}', '\x1b[38;5;12m{}']

    def test_two_color_foreground(self):
        """ tests string with one type of formatting applied to the first half,
        and a second type of formatting applied to the second half
        """
        raw = '\x1b[38;5;12mstuff\x1b[0m\x1b[38;5;9mthings\x1b[0m'
        ansi_text = AnsiText(raw)
        assert str(ansi_text) == raw
        assert ansi_text.text == 'stuffthings'
        assert ansi_text.fmt == [
            '\x1b[38;5;12m{}',
            '\x1b[0m\x1b[38;5;9m{}\x1b[0m']

class TestWriteIndexGroups:
    """ Tests to see if we're able to write to the AnsiText object as expected.
    """

    def test_write_1(self):
        ''' basic test overwriting group 0 '''
        text = '\x1b[38;5;12mstuff \x1b[0m\x1b[38;5;9mthings\x1b[0m'
        atext = AnsiText(text)
        atext[0] = 'dogs! '
        assert atext.text == 'dogs! things'
        assert str(atext) == '\x1b[38;5;12mdogs! \x1b[0m\x1b[38;5;9mthings\x1b[0m'

    def test_write_2(self):
        ''' basic test, overwriting last group '''
        text = '\x1b[38;5;12mstuff \x1b[0m\x1b[38;5;9mthings\x1b[0m'
        atext = AnsiText(text)
        atext[-1] = 'and doggos!'
        assert atext.text == 'stuff and doggos!'
        assert str(atext) == '\x1b[38;5;12mstuff \x1b[0m\x1b[38;5;9mand doggos!\x1b[0m'

    def test_write_3(self):
        '''testing deleting a group '''
        text = 'stuff\x1b[38;5;9mthings\x1b[0m'
        atext = AnsiText(text)
        del atext[0]
        assert atext.text == 'things'
        assert str(atext) == '\x1b[38;5;9mthings\x1b[0m'

class TestWriteNoGroups:

    def test_write_1(self):
        ''' basic tests writing to plaintext '''
        text = '\x1b[38;5;12mstuff \x1b[0m\x1b[38;5;9mthings\x1b[0m'
        atext = AnsiText(text,index_groups=False)
        atext[:5] = 'dogs!'
        atext[-1] = '!'
        assert atext.text == 'dogs! thing!'
        assert str(atext) == '\x1b[38;5;12mdogs! \x1b[0m\x1b[38;5;9mthing!\x1b[0m'

    def test_write_2(self):
        ''' more tests writing to plaintext '''
        text = '\x1b[38;5;12mstuff \x1b[0m\x1b[38;5;9mthings\x1b[0m'
        atext = AnsiText(text,index_groups=False)
        atext[5:] = 'dog'
        atext[:5] = 'good-'
        assert atext.text == 'good-dog'
        assert str(atext) == '\x1b[38;5;12mgood-d\x1b[0m\x1b[38;5;9mog\x1b[0m'

    def test_write_3(self):
        ''' more tests writing to plaintext '''
        text = '\x1b[38;5;12mstuff \x1b[0m\x1b[38;5;9mthings\x1b[0m'
        atext = AnsiText(text,index_groups=False)
        atext[5:] = 'dog'
        atext[0] = 'X'
        atext[-1] = 'X'
        assert atext.text == 'XtuffdoX'
        assert str(atext) == '\x1b[38;5;12mXtuffd\x1b[0m\x1b[38;5;9moX\x1b[0m'

class TestIndexing:
    """ Testing whether AnsiText indexing works as expected
    """
    def test_indexing_basic(self):
        " tests whether we can index into the string properly"
        text = 'some basic text'
        ansi_text = AnsiText(text, index_groups=False)
        assert ansi_text[:] == 'some basic text'
        assert ansi_text[0] == 's'
        assert ansi_text[:6] == 'some b'
        assert ansi_text[-1] == 't'
        assert ansi_text[::-1] == 'txet cisab emos'

    def test_indexing_colored_text(self):
        " tests whether we can index into a string with basic ansi formatting"
        text = '\x1b[38;5;12mstuff\x1b[0m'
        ansi_text = AnsiText(text, index_groups=False)
        assert ansi_text[:] == 'stuff'
        assert ansi_text[0] == 's'
        assert ansi_text[:3] == 'stu'
        assert ansi_text[-1] == 'f'
        assert ansi_text[::-1] == 'ffuts'

    def test_indexing_two_color_text(self):
        " tests whether we can index into a string with basic ansi formatting"
        text = '\x1b[38;5;12mstuff\x1b[0m\x1b[38;5;9mthings\x1b[0m'
        ansi_text = AnsiText(text, index_groups=False)
        assert ansi_text[:] == 'stuffthings'
        assert ansi_text[0] == 's'
        assert ansi_text[:7] == 'stuffth'
        assert ansi_text[-1] == 's'
        assert ansi_text[-2] == 'g'
        assert ansi_text[::-1] == 'sgnihtffuts'

########################
# Testing AnsiText regex
########################
class TestRegex:
    """ Tests whether the AnsiText regex functions as expected
    """
    def test_regex_basic(self):
        """ text with no formatting """
        text = 'some basic text'
        regex = get_regex()
        m = [i for i in re.finditer(regex, text)]
        assert [i.group('fmt') for i in m] == [None]
        assert [i.group('text') for i in m] == [text]
        assert [i.group('end') for i in m] == [None]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_basic_multiline(self):
        """ multiline text with no formatting """
        text = 'some basic text\nwith newlines and\nstuff!'
        regex = get_regex()
        m = [i for i in re.finditer(regex, text)]
        assert [i.group('fmt') for i in m] == [None]
        assert [i.group('text') for i in m] == [text]
        assert [i.group('end') for i in m] == [None]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_simple_color(self):
        """ text with minimal formatting """
        text = '\x1b[38;5;12mstuff\x1b[0m'
        regex = get_regex()
        m = [i for i in re.finditer(regex, text)]
        assert [i.group('fmt') for i in m] == ['\x1b[38;5;12m']
        assert [i.group('text') for i in m] == ['stuff']
        assert [i.group('end') for i in m] == [CLEAR]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_color_no_stop(self):
        """ text with a formatting start, but no clear statement"""
        text = '\x1b[38;5;12mstuff'
        regex = get_regex()
        m = [i for i in re.finditer(regex, text)]
        assert [i.group('fmt') for i in m] == ['\x1b[38;5;12m']
        assert [i.group('text') for i in m] == ['stuff']
        assert [i.group('end') for i in m]  == [None]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_multicolor_no_stops(self):
        " text where the formatting changes without any clear statements"
        text = '\x1b[38;5;12mstuff\x1b[38;5;9mthings\x1b[38;5;14mdetritus'
        regex = get_regex()
        m = [i for i in re.finditer(regex, text)]
        assert [i.group('fmt') for i in m] == [
            '\x1b[38;5;12m',
            '\x1b[38;5;9m',
            '\x1b[38;5;14m']
        assert [i.group('text') for i in m] == [
            'stuff',
            'things',
            'detritus']
        assert [i.group('end') for i in m] == [None, None, None]
        assert len(m) == 3
        assert m[0].span() == (0, 15)

    def test_regex_color_multiline(self):
        """ multiline text with minimal formatting"""
        text = textwrap.dedent('''\
            \x1b[38;5;12mstuff
            and things
            and junk\x1b[0m''')
        regex = get_regex()
        m = [i for i in re.finditer(regex, text)]
        assert [i.group('fmt') for i in m] == ['\x1b[38;5;12m']
        assert [i.group('text') for i in m] == ['stuff\nand things\nand junk']
        assert [i.group('end') for i in m] == [CLEAR]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_multicolor_multiline(self):
        """ multiline text which changes formatting """
        text = textwrap.dedent('''\
            \x1b[38;5;12mstuff
            and \x1b[0m\x1b[38;5;9mthings
            and junk\x1b[0m''')
        regex = get_regex()
        m = [i for i in re.finditer(regex, text)]
        assert [i.group('fmt') for i in m] == [
            '\x1b[38;5;12m',
            '\x1b[0m\x1b[38;5;9m']
        assert [i.group('text') for i in m] == [
            'stuff\nand ',
            'things\nand junk']
        assert [i.group('end') for i in m] == [None, CLEAR]
        assert len(m) == 2
        assert m[0].span() == (0, 20)

class TestSubString:
    """tests of substring read functionality"""
    def test_read_with_ansi(self):
        "does basic tests for ANSI formatted text"
        text = '\x1b[38;5;12mABCDEFG'
        regex = get_regex()
        match = re.match(regex, text)
        substring = AnsiSubString(match)
        assert substring.text == 'ABCDEFG'
        assert str(substring) == text
        assert substring._text == list('ABCDEFG')
        assert substring[0] == 'A'
        assert substring[-1] == 'G'
        assert substring[:3] == 'ABC'
        assert substring[:] == 'ABCDEFG'
        assert substring[::-1] == 'GFEDCBA'

    def test_write_with_ansi(self):
        "tests of substring write functionality"
        text = '\x1b[38;5;12mABCDEFG'
        regex = get_regex()
        match = re.match(regex, text)
        substring = AnsiSubString(match)
        substring[0] = '0'
        assert substring.text == '0BCDEFG'
        assert str(substring) == '\x1b[38;5;12m0BCDEFG'
        substring[:3] = '123'
        assert substring.text == '123DEFG'
        substring.text = 'DOG'
        assert substring[:] == 'DOG'
        assert substring.text == 'DOG'
        assert substring._text == list('DOG')
