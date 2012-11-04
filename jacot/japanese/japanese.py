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

HINT_UTF8 = 0
HINT_CP932 = 1
HINT_EUCJP = 2

################################################################################
#
# Japanese Scanner implementation
#
class JapaneseScanner(tff.Scanner):

    __data = None
    __utf8_state = 0
    __cp932_state = 0
    __eucjp_state = 0
    __count = 0
    __hint = HINT_UTF8 

    def assign(self, value, termenc):
        self.__data = list(value)
        self.__utf8_state = 0
        self.__cp932_state = 0
        self.__eucjp_state = 0

        self.__count = 0

    def __iter__(self):
        for x in self.__data:
            c = ord(x)
            if self.__count != 0 and self.__cp932_state != 0:
                if 0x40 <= c and c <= 0xfc:
                    try:
                        self.__cp932_state = ord((chr(self.__cp932_state) + x).decode('cp932'))
                        if self.__count == 1:
                            yield self.__cp932_state
                            self.__cp932_state = 0
                            self.__eucjp_state = 0
                            self.__utf8_state = 0
                            self.__count = 0
                            continue     
                    except:
                        pass
                self.__hint = HINT_UTF8
                self.__cp932_state = 0
            if self.__count != 0 and self.__eucjp_state != 0:
                if 0xa1 <= c and c <= 0xfe:
                    try:
                        yield ord((chr(self.__eucjp_state) + x).decode('eucjp'))
                        self.__cp932_state = 0
                        self.__eucjp_state = 0
                        self.__count = 0
                        self.__hint = HINT_EUCJP
                        continue     
                    except:
                        pass
                self.__eucjp_state = 0
            if c < 0x80:
                # 0xxxxxxx
                self.__utf8_state = 0
                self.__count = 0
                yield c
            elif c >> 6 == 0x02:
                # 10xxxxxx
                if self.__count == 0:
                    if 0x81 <= c and c <= 0x9f: # cp932 first
                        self.__cp932_state = c
                    elif 0xa1 <= c and c <= 0xa8: # eucjp first
                        self.__eucjp_state = c
                    elif c == 0xad: # eucjp first NEC
                        self.__eucjp_state = c
                    elif 0xb0 <= c: # eucjp first
                        self.__eucjp_state = c
                    else:
                        yield 0x3f # ?
                    self.__count = 1
                    self.__utf8_state = 0
                else:
                    self.__utf8_state = self.__utf8_state << 6 | c & 0x3f
                    self.__count -= 1
                    if self.__count == 0:
                        if self.__utf8_state < 0x80:
                            yield 0x3f
                        else:
                            self.__hint = HINT_UTF8
                            yield self.__utf8_state
                        self.__count = 0
                        self.__utf8_state = 0
            elif c >> 5 == 0x06:
                # 110xxxxx 10xxxxxx
                if self.__count != 0:
                    self.__count = 0
                    yield 0x3f
                else:
                    self.__utf8_state = c & 0x1f
                    self.__count = 1
                    self.__eucjp_state = c
            elif c >> 4 == 0x0e:
                # 1110xxxx 10xxxxxx 10xxxxxx
                if self.__count != 0:
                    self.__count = 0
                    yield 0x3f
                else:
                    self.__utf8_state = c & 0x0f
                    self.__count = 2
                    if self.__hint == HINT_CP932:
                        self.__cp932_state = c
                    if self.__hint == HINT_EUCJP:
                        self.__eucjp_state = c
            elif c >> 3 == 0x1e:
                # 11110xxx
                if self.__count != 0:
                    self.__count = 0
                    yield 0x3f
                else:
                    self.__utf8_state = c & 0x07
                    self.__count = 3
                    if c & 0x07 <= 0x4:
                        self.__eucjp_state = c
            elif c >> 2 == 0x3e:
                # 111110xx
                if self.__count != 0:
                    self.__count = 0
                    yield 0x3f
                else:
                    self.__utf8_state = c & 0x03
                    self.__count = 4
                    self.__eucjp_state = c
            elif c >> 1 == 0x7e:
                # 1111110x
                if self.__count != 0:
                    self.__count = 0
                    yield 0x3f
                else:
                    self.__utf8_state = c & 0x01
                    self.__count = 5
                    if c & 0x01 == 0:
                        self.__eucjp_state = c


