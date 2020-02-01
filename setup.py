from setuptools import setup, find_packages
import sys

if sys.hexversion < 0x02070000:
    sys.exit("Python 2.7 or newer is required to use this package.")

setup(
    name="legato",
    version="1.1",
    author="S[&]T",
    url="https://github.com/stcorp/legato",
    description="Task trigger daemon",
    license="BSD",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "legato = legato.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: System",
    ],
    install_requires=[
        "pyyaml",
        "schedule",
        "watchdog"
    ]
)
