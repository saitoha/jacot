# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from jacot import __version__, __license__, __author__, __doc__

setup(name                  = 'jacot',
      version               = __version__,
      description           = "Japanese Auto character set Conversion On Tty",
      long_description      = open("README.rst").read(),
      py_modules            = ['jacot'],
      eager_resources       = ['jacot/skk', 'jacot/skk/SKK-JISYO.L', 'jacot/skk/SKK-JISYO.S'],
      classifiers           = ['Development Status :: 4 - Beta',
                               'Topic :: Terminals',
                               'Environment :: Console',
                               'Intended Audience :: End Users/Desktop',
                               'License :: OSI Approved :: GNU General Public License (GPL)',
                               'Programming Language :: Python'
                               ],
      keywords              = 'japanese terminal',
      author                = __author__,
      author_email          = 'user@zuse.jp',
      url                   = 'https://github.com/saitoha/jacot',
      license               = __license__,
      packages              = find_packages(exclude=[]),
      zip_safe              = False,
      include_package_data  = True,
      install_requires      = [],
      entry_points          = """
                              [console_scripts]
                              jacot = jacot:main
                              """
      )

