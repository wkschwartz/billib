#! /usr/bin/env python3

"""Install billib modules, packages, and scripts written in or for Python.

This script may exclude from installation any code that is not ready for use.
"""


from distutils.core import setup

from sortedtable import __doc__ as LONGDESC, __version__


if __name__ == '__main__':
	setup(
		name='exposure',
		version=__version__,
		description='Ordered symbol table data types.',
		long_description=LONGDESC,
		author='William Schwartz',
		author_email='"William Schwartz" <wkschwartz@gmail.com>',
		url='http://github.com/wkschwartz/billib',
		py_modules=['sortedtable']
	)
