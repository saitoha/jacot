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

from tffi import * # terminal filter framework interface

################################################################################
#
# Scanner implementation
#
class DefaultScanner(Scanner):
    ''' scan input stream and iterate characters '''
    __data = None

    def assign(self, value):
        self.__data = list(value)

    def __iter__(self):
        for x in self.__data:
            yield ord(x)

################################################################################
#
# Parser implementation
#
class DefaultParser(Parser):
    ''' default parser, don't parse ESC/CSI/string seqneces '''
    def __init__(self):
        pass

    def parse(self, context):
        for c in context:
            context.dispatch_char(c)
 
################################################################################
#
# Handler implementation
#
class DefaultHandler(EventObserver):
    ''' default handler, pass through all ESC/CSI/string seqnceses '''
    def __init__(self):
        pass

# EventObserver
    def handle_csi(self, context, parameter, intermediate, final):
        context.write(0x1b)
        context.write(0x5b)
        for c in parameter:
            context.write(c)
        for c in intermediate:
            context.write(c)
        context.write(final)

    def handle_esc(self, context, prefix, final):
        context.write(0x1b)
        for c in prefix:
            context.write(c)
        context.write(final)

    def handle_control_string(self, context, prefix, value):
        context.write(0x1b)
        context.write(prefix)
        for c in value:
            context.write(c)

    def handle_char(self, context, c):
        if c < 0x20 or c == 0x7f:
            context.write(c)
        else: 
            context.write(c)

