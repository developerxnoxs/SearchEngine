from setuptools import setup, find_packages

setup(
    name='multi-search-engine',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['requests', 'beautifulsoup4'],
    author='developerxnoxs',
    author_email='developerxnoxs@gmail.com',
    description='Simple multi search engine wrapper (Google, DuckDuckGo, Mojeek, YahooSearch)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/developerxnoxs/SearchEngine',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
