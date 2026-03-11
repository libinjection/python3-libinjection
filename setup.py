"""
libinjection module for python

 Copyright 2012, 2013, 2014 Nick Galbreath
 nickg@client9.com
 BSD License -- see COPYING.txt for details
"""
import os

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


def get_libinjection_version():
    """Read the libinjection version from the upstream source file, if available."""
    version_file = os.path.join(os.path.dirname(__file__),
                                'upstream', 'src', 'libinjection_sqli.c')
    if os.path.exists(version_file):
        with open(version_file) as f:
            for line in f:
                if '#define LIBINJECTION_VERSION' in line and '__clang_analyzer__' not in line:
                    # Extract version string from: #define LIBINJECTION_VERSION "x.y.z"
                    parts = line.strip().split('"')
                    if len(parts) >= 2:
                        return parts[1]
    return 'undefined'


LIBINJECTION_VERSION = get_libinjection_version()

MODULE = Extension(
    'libinjection._libinjection', [
        'libinjection/libinjection_wrap.c',
        'libinjection/libinjection_sqli.c',
        'libinjection/libinjection_html5.c',
        'libinjection/libinjection_xss.c'
    ],
    swig_opts=['-Wextra', '-builtin'],
    define_macros = [('LIBINJECTION_VERSION', '"{}"'.format(LIBINJECTION_VERSION))],
    include_dirs = [],
    libraries = [],
    library_dirs = [],
    )

setup (
    name             = 'libinjection',
    version          = '3.9.1',
    description      = 'Wrapper around libinjection c-code to detect sqli',
    author           = 'Nick Galbreath',
    author_email     = 'nickg@client9.com',
    url              = 'https://libinjection.client9.com/',
    ext_modules      = [MODULE],
    packages         = ['libinjection'],
    long_description = '''
wrapper around libinjection
''',
       classifiers   = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Database',
        'Topic :: Security',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Internet :: WWW/HTTP'
        ]
    )
