# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from pathlib import Path

import setuptools


ROOT_DIRECTORY = Path(__file__).parent.resolve()


setuptools.setup(
    name="license_tools",
    description="Collection of tools for working with Open Source licenses",
    version="0.5.0",
    license="Apache-2.0",
    long_description=Path(ROOT_DIRECTORY / "README.md").read_text(encoding="UTF-8"),
    long_description_content_type="text/markdown",
    author="stefan6419846",
    url="https://github.com/stefan6419846/license_tools",
    packages=setuptools.find_packages(include=["license_tools", "license_tools.*"]),
    include_package_data=True,
    python_requires=">=3.8, <4",
    install_requires=[
        "scancode-toolkit",
        "typecode-libmagic",
        "joblib",
        "fontTools[woff]",
    ],
    extras_require={
        "dev": [
            "flake8",
            "flake8-bugbear",
            "pep8-naming",
            "mypy",
            "requests",
            "types-requests",
            "importlib_resources; python_version<'3.9'",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    keywords=["open source", "license", "package", "dependency", "licensing"],
)
