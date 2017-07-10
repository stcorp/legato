from setuptools import setup, find_packages
import sys

if sys.hexversion < 0x02070000:
    sys.exit("Python 2.7 or newer is required to use this package.")

setup(
    name="legato",
    version="1.0",
    author="S[&]T",
    author_email="info@stcorp.nl",
    url="http://stcorp.nl/",
    description="Task trigger daemon",
    license="BSD",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "legato = legato.daemon:main",
        ],
    },
    install_requires=[
        "watchdog",
        "schedule"
    ],
    py_modules=["legato"]
)
