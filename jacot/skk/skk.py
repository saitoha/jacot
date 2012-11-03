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

import sys
import os
import inspect
import re
import kanadb
import romanrule

from jacot import tff

tango_jisyo = {}
okuri_jisyo = {}
filename = inspect.getfile(inspect.currentframe())
dirpath = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
p = re.compile('^(.+?)([a-z])? /(.+)/')
for line in open(dirpath + '/SKK-JISYO.L'):
    if line[1] == ';':
        continue
    line = unicode(line, 'eucjp')
    g = p.match(line)
    key = g.group(1)
    okuri = g.group(2)
    value = g.group(3)
    if okuri is None:
        tango_jisyo[key] = value
    else:
        okuri_jisyo[key] = value

################################################################################
#
# CharacterContext
#
class CharacterContext:

    def __init__(self):
        self.__hira_tree = romanrule.makehiratree()
        self.__kata_tree = romanrule.makekatatree()
        self.__current_tree = self.__hira_tree
        self.reset()

    def switch_hira(self):
        self.__current_tree = self.__hira_tree

    def switch_kata(self):
        self.__current_tree = self.__kata_tree

    def reset(self):
        self.context = self.__current_tree

    def isempty(self):
        return self.context == self.__current_tree

    def isfinal(self):
        return self.context.has_key('value')

    def drain(self):
        if self.context.has_key('value'):
            s = self.context['value']
            if self.context.has_key('next'):
                self.context = self.context['next']
            else:
                self.reset()
            return s
        return u''

    def getbuffer(self):
        return self.context['buffer']

    def put(self, c):
        if self.context.has_key(c):
            self.context = self.context[c]
            return True
        return False

    def back(self):
        self.context = self.context['prev']

SKK_MODE_ASCII = 0
SKK_MODE_HIRAGANA = 1
SKK_MODE_KATAKANA = 2

COOK_MARK = u'▽'
SELECT_MARK = u'▼'
OKURI_MARK = u'*'

def trace(s):
    sys.stdout.write('\x1b]0;%s\x1b\\' % s)

################################################################################
#
# Candidate
#
class Candidate():

    def __init__(self):
        self.reset()

    def assign(self, value, okuri=u''):
        self.__index = 0
        self.__list = value.split(u'/')
        self.__okuri = okuri

    def reset(self):
        self.__index = 0
        self.__list = None
        self.__okuri = None

    def isempty(self):
        return self.__list == None

    def getcurrent(self):
        self.__index %= len(self.__list)
        value = self.__list[self.__index]

        # 補足説明
        index = value.find(";")
        if index >= 0:
            trace(value[index:])
            value = value[:index]

        return SELECT_MARK + value + self.__okuri

    def getwidth(self):
        if self.isempty():
            return 0
        return len(self.getcurrent()) * 2

    def movenext(self):
        self.__index += 1

    def moveprev(self):
        self.__index -= 1

