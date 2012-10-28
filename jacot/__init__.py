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

"""=====================================================
jacot - Japanese Auto character set Conversion On Tty
=====================================================

This module Provides the auto-conversion filter
supports well-known Japanese Encodings(CP932/EUC-JP).

Install
-------

.. code-block:: bash

    $ git clone https://github.com/saitoha/jacot.git
    $ cd jacot
    $ python setup.py install

Usage
-----

.. code-block:: bash

    $ jacot.py [options] [command | -]

- Options:

    -h, --help            show this help message and exit
    -t TERM, --term=TERM  override TERM environment variable
    -l LANG, --lang=LANG  override LANG environment variable
    -o ENC, --outenc=ENC  set output encoding

- Example:

... 1. Create auto-conversion TTY session, like cocot.::

    $ LANG=ja_JP.UTF-8 $SHELL
    $ echo 'あいうえお今日は≠〆＞' | iconv -t cp932
    ???????????????́??Y??
    $ jacot
    $ echo 'あいうえお今日は≠〆＞' | iconv -t cp932
    あいうえお今日は≠〆＞


... 2. Read from stdin, without TTY session, just like nkf.::

    $ LANG=ja_JP.UTF-8 $SHELL
    $ echo '三 ┏( ^o^)┛' | iconv -t eucjp | jacot
    三 ┏( ^o^)┛

... 3. Set terminal output encoding::

    $ LANG=ja_JP.EUC-JP $SHELL
    $ jacot -o eucjp
    $ echo '三 ┏( ^o^)┛' | iconv -t sjis
    三 ┏( ^o^)┛


"""

__author__  = "Hayaki Saito (user@zuse.jp)"
__version__ = "0.1.1"
__license__ = "GPL v3"

import jacot

def main():
    import sys, os, optparse, select
    # parse options and arguments
    parser = optparse.OptionParser(usage='usage: %prog [options] [command | - ]')

    parser.add_option('-t', '--term', dest='term',
                      help='override TERM environment variable')

    parser.add_option('-l', '--lang', dest='lang',
                      help='override LANG environment variable')

    parser.add_option('-o', '--outenc', dest='enc', default='UTF-8',
                      help='set output encoding')

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
    outenc = options.enc

    settings = jacot.Settings(command, term, lang, outenc, sys.stdin, sys.stdout)

    if command == '-':
        # wait for incoming data
        sys.stdout.write(jacot.convert(sys.stdin.read(), outenc))
    else:
        # check if stdin is available
        if select.select([sys.stdin, ], [], [], 0.0)[0]:
            sys.stdout.write(jacot.convert(sys.stdin.read(), outenc))
        else:
            jacot.Session().start(settings)

''' main '''
if __name__ == '__main__':    
    main()

