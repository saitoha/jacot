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

import os, termios, pty, signal, fcntl, struct, select
from tffinterface import *

BUFFER_SIZE=1024

################################################################################
#
# DefaultPTY
#
class DefaultPTY(PTY):

    __stdin_fileno = None
    __backup = None
    __master = None

    def __init__(self, settings):
        self.__stdin_fileno = settings.stdin.fileno()
        vdisable = os.fpathconf(self.__stdin_fileno, 'PC_VDISABLE')
        self.__backup = termios.tcgetattr(self.__stdin_fileno)
        new = termios.tcgetattr(self.__stdin_fileno)
        new[3] = new[3] &~ (termios.ECHO | termios.ICANON)
        new[6][termios.VINTR] = vdisable
        #new[6][termios.VQUIT] = vdisable
        new[6][termios.VSUSP] = vdisable
        termios.tcsetattr(self.__stdin_fileno, termios.TCSANOW, new)
        pid, master = pty.fork()
        if not pid:
            os.environ['TERM'] = settings.term 
            os.environ['LANG'] = settings.lang 
            os.execlp('/bin/sh',
                      '/bin/sh', '-c',
                      'cd $HOME && exec %s' % settings.command)

        self.__pid = pid
        self.__master = master
        signal.signal(signal.SIGWINCH, lambda no, frame: self.fitsize())
    
        # call resize once
        self.fitsize()
 
    def __del__(self):
        termios.tcsetattr(self.__stdin_fileno, termios.TCSANOW, self.__backup)

    def fitsize(self):
         winsize = fcntl.ioctl(self.__stdin_fileno, termios.TIOCGWINSZ, 'hhhh')
         height, width = struct.unpack('hh', winsize)
         self.resize(height, width)

    def resize(self, height, width):
         winsize = struct.pack('HHHH', height, width, 0, 0)
         fcntl.ioctl(self.__master, termios.TIOCSWINSZ, winsize)
         # notify Application process that terminal size has been changed.
         os.kill(self.__pid, signal.SIGWINCH)
         return height, width

    def read(self):
        return os.read(self.__master, BUFFER_SIZE)

    def write(self, data):
        os.write(self.__master, data)

    def drive(self):
        master = self.__master
        stdin_fileno = self.__stdin_fileno
        rfds = [stdin_fileno, master]
        wfds = []
        xfds = [stdin_fileno, master]
        try:
            while True: 
                try:
                    rfd, wfd, xfd = select.select(rfds, wfds, xfds)
                    if xfd:
                        break
                    for fd in rfd:
                        if fd == stdin_fileno:
                            data = os.read(stdin_fileno, BUFFER_SIZE)
                            if data:
                                yield data, None
                        elif fd == master:
                            data = self.read()
                            if data:
                                yield None, data
                except select.error, e:
                    no, msg = e
                    if not no == errno.EINTR:
                        raise
        finally:
            os.close(master)

''' main '''
if __name__ == '__main__':    
    pass


