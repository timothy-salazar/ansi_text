""" Tests for pytest """
import re
import textwrap
from ansi_text import AnsiText, get_regex


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

class TestWrite:
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
