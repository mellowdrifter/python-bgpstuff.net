"""Setup file for packaging.
"""

import pathlib
import setuptools

here = pathlib.Path(__file__).parent

with open(f"{here}/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bgpstuff",
    version="0.0.1",
    author="Darren O'Connor",
    author_email="nouser@bgpstuff.net",
    description="Python Client for Connecting to BGPStuff.net",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mellowdrifter/python-bgpstuff.net",
    packages=setuptools.find_packages(),
    license="Apache Software License (http://www.apache.org/licenses/LICENSE-2.0)",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "bgpstuff = bgpstuff.cli:cli",
        ],
    },
    install_requires=["ipaddress", "ratelimit", "requests"],
    python_requires=">=3.6",
)
