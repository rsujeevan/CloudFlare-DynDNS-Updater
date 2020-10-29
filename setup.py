"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

__version__ = ""
exec(open(here / "cfdyndnsup" / "version.py").read())

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
setup(
    name="cfdyndnsup",  # Required
    version=__version__,  # Required
    description="A simple tool to update CloudFlare DNS record with the device's external ip.",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/rsujeevan/CloudFlare-DynDNS-Updater",  # Optional
    author="Sujeevan Rasaratnam",  # Optional
    author_email="me@sujeevan.com",  # Optional
    license="MIT",
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: Name Service (DNS)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="CloudFlare, dyndns, dns",  # Optional
    packages=find_packages(exclude=("test",)),
    python_requires=">=3.6, <4",
    install_requires=["requests >= 2.0"],  # Optional
    extras_require={  # Optional
        "dev": ["wheel", "flake8", "black"],
        # 'test': ['coverage'],
    },
    entry_points={  # Optional
        "console_scripts": [
            "cfdyndnsup=cfdyndnsup.update:main",
        ],
    },
    project_urls={  # Optional
        "Bug Reports": "https://github.com/rsujeevan/CloudFlare-DynDNS-Updater/issues",
        "Source": "https://github.com/rsujeevan/CloudFlare-DynDNS-Updater/",
    },
)
