from distutils.core import setup
from setuptools import find_packages


setup(
    name='Lensrater',
    version='0.1',
    description="Quick image classifier for strong lens searches",
    long_description=open('README.md', encoding="utf-8").read(),
    author="Colin Jacobs",
    author_email="colin@coljac.net",
    url="https://github.com/coljac/lensrater",
    # data_files=[('help', ['help/help.txt'])],
    entry_points={
        'console_scripts': ['lensrater=lensrater:main']
        },
    packages=['lensrater'], 
    license='MIT License'
)
