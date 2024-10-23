# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import re
from typing import cast
from unittest import TestCase

from license_tools.tools import image_tools
from tests import get_file
from tests.data import LICENSE_PATH, SETUP_PATH


class GetMimeTypeTestCase(TestCase):
    def test_get_mime_type(self) -> None:
        self.assertEqual(
            "text/x-script.python",
            image_tools._get_mime_type(SETUP_PATH)
        )
        self.assertEqual(
            "text/plain",
            image_tools._get_mime_type(LICENSE_PATH)
        )

        with get_file("croissant.jpg") as path:
            self.assertEqual(
                "image/jpeg",
                image_tools._get_mime_type(path)
            )


class IsImageTestCase(TestCase):
    def test_is_image(self) -> None:
        self.assertFalse(image_tools.is_image(SETUP_PATH))
        self.assertFalse(image_tools.is_image(LICENSE_PATH))

        with get_file("Carlito-Regular.ttf") as path:
            self.assertFalse(image_tools.is_image(path))

        with get_file("croissant.jpg") as path:
            self.assertTrue(image_tools.is_image(path))


class CheckImageMetadataTestCase(TestCase):
    maxDiff = None

    def test_python(self) -> None:
        self.assertIsNone(image_tools.check_image_metadata(SETUP_PATH))

    def test_font(self) -> None:
        with get_file("Carlito-Regular.ttf") as path:
            self.assertIsNone(image_tools.check_image_metadata(path))

    def assert_regex(self, expected_regex: str, text: str) -> None:
        # Like `assertRegex`, but using `match` instead of `search` and
        # providing the actual text as failure message.
        if not re.match(expected_regex, text):
            self.fail(text)

    def test_croissant_jpg(self) -> None:
        with get_file("croissant.jpg") as path:
            result = image_tools.check_image_metadata(path)

        self.assertIsNotNone(result)

        self.assert_regex(
            expected_regex=r"""
^\[ExifTool\]      ExifTool Version Number         : \d+\.\d+
\[File\]          File Name                       : croissant\.jpg
\[File\]          File Size                       : (184 kB|180 KiB)
\[File\]          File Modification Date/Time     : \d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}
\[File\]          File Permissions                : \-rw\-r\-\-r\-\-
\[File\]          File Type                       : JPEG
\[File\]          File Type Extension             : jpg
\[File\]          MIME Type                       : image/jpeg
\[File\]          Exif Byte Order                 : Little\-endian \(Intel, II\)
\[File\]          Current IPTC Digest             : fce11f89c8b7c9782f346234075877eb
\[File\]          Image Width                     : 1280
\[File\]          Image Height                    : 853
\[File\]          Encoding Process                : Baseline DCT, Huffman coding
\[File\]          Bits Per Sample                 : 8
\[File\]          Color Components                : 3
\[File\]          Y Cb Cr Sub Sampling            : YCbCr4:4:4 \(1 1\)
\[Ducky\]         Quality                         : 70%
\[XMP\]           XMP Toolkit                     : Adobe XMP Core 5\.0\-c060 61\.134777, 2010/02/12\-17:32:00
\[XMP\]           Marked                          : False
\[XMP\]           Web Statement                   : http://www\.publicdomainpictures\.net
\[XMP\]           Original Document ID            : xmp\.did:D61CE24A664AE011B7F5DC66CB8B70E4
\[XMP\]           Document ID                     : xmp\.did:13A209884A6E11E09364B31F7A5A30E9
\[XMP\]           Instance ID                     : xmp\.iid:13A209874A6E11E09364B31F7A5A30E9
\[XMP\]           Creator Tool                    : Adobe Photoshop CS5 Windows
\[XMP\]           Derived From Instance ID        : xmp\.iid:EE2C2F47694AE011B7F5DC66CB8B70E4
\[XMP\]           Derived From Document ID        : xmp\.did:D61CE24A664AE011B7F5DC66CB8B70E4
\[XMP\]           Creator                         : Petr Kratochvil
\[XMP\]           Title                           : croissant
\[IPTC\]          Coded Character Set             : UTF8
\[IPTC\]          Application Record Version      : 2
\[Photoshop\]     IPTC Digest                     : fce11f89c8b7c9782f346234075877eb
\[ICC_Profile\]   Profile CMM Type                : Linotronic
\[ICC_Profile\]   Profile Version                 : 2\.1\.0
\[ICC_Profile\]   Profile Class                   : Display Device Profile
\[ICC_Profile\]   Color Space Data                : RGB
\[ICC_Profile\]   Profile Connection Space        : XYZ
\[ICC_Profile\]   Profile Date Time               : 1998:02:09 06:49:00
\[ICC_Profile\]   Profile File Signature          : acsp
\[ICC_Profile\]   Primary Platform                : Microsoft Corporation
\[ICC_Profile\]   CMM Flags                       : Not Embedded, Independent
\[ICC_Profile\]   Device Manufacturer             : Hewlett\-Packard
\[ICC_Profile\]   Device Model                    : sRGB
\[ICC_Profile\]   Device Attributes               : Reflective, Glossy, Positive, Color
\[ICC_Profile\]   Rendering Intent                : Perceptual
\[ICC_Profile\]   Connection Space Illuminant     : 0\.9642 1 0\.82491
\[ICC_Profile\]   Profile Creator                 : Hewlett\-Packard
\[ICC_Profile\]   Profile ID                      : 0
\[ICC_Profile\]   Profile Copyright               : Copyright \(c\) 1998 Hewlett\-Packard Company
\[ICC_Profile\]   Profile Description             : sRGB IEC61966\-2\.1
\[ICC_Profile\]   Media White Point               : 0\.95045 1 1\.08905
\[ICC_Profile\]   Media Black Point               : 0 0 0
\[ICC_Profile\]   Red Matrix Column               : 0\.43607 0\.22249 0\.01392
\[ICC_Profile\]   Green Matrix Column             : 0\.38515 0\.71687 0\.09708
\[ICC_Profile\]   Blue Matrix Column              : 0\.14307 0\.06061 0\.7141
\[ICC_Profile\]   Device Mfg Desc                 : IEC http://www\.iec\.ch
\[ICC_Profile\]   Device Model Desc               : IEC 61966\-2\.1 Default RGB colour space \- sRGB
\[ICC_Profile\]   Viewing Cond Desc               : Reference Viewing Condition in IEC61966\-2\.1
\[ICC_Profile\]   Viewing Cond Illuminant         : 19\.6445 20\.3718 16\.8089
\[ICC_Profile\]   Viewing Cond Surround           : 3\.92889 4\.07439 3\.36179
\[ICC_Profile\]   Viewing Cond Illuminant Type    : D50
\[ICC_Profile\]   Luminance                       : 76\.03647 80 87\.12462
\[ICC_Profile\]   Measurement Observer            : CIE 1931
\[ICC_Profile\]   Measurement Backing             : 0 0 0
\[ICC_Profile\]   Measurement Geometry            : Unknown
\[ICC_Profile\]   Measurement Flare               : 0\.999%
\[ICC_Profile\]   Measurement Illuminant          : D65
\[ICC_Profile\]   Technology                      : Cathode Ray Tube Display
\[ICC_Profile\]   Red Tone Reproduction Curve     : \(Binary data 2060 bytes, use \-b option to extract\)
\[ICC_Profile\]   Green Tone Reproduction Curve   : \(Binary data 2060 bytes, use \-b option to extract\)
\[ICC_Profile\]   Blue Tone Reproduction Curve    : \(Binary data 2060 bytes, use \-b option to extract\)
\[APP14\]         DCT Encode Version              : 100
\[APP14\]         APP14 Flags 0                   : \[14\], Encoded with Blend=1 downsampling
\[APP14\]         APP14 Flags 1                   : \(none\)
\[APP14\]         Color Transform                 : YCbCr
\[Composite\]     Image Size                      : 1280x853
\[Composite\]     Megapixels                      : 1\.1
            """.strip() + "\n$",
            text=cast(str, result)
        )

    def test_mountain_jpg(self) -> None:
        with get_file("mountain.jpg") as path:
            result = image_tools.check_image_metadata(path)

        self.assertIsNotNone(result)

        self.assert_regex(
            expected_regex=r"""
^\[ExifTool\]      ExifTool Version Number         : \d+\.\d+
\[ExifTool\]      Warning                         : \[minor\] Adjusted MakerNotes base by \-108
\[File\]          File Name                       : mountain\.jpg
\[File\]          File Size                       : (424 kB|414 KiB)
\[File\]          File Modification Date/Time     : \d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}
\[File\]          File Permissions                : \-rw\-r\-\-r\-\-
\[File\]          File Type                       : JPEG
\[File\]          File Type Extension             : jpg
\[File\]          MIME Type                       : image/jpeg
\[File\]          Current IPTC Digest             : d41d8cd98f00b204e9800998ecf8427e
\[File\]          Exif Byte Order                 : Big\-endian \(Motorola, MM\)
\[File\]          Image Width                     : 630
\[File\]          Image Height                    : 420
\[File\]          Encoding Process                : Baseline DCT, Huffman coding
\[File\]          Bits Per Sample                 : 8
\[File\]          Color Components                : 3
\[File\]          Y Cb Cr Sub Sampling            : YCbCr4:4:4 \(1 1\)
\[JFIF\]          JFIF Version                    : 1\.01
\[JFIF\]          Resolution Unit                 : inches
\[JFIF\]          X Resolution                    : 180
\[JFIF\]          Y Resolution                    : 180
\[Photoshop\]     IPTC Digest                     : d41d8cd98f00b204e9800998ecf8427e
\[EXIF\]          Image Description               : 
\[EXIF\]          Make                            : Canon
\[EXIF\]          Camera Model Name               : Canon PowerShot G7 X
\[EXIF\]          Orientation                     : Horizontal \(normal\)
\[EXIF\]          X Resolution                    : 180
\[EXIF\]          Y Resolution                    : 180
\[EXIF\]          Resolution Unit                 : inches
\[EXIF\]          Software                        : Camera\+ 8\.0\.2
\[EXIF\]          Modify Date                     : 2016:06:17 15:15:38
\[EXIF\]          Artist                          : 
\[EXIF\]          Host Computer                   : iPhone \(iPhone OS 9\.3\.5\)
\[EXIF\]          Y Cb Cr Positioning             : Centered
\[EXIF\]          Copyright                       : 
\[EXIF\]          Exposure Time                   : 1/1250
\[EXIF\]          F Number                        : 4\.5
\[EXIF\]          ISO                             : 250
\[EXIF\]          Sensitivity Type                : Recommended Exposure Index
\[EXIF\]          Recommended Exposure Index      : 250
\[EXIF\]          Exif Version                    : 0230
\[EXIF\]          Date/Time Original              : 2016:06:17 15:15:38
\[EXIF\]          Create Date                     : 2016:06:17 15:15:38
\[EXIF\]          Components Configuration        : Y, Cb, Cr, \-
\[EXIF\]          Shutter Speed Value             : 1/1244
\[EXIF\]          Aperture Value                  : 4\.5
\[EXIF\]          Exposure Compensation           : 0
\[EXIF\]          Max Aperture Value              : 2\.0
\[EXIF\]          Metering Mode                   : Multi\-segment
\[EXIF\]          Flash                           : Off, Did not fire
\[EXIF\]          Focal Length                    : 10\.3 mm
\[EXIF\]          User Comment                    : 
\[EXIF\]          Flashpix Version                : 0100
\[EXIF\]          Color Space                     : sRGB
\[EXIF\]          Exif Image Width                : 3420
\[EXIF\]          Exif Image Height               : 2280
\[EXIF\]          Focal Plane X Resolution        : 10584\.13793
\[EXIF\]          Focal Plane Y Resolution        : 10573\.91304
\[EXIF\]          Focal Plane Resolution Unit     : inches
\[EXIF\]          Sensing Method                  : One\-chip color area
\[EXIF\]          File Source                     : Digital Camera
\[EXIF\]          Custom Rendered                 : Normal
\[EXIF\]          Exposure Mode                   : Auto
\[EXIF\]          White Balance                   : Auto
\[EXIF\]          Digital Zoom Ratio              : 1
\[EXIF\]          Scene Capture Type              : Standard
\[EXIF\]          Owner Name                      : 
\[EXIF\]          Compression                     : JPEG \(old\-style\)
\[EXIF\]          X Resolution                    : 72
\[EXIF\]          Y Resolution                    : 72
\[EXIF\]          Resolution Unit                 : inches
\[EXIF\]          Thumbnail Offset                : 6928
\[EXIF\]          Thumbnail Length                : 10506
\[EXIF\]          Thumbnail Image                 : \(Binary data 10506 bytes, use \-b option to extract\)
\[MakerNotes\]    Macro Mode                      : Normal
\[MakerNotes\]    Self Timer                      : Off
\[MakerNotes\]    Quality                         : Fine
\[MakerNotes\]    Canon Flash Mode                : Off
\[MakerNotes\]    Continuous Drive                : Single
\[MakerNotes\]    Focus Mode                      : Single
\[MakerNotes\]    Record Mode                     : JPEG
\[MakerNotes\]    Canon Image Size                : Large
\[MakerNotes\]    Easy Mode                       : Full auto
\[MakerNotes\]    Digital Zoom                    : None
\[MakerNotes\]    Contrast                        : Normal
\[MakerNotes\]    Saturation                      : Normal
\[MakerNotes\]    Sharpness                       : 0
\[MakerNotes\]    Camera ISO                      : Auto
\[MakerNotes\]    Metering Mode                   : Evaluative
\[MakerNotes\]    Focus Range                     : Auto
\[MakerNotes\]    AF Point                        : Face Detect
\[MakerNotes\]    Canon Exposure Mode             : Easy
\[MakerNotes\]    Lens Type                       : n/a
\[MakerNotes\]    Max Focal Length                : 36\.8 mm
\[MakerNotes\]    Min Focal Length                : 8\.8 mm
\[MakerNotes\]    Focal Units                     : 1000/mm
\[MakerNotes\]    Max Aperture                    : 2
\[MakerNotes\]    Min Aperture                    : 11
\[MakerNotes\]    Flash Bits                      : \(none\)
\[MakerNotes\]    Focus Continuous                : Continuous
\[MakerNotes\]    AE Setting                      : Normal AE
\[MakerNotes\]    Image Stabilization             : On \(2\)
\[MakerNotes\]    Zoom Source Width               : 5472
\[MakerNotes\]    Zoom Target Width               : 5472
\[MakerNotes\]    Spot Metering Mode              : Center
\[MakerNotes\]    Manual Flash Output             : n/a
\[MakerNotes\]    Auto ISO                        : 116
\[MakerNotes\]    Base ISO                        : 200
\[MakerNotes\]    Measured EV                     : 14\.31
\[MakerNotes\]    Target Aperture                 : 4\.5
\[MakerNotes\]    Target Exposure Time            : 1/1244
\[MakerNotes\]    Exposure Compensation           : 0
\[MakerNotes\]    White Balance                   : Auto
\[MakerNotes\]    Slow Shutter                    : Off
\[MakerNotes\]    Shot Number In Continuous Burst : 0
\[MakerNotes\]    Optical Zoom Code               : 9
\[MakerNotes\]    Flash Guide Number              : 0
\[MakerNotes\]    Flash Exposure Compensation     : 0
\[MakerNotes\]    Auto Exposure Bracketing        : Off
\[MakerNotes\]    AEB Bracket Value               : 0
\[MakerNotes\]    Control Mode                    : Camera Local Control
\[MakerNotes\]    Focus Distance Upper            : 65\.53 m
\[MakerNotes\]    Focus Distance Lower            : 0 m
\[MakerNotes\]    F Number                        : 4\.8
\[MakerNotes\]    Exposure Time                   : 1/1448
\[MakerNotes\]    Bulb Duration                   : 0
\[MakerNotes\]    Camera Type                     : Compact
\[MakerNotes\]    Auto Rotate                     : None
\[MakerNotes\]    ND Filter                       : Off
\[MakerNotes\]    Self Timer 2                    : 0
\[MakerNotes\]    Flash Output                    : 0
\[MakerNotes\]    Canon Image Type                : IMG:PowerShot G7 X JPEG
\[MakerNotes\]    Canon Firmware Version          : Firmware Version 1\.00
\[MakerNotes\]    File Number                     : 118\-4673
\[MakerNotes\]    Camera Temperature              : 27 C
\[MakerNotes\]    Canon Model ID                  : PowerShot G7 X
\[MakerNotes\]    Thumbnail Image Valid Area      : 0 159 7 112
\[MakerNotes\]    Date Stamp Mode                 : Off
\[MakerNotes\]    My Color Mode                   : Off
\[MakerNotes\]    Firmware Revision               : 1\.00 rev 4\.00
\[MakerNotes\]    Categories                      : \(none\)
\[MakerNotes\]    Intelligent Contrast            : Off
\[MakerNotes\]    Image Unique ID                 : 24175e01993d4a6282f6143d3085d4d7
\[MakerNotes\]    Faces Detected                  : 0
\[MakerNotes\]    Time Zone                       : \+00:00
\[MakerNotes\]    Time Zone City                  : \(not set\)
\[MakerNotes\]    Daylight Savings                : Off
\[MakerNotes\]    AF Area Mode                    : Auto
\[MakerNotes\]    Num AF Points                   : 35
\[MakerNotes\]    Valid AF Points                 : 31
\[MakerNotes\]    Canon Image Width               : 5472
\[MakerNotes\]    Canon Image Height              : 3648
\[MakerNotes\]    AF Image Width                  : 100
\[MakerNotes\]    AF Image Height                 : 100
\[MakerNotes\]    AF Area Widths                  : 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12
\[MakerNotes\]    AF Area Heights                 : 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18 18
\[MakerNotes\]    AF Area X Positions             : \-24 \-12 0 12 24 \-36 \-24 \-12 0 12 24 36 \-36 \-24 \-12 0 12 24 36 \-36 \-24 \-12 0 12 24 36 \-24 \-12 0 12 24 0 12 24 36
\[MakerNotes\]    AF Area Y Positions             : \-36 \-36 \-36 \-36 \-36 \-18 \-18 \-18 \-18 \-18 \-18 \-18 0 0 0 0 0 0 0 18 18 18 18 18 18 18 36 36 36 36 36 36 36 36 36
\[MakerNotes\]    AF Points In Focus              : 6,7,12,13,14,19,20
\[MakerNotes\]    Aspect Ratio                    : 3:2
\[MakerNotes\]    Cropped Image Width             : 5472
\[MakerNotes\]    Cropped Image Height            : 3648
\[MakerNotes\]    Cropped Image Left              : 0
\[MakerNotes\]    Cropped Image Top               : 0
\[MakerNotes\]    VRD Offset                      : 0
\[Composite\]     Drive Mode                      : Single\-frame Shooting
\[Composite\]     ISO                             : 233
\[Composite\]     Lens                            : 8\.8 \- 36\.8 mm
\[Composite\]     Shooting Mode                   : Full auto
\[Composite\]     Aperture                        : 4\.5
\[Composite\]     Image Size                      : 630x420
\[Composite\]     Lens ID                         : Unknown 8\-36mm
\[Composite\]     Megapixels                      : 0\.265
\[Composite\]     Scale Factor To 35 mm Equivalent: 4\.4
\[Composite\]     Shutter Speed                   : 1/1250
\[Composite\]     Lens                            : 8\.8 \- 36\.8 mm \(35 mm equivalent: 38\.6 \- 161\.4 mm\)
\[Composite\]     Circle Of Confusion             : 0\.007 mm
\[Composite\]     Depth Of Field                  : inf \(3\.12 m \- inf\)
\[Composite\]     Field Of View                   : 43\.4 deg
\[Composite\]     Focal Length                    : 10\.3 mm \(35 mm equivalent: 45\.2 mm\)
\[Composite\]     Hyperfocal Distance             : 3\.45 m
\[Composite\]     Light Value                     : 13\.3
            """.strip() + "\n$",  # noqa: E501, W291
            text=cast(str, result)
        )
