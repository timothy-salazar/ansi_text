import re
import textwrap
from ansi_text import AnsiText


CLEAR = '\x1b[0m'

class TestBasic:
    """ Basic test cases where we provide AnsiText with input
    and examine the output
    """
    def test_basic(self):
        "Most basic test case"
        raw = 'some basic text'
        ansi_text = AnsiText()
        ansi_text.read(raw)
        assert str(ansi_text) == raw
        assert ansi_text.plaintext == raw
        assert ansi_text.format_str == '{0}'
        # assert ansi_text.format_dict == {0:raw}

    def test_one_color_foreground(self):
        "Tests string with one type of formatting applied throughout"
        text = '\x1b[38;5;12mstuff\x1b[0m'
        ansi_text = AnsiText()
        ansi_text.read(text)
        assert str(ansi_text) == text
        assert ansi_text.plaintext == 'stuff'
        assert ansi_text.format_str == '\x1b[38;5;12m{0}\x1b[0m'
        # assert ansi_text.format_dict == {0:'stuff'}

    def test_one_color_no_end(self):
        "Tests string with one type of formatting, no end"
        text = '\x1b[38;5;12mstuff'
        ansi_text = AnsiText()
        ansi_text.read(text)
        assert str(ansi_text) == text
        assert ansi_text.plaintext == 'stuff'
        assert ansi_text.format_str == '\x1b[38;5;12m{0}'
        # assert ansi_text.format_dict == {0:'stuff'}

    def test_one_color_partway_through(self):
        "Tests string with one type of formatting, no end"
        text = 'things and\x1b[38;5;12mstuff\x1b[0m'
        ansi_text = AnsiText()
        ansi_text.read(text)
        assert str(ansi_text) == text
        assert ansi_text.format_str == '{0}\x1b[38;5;12m{1}\x1b[0m'
        # assert ansi_text.format_dict == {0:'things and', 1:'stuff'}

    def test_one_color_partway_through_no_end(self):
        "Tests string with one type of formatting, no end"
        text = 'things and\x1b[38;5;12mstuff'
        ansi_text = AnsiText()
        ansi_text.read(text)
        assert str(ansi_text) == text
        assert ansi_text.plaintext == 'things andstuff'
        assert ansi_text.format_str == '{0}\x1b[38;5;12m{1}'
        # assert ansi_text.format_dict == {0:'things and', 1:'stuff'}
        
    def test_two_color_foreground(self):
        """ tests string with one type of formatting applied to the first half,
        and a second type of formatting applied to the second half
        """
        text = '\x1b[38;5;12mstuff\x1b[0m\x1b[38;5;9mthings\x1b[0m'
        ansi_text = AnsiText()
        ansi_text.read(text)
        assert str(ansi_text) == text
        assert ansi_text.plaintext == 'stuffthings'
        assert ansi_text.format_str == '\x1b[38;5;12m{0}\x1b[0m\x1b[38;5;9m{1}\x1b[0m'
        # assert ansi_text.format_dict == {0:'stuff', 1:'things'}

class TestIndexing:
    """ Testing whether AnsiText indexing works as expected
    """
    def test_indexing_basic(self):
        " tests whether we can index into the string properly"
        text = 'some basic text'
        ansi_text = AnsiText()
        ansi_text.read(text)
        assert ansi_text[:] == 'some basic text'
        assert ansi_text[0] == 's'
        assert ansi_text[:6] == 'some b'
        assert ansi_text[-1] == 't'

    def test_indexing_colored_text(self):
        " tests whether we can index into a string with basic ansi formatting"
        text = '\x1b[38;5;12mstuff\x1b[0m'
        ansi_text = AnsiText()
        ansi_text.read(text)
        assert ansi_text[:] == 'stuff'
        assert ansi_text[0] == 's'
        assert ansi_text[:3] == 'stu'
        assert ansi_text[-1] == 'f'

    def test_indexing_two_color_text(self):
        " tests whether we can index into a string with basic ansi formatting"
        text = '\x1b[38;5;12mstuff\x1b[0m\x1b[38;5;9mthings\x1b[0m'
        ansi_text = AnsiText()
        ansi_text.read(text)
        assert ansi_text[:] == 'stuffthings'
        assert ansi_text[0] == 's'
        assert ansi_text[:7] == 'stuffth'
        assert ansi_text[-2] == 'g'

class TestMutable:
    def test_overwrite(self):
        pass

########################
# Testing AnsiText regex
########################
class TestRegex:
    """ Tests whether the AnsiText regex functions as expected
    """
    def test_regex_basic(self):
        """ text with no formatting """
        text = 'some basic text'
        ansi_text = AnsiText()
        m = [i for i in re.finditer(ansi_text.regex, text)]
        assert [i.group('fmt') for i in m] == [None]
        assert [i.group('text') for i in m] == [text]
        assert [i.group('end') for i in m] == [None]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_basic_multiline(self):
        """ multiline text with no formatting """
        text = 'some basic text\nwith newlines and\nstuff!'
        ansi_text = AnsiText()
        m = [i for i in re.finditer(ansi_text.regex, text)]
        assert [i.group('fmt') for i in m] == [None]
        assert [i.group('text') for i in m] == [text]
        assert [i.group('end') for i in m] == [None]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_simple_color(self):
        """ text with minimal formatting """
        text = '\x1b[38;5;12mstuff\x1b[0m'
        ansi_text = AnsiText()
        m = [i for i in re.finditer(ansi_text.regex, text)]
        assert [i.group('fmt') for i in m] == ['\x1b[38;5;12m']
        assert [i.group('text') for i in m] == ['stuff']
        assert [i.group('end') for i in m] == [CLEAR]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_color_no_stop(self):
        """ text with a formatting start, but no clear statement"""
        text = '\x1b[38;5;12mstuff'
        ansi_text = AnsiText()
        m = [i for i in re.finditer(ansi_text.regex, text)]
        assert [i.group('fmt') for i in m] == ['\x1b[38;5;12m']
        assert [i.group('text') for i in m] == ['stuff']
        assert [i.group('end') for i in m]  == [None]
        assert len(m) == 1
        assert m[0].span() == (0, len(text))

    def test_regex_multicolor_no_stops(self):
        " text where the formatting changes without any clear statements"
        text = '\x1b[38;5;12mstuff\x1b[38;5;9mthings\x1b[38;5;14mdetritus'
        ansi_text = AnsiText()
        m = [i for i in re.finditer(ansi_text.regex, text)]
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
        ansi_text = AnsiText()
        m = [i for i in re.finditer(ansi_text.regex, text)]
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
        ansi_text = AnsiText()
        m = [i for i in re.finditer(ansi_text.regex, text)]
        assert [i.group('fmt') for i in m] == [
            '\x1b[38;5;12m',
            '\x1b[0m\x1b[38;5;9m']
        assert [i.group('text') for i in m] == [
            'stuff\nand ',
            'things\nand junk']
        assert [i.group('end') for i in m] == [None, CLEAR]
        assert len(m) == 2
        assert m[0].span() == (0, 20)
