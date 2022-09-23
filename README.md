# ANSI Text
This repo contains code for reading and manipulating text that has had formatting applied using ANSI escape sequences (colored foreground, colored background, bold, underline, etc.).

This isn't really all that useful for composing ANSI formatted text, it's
more of a utility for easily editing text that already has had ANSI
formatting applied to it. Once text has been read into an AnsiText object, the text can then be accessed and manipulated in a number of ways. 

## Reading text into AnsiText object:
If you have a string of text that already has ANSI formatting applied to it, you can read it into an AnsiText object when the AnsiText object is created:
```python
>>> text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
>>> atext = AnsiText(text)
```

or by using the 'read' method:
```python
>>> text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
>>> atext.read(text)
```

## Reading from AnsiText object:
Operations that use the __str__() method, such as print() or str(), will receive the formatted text. If you use str(), you'll be able to see the escape sequences used to format the text. If you use print(), the colored string will be visible in your terminal:
![](./images/atext_read.png)

The unformatted text can be accessed using the 'text' attribute:
```python
>>> text = '\x1b[38;5;12mANSI formatted text\x1b[0m'
>>> atext = AnsiText(text)
>>> atext.text
ANSI formatted text
```
## Editing AnsiText object:
When the text is read into the AnsiText object it will detect if the formatting changes through the string. The plaintext and formatting information for each of these is stored in an AnsiSubString object. 

These substrings can be accessed either through the groups attribute, or by indexing into the AnsiText object. This also allows for item assignment, which will replace the plaintext for a given group while retaining the ANSI formatting.

![](./images/atext_groups.png)


