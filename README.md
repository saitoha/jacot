
jacot
=====

Overview
--------
 Provides the auto-conversion filter supports well-known Japanese Encodings(CP932/EUC-JP).

Install
-------

```
 $ git clone https://github.com/saitoha/jacot.git
 $ cd jacot
 $ python setup.py install
```

or via pip

```
 $ pip install jacot
```

Usage
-----

```
 $ jacot [options] [command | -]
```

### Options:
<pre>
  -h, --help            show this help message and exit
  -t TERM, --term=TERM  override TERM environment variable
  -l LANG, --lang=LANG  override LANG environment variable
  -o ENC, --outenc=ENC  set output encoding
  -s, --enable-skk      enable SKK input method
</pre>

### Example:

#### 1. Create auto-conversion TTY session, like cocot.

```
 $ LANG=ja_JP.UTF-8 $SHELL
 $ echo 'あいうえお今日は≠〆＞' | iconv -t cp932
 ???????????????́??Y??
 $ jacot
 $ echo 'あいうえお今日は≠〆＞' | iconv -t cp932
 あいうえお今日は≠〆＞
```

#### 2. Read from stdin, without TTY session, just like nkf.

```
 $ LANG=ja_JP.UTF-8 $SHELL
 $ '三 ┏( ^o^)┛' | iconv -t eucjp | jacot
 三 ┏( ^o^)┛
```

#### 3. Set terminal encoding

```
 $ LANG=ja_JP.EUC-JP $SHELL
 $ jacot -o eucjp
 $ '三 ┏( ^o^)┛' | iconv -t sjis
 三 ┏( ^o^)┛
```

#### 4. Use SKK input method

```
 $ jacot --enable-skk

```

Dependency
----------
 - Masahiko Sato et al./SKK Development Team's SKK-JISYO.L

   This package includes the large SKK dictionary, SKK-JISYO.L.
   http://openlab.jp/skk/skk/dic/SKK-JISYO.L

How It Works
------------
Comming soon...

Reference
---------
 - Luit - locale and ISO 2022 support for Unicode terminals http://www.pps.univ-paris-diderot.fr/~jch/software/luit/
 - cocot - COde COnverter on Tty http://vmi.jp/software/cygwin/cocot.html
 - cygwin ck terminal emulator http://www.geocities.jp/meir000/ck/ 
 - Unicode Text Editor MinEd http://towo.net/mined/
 - libfep https://github.com/ueno/libfep

TODO
-----
 - Improve conversion algorithm (ck)
 - Implement glyph substitution or replacement mechanism with considering East Asian Width. (cocot)
 - Auto terminal encodings detection. (MinEd)
 - Switch auto detection on/off setting with private sequence "DECSET/DECRST 8850".
 - Improve Terminal Filter Framework(TFF), support plugin architecture.
 - libfep like API/language binding, socket connection support
 - Support Python 3.x


