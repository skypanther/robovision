from setuptools import setup
from codecs import open
from os import path

__version__ = '0.0.1'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='robovision',
    version=__version__,
    description='Image processing functions useful for FRC robotics teams (and other purposes)',
    long_description=long_description,
    url='https://github.com/skypanther/robovision',
    download_url='https://github.com/skypanther/robovision/tarball/' + __version__,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    keywords=['robot', 'first robotics', 'frc', 'computer vision', 'image processing', 'opencv'],
    packages=['robovision', 'robovision.preprocessor'],
    include_package_data=True,
    author='Tim Poulsen',
    author_email='tim@skypanther.com'
)
