jacot
=====

This module provides the auto-conversion filter
supports well-known Japanese Encodings(CP932/EUC-JP).

Install
-------

via github ::

    $ git clone https://github.com/saitoha/jacot.git
    $ cd jacot
    $ python setup.py install

or via pip ::

    $ pip install jacot


Usage
-----

::

    $ jacot [options] [command | -]


* Options::

    -h, --help                  show this help message and exit
    --version                   show version
    -t TERM, --term=TERM        override TERM environment variable
    -l LANG, --lang=LANG        override LANG environment variable
    -o ENC, --outenc=ENC        set output encoding
    --disable-input-conversion  disable input auto conversion
    --disable-output-conversion disable output auto conversion
    -s, --enable-skk            use SKK input method

Dependence
----------
 - Hayaki Saito's TFF, Terminal Filter Framework
   https://github.com/saitoha/tff

 - Hayaki Saito's Sentimental-SKK
   https://github.com/saitoha/sentimental-skk

   Sentimental-SKK package includes the large SKK dictionary, 
   SKK-JISYO.L (Masahiko Sato et al./SKK Development Team).
   http://openlab.jp/skk/skk/dic/SKK-JISYO.L

References
----------
 - Luit - locale and ISO 2022 support for Unicode terminals http://www.pps.univ-paris-diderot.fr/~jch/software/luit/
 - cocot - COde COnverter on Tty http://vmi.jp/software/cygwin/cocot.html
 - cygwin ck terminal emulator http://www.geocities.jp/meir000/ck/ 
 - Unicode Text Editor MinEd http://towo.net/mined/
 - libfep https://github.com/ueno/libfep
 - Daredevil SKK (DDSKK) http://openlab.ring.gr.jp/skk/ddskk-ja.html


