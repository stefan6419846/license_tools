# License tools

Collection of tools for working with Open Source licenses, focusing on Python packages.

## Features

At the moment, this primarily provides some convenience wrappers around the [ScanCode toolkit](https://github.com/nexB/scancode-toolkit/) by nexB Inc.

* Use *dataclasses* instead of dictionaries for returning data.
* Automatically download a specific Python package from PyPI and analyze it.
* Aggregate how often each license has been used inside the current artifact.
* Look into shared object files (`*.so*`) to see what they are linking to.
* Look into font files to easily analyze their metadata.
* Make everything available from the terminal.
* Drop all confusing parameters.

## Installation

You can install this package from PyPI:

```bash
python -m pip install license_tools
```

Alternatively, you can use the package from source directly after installing the required dependencies.

## Usage

To see the supported CLI parameters, just run:

```bash
python -m license_tools --help
```

Example: To see the licenses of a specific *joblib* package version, use something like this:

```bash
python -m license_tools --package "joblib==1.2.0"
```

If you want to use the package as a library, have a look at the `license_tools.retrieval.run` method for example to see how everything interacts.

## License

This package is subject to the terms of the Apache-2.0 license.

## Disclaimer

All results are generated automatically and provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. No generated content should be considered or used as legal advice. Consult an Attorney for any legal advice.
