# Development version

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
