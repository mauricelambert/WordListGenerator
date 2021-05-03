#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package build a custom WordList (BruteForce).
#    Copyright (C) 2021  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""This package build a custom WordList (BruteForce).

>>> import io
>>> wordlist = WordList(
...     {
...         "%(123)": PatternEnumerator("123", "123", False, None),
...         "%(aAbBc)": PatternEnumerator("aAbBc", "A[a-c]B", False, None),
...         "%(words)": PatternEnumerator("words", "(word1|word2)", False, None),
...         "%(file)": PatternEnumerator("file", None, True, "test.txt"),
...     },
...     max_words=5
... )
>>> wordlist.output = io.StringIO()
>>> wordlist.output.close = lambda: None
>>> wordlist.patterns["%(123)"].build_chars()
>>> wordlist.patterns["%(aAbBc)"].build_chars()
>>> wordlist.patterns["%(words)"].build_chars()
>>> wordlist.patterns["%(file)"].build_chars()
>>> wordlist.run("A%(aAbBc)B%(file)C%(num)%(words)D")
>>> len(wordlist.output.getvalue().split())
5
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__url__ = 'https://github.com/mauricelambert/WordListGenerator'

__all__ = ["PatternEnumerator", "WordList"]

copyright = """
WordListGenerator  Copyright (C) 2021  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__copyright__ = copyright
__description__ = "This package build a custom WordList (BruteForce)."

print(copyright)

# python3 -m doctest -v WordList.py

from string import ascii_uppercase, ascii_lowercase, digits, punctuation
from re import search, compile as recompile
from argparse import ArgumentParser
from typing import TypeVar, Tuple
from dataclasses import dataclass
from time import perf_counter
from sys import exit
from os import path
import sys
import io

ascii_visible = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

StringOrNone = TypeVar("StringOrNone", str, None)

@dataclass
class PatternEnumerator:
    name: str
    chars: str
    is_file: bool
    filename: str

    def build_chars(self):

        """This function build list of characters from pattern.

        >>> p = PatternEnumerator("1", "a[1-3]B", False, None)
        >>> p.build_chars()
        >>> len(p.chars)
        5
        >>> p = PatternEnumerator("1", "B[3-1]a", False, None)
        >>> p.build_chars()
        >>> len(p.chars)
        5
        >>> p = PatternEnumerator("1", None, True, "filename.txt")
        >>> p.build_chars()
        >>> p.chars
        """

        if not self.is_file:
            chars = set()
            regex = recompile(r"\[.\-.\]")

            for result in regex.finditer(self.chars):
                pattern = result.group()
                
                start = ord(pattern[1])
                end = ord(pattern[3])

                if start > end:
                    start, end = end, start

                for char in range(start, end + 1):
                    chars.add(chr(char))

                self.chars = self.chars.replace(pattern, "", 1)

            regex = recompile(r'\((\w+\|)+\w+\)')

            for result in regex.finditer(self.chars):
                pattern = result.group()

                for word in pattern[1:-1].split('|'):
                    chars.add(word)

                self.chars = self.chars.replace(pattern, "", 1)
            
            for char in self.chars:
                chars.add(char)

            self.chars = chars

    def get_values(self, encoding: str="utf-8", delimiter: str="\n"):

        """Generator to return values from pattern.

        >>> p = PatternEnumerator("1", {'1', '2'}, False, None)
        >>> print(*sorted(p.get_values()))
        1 2
        >>> p = PatternEnumerator("file", None, True, "test.txt")
        >>> list_ = list(p.get_values()); print(list_[0])
        abcc1
        >>> len(list_)
        5
        """

        if self.is_file:
            with open(self.filename, encoding="utf-8") as file:
                word = self.get_word_from_file(file, delimiter)
                while word:
                    yield word
                    word = self.get_word_from_file(file, delimiter)
        else:
            yield from self.chars

    def get_word_from_file(self, file: io.TextIOWrapper, delimiter: str="\n"):

        """This function return word from custom WordList.

        >>> a = io.TextIOWrapper(io.BytesIO(b'abc\\n123\\ntest'))
        >>> p = PatternEnumerator("1", None, True, "filename.txt")
        >>> w=True
        >>> while w: print(w:=p.get_word_from_file(a))
        abc
        123
        test
        <BLANKLINE>
        >>> 
        """

        word = last = file.read(1)
        while last != delimiter and last:
            last = file.read(1)
            if last != delimiter:
                word += last

        return word

class WordList:

    """This class build custom WordList.

    >>> w = WordList({"%(1)": PatternEnumerator("1", {"1"}, False, None)})
    >>> w.run('AB%(1)')
    AB1
    >>> 
    """

    def __init__(self, patterns: dict, filename: str=None, delimiter: str = "\n", max_words: int=None, max_time: float=None, encoding: str="utf-8"):
        self.counter = 0
        self.max_time = max_time
        self.patterns = patterns
        self.encoding = encoding
        self.max_words = max_words
        self.delimiter = delimiter
        self.start_time = perf_counter()
        self.output = sys.stdout if filename is None else open(filename, 'w', encoding=encoding)
        self.regex = "(%s)" % '|'.join([f'%\\({patterns[name].name}\\)' for name in patterns.keys()])

    def run(self, string: str) -> None:

        """This function create wordlist.

        >>> w = WordList({"%(1)": PatternEnumerator("1", ["1", "2"], False, None)}, max_words=1)
        >>> w.run('AB%(1)')
        AB1
        >>> w = WordList({"%(1)": PatternEnumerator("1", ["1", "2"], False, None)}, max_time=0)
        >>> w.run('AB%(1)')
        AB1
        >>>
        """

        check_counter = self.max_words is not None
        check_time = self.max_time is not None

        for word in self.visit_pattern(string):
            self.counter += 1
            self.output.write(f'{word}{self.delimiter}')

            if (check_counter and self.counter >= self.max_words) or (check_time and perf_counter() - self.start_time > self.max_time):
                break

        if self.output is not sys.stdout:
            self.output.close()

    def visit_pattern(self, string: str) -> StringOrNone:

        """This function find first pattern in a string.

        >>> w = WordList({"%(1)": PatternEnumerator("1", ["1", "2"], False, None)})
        >>> for word in w.visit_pattern('AB%(1)'): print(word)
        AB1
        AB2
        >>> 
        """

        result = search(self.regex, string)

        if result is not None:
            yield from self.launch_pattern_loop(string, result.group())
        else:
            yield string

    def launch_pattern_loop(self, string: str, pattern: str) -> None:

        """This function get the PatternEnumerator, replace the pattern
        and call visit_pattern with the new string.

        >>> w = WordList({"%(1)": PatternEnumerator("1", ["1", "2"], False, None)})
        >>> for word in w.visit_pattern('AB%(1)'): print(word)
        AB1
        AB2
        >>> 
        """

        enumerator = self.patterns[pattern]

        for value in enumerator.get_values(self.encoding, self.delimiter):
            yield from self.visit_pattern(string.replace(pattern, value, 1))


def parse():

    """This function parse arguments."""

    parser = ArgumentParser()
    parser.add_argument("--pattern", "-p", help="[REQUIRED] Pattern to build the wordlist.", required=True)
    parser.add_argument("--wordlists", "-w", help="Add wordlists in pattern.", nargs="+", default=[])
    parser.add_argument("--patterns-enumerator", "-e", help="Add enumerators in pattern.", nargs="+", default=[])
    parser.add_argument("--encoding", "-E", help="Encoding for input files and output files.")
    parser.add_argument("--max-words", "-m", help="Wordlist length.", type=int)
    parser.add_argument("--max-time", "-t", help="Maximum time to build wordlist.", type=float)
    parser.add_argument("--delimiter", "-d", help="Change delimiter for input and output file.", default="\n")
    parser.add_argument("--filename", "-f", help="File to save the wordlist (default is terminal).")
    return parser.parse_args()


def _get_pattern_name(pattern: str) -> Tuple[str, str, str]:

    """This function split the pattern to get name, values or 
    build pattern from name."""

    values = None
    if "=" in pattern:
        pattern, values = pattern.split("=", 1)

    if pattern[:2] == "%(" and pattern[-1] == ")":
        name = pattern[2:-1]
    else:
        name, pattern = pattern, f'%({pattern})'

    if values is None:
        values = name

    return pattern, name, values


def main() -> None:
    args = parse()

    patterns = {
        "%(digits)": PatternEnumerator("digits", digits, False, None),
        "%(punctuation)": PatternEnumerator("punctuation", punctuation, False, None),
        "%(ascii_uppercase)": PatternEnumerator("ascii_uppercase", ascii_uppercase, False, None),
        "%(ascii_lowercase)": PatternEnumerator("ascii_lowercase", ascii_lowercase, False, None),
        "%(ascii_visible)": PatternEnumerator("ascii_visible", ascii_visible, False, None),
    }
    for pattern in args.patterns_enumerator:

        pattern, name, values = _get_pattern_name(pattern)
        
        patterns[pattern] = PatternEnumerator(name, values, False, None)
        patterns[pattern].build_chars()

    for wordlist in args.wordlists:

        pattern, name, values = _get_pattern_name(wordlist)

        if not path.exists(values):
            print(
                f"Error: file {values} doesn't exist (wordlist argument: {wordlist})."
            )
            exit(1)

        patterns[pattern] = PatternEnumerator(name, None, True, values)

    wordlist = WordList(
        patterns,
        args.filename,
        args.delimiter,
        args.max_words,
        args.max_time,
        args.encoding,
    )
    wordlist.run(args.pattern)


if __name__ == "__main__":
    main()