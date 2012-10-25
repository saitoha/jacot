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

import sys, os, errno, signal, fcntl, select, pty, termios
import struct
import optparse
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
                if (0x40 <= c and c <= 0x7e) or (0x80 <= c and c <= 0xfc):
                   yield ord((chr(self.__cp932_state) + x).decode('cp932'))
                   self.__cp932_state = 0
                   self.__eucjp_state = 0
                   self.__count = 0
                   #self.__hint = HINT_CP932
                   continue     
                self.__cp932_state = 0
            if self.__count != 0 and self.__eucjp_state != 0:
                if 0xa1 <= c and c <= 0xfe:
                   yield ord((chr(self.__eucjp_state) + x).decode('eucjp'))
                   self.__cp932_state = 0
                   self.__eucjp_state = 0
                   self.__count = 0
                   #self.__hint = HINT_EUCJP
                   continue     
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
                    if self.__count != 0 and self.__cp932_state != 0:
                        if 0x40 <= c and c <= 0x7e:
                           yield ord((chr(self.__cp932_state) + x).decode('cp932'))
                           self.__cp932_state = 0
                           self.__eucjp_state = 0
                           self.__count = 0
                           #self.__hint = HINT_CP932
                           continue     
                        self.__cp932_state = 0
                    self.__utf8_state = self.__utf8_state << 6 | c & 0x3f
                    self.__count -= 1
                    if self.__count == 0:
                        if self.__utf8_state < 0x80:
                            yield 0x3f
                        else:
                            yield self.__utf8_state
                        self.__count = 0
                        self.__utf8_state = 0
                        #self.__hint = HINT_UTF8
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
# Parser implementation
#
STATE_GROUND = 0
STATE_ESC = 1
STATE_ESC_FINAL = 2

STATE_CSI_PARAMETER = 3
STATE_CSI_INTERMEDIATE = 4
STATE_CSI_FINAL = 5

STATE_OSC = 6
STATE_STR = 7 

class SequenceParser(tff.Parser):
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


def start_session(stdin, stdout, command, term, lang, termenc):
    parser = SequenceParser()
    context = ParseContext(termenc)
    stdin_fileno = stdin.fileno()
    vdisable = os.fpathconf(stdin_fileno, 'PC_VDISABLE')
    backup = termios.tcgetattr(stdin_fileno)
    try:
        new = termios.tcgetattr(stdin_fileno)
        new[3] = new[3] &~ (termios.ECHO | termios.ICANON)
        new[6][termios.VINTR] = vdisable
        #new[6][termios.VQUIT] = vdisable
        new[6][termios.VSUSP] = vdisable
        termios.tcsetattr(stdin_fileno, termios.TCSANOW, new)
        pid, master = pty.fork()
        if not pid:
            os.environ['TERM'] = term 
            os.environ['LANG'] = lang 
            os.execlp('/bin/sh',
                      '/bin/sh', '-c',
                      'cd $HOME && exec %s' % command)

        try:
            def resize():
                winsize = fcntl.ioctl(stdin_fileno, termios.TIOCGWINSZ, 'hhhh')
                height, width = struct.unpack('hh', winsize)
                winsize = struct.pack('HHHH', height, width, 0, 0)
                fcntl.ioctl(master, termios.TIOCSWINSZ, winsize)
                # notify Application process that terminal size has been changed.
                os.kill(pid, signal.SIGWINCH)
                return height, width

            signal.signal(signal.SIGWINCH, lambda no, frame: resize())

            height, width = resize()
    
            stdin_fileno = stdin.fileno()
            rfds = [stdin_fileno, master]
            wfds = []
            xfds = [stdin_fileno, master]
            while True: 
                try:
                    rfd, wfd, xfd = select.select(rfds, wfds, xfds)
                    if xfd:
                        break
                    for fd in rfd:
                        if fd == stdin_fileno:
                            data = os.read(stdin_fileno, BUFFER_SIZE)
                            if not data:
                                break
                            os.write(master, data)
                        elif fd == master:
                            data = os.read(master, BUFFER_SIZE)
                            context.assign(data)
                            parser.parse(context)
                            stdout.write(context.getvalue())
                            stdout.flush()
                except select.error, e:
                    no, mst = e
                    if not no == errno.EINTR:
                        raise

        finally:
            os.close(master)

    finally:
        termios.tcsetattr(stdin_fileno, termios.TCSANOW, backup)

def do_conversion(stdin, stdout, termenc):
    parser = SequenceParser()
    data = os.read(stdin.fileno(), BUFFER_SIZE)
    context = ParseContext(termenc)
    context.assign(data)
    parser.parse(context)
    stdout.write(context.getvalue())


def start():
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

    if command == '-':
        # wait for incoming data
        do_conversion(sys.stdin, sys.stdout, outenc)
    else:
        # check if stdin is available
        if select.select([sys.stdin, ], [], [], 0.0)[0]:
            do_conversion(sys.stdin, sys.stdout, outenc)
        else:
            start_session(sys.stdin, sys.stdout, command, term, lang, outenc)

''' main '''
if __name__ == '__main__':    
    start()

