# License tools

Collection of tools for working with Open Source licenses, focusing on Python packages.

## Features

At the moment, this primarily provides some convenience wrappers around the [ScanCode toolkit](https://github.com/nexB/scancode-toolkit/) by nexB Inc. to be used as either as standalone CLI or library.

* Automatically download a specific Python package from PyPI and analyze it.
* Aggregate how often each license has been used inside the current artifact.
* Look into shared object files and ELF binaries to see what they are linking to (dynamically).
* Look into font files to easily analyze their metadata.
* Look into RPM file metadata.
* Recursively look into nested archives, for example by unpacking the actual upstream source code archives inside RPM (source) files.
* Make everything available from the terminal.

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

Example: To see the licenses of a specific *pypdf* package version, use something like this:

```bash
$ python -m license_tools --package "pypdf==3.4.17"
              pypdf-3.17.4.dist-info/LICENSE                                    BSD-3-Clause [100.0]
             pypdf-3.17.4.dist-info/METADATA                                    BSD-3-Clause [99.0]
               pypdf-3.17.4.dist-info/RECORD                                    
                pypdf-3.17.4.dist-info/WHEEL                                    
                           pypdf/__init__.py                                    
                              pypdf/_cmap.py                                    
                   pypdf/_codecs/__init__.py                                    
               pypdf/_codecs/adobe_glyphs.py                                    BSD-3-Clause [100.0]
                     pypdf/_codecs/pdfdoc.py                                    
                        pypdf/_codecs/std.py                                    
                     pypdf/_codecs/symbol.py                                    
                   pypdf/_codecs/zapfding.py                                    
          pypdf/_crypt_providers/__init__.py                                    BSD-3-Clause [100.0]
             pypdf/_crypt_providers/_base.py                                    BSD-3-Clause [100.0]
     pypdf/_crypt_providers/_cryptography.py                                    BSD-3-Clause [100.0]
         pypdf/_crypt_providers/_fallback.py                                    BSD-3-Clause [100.0]
     pypdf/_crypt_providers/_pycryptodome.py                                    BSD-3-Clause [100.0]
                        pypdf/_encryption.py                                    BSD-3-Clause [100.0]
                            pypdf/_merger.py                                    BSD-3-Clause [100.0]
                              pypdf/_page.py                                    BSD-3-Clause [100.0]
                       pypdf/_page_labels.py                                    
                         pypdf/_protocols.py                                    
                            pypdf/_reader.py                                    BSD-3-Clause [100.0]
          pypdf/_text_extraction/__init__.py                                    
                             pypdf/_utils.py                                    BSD-3-Clause [100.0]
                           pypdf/_version.py                                    
                            pypdf/_writer.py                                    BSD-3-Clause [100.0]
                pypdf/_xobj_image_helpers.py                                    
               pypdf/annotations/__init__.py                                    
                  pypdf/annotations/_base.py                                    
    pypdf/annotations/_markup_annotations.py                                    
pypdf/annotations/_non_markup_annotations.py                                    
                          pypdf/constants.py                                    
                             pypdf/errors.py                                    
                            pypdf/filters.py                                    BSD-3-Clause [100.0]
                   pypdf/generic/__init__.py                                    BSD-3-Clause [100.0]
                      pypdf/generic/_base.py                                    BSD-3-Clause [100.0]
           pypdf/generic/_data_structures.py                                    BSD-3-Clause [100.0]
                       pypdf/generic/_fit.py                                    
                   pypdf/generic/_outline.py                                    
                 pypdf/generic/_rectangle.py                                    
                     pypdf/generic/_utils.py                                    
                pypdf/generic/_viewerpref.py                                    BSD-3-Clause [100.0]
                          pypdf/pagerange.py                                    BSD-3-Clause [99.0]
                         pypdf/papersizes.py                                    
                              pypdf/py.typed                                    
                              pypdf/types.py                                    
                                pypdf/xmp.py                                    

====================================================================================================

                                                          BSD-3-Clause  20
                                                                  None  28
```

If you want to use the package as a library, have a look at the `license_tools.retrieval.run` method for example to see how everything interacts.

## License

This package is subject to the terms of the Apache-2.0 license.

## Disclaimer

All results are generated automatically and provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. No generated content should be considered or used as legal advice. Consult an Attorney for any legal advice.
