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

_eisuudb = [[u'0' , u'０'], [u'1' , u'１'], [u'2' , u'２'], [u'3' , u'３'], [u'4' , u'４'], [u'5' , u'５'],
            [u'6' , u'６'], [u'7' , u'７'], [u'8' , u'８'], [u'9' , u'９'], [u'^' , u'＾'], [u'@' , u'＠'],
            [u'[' , u'［'], [u']' , u'］'], [u':' , u'：'], [u';' , u'；'], [u',' , u'，'], [u'.' , u'．'],
            [u'/' , u'／'], [u'_' , u'＿'], [u'*' , u'＊'], [u'!' , u'！'], [u'#' , u'＃'], [u'$' , u'＄'],
            [u'%' , u'％'], [u'&' , u'＆'], [u'(' , u'（'], [u')' , u'）'], [u'=' , u'＝'], [u'~' , u'〜'],
            [u'|' , u'｜'], [u'{' , u'｛'], [u'}' , u'｝'], [u'+' , u'＋'], [u'*' , u'＊'], [u'<' , u'＜'],
            [u'>' , u'＞'], [u'?' , u'？'], [u'A' , u'Ａ'], [u'B' , u'Ｂ'], [u'C' , u'Ｃ'], [u'D' , u'Ｄ'],
            [u'E' , u'Ｅ'], [u'F' , u'Ｆ'], [u'G' , u'Ｇ'], [u'H' , u'Ｈ'], [u'I' , u'Ｉ'], [u'J' , u'Ｊ'],
            [u'K' , u'Ｋ'], [u'L' , u'Ｌ'], [u'M' , u'Ｍ'], [u'N' , u'Ｎ'], [u'O' , u'Ｏ'], [u'P' , u'Ｐ'],
            [u'Q' , u'Ｑ'], [u'R' , u'Ｒ'], [u'S' , u'Ｓ'], [u'T' , u'Ｔ'], [u'U' , u'Ｕ'], [u'V' , u'Ｖ'],
            [u'W' , u'Ｗ'], [u'X' , u'Ｘ'], [u'Y' , u'Ｙ'], [u'Z' , u'Ｚ'], [u'a' , u'ａ'], [u'b' , u'ｂ'],
            [u'c' , u'ｃ'], [u'd' , u'ｄ'], [u'e' , u'ｅ'], [u'f' , u'ｆ'], [u'g' , u'ｇ'], [u'h' , u'ｈ'],
            [u'i' , u'ｉ'], [u'j' , u'ｊ'], [u'k' , u'ｋ'], [u'l' , u'ｌ'], [u'm' , u'ｍ'], [u'n' , u'ｎ'],
            [u'o' , u'ｏ'], [u'p' , u'ｐ'], [u'q' , u'ｑ'], [u'r' , u'ｒ'], [u's' , u'ｓ'], [u't' , u'ｔ'],
            [u'u' , u'ｕ'], [u'v' , u'ｖ'], [u'w' , u'ｗ'], [u'x' , u'ｘ'], [u'y' , u'ｙ'], [u'z' , u'ｚ']]

_han_to_zen = {}
_han_to_zen_cp = {}

for han, zen in _eisuudb:
    _han_to_zen[han] = zen
    _han_to_zen_cp[ord(han)] = ord(zen)
 
def to_zenkaku(s):
    ''' convert ascii string into Japanese Zenkaku string '''
    def conv(c):
        if _han_to_zen.has_key(c):
            return _han_to_zen[c]
        return c
    return ''.join([conv(c) for c in s])

def to_zenkaku_cp(code):
    ''' convert some ascii code points into Japanese Zenkaku code points '''
    if _han_to_zen_cp.has_key(code):
        return _han_to_zen_cp[code]
    return code

