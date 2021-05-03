from setuptools import setup, find_packages
import WordListGenerator

setup(
    name = WordListGenerator.__name__,
 
    version = WordListGenerator.__version__,
    py_modules=[WordListGenerator.__name__],
    install_requires = [],

    author=WordListGenerator.__author__,
    author_email=WordListGenerator.__author_email__,
    maintainer=WordListGenerator.__maintainer__,
    maintainer_email=WordListGenerator.__maintainer_email__,
 
    description = WordListGenerator.__description__,
    long_description = open('README.md').read(),
    long_description_content_type="text/markdown",
 
    include_package_data = True,

    url = WordListGenerator.__url__,
    project_urls = {
        "Documentation": "https://mauricelambert.github.io/info/python/security/PyWCGIshell.html",
        "Python exe": "https://mauricelambert.github.io/info/python/security/PyWCGIshell.pyz",
    },
 
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Topic :: Security",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],

    entry_points = {
        'console_scripts': [
            'WordListGenerator = WordListGenerator:main',
        ],
    },
 
    python_requires='>=3.6',
)