################################################################################
#
# SKKHandler
#
class SKKHandler(tff.DefaultHandler):

    def __init__(self):
        self.__context = CharacterContext()
        self.__mode = SKK_MODE_ASCII
        self.__word_buffer = u'' 
        self.__candidate_buffer = Candidate()

    def __reset(self):
        self.__clear()
        self.__context.reset()
        self.__candidate_buffer.reset()
        self.__word_buffer = u'' 

    def __clear(self):
        candidate_length = self.__candidate_buffer.getwidth()
        cooking_length = len(self.__word_buffer) * 2 + len(self.__context.getbuffer())
        s = ' ' * max(candidate_length, cooking_length)
        sys.stdout.write('\x1b7%s\x1b8\x1b[?25h' % s)
        sys.stdout.flush()

    def __display(self):
        if not self.__candidate_buffer.isempty():
            value = self.__candidate_buffer.getcurrent()
            sys.stdout.write('\x1b7\x1b[1;4;32;44m%s\x1b8\x1b[?25l' % value)
        else:
            s1 = self.__word_buffer
            s2 = self.__context.getbuffer() 
            if not len(s1) + len(s2) == 0:
                sys.stdout.write('\x1b7\x1b[1;4;31m%s\x1b[1;4;33m%s\x1b8\x1b[?25l' % (s1, s2))
            else:
                sys.stdout.write('\x1b[?25h')
        sys.stdout.flush()

    def __fix(self):
        s = self.__context.getbuffer()
        if s == 'n':
            self.__context.put(0x6e) # n
        s = self.__context.drain()
        if len(self.__word_buffer) == 0:
            self.__word_buffer += COOK_MARK
        self.__word_buffer += s

    def __iscooking(self):
        if not self.__candidate_buffer.isempty():
            return True
        if len(self.__word_buffer) > 0:
            return True
        if not self.__context.isempty():
            return True
        return False

    def __convert_kana(self, value):
        if self.__mode == SKK_MODE_HIRAGANA:
            return kanadb.to_kata(value)
        elif self.__mode == SKK_MODE_KATAKANA:
            return kanadb.to_hira(value)
        else:
            raise

    def __toggle_kana(self):
        if self.__mode == SKK_MODE_HIRAGANA:
            self.__mode = SKK_MODE_KATAKANA
            self.__context.switch_kata()
        elif self.__mode == SKK_MODE_KATAKANA:
            self.__mode = SKK_MODE_HIRAGANA
            self.__context.switch_hira()
        else:
            raise
        self.__reset()

    def __tango_henkan(self):
        key = self.__word_buffer[1:]
        if tango_jisyo.has_key(key):
            self.__candidate_buffer.assign(tango_jisyo[key], u'')
            self.__clear()
            self.__display()
            return True
        return False

    def __okuri_henkan(self):
        #trace("okuri-henkan: " + self.__word_buffer)
        key, okuri = self.__word_buffer[1:].split(OKURI_MARK)
        if okuri_jisyo.has_key(key):
            self.__candidate_buffer.assign(okuri_jisyo[key], okuri)
            self.__clear()
            self.__word_buffer = u''
            return True
        elif tango_jisyo.has_key(key):
            self.__candidate_buffer.assign(tango_jisyo[key], okuri)
            self.__clear()
            self.__word_buffer = u''
            return True
        return False

    def __kakutei(self, context):
        self.__fix()
        if self.__candidate_buffer.isempty():
            word = self.__word_buffer[1:]
        else:
            word = self.__candidate_buffer.getcurrent()[1:]
        self.__reset()
        context.writestring(word)

    def handle_char(self, context, c):
        if c == 0x07:
            self.__reset()
        elif c == 0x0a: # LF C-j
            if self.__mode == SKK_MODE_ASCII:
                self.__mode = SKK_MODE_HIRAGANA
            else:
                if self.__iscooking():
                    self.__kakutei(context)
                else:
                    context.write(c)
        elif c == 0x0d: # CR C-m
            if self.__iscooking():
                self.__kakutei(context)
            else:
                context.write(c)
        elif c == 0x08 or c == 0x7f: # BS or DEL
            if self.__context.isempty():
                word = self.__word_buffer
                if len(word) == 0:
                    context.write(c)
                else:
                    self.__clear()
                    self.__word_buffer = self.__word_buffer[:-1]
                    self.__display()
            else:
                self.__clear()
                self.__context.back()
                self.__display()
        elif c == 0x20:        
            if self.__mode == SKK_MODE_ASCII:
                context.write(c)
            else:
                if self.__iscooking():
                    # 単語変換
                    if self.__candidate_buffer.isempty():
                        if not self.__tango_henkan():
                            self.__kakutei(context)
                    else:
                        self.__clear()
                        self.__candidate_buffer.movenext()
                        self.__display()
                else:
                    context.write(c)
        elif c < 0x20 or 0x7f < c:
            if self.__mode == SKK_MODE_ASCII:
                context.write(c)
            else:
                self.__reset()
                context.write(c)
        else:
            if self.__mode == SKK_MODE_ASCII:
                context.write(c)
            elif self.__mode == SKK_MODE_HIRAGANA or self.__mode == SKK_MODE_KATAKANA:
                if c == 0x71: # q
                    word = self.__word_buffer
                    if self.__iscooking():
                        self.__fix()
                        word = self.__word_buffer
                        self.__reset()
                        s = self.__convert_kana(word[1:])
                        context.writestring(s)
                    else:
                        self.__toggle_kana()
                elif c == 0x6c: # l
                    self.__mode = SKK_MODE_ASCII
                    self.__reset()
                else:
                    # 変換中か
                    if not self.__candidate_buffer.isempty():
                        # 変換中であれば、現在の候補をバックアップしておく
                        backup = self.__candidate_buffer.getcurrent()
                        self.__word_buffer = u''
                    else:
                        backup = None

                    if 0x41 <= c and c <= 0x5a: # A - Z
                        # 大文字のとき
                        self.__context.put(c + 0x20) # 子音に変換し、文字バッファに溜める

                        # バックアップがあるか
                        if backup:
                            # バックアップがあるとき、変換候補をリセット
                            self.__candidate_buffer.reset()

                            # 現在の候補を確定
                            context.writestring(backup[1:])
                            self.__word_buffer = COOK_MARK
                            if self.__context.isfinal():
                                # cが母音のとき、文字バッファを吸い出し、
                                s = self.__context.drain()
                                # 単語バッファに追加
                                self.__word_buffer += s
                            s = backup[1:]
                            s += self.__word_buffer
                            s += self.__context.getbuffer()
                            sys.stdout.write('\x1b7\x1b[1;4;35m%s\x1b8\x1b[?25l' % s)

                        # 先行する入力があるか
                        elif len(self.__word_buffer) > 1:
                            # 先行する入力があるとき、送り仮名マーク('*')をつける
                            if self.__word_buffer[-1] != OKURI_MARK:
                                self.__word_buffer += OKURI_MARK
                            # cが母音か
                            if self.__context.isfinal():
                                # cが母音のとき、文字バッファを吸い出し、
                                s = self.__context.drain()
                                # 単語バッファに追加し、
                                self.__word_buffer += s
                                # 送り仮名変換
                                self.__okuri_henkan()
                        else:
                            # 先行する入力が無いとき、単語バッファを編集マーク('▽')とする
                            self.__word_buffer = COOK_MARK
                            # cが母音か
                            if self.__context.isfinal():
                                # cが母音のとき、文字バッファを吸い出し、
                                s = self.__context.drain()
                                # 単語バッファに追加
                                self.__word_buffer += s

                            #trace("word_buffer: [%s], buckup: [%s], context: [%s]"
                            #                % (self.__word_buffer, backup, self.__context.getbuffer()))
                    elif self.__context.put(c):
                        #trace("word_buffer: [%s], buckup: [%s], context: [%s]"
                        #                    % (self.__word_buffer, backup, self.__context.getbuffer()))
                        if not backup is None:
                            self.__candidate_buffer.reset()
                            context.writestring(backup[1:])
                            s = backup[1:]
                            s += self.__word_buffer
                            s += self.__context.getbuffer()
                            sys.stdout.write('\x1b7\x1b[1;4;31m%s\x1b8\x1b[?25l' % s)
                            self.__word_buffer = u''
                        if self.__context.isfinal():
                            s = self.__context.drain()
                            if backup or len(self.__word_buffer) == 0:
                                context.writestring(s)
                            else:
                                # 送り仮名つき変換
                                if self.__word_buffer[-1] == OKURI_MARK:
                                    self.__word_buffer += s
                                    self.__okuri_henkan()
                                else:
                                    self.__word_buffer += s
                    else:
                        self.__reset()
                        context.write(c)
                    self.__display()

