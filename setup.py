#from distutils.core import setup
from setuptools import setup, find_packages

setup(name='jacot',
      version='0.1.0',
      description="Japanese Auto-detect Converter On Tty",
      py_modules=['jacot'],
      classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Natulal Language :: Japanese',
              'Intended Audience :: End Users/Desktop',
              'License :: OSI Approved :: GPL v3',
              'Programming Language :: Python',
              'Topic :: Terminal'
              ],
      keywords='japanese utf8 eucjp cp932',
      author='Hayaki Saito',
      author_email='user@zuse.jp',
      license='GPL v3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=True,
      install_requires=[],
      entry_points="""
      [console_scripts]
      jacot = jacot:main
      """
      )

