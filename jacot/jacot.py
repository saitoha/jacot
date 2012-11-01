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

import sys, os
import traceback
import codecs
try:
    from cStringIO import StringIO
except:
    try:
        from StringIO import StringIO
    except:
        from io import StringIO

# TFF
import tff

BUFFER_SIZE = 1024

################################################################################
#
# Dispatcher implementation
#

HINT_UTF8 = 0
HINT_CP932 = 1
HINT_EUCJP = 2

class ParseContext(tff.OutputStream, tff.EventDispatcher):

    __scanner = None
    __handler = None
    __output = None

    def __init__(self, termenc = 'UTF-8', handler = tff.DefaultHandler()):
        self.__scanner = JapaneseScanner()
        self.__handler = handler
        self.__output = codecs.getwriter(termenc)(StringIO())

    def __iter__(self):
        return self.__scanner.__iter__()

    def assign(self, data):
        self.__scanner.assign(data)
        self.__output.truncate(0)

# OutputStream
    def write(self, c):
        if c < 0x80:
            self.__output.write(chr(c))
        else:
            try:
                self.__output.write(unichr(c))
            except:
                self.__output.write('?')

    def getvalue(self):
        return self.__output.getvalue()

# EventDispatcher
    def dispatch_esc(self, prefix, final):
        self.__handler.handle_esc(self, prefix, final)

    def dispatch_csi(self, parameter, intermediate, final):
        self.__handler.handle_csi(self, parameter, intermediate, final)

    def dispatch_control_string(self, prefix, value):
        self.__handler.handle_control_string(self, prefix, value)

    def dispatch_char(self, c):
        self.__handler.handle_char(self, c)

################################################################################
#
# Scanner implementation
#
class JapaneseScanner(tff.Scanner):

    __data = None
    __utf8_state = 0
    __cp932_state = 0
    __eucjp_state = 0
    __count = 0
    __hint = HINT_UTF8 

    def assign(self, value):
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

################################################################################
#
# OutputParser implementation
#
STATE_GROUND = 0
STATE_ESC = 1
STATE_ESC_FINAL = 2

STATE_CSI_PARAMETER = 3
STATE_CSI_INTERMEDIATE = 4
STATE_CSI_FINAL = 5

STATE_OSC = 6
STATE_STR = 7 

class SequenceOutputParser(tff.Parser):
    ''' parse ESC/CSI/string seqneces '''

    __parse_state = STATE_GROUND
    __csi_parameter = [] 
    __csi_intermediate = [] 
    __esc_prefix = [] 
    __str = [] 
    __str_prefix = None 
    __str_esc_state = False

    def __init__(self):
        pass

    def parse(self, context):
        for c in context:
            if self.__parse_state == STATE_OSC:
                # parse control string
                if c == 0x1b:
                    self.__str_esc_state = True
                elif c == 0x5c and self.__str_esc_state == True:
                    context.dispatch_control_string(self.__str_prefix, self.__str)
                    self.__parse_state = STATE_GROUND
                elif c == 0x07:
                    context.dispatch_control_string(self.__str_prefix, self.__str)
                    self.__parse_state = STATE_GROUND
                elif c < 0x20:
                    self.__parse_state = STATE_GROUND
                else:
                    self.__str.append(c)

            elif self.__parse_state == STATE_STR:
                # parse control string
                if c == 0x1b:
                    self.__str_esc_state = True
                elif c == 0x5c and self.__str_esc_state == True:
                    context.dispatch_control_string(self.__str_prefix, self.__str)
                    self.__parse_state = STATE_GROUND
                elif c < 0x20:
                    self.__parse_state = STATE_GROUND
                else:
                    self.__str.append(c)

            elif c == 0x1b: # ESC
                self.__esc_prefix = []
                self.__parse_state = STATE_ESC

            elif c < 0x20 or c == 0x7f: # control character
                context.dispatch_char(c)
                self.__parse_state = STATE_GROUND

            elif self.__parse_state == STATE_ESC:
                if c == 0x5b: # [
                    self.__csi_parameter = []
                    self.__csi_intermediate = [] 
                    self.__parse_state = STATE_CSI_PARAMETER
                elif c == 0x5d: # ]
                    self.__str_esc_state = False
                    self.__str = [] 
                    self.__str_prefix = c 
                    self.__parse_state = STATE_OSC
                elif c == 0x50 or c == 0x5e or c == 0x5f: # P or ^ or _
                    self.__str_esc_state = False
                    self.__str = []
                    self.__str_prefix = c 
                    self.__parse_state = STATE_STR
                elif 0x20 <= c or c <= 0x2f: # SP to /
                    self.__esc_prefix.append(c)
                    self.__parse_state = STATE_ESC_FINAL
                else:
                    context.dispatch_esc(self.__esc_prefix, c)
                    self.__parse_state = STATE_GROUND

            elif self.__parse_state == STATE_ESC_FINAL:
                context.dispatch_esc(self.__esc_prefix, c)
                self.__parse_state = STATE_GROUND

            elif self.__parse_state == STATE_CSI_PARAMETER:
                # parse control sequence
                #
                # CSI P ... P I ... I F
                #     ^
                if 0x30 <= c and c <= 0x3f: # parameter, 0 to ?
                    self.__csi_parameter.append(c)
                elif 0x20 <= c and c <= 0x2f: # intermediate, SP to /
                    self.__csi_intermediate.append(c)
                    self.__parse_state = STATE_CSI_INTERMEDIATE
                elif 0x40 <= c and c <= 0x7e: # Final byte, @ to ~
                    context.dispatch_csi(self.__csi_parameter,
                                         self.__csi_intermediate,
                                         c)
                    self.__parse_state = STATE_GROUND
                else:
                    self.__parse_state = STATE_GROUND

            elif self.__parse_state == STATE_CSI_INTERMEDIATE:
                # parse control sequence
                #
                # CSI P ... P I ... I F
                #             ^
                if 0x20 <= c and c <= 0x2f: # intermediate, SP to /
                    self.__csi_intermediate.append(c)
                    self.__parse_state = STATE_CSI_INTERMEDIATE
                elif 0x40 <= c and c <= 0x7e: # Final byte, @ to ~
                    context.dispatch_csi(self.__csi_parameter,
                                         self.__csi_intermediate,
                                         c)
                    self.__parse_state = STATE_GROUND
                else:
                    self.__parse_state = STATE_GROUND

            else:
                context.dispatch_char(c)


 
################################################################################
#
# Settings
#
class Settings:

    command = None
    term = None
    lang = None
    stdin = None
    stdout = None
    termenc = None

    def __init__(self, command, term, lang, termenc, stdin, stdout):
        self.command = command
        self.term = term
        self.lang = lang
        self.termenc = termenc
        self.stdin = stdin
        self.stdout = stdout


################################################################################
#
# Session
#
class Session:

    def start(self, settings):
        tty = tff.DefaultPTY(settings)
        output_context = ParseContext(settings.termenc)
        output_parser = SequenceOutputParser()
        stdout = settings.stdout
        for idata, odata in tty.drive():
            if idata:
                tty.write(idata)
            if odata:
                output_context.assign(odata)
                output_parser.parse(output_context)
                stdout.write(output_context.getvalue())
                stdout.flush()

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
    output_parser = SequenceOutputParser()
    output_context = ParseContext(termenc)
    output_context.assign(data)
    output_parser.parse(output_context)
    return output_context.getvalue()

def test():
    import doctest
    doctest.testmod()

''' main '''
if __name__ == '__main__':    
    test()

