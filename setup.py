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
    install_requires=[
        "pyyaml",
        "schedule",
        "watchdog"
    ]
)
