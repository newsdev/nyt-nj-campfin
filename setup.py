import os.path
from pip.download import PipSession
from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'), session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='nyt-nj-campfin',
    version='0.0.1',
    author='Rachel Shorey',
    author_email='rachel.shorey@nytimes.com',
    url='https://github.com/newsdev/nyt-nj-campfin',
    description='Scraper for New Jersey campaign finance disclosures',
    packages=('njcampfin',),
    entry_points={
        'console_scripts': (
            'get_filing_list = njcampfin:get_filing_list',
        ),
    },
    license="Apache License 2.0",
    keywords='campaign finance new jersey government elections',
    install_requires=reqs
)