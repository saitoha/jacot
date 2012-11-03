jacot
=====

This module Provides the auto-conversion filter
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

    $ jacot [options] [command | -]


* Options::

    -h, --help            show this help message and exit
    -t TERM, --term=TERM  override TERM environment variable
    -l LANG, --lang=LANG  override LANG environment variable
    -o ENC, --outenc=ENC  set output encoding
    -s, --enable-skk      enable SKK input method


