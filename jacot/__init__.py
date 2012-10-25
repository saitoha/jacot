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

"""
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

.. Options:

  -h, --help            show this help message and exit
  -t TERM, --term=TERM  override TERM environment variable
  -l LANG, --lang=LANG  override LANG environment variable
  -o ENC, --outenc=ENC  set output encoding

.. Example:

... 1. Create auto-conversion TTY session, like cocot.

.... code-block:: bash

 $ LANG=ja_JP.UTF-8 $SHELL
 $ echo 'あいうえお今日は≠〆＞' | iconv -t cp932
 ???????????????́??Y??
 $ jacot
 $ echo 'あいうえお今日は≠〆＞' | iconv -t cp932
 あいうえお今日は≠〆＞


... 2. Read from stdin, without TTY session, just like nkf.

.... code-block:: bash

 $ LANG=ja_JP.UTF-8 $SHELL
 $ '三 ┏( ^o^)┛' | iconv -t eucjp | jacot
 三 ┏( ^o^)┛

... 3. Set terminal encoding

.... code-block:: bash

 $ LANG=ja_JP.EUC-JP $SHELL
 $ jacot -o eucjp
 $ '三 ┏( ^o^)┛' | iconv -t sjis
 三 ┏( ^o^)┛


"""

__author__  = "Hayaki Saito (user@zuse.jp)"
__version__ = "0.1.0"
__license__ = "GPL v3"

import jacot

def main():
    jacot.start()

