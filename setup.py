
from distutils.core import setup
from baanprint import __version__

# the setup.py is mainly here so that tox can run the tests.
# BaanPrint isn't published on pypi.

setup(
    name='BaanPrint',
    version=__version__,
    author='Mathias Fussenegger',
    author_email='pip@zignar.net',
    packages=['baanprint'],
    scripts=['bin/bwprint.py'],
    url='http://pypi.python.org/pypi/BaanPrint/',
    license='LICENSE.txt',
    description='Simple Infor ERP LN Output Management Framework',
    long_description='Simple output management framework for Infor ERP LN',
    install_requires=[
        'Yapsy',
        'argh',
        'pyPdf'
    ],
)
