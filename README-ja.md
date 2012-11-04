
jacot
=====

概要
--------
 ターミナルとアプリケーションの間の入出力に介入し、CP932/EUC-JP/UTF-8が混在したエンコーディングを解釈します。
 また、入力の円サインをバックスラッシュに変換したり、日本語入力メソッドSKKを独自に提供するなど、
 ターミナルで日本語を扱う際に発生しがちな諸問題の解決を目指すサバイバルツールとしての側面を持ちます。

インストール
------------

```
 $ git clone https://github.com/saitoha/jacot.git
 $ cd jacot
 $ python setup.py install
```

またはpip経由で、

```
 $ pip install jacot
```

とします。

使い方
------

```
 $ jacot [options] [command | -]
```

### Options:
<pre>
  -h, --help            ヘルプメッセージを出力します。 
  --version             バージョンを表示します。
  -t TERM, --term=TERM  環境変数TERMを上書きします。
  -l LANG, --lang=LANG  環境変数LANGを上書きします。
  -o ENC, --outenc=ENC  出力エンコーディングを設定します。 
  --disable-input-conversion
                        入力方向の自動変換を抑制します。
  --disable-output-conversion
                        出力方向の自動変換を抑制します。
  -s, --enable-skk      SKK日本語入力メソッド、円サイン->バックスラッシュ変換を有効にします。 

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

How It Works
------------
Comming soon...

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

TODO
-----
 - Improve conversion algorithm (ck)
 - Implement glyph substitution or replacement mechanism with considering East Asian Width. (cocot)
 - Auto terminal encodings detection. (MinEd)
 - Switch auto detection on/off setting with private sequence "DECSET/DECRST 8850".
 - Improve Terminal Filter Framework(TFF), support plugin architecture.
 - libfep like API/language binding, socket connection support
 - Support Python 3.x


