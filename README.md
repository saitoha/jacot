
jacot - Japanese Auto character set Conversion On Tty
=====================================================

Overview
--------
 Provides the auto-conversion filter supports well-known Japanese Encodings(CP932/EUC-JP).

Install
-------
 $ python setup.py install

Usage
-----
 $ jacot.py [options] [command | -]

### Options:
  -h, --help            show this help message and exit
  -t TERM, --term=TERM  override TERM environment variable
  -l LANG, --lang=LANG  override LANG environment variable
  -o ENC, --outenc=ENC  set output encoding

Example
------- 

### Example 1: Create auto-conversion TTY session

```
 $ LANG=ja_JP.UTF-8 $SHELL
 $ echo 'あいうえお今日は≠〆＞' | iconv -t cp932
 ???????????????́??Y??
 $ jacot
 $ echo 'あいうえお今日は≠〆＞' | iconv -t cp932
 あいうえお今日は≠〆＞
```

### Example 2: Read from stdin, without TTY session

```
 $ LANG=ja_JP.UTF-8 $SHELL
 $ '三 ┏( ^o^)┛' | iconv -t eucjp | jacot
 三 ┏( ^o^)┛
```

