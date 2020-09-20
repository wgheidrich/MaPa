from setuptools import setup, find_packages
import sys
from os import chdir

with open('README.md') as f:
    readme = f.read()


print('-'*50,file=sys.stderr)
print("Packages:",find_packages(),file=sys.stderr)
print('-'*50,file=sys.stderr)

setup(
    name='MaPa',
    version='1.0',
    packages=find_packages(),
    description='Math Parser library for Python',
    author='Wolfgang Heidrich',
    author_email="wolfgang.heidrich@kaust.edu.sa",
    license="Python Software License",
    url="https://github.com/wgheidrich/MaPa",
    install_requires=[
        'ply'
    ],
    entry_points={
        "console_scripts" : ["mapa-calc = mapa.mapa:main"]
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Manufacturing',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Programming Language :: Python :: 3',
    ],
    long_description=readme,
)


