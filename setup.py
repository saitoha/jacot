
from setuptools import setup, find_packages
from jacot import __version__, __license__, __author__, __doc__

setup(name              = 'jacot',
      version           = __version__,
      description       = "Japanese Auto character set Conversion On Tty",
      long_description  = __doc__,
      py_modules        = ['jacot'],
      classifiers       = ['Development Status :: 4 - Beta',
                           'Topic :: Terminals',
                           'Environment :: Console',
                           'Intended Audience :: End Users/Desktop',
                           'License :: OSI Approved :: GNU General Public License (GPL)',
                           'Programming Language :: Python'
                           ],
      keywords          = 'japanese terminal',
      author            = __author__,
      author_email      = 'user@zuse.jp',
      url               = 'https://github.com/saitoha/jacot',
      license           = __license__,
      packages          = find_packages(exclude=['ez_setup',
                                                 'examples',
                                                 'tests']),
      zip_safe          = True,
      install_requires  = [],
      entry_points      = """
                          [console_scripts]
                          jacot = jacot:main
                          """
      )

