# Development version

* Add option to display Python package metadata.
* Refactor tests to download each external artifact only once.
* Add example output to README.

# Version 0.7.0 - 2024-02-12

* Move detected licenses from archives to the regular results instead of just printing it.
* Replace `NOT_REQUESTED` by `None` as `NOT_REQUESTED` could not be used as a reliable filter within external code.
* Add support for OTF font files.
* Cleanup unpacked archives when done with it.

# Version 0.6.0 - 2024-01-26

* Skip symlinks for LDD analysis.
* Analyze nested archives.
* Analyze more archives, including RPM files.
* Speed-up analysis of packed archive files (will be unpacked in a separate step), ELF binaries and fonts by not scanning the whole binary blob, 
  but only looking at the metadata (if available).
* Handle more types of ELF binaries.
* Move tools to dedicated submodule.
* Fix shipping of font data in sdist.

# Version 0.5.0 - 2023-12-11

* Move code to dedicated files.
* Add support for analyzing fonts.

# Version 0.4.0 - 2023-11-21

* Switch to *mypy* strict mode.
* Add unit tests.
* Fix handling of license clues.
* Drop support for Python 3.7.
* Add support for download URLs.

# Version 0.3.2 - 2023-08-21

* Fix type hints.
* Mark package as typed.

# Version 0.3.1 - 2023-08-03

* Dynamically adjust the width of the path column.

# Version 0.3.0 - 2023-06-19

* Do not hide stderr output from `pip download` to directly see the corresponding issue.
* Allow running on local archive files from CLI, for example because the package version is not available for the Python version used for the analysis.
* Migrate retrieval parameter handling to flags to avoid duplicates.

# Version 0.2.0 - 2023-06-15

* Make sure to delete the temporary run-specific directories on exit.
* Add some code documentation.

# Version 0.1.3 - 2023-06-14

* Avoid running shared object linking analysis twice.

# Version 0.1.2 - 2023-06-14

* Fix defaults for retrieval parameters.
* Fix display of shared object linking data if the file is no shared object.

# Version 0.1.1 - 2023-06-13

* Fix README rendering on PyPI.

# Version 0.1.0 - 2023-06-13

* First public release.
