from ansi_text import AnsiText

def test_basic():
    "Most basic test case"
    text = 'some basic text'
    ansi_text = AnsiText()
    ansi_text.read(text)
    assert str(AnsiText) == text
    assert ansi_text.format_str == ''
    assert ansi_text.format_dict == dict()

def test_one_color_foreground():
    "Tests string with one type of formatting applied throughout"
    text = '\x1b[38;5;12mstuff\x1b[0m'
    ansi_text = AnsiText()
    ansi_text.read(text)
    assert str(AnsiText) == text
    assert ansi_text.format_str == '\x1b[38;5;12m{0}\x1b[0m'
    assert ansi_text.format_dict == {0:'stuff'}
    
def test_two_color_foreground():
    """ tests string with one type of formatting applied to the first half,
    and a second type of formatting applied to the second half
    """
    text = '\x1b[38;5;12mstuff\x1b[0m\x1b[38;5;9mthings\x1b[0m'
    ansi_text = AnsiText()
    ansi_text.read(text)
    assert str(AnsiText) == text
    assert ansi_text.format_str == '\x1b[38;5;12m{0}\x1b[0m\x1b[38;5;9m{1}\x1b[0m'
    assert ansi_text.format_dict == {0:'stuff', 1:'things'}


def test_indexing_basic():
    " tests whether we can index into the string properly"
    text = 'some basic text'
    ansi_text = AnsiText()
    ansi_text.read(text)
    assert ansi_text[:] == text
    assert ansi_text[0] == 's'
    assert ansi_text[:6] == 'some b'
    assert ansi_text[-1] == 't'

def test_indexing_colored_text():
    " tests whether we can index into a string with basic ansi formatting"
    text = '\x1b[38;5;12mstuff\x1b[0m'
    ansi_text = AnsiText()
    ansi_text.read(text)
    assert ansi_text[:] == 'stuff'
    assert ansi_text[0] == 's'
    assert ansi_text[:3] == 'stu'
    assert ansi_text[-1] == 'f'

def test_indexing_two_color_text():
    " tests whether we can index into a string with basic ansi formatting"
    text = '\x1b[38;5;12mstuff\x1b[0m\x1b[38;5;9mthings\x1b[0m'
    ansi_text = AnsiText()
    ansi_text.read(text)
    assert ansi_text[:] == 'stuffthings'
    assert ansi_text[0] == 's'
    assert ansi_text[:7] == 'stuffth'
    assert ansi_text[-2] == 'g'
