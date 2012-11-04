#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012  Hayaki Saito <user@zuse.jp>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****

import tff
import locale

################################################################################
#
# do_conversion
#
def convert(data, termenc = "UTF-8"):
    """ 
    >>> convert("")
    ''
    >>> convert("abc")
    'abc'
    >>> print convert("あいうえお")
    あいうえお
    >>> print convert('\xe3\x81\x82\xe3\x81\x84\xe3\x81\x86\xe3\x81\x88\xe3\x81\x8a')
    あいうえお
    >>> print convert('\xa4\xa2\xa4\xa4\xa4\xa6\xa4\xa8\xa4\xaa')
    あいうえお
    >>> print convert('\x82\xa0\x82\xa2\x82\xa4\x82\xa6\x82\xa8')
    あいうえお
    >>> print convert('\xa4\xa2\xa4\xa4\xa4\xa6\xa4\xa8\xa4\xaa\x82\xa0\x82\xa2\x82\xa4\x82\xa6\x82\xa8\xe3\x81\x82\xe3\x81\x84\xe3\x81\x86\xe3\x81\x88\xe3\x81\x8a')
    あいうえおあいうえおあいうえお
    >>> print convert('\x82\xa0\x82\xa2\x82\xa4\x82\xa6\x82\xa8\xe3\x81\x82\xe3\x81\x84\xe3\x81\x86\xe3\x81\x88\xe3\x81\x8a\xa4\xa2\xa4\xa4\xa4\xa6\xa4\xa8\xa4\xaa')
    あいうえおあいうえおあいうえお
    """
    output_parser = SequenceParser()
    output_context = ParseContext(termenc)
    output_context.assign(data)
    output_parser.parse(output_context)
    return output_context.getvalue()

def test():
    import doctest
    doctest.testmod()

def main():
    import sys, os, optparse, select
    # parse options and arguments
    parser = optparse.OptionParser(usage='usage: %prog [options] [command | - ]')

    parser.add_option('-t', '--term', dest='term',
                      help='override TERM environment variable')

    parser.add_option('-l', '--lang', dest='lang',
                      help='override LANG environment variable')

    parser.add_option('-o', '--outenc', dest='enc',
                      help='set output encoding')

    parser.add_option("-s", "--enable-skk",
                      action="store_true", dest="skk", default=False,
                      help="use SKK input method")

    (options, args) = parser.parse_args()

    # retrive starting command
    if len(args) > 0:
        command = args[0]
    elif not os.getenv('SHELL') is None:
        command = os.getenv('SHELL')
    else:
        command = '/bin/sh'

    # retrive TERM setting
    if not options.term is None:
        term = options.term
    elif not os.getenv('TERM') is None:
        term = os.getenv('TERM')
    else:
        term = 'xterm'

    # retrive LANG setting
    if not options.lang is None:
        lang = options.term
    elif not os.getenv('LANG') is None:
        lang = os.getenv('LANG')
    else:
        lang = 'ja_JP.UTF-8'

    # retrive terminal encoding setting
    if not options.enc is None:
        termenc = options.enc
    else:
        language, encoding = locale.getdefaultlocale()
        termenc = encoding

    # retrive skk setting
    if options.skk:
        import skk
        inputhandler = skk.InputHandler(sys.stdout, termenc)
        outputhandler = skk.OutputHandler()
    else:
        inputhandler = tff.DefaultHandler()
        outputhandler = tff.DefaultHandler()

    if command == '-':
        # wait for incoming data
        sys.stdout.write(convert(sys.stdin.read(), termenc))
        return
    else:
        # check if stdin is available
        if select.select([sys.stdin, ], [], [], 0.0)[0]:
            sys.stdout.write(convert(sys.stdin.read(), outenc))
            return

    import japanese
    settings = tff.Settings(command=command,
                            term=term,
                            lang=lang,
                            termenc=termenc,
                            stdin=sys.stdin,
                            stdout=sys.stdout,
                            inputscanner=tff.DefaultScanner(),#japanese.JapaneseScanner(),
                            inputparser=tff.DefaultParser(),
                            inputhandler=inputhandler,
                            outputscanner=tff.DefaultScanner(),#japanese.JapaneseScanner(),
                            outputparser=tff.DefaultParser(),
                            outputhandler=outputhandler)
    session = tff.Session()
    sys.stdout.write("\x1b]0;[jacot]\x1b\\")
    session.start(settings)

''' main '''
if __name__ == '__main__':    
    main()

