
from setuptools import setup, find_packages
from dr_george.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='dr_george',
    version=VERSION,
    description='Dr. George analyzes public weather data.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Tom Atwell',
    author_email='klenwell@gmail.com',
    url='https://github.com/klenwell/dr-george',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'dr_george': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        dr_george = dr_george.main:main
    """,
)
