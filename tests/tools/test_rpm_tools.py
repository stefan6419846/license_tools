# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from license_tools.tools import rpm_tools
from license_tools.utils.path_utils import get_files_from_directory
from tests import get_from_url
from tests.data import LIBAIO1__0_3_109_1_25__RPM, LIBAIO1__0_3_109_1_25__SRC_RPM


class ExtractTestCase(TestCase):
    def test_unpack_rpm_file(self) -> None:
        with get_from_url(LIBAIO1__0_3_109_1_25__RPM) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            rpm_tools.extract(
                archive_path=path, target_path=directory
            )
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(
                [
                    "lib64/libaio.so.1",
                    "lib64/libaio.so.1.0.1",
                    "usr/share/doc/packages/libaio1/COPYING",
                    "usr/share/doc/packages/libaio1/TODO",
                ],
                actual,
            )


class FileModesTestCase(TestCase):
    def test_make_verbose(self) -> None:
        modes = [41471, 33261, 16877, 33188]
        expected_by_mode = [
            [
                "IS_SYMBOLIC_LINK",
                "READ_BY_OWNER_ALTERNATIVE",
                "WRITE_BY_OWNER_ALTERNATIVE",
                "EXECUTE_BY_OWNER_ALTERNATIVE",
                "READ_WRITE_EXECUTE_BY_OWNER",
                "READ_BY_OWNER",
                "WRITE_BY_OWNER",
                "EXECUTE_BY_OWNER",
                "READ_WRITE_EXECUTE_BY_GROUP",
                "READ_BY_GROUP",
                "WRITE_BY_GROUP",
                "EXECUTE_BY_GROUP",
                "READ_WRITE_EXECUTE_BY_OTHERS",
                "READ_BY_OTHERS",
                "WRITE_BY_OTHERS",
                "EXECUTE_BY_OTHERS",
            ],
            [
                "IS_REGULAR_FILE",
                "READ_BY_OWNER_ALTERNATIVE",
                "WRITE_BY_OWNER_ALTERNATIVE",
                "EXECUTE_BY_OWNER_ALTERNATIVE",
                "READ_WRITE_EXECUTE_BY_OWNER",
                "READ_BY_OWNER",
                "WRITE_BY_OWNER",
                "EXECUTE_BY_OWNER",
                "READ_BY_GROUP",
                "EXECUTE_BY_GROUP",
                "READ_BY_OTHERS",
                "EXECUTE_BY_OTHERS",
            ],
            [
                "IS_DIRECTORY",
                "READ_BY_OWNER_ALTERNATIVE",
                "WRITE_BY_OWNER_ALTERNATIVE",
                "EXECUTE_BY_OWNER_ALTERNATIVE",
                "READ_WRITE_EXECUTE_BY_OWNER",
                "READ_BY_OWNER",
                "WRITE_BY_OWNER",
                "EXECUTE_BY_OWNER",
                "READ_BY_GROUP",
                "EXECUTE_BY_GROUP",
                "READ_BY_OTHERS",
                "EXECUTE_BY_OTHERS",
            ],
            [
                "IS_REGULAR_FILE",
                "READ_BY_OWNER_ALTERNATIVE",
                "WRITE_BY_OWNER_ALTERNATIVE",
                "READ_BY_OWNER",
                "WRITE_BY_OWNER",
                "READ_BY_GROUP",
                "READ_BY_OTHERS",
            ],
        ]
        for mode, expected in zip(modes, expected_by_mode):
            with self.subTest(mode=mode):
                self.assertEqual(expected, rpm_tools.FileModes.make_verbose(mode))


class CheckRpmHeadersTestCase(TestCase):
    maxDiff = None

    def test_binary(self) -> None:
        if sys.version_info < (3, 11):
            file_flags = "[<FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.DOC: 2>, <FileFlags.DOC: 2>]"
            file_verification_flags = "[<VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.0: 0>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>]"  # noqa: E501
            required_names_flags = "[<DependencyFlags.SCRIPT_POST|INTERP: 1280>, <DependencyFlags.SCRIPT_POSTUN|INTERP: 4352>, <DependencyFlags.FIND_REQUIRES: 16384>, <DependencyFlags.FIND_REQUIRES: 16384>, <DependencyFlags.RPMLIB|EQUAL|LESS: 16777226>, <DependencyFlags.RPMLIB|EQUAL|LESS: 16777226>, <DependencyFlags.RPMLIB|EQUAL|LESS: 16777226>, <DependencyFlags.RPMLIB|EQUAL|LESS: 16777226>]"  # noqa: E501
        else:
            file_flags = "[<FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags.DOC: 2>, <FileFlags.DOC: 2>]"
            file_verification_flags = "[<VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags: 0>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>]"  # noqa: E501
            required_names_flags = "[<DependencyFlags.INTERP|SCRIPT_POST: 1280>, <DependencyFlags.INTERP|SCRIPT_POSTUN: 4352>, <DependencyFlags.FIND_REQUIRES: 16384>, <DependencyFlags.FIND_REQUIRES: 16384>, <DependencyFlags.LESS|EQUAL|RPMLIB: 16777226>, <DependencyFlags.LESS|EQUAL|RPMLIB: 16777226>, <DependencyFlags.LESS|EQUAL|RPMLIB: 16777226>, <DependencyFlags.LESS|EQUAL|RPMLIB: 16777226>]"  # noqa: E501

        with get_from_url(LIBAIO1__0_3_109_1_25__RPM) as rpm_path:
            results = rpm_tools.check_rpm_headers(rpm_path)
        self.assertEqual(
            r"""
                                                            Header Signatures: b'\x00\x00\x00>\x00\x00\x00\x07\xff\xff\xffp\x00\x00\x00\x10'
                                              OpenPGP RSA Signature Of Header: b'\x89\x01\x15\x03\x05\x00[\x08R$p\xaf\x9e\x819\xdb|\x82\x01\x08\x8a\xe2\x08\x00\xc2_\x1a\x1f\xc7E>\x9f\x96"(\x0eF4b>\xb4\x00\x99\xb1y\xab\xb1\xa8>\xe4\xe4\xeb\x99\xe2?D`\xd3\x0eS\xc7P{{\x88\x8d\xa3dB\xa3\xef\\{{\xa3\xf8\x06cg\xc1\x98\xea\x82u\xa4\xb9.r^o\x91\xe2o\x19\x1c\xcc$\xf9\xcd\x1b\x85\x98f[\xa2\xdd!3_\xde\x81\xea`\x99\xeb\x83Y\xd1\xfaw\x81\xf774\xd1\x11\xf6\xbf\x98\xb2\xb1\x84\xf1\x9e^l\x1eY\xc9\x9c\x1c\xed\xc8\xd3[X\xeb\xc7h7\x82V\xab\x80\xd7]\xb0\xdbC\x86\xe2\xc0\x9d\x86\xd0 %\x1e{{\x1c\xd394\x89\xabp8\x04GE\xf4Z4(\xeaoF\xec\xe1\x9c&\xd1\x17z\x8dC/\x08\xf0\x0e(\xcc9\x04\xddJ\xb3b\xe4)\x8b\'\xac\x15\xb6\x1a?\xb2\xd9\xdf\xbeJ\xf7\xd8\xfa~*\xaa\xa5S\x8c\xd8\x0c\xd1J\xec<j\xee\xf3\xab9\x10Fe\xaa4I\xf4;\xd4v\x83\xe9BMN\xff\xd3{{\xb2\xd1(Py"\x1f\'\'(\xc9?:\xb1\xee\xd9\x0f\x1f\x8c\x9d|P'
                                                        SHA1 Digest Of Header: dbeb3eb27337e5d21b569b6cc73165320c35164b
                                                      SHA256 Digest Of Header: 3c4d1b9d2da6a1223c2ed6b2187f6c9618982c9526405ab88112fde3a06fe03e
                                                       Installed Package Size: 32262
                                          PGP Signature From Signature Header: b'\x89\x01\x15\x03\x05\x00[\x08R$p\xaf\x9e\x819\xdb|\x82\x01\x08\xdb`\x07\xfe%\xfa\x0e\x97\xacl\xf7\x12\xb5\xf0h\xd8\x12q\x88\x008\xf0\xa7\xffJF\x91\xfb4\xb5<:\xf5\x84=\xbb\xeeFH]3\xf7{{\x87\xa9G\xa5\xeb\x0f*V\xcf\x97O\xea\x9f\xaf:v8\x90\xf2\xbd\x9dh\xf2\xee(\xf4\x8a\x0f8\x15\xa9\xd2;Op\x04a\x11\x11\xf1\xd2\xf0ir\xcaC\xa3\xe4\x84\xcd\xac\x91]\xf3\xed/\xc5\xf2H\x17[j\xc1\x95\x11\nX\x8d\x0f\xed\xb6\xbcy,\xcc\xd7\xbajh\x94o\xca\xe1\x10\x9ap\xd1\xa9\x9f^\xb8\x08\xe0j\x18\xc1!\x9f\xc0\xa5\xf8\xeb.Z\x81L\x82\x97\xf0.\xed\xe2UHu\xd0(\xfc\x0f\xab\xf3FvC\xe08K\x10\xdb\xf9\x08\xb0\x18 \xff!\xce\xe5\xb4\xd6\xec\xbf\x7f\xe2\xb2\xa1\xc7\x92\xc3\n\x8bA\xdd\xfdf\x18*\xc8\x98\xc4\xcf\x15%\x1c\x9f\xc7\x16\xb0@:9\xbd\xc3|\xc2}}\xd2i\xa3\xe2t\x98\x8e\np\x1eQ\x9dd\xb3K\x1f\x03\x9eA\x92O\xcb\x8f\xa1\xdf\x17~1\x94\xcd\xe7c\xd6\xd0\xb1O\xe5* \xdd\x0f'
                                               MD5 Digest Of Header + Payload: b'\x983\xff\x1f\x06\xea\xc3\xd5\xf1\xec\xf9\x1b\xba\xd95\r'
                                                                 Payload Size: 33116
                                                               Reserved Space: 4128
                                            Unmodified, Original Header Image: b'\x00\x00\x00?\x00\x00\x00\x07\xff\xff\xfb\xd0\x00\x00\x00\x10'
                                                   Header Translation Locales: ['C']
                                                                 Package Name: libaio1
                                                              Package Version: 0.3.109
                                                              Package Release: 1.25
                                                             One-line Summary: Linux-Native Asynchronous I/O Access Library
                                                       Multi-line Description: The Linux-native asynchronous I/O facility ("async I/O", or "aio") has
a richer API and capability set than the simple POSIX async I/O
facility. This library provides the Linux-native API for async I/O. The
POSIX async I/O facility requires this library to provide
kernel-accelerated async I/O capabilities, as do applications that
require the Linux-native async I/O API.
                                                           Package Build Time: datetime.datetime(2018, 5, 25, 18, 12, 44, tzinfo=datetime.timezone.utc)
                                                     Hostname Of Build System: sheep53
                                                            Distribution Name: SUSE Linux Enterprise 15
                                                               Package Vendor: SUSE LLC <https://www.suse.com/>
                                                          License Of Contents: LGPL-2.1+
                                                                     Packager: https://www.suse.com/
                                                                Package Group: System/Libraries
                                                                 Upstream URL: http://kernel.org/pub/linux/libs/aio/
                                                             Operating System: linux
                                                                 Architecture: x86_64
                                                 File Sizes (when all < 4 GB): [15, 5608, 0, 26532, 122]
                                                             Unix Files Modes: ['<FileModes.IS_SYMBOLIC_LINK|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|EXECUTE_BY_OWNER_ALTERNATIVE|READ_WRITE_EXECUTE_BY_OWNER|READ_BY_OWNER|WRITE_BY_OWNER|EXECUTE_BY_OWNER|READ_WRITE_EXECUTE_BY_GROUP|READ_BY_GROUP|WRITE_BY_GROUP|EXECUTE_BY_GROUP|READ_WRITE_EXECUTE_BY_OTHERS|READ_BY_OTHERS|WRITE_BY_OTHERS|EXECUTE_BY_OTHERS: 41471>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|EXECUTE_BY_OWNER_ALTERNATIVE|READ_WRITE_EXECUTE_BY_OWNER|READ_BY_OWNER|WRITE_BY_OWNER|EXECUTE_BY_OWNER|READ_BY_GROUP|EXECUTE_BY_GROUP|READ_BY_OTHERS|EXECUTE_BY_OTHERS: 33261>', '<FileModes.IS_DIRECTORY|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|EXECUTE_BY_OWNER_ALTERNATIVE|READ_WRITE_EXECUTE_BY_OWNER|READ_BY_OWNER|WRITE_BY_OWNER|EXECUTE_BY_OWNER|READ_BY_GROUP|EXECUTE_BY_GROUP|READ_BY_OTHERS|EXECUTE_BY_OTHERS: 16877>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>']
                                                 Device IDs (of device files): [0, 0, 0, 0, 0]
                                                 File Modification Timestamps: [datetime.datetime(2018, 5, 25, 18, 12, 43, tzinfo=datetime.timezone.utc), datetime.datetime(2018, 5, 25, 18, 12, 43, tzinfo=datetime.timezone.utc), datetime.datetime(2018, 5, 25, 18, 12, 44, tzinfo=datetime.timezone.utc), datetime.datetime(2009, 10, 9, 18, 17, 2, tzinfo=datetime.timezone.utc), datetime.datetime(2009, 10, 9, 18, 17, 2, tzinfo=datetime.timezone.utc)]
                                                                    File Hash: ['', 'bf8977f717cdf65b34fdad5e00daec89bdbc9a6ac512887c5cf2e78ff7cc7191', '', '5bbcbb737e60fe9deba08ecbd00920cfcc3403ba2e534c64fdeea49d6bb87509', 'f7b7efb8cb7bf444fe0f8c97f0989308e0a6d54e888c87db501494973d2c656b']
                                                         File Symlink Targets: ['libaio.so.1.0.1', '', '', '', '']
                                                                   File Flags: {file_flags}
                                                        File Unix Owner Names: ['root', 'root', 'root', 'root', 'root']
                                                        File Unix Group Names: ['root', 'root', 'root', 'root', 'root']
                                                          Source RPM Filename: libaio-0.3.109-1.25.src.rpm
                                                      File Verification Flags: {file_verification_flags}
                                                               Provided Names: ['libaio', 'libaio.so.1()(64bit)', 'libaio.so.1(LIBAIO_0.1)(64bit)', 'libaio.so.1(LIBAIO_0.4)(64bit)', 'libaio1', 'libaio1(x86-64)']
                                                       Required Names (Flags): {required_names_flags}
                                                               Required Names: ['/sbin/ldconfig', '/sbin/ldconfig', 'libc.so.6()(64bit)', 'libc.so.6(GLIBC_2.4)(64bit)', 'rpmlib(CompressedFileNames)', 'rpmlib(FileDigests)', 'rpmlib(PayloadFilesHavePrefix)', 'rpmlib(PayloadIsXz)']
                                                    Required Names (Versions): ['', '', '', '', '3.0.4-1', '4.6.0-1', '4.0-1', '5.2-1']
                                                     RPM Version For Building: 4.14.1
                                                         Changelog Timestamps: [datetime.datetime(2016, 4, 17, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2014, 8, 26, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2013, 3, 1, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2012, 2, 17, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2012, 2, 16, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2012, 2, 13, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 11, 28, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 11, 28, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 10, 5, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 9, 30, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 3, 15, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2010, 2, 12, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2010, 1, 23, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2009, 8, 2, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2009, 3, 3, 12, 0, tzinfo=datetime.timezone.utc)]
                                                            Changelog Authors: ['meissner@suse.com', 'fcrozat@suse.com', 'dmueller@suse.com', 'coolo@suse.com', 'mvyskocil@suse.cz', 'coolo@suse.com', 'jengelh@medozas.de', 'ro@suse.de', 'uli@suse.com', 'adrian@suse.de', 'jengelh@medozas.de', 'jengelh@medozas.de', 'jengelh@medozas.de', 'jansimon.moeller@opensuse.org', 'crrodriguez@suse.de']
                                                              Changelog Texts: ['- libaio-optflags.diff: readd -stdlib to allow -fstack-protector-strong\n  builds (unclear why it was not allowed)\n- 01_link_libgcc.patch, 02_libdevdir.patch: refreshed', '- Add obsoletes/provides to baselibs.conf (bsc#881698)', '- Add libaio-aarch64-support.diff:\n  * add support for aarch64\n- Add libaio-generic-arch.diff:\n  * support all archtes (also aarch64)', '- fix baselibs.conf after shlib split', '- fix typo versoin/version', '- patch license to follow spdx.org standard', '- Remove redundant/unwanted tags/section (cf. specfile guidelines)\n- Employ shlib packaging', '- fix lib64 platform check', '- cross-build fix: use %__cc macro', '- drop debian arm hack to fix build on arm ;)', '- Update to libaio 0.3.109\n  * add ARM architecture support (grabbed from Debian arches tree)\n  * replace check of __i386__ with __LP64__ in test harness\n- refreshed patches', '- fix more symbolic links to not include a /usr/src/ prefix', '- update to libaio 0.3.107\n- add more patches from Debian to fix compile errors on SPARC\n- package baselibs.conf', '- add ARM support to libaio sources', '- remove static libraries\n- fix -devel package dependencies']
                                    Post-installation Interpreter + Arguments: /sbin/ldconfig
                                  Post-uninstallation Interpreter + Arguments: /sbin/ldconfig
                                                               Obsolete Names: ['libaio']
                                                   Cookie For Build Operation: sheep53 1527271964
                                                                 File Devices: [1, 1, 1, 1, 1]
                                                  Abstract File Inode Numbers: [1, 2, 3, 4, 5]
                                                               File Languages: ['', '', '', '', '']
                                                       Provided Names (Flags): [<DependencyFlags.EQUAL: 8>, <DependencyFlags.FIND_PROVIDES: 32768>, <DependencyFlags.FIND_PROVIDES: 32768>, <DependencyFlags.FIND_PROVIDES: 32768>, <DependencyFlags.EQUAL: 8>, <DependencyFlags.EQUAL: 8>]
                                                    Provided Names (Versions): ['0.3.109-1.25', '', '', '', '0.3.109-1.25', '0.3.109-1.25']
                                                       Obsolete Names (Flags): <DependencyFlags.LESS: 2>
                                                    Obsolete Names (Versions): ['0.3.109-1.25']
                                     Index Into Directory Names For Basenames: [0, 0, 1, 2, 2]
                                                                    Basenames: ['libaio.so.1', 'libaio.so.1.0.1', 'libaio1', 'COPYING', 'TODO']
                                                              Directory Names: ['/lib64/', '/usr/share/doc/packages/', '/usr/share/doc/packages/libaio1/']
                                               %{{optflags}} Value During Build: -fmessage-length=0 -grecord-gcc-switches -O2 -Wall -D_FORTIFY_SOURCE=2 -fstack-protector-strong -funwind-tables -fasynchronous-unwind-tables -fstack-clash-protection -g
                                                    Distribution-specific URL: obs://build.suse.de/SUSE:SLE-15:GA/standard/77c22af2cb0aefbc84316daac8f5b8ac-libaio
                                                               Payload Format: cpio
                                                      Payload Compressor Name: xz
                                                     Payload Compressor Level: 5
                                                             Package Platform: x86_64-suse-linux
                                                  Index Into Class Dictionary: [0, 1, 2, 3, 3]
                               Class Dictionary (File Class libmagic Entries): ['', 'ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, BuildID[sha1]=98eb213e51c843c9263a66ad0a5718c06a388a1c, stripped', 'directory', 'ASCII text']
Index Into File Dependencies Dictionary Denoting Start Of File's Dependencies: [0, 0, 0, 0, 0]
                       Number Of File Dependencies in Dependencies Dictionary: [0, 6, 0, 0, 0]
                                                 File Dependencies Dictionary: [1342177282, 1342177283, 1342177283, 1342177281, 1375731715, 1375731714]
                                                    Source Package Identifier: b'\xcc\x8cLq\xe6\xf8\xcb\xbf\xfa\x14\xcc6Li\x18\x85'
                                                        File Digest Algorithm: <FileDigestAlgorithm.SHA512: 8>
                                                  Header String Data Encoding: utf-8
                                   Cryptographic Digest Of Compressed Payload: ['f001b298e5add90e4d2fdbc442b92b8aae7beb5fac77159a5baa33fb7217d48a']
                                                     Payload Digest Algorithm: <FileDigestAlgorithm.SHA512: 8>
"""[1:-1].format(file_flags=file_flags, file_verification_flags=file_verification_flags, required_names_flags=required_names_flags),  # noqa: E501
            results
        )

    def test_source(self) -> None:
        if sys.version_info < (3, 11):
            file_flags = "[<FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.0: 0>, <FileFlags.SPECFILE: 32>]"  # noqa: E501
            required_names_flags = "[<DependencyFlags.RPMLIB|EQUAL|LESS: 16777226>, <DependencyFlags.RPMLIB|EQUAL|LESS: 16777226>]"
            file_verification_flags = "[<VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>, <VerifyFlags.2147483648|1073741824|536870912|268435456|134217728|67108864|33554432|16777216|8388608|4194304|2097152|1048576|524288|262144|131072|65536|32768|16384|8192|4096|2048|1024|512|CAPS|RDEV|MODE|MTIME|GROUP|USER|LINK_TO|SIZE|MD5: 4294967295>]"  # noqa: E501
        else:
            file_flags = "[<FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags: 0>, <FileFlags.SPECFILE: 32>]"  # noqa: E501
            required_names_flags = "[<DependencyFlags.LESS|EQUAL|RPMLIB: 16777226>, <DependencyFlags.LESS|EQUAL|RPMLIB: 16777226>]"
            file_verification_flags = "[<VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>, <VerifyFlags.MD5|SIZE|LINK_TO|USER|GROUP|MTIME|MODE|RDEV|CAPS|4294966784: 4294967295>]"  # noqa: E501

        with get_from_url(LIBAIO1__0_3_109_1_25__SRC_RPM) as rpm_path:
            results = rpm_tools.check_rpm_headers(rpm_path)
        self.assertEqual(
            r"""
                         Header Signatures: b'\x00\x00\x00>\x00\x00\x00\x07\xff\xff\xffp\x00\x00\x00\x10'
           OpenPGP RSA Signature Of Header: b'\x89\x01\x15\x03\x05\x00[\x08R$p\xaf\x9e\x819\xdb|\x82\x01\x08H\x05\x08\x00\x85wx\x9dG\xe0$\xfe\xf8\xf1*y\xfa\xc1\x0c\xa1-\xc9 B\xed\xf3\xfa\'\x80v\x91\xe1Wl\x02\xaf\x94\x06>^$\xe1\xca\xf3\x06\xc5\xaa\xa6\xa1\x85\x98\xa3\xdc\x00+\x03\xdd\x98\xef\xd2\x1d\x9b*\xb6Bu6J\xad\xf0\x12\xc9\xbb8"\x84\x9e\xbd\x87)\x94\xf3\xb4\x832\x99\xc1k\xf7r\xa3\xbf\xe9\xecA\xaf\x86\x02\xee\xb7\xb36;8\xc5\x19{{C\xfat\xdc\xec,\xdc\xef)\x92\xc4\xd3\xcd7\x88\xe0q\x18@\x95\x89n\xc3\x8a\xaah\\\x83\xd4L\xaa.\x00\xf3[\xce\xab\x17*D\xe4\xa4-\x1d-\x89\x15^\x02m\xec"\xca\n\xc4\xb9>\xcbS?\x14\x03\x00\x05#x\xb5\x83f\xc68A\x16\xe2k\x0e\x7f\x9bi\x9a\xe9\x88\xda\xf2j\t!K\xe7d\xa5\xf3\xaa2\xaay\xf2v\'\xb0\x11\xc9\x9an\xf2\x06\xefW6d\xa8\xf1\x85\xc7)\xc1\x05<\xea|\x8cJ\xb2\xc0\xd9\xe7\x10V=\xcd4\xf5:\xff\xf1\x1cL\xe5\xff9_\x14\'\x85u\xcd\xae\x8f\x11J\xf8\xd46'
                     SHA1 Digest Of Header: 42dd9660c0752a72f332b198f09c57a2a27a621e
                   SHA256 Digest Of Header: 453f75a56cd0fec8359b87d82e5423d332a4fe4c4fd2379261eea0d784e07a9a
                    Installed Package Size: 158737
       PGP Signature From Signature Header: b'\x89\x01\x15\x03\x05\x00[\x08R$p\xaf\x9e\x819\xdb|\x82\x01\x08\xc5c\x08\x00\xa5a\xe4\x8f\xa4_R\xb1s;:,+He40\x13\xdaZ\xb9\x83\xbf\xb4\xc7\xa2\xe1\x9c\x80\xcf\x07\x02\x04\xbd0\x84\xfa\xf5\x93\xaf\xb0\xf3Y\xe7C\x84\xc1wFe\'\xc3\xcaGC\xb8}}\x8d\xd4E\x11\x03\xf1\xab\xe8\xf8\x9aw\xcb\x8e\xf7J(\x90\xb8h\xe0\x07\xf3\xbd\x12\x0b\xac\xa0\xf0#\x1c"/DRL\xfep5\x11@\x07cS?\xfb\\)&\xc86\x18\xb1G\xdf\xcd\xe7\xc1(1S-\xdc]\xc1\x00\xd6\x9a\x85D\xf1\xb6\x9f\xc2\xc2\xa8o\xe8\x9d\xceGk\xca\xdb.Id0[ZW\x1f\xb1C\xdd5\x82\x83\x1a\xa0\xca\x89\x18G\xfd\x98Y\x1d.D\x8b\xbdJuq\x13\xaf\xb1L\xd13\xcer6}}(\xd9\x7fhb\x97\x8a\x0b\x859\xf5(3\xd9\x0b\xcf=N\x05Ljh\x11^\xe0\x8f\x1b\xb4\x03\xb6\x1aq\xf0Z\xcd\xf6nf+\x86\x18\xa5zD\xcf\xab\x83\x16\x8e\xbceF<\xa8\x9b\x86\xf5\xd6\xf51G^\\\xad\x9d\x87\xb5\x12\x7f\x94\'v6n\x98'
            MD5 Digest Of Header + Payload: b'\xcc\x8cLq\xe6\xf8\xcb\xbf\xfa\x14\xcc6Li\x18\x85'
                              Payload Size: 160320
                            Reserved Space: 4128
         Unmodified, Original Header Image: b'\x00\x00\x00?\x00\x00\x00\x07\xff\xff\xfc\xb0\x00\x00\x00\x10'
                Header Translation Locales: ['C']
                              Package Name: libaio
                           Package Version: 0.3.109
                           Package Release: 1.25
                          One-line Summary: Linux-Native Asynchronous I/O Access Library
                    Multi-line Description: The Linux-native asynchronous I/O facility ("async I/O", or "aio") has
a richer API and capability set than the simple POSIX async I/O
facility. This library provides the Linux-native API for async I/O. The
POSIX async I/O facility requires this library to provide
kernel-accelerated async I/O capabilities, as do applications that
require the Linux-native async I/O API.
                        Package Build Time: datetime.datetime(2018, 5, 25, 18, 12, 44, tzinfo=datetime.timezone.utc)
                  Hostname Of Build System: sheep53
                         Distribution Name: SUSE Linux Enterprise 15
                            Package Vendor: SUSE LLC <https://www.suse.com/>
                       License Of Contents: LGPL-2.1+
                                  Packager: https://www.suse.com/
                             Package Group: Development/Libraries/C and C++
                         Source File Names: ['baselibs.conf', 'libaio-0.3.109.tar.bz2']
                          Patch File Names: ['libaio-generic-arch.diff', 'libaio-aarch64-support.diff', '03_man_errors.patch', '02_libdevdir.patch', '01_link_libgcc.patch', '00_arches_sh.patch', '00_arches.patch', 'libaio-optflags.diff']
                              Upstream URL: http://kernel.org/pub/linux/libs/aio/
                          Operating System: linux
                              Architecture: x86_64
              File Sizes (when all < 4 GB): [22666, 5028, 500, 2159, 73868, 207, 43579, 1018, 2053, 512, 7147]
                          Unix Files Modes: ['<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>', '<FileModes.IS_REGULAR_FILE|READ_BY_OWNER_ALTERNATIVE|WRITE_BY_OWNER_ALTERNATIVE|READ_BY_OWNER|WRITE_BY_OWNER|READ_BY_GROUP|READ_BY_OTHERS: 33188>']
              Device IDs (of device files): [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
              File Modification Timestamps: [datetime.datetime(2011, 3, 24, 8, 43, 41, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 3, 24, 8, 43, 41, tzinfo=datetime.timezone.utc), datetime.datetime(2016, 4, 22, 14, 18, tzinfo=datetime.timezone.utc), datetime.datetime(2016, 4, 22, 14, 18, tzinfo=datetime.timezone.utc), datetime.datetime(2010, 2, 11, 19, 16, 55, tzinfo=datetime.timezone.utc), datetime.datetime(2014, 8, 26, 11, 53, 35, tzinfo=datetime.timezone.utc), datetime.datetime(2009, 11, 20, 14, 31, 19, tzinfo=datetime.timezone.utc), datetime.datetime(2013, 3, 1, 10, 32, 38, tzinfo=datetime.timezone.utc), datetime.datetime(2013, 3, 1, 10, 32, 38, tzinfo=datetime.timezone.utc), datetime.datetime(2016, 4, 22, 14, 18, tzinfo=datetime.timezone.utc), datetime.datetime(2018, 5, 25, 18, 12, 42, tzinfo=datetime.timezone.utc)]
                                 File Hash: ['ab4b71ed9914e09c9470ed193e6049ab251e2f13bc17e7a54f5c74c0965c841e', 'e14215abee7b135f9d0d832e3544b30dc3e7540b0ccec8414ce42b1a47a86986', '9e615a1fe27800756e68017d25c8e029614a72993d27d4ecfe59d410867a0b8f', '2474d6f7378e254d47370b68a992f08ad30e8b522234c283754361accec55aea', 'cb4b2b1a128f9eb1ab6f39660359098950cb1906eb883d8b6ad38e8fa8c319fa', 'aa4d278101271a5a269ca3471402203d70f8da05c42d46c52be1b2e24f95cf59', 'b5cefce0a3cb49f8dca4d00e9480c0d9b45b75863bd44764156e322ee214e794', '76beebbc9cc994a1be1dbe686a4c20d5374462da03ffa512083ccd2dac940c1e', 'e91be00e676f63a54a82699c3e20766248587edc09f84bfd8207743519a8dfca', 'fa8847f11938773bd93ab17bd2b1319bb2fe094561aeaaf75fd840205ff112ff', '6261948d71f6ff1c4c321ddef3bb655196d898ac08b44ec7ec1ee20d9d59dcf6']
                      File Symlink Targets: ['', '', '', '', '', '', '', '', '', '', '']
                                File Flags: {file_flags}
                     File Unix Owner Names: ['root', 'root', 'root', 'root', 'root', 'root', 'root', 'root', 'root', 'root', 'root']
                     File Unix Group Names: ['root', 'root', 'root', 'root', 'root', 'root', 'root', 'root', 'root', 'root', 'root']
                   File Verification Flags: {file_verification_flags}
                    Required Names (Flags): {required_names_flags}
                            Required Names: ['rpmlib(CompressedFileNames)', 'rpmlib(FileDigests)']
                 Required Names (Versions): ['3.0.4-1', '4.6.0-1']
                  RPM Version For Building: 4.14.1
                      Changelog Timestamps: [datetime.datetime(2016, 4, 17, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2014, 8, 26, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2013, 3, 1, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2012, 2, 17, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2012, 2, 16, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2012, 2, 13, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 11, 28, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 11, 28, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 10, 5, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 9, 30, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2011, 3, 15, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2010, 2, 12, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2010, 1, 23, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2009, 8, 2, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2009, 3, 3, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2008, 12, 10, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2008, 12, 4, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2008, 4, 10, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2007, 9, 27, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2007, 8, 2, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2006, 1, 25, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2005, 5, 5, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2005, 4, 27, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2004, 12, 1, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2004, 4, 20, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2004, 3, 12, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2004, 3, 2, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2004, 1, 11, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2003, 10, 1, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2003, 4, 23, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2003, 4, 23, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2003, 4, 11, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2003, 4, 3, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2002, 10, 1, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2002, 9, 20, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2002, 9, 19, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2002, 9, 17, 12, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2002, 9, 4, 12, 0, tzinfo=datetime.timezone.utc)]
                         Changelog Authors: ['meissner@suse.com', 'fcrozat@suse.com', 'dmueller@suse.com', 'coolo@suse.com', 'mvyskocil@suse.cz', 'coolo@suse.com', 'jengelh@medozas.de', 'ro@suse.de', 'uli@suse.com', 'adrian@suse.de', 'jengelh@medozas.de', 'jengelh@medozas.de', 'jengelh@medozas.de', 'jansimon.moeller@opensuse.org', 'crrodriguez@suse.de', 'olh@suse.de', 'olh@suse.de', 'ro@suse.de', 'hare@suse.de', 'hare@suse.de', 'mls@suse.de', 'schwab@suse.de', 'kukuk@suse.de', 'kukuk@suse.de', 'meissner@suse.de', 'kukuk@suse.de', 'ro@suse.de', 'adrian@suse.de', 'schwab@suse.de', 'coolo@suse.de', 'coolo@suse.de', 'ro@suse.de', 'kukuk@suse.de', 'meissner@suse.de', 'fehr@suse.de', 'schwab@suse.de', 'ro@suse.de', 'fehr@suse.de']
                           Changelog Texts: ['- libaio-optflags.diff: readd -stdlib to allow -fstack-protector-strong\n  builds (unclear why it was not allowed)\n- 01_link_libgcc.patch, 02_libdevdir.patch: refreshed', '- Add obsoletes/provides to baselibs.conf (bsc#881698)', '- Add libaio-aarch64-support.diff:\n  * add support for aarch64\n- Add libaio-generic-arch.diff:\n  * support all archtes (also aarch64)', '- fix baselibs.conf after shlib split', '- fix typo versoin/version', '- patch license to follow spdx.org standard', '- Remove redundant/unwanted tags/section (cf. specfile guidelines)\n- Employ shlib packaging', '- fix lib64 platform check', '- cross-build fix: use %__cc macro', '- drop debian arm hack to fix build on arm ;)', '- Update to libaio 0.3.109\n  * add ARM architecture support (grabbed from Debian arches tree)\n  * replace check of __i386__ with __LP64__ in test harness\n- refreshed patches', '- fix more symbolic links to not include a /usr/src/ prefix', '- update to libaio 0.3.107\n- add more patches from Debian to fix compile errors on SPARC\n- package baselibs.conf', '- add ARM support to libaio sources', '- remove static libraries\n- fix -devel package dependencies', '- use Obsoletes: -XXbit only for ppc64 to help solver during distupgrade\n  (bnc#437293)', '- obsolete old -XXbit packages (bnc#437293)', '- added baselibs.conf file to build xxbit packages\n  for multilib support', '- Fix dangling symlink (#307063)', '- Use RPM_OPT_FLAGS\n- Fix installation directories', '- converted neededforbuild to BuildRequires', '- Fix ia64 assembler.', '- Update to version 0.3.104', '- Update to version 0.3.102 [#44374]', '- fixed ppc64 alignment problems. [#38801/LTC#7503]', '- Update to 0.3.98 [Bug #35266]', '- use -fPIC for shared objects on ppc', '- add %defattr and %run_ldconfig', '- Fix for ia64.', '- fix build for lib64', '- use BuildRoot', '- fix header to be includable with glibc (#26033)', '- Add missing "const" to libaio.h [#26030]', '- Fixed __syscall_return for ppc.', '- Add syscall defines for x86_64\n- add Andreas fix for testsuite main program to compile on x86_64\n- add another fix to make testsuite build again on ia64', '- Add missing bits for ia64.', '- removed bogus self-provides', '- make package from  libaio-0.3.15-2.5']
                Cookie For Build Operation: sheep53 1527271964
                              File Devices: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
               Abstract File Inode Numbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
                            File Languages: ['', '', '', '', '', '', '', '', '', '', '']
                                Source RPM: 1
  Index Into Directory Names For Basenames: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                                 Basenames: ['00_arches.patch', '00_arches_sh.patch', '01_link_libgcc.patch', '02_libdevdir.patch', '03_man_errors.patch', 'baselibs.conf', 'libaio-0.3.109.tar.bz2', 'libaio-aarch64-support.diff', 'libaio-generic-arch.diff', 'libaio-optflags.diff', 'libaio.spec']
                           Directory Names: ['']
                 Distribution-specific URL: obs://build.suse.de/SUSE:SLE-15:GA/standard/77c22af2cb0aefbc84316daac8f5b8ac-libaio
                            Payload Format: cpio
                   Payload Compressor Name: gzip
                  Payload Compressor Level: 9
                     File Digest Algorithm: <FileDigestAlgorithm.SHA512: 8>
               Header String Data Encoding: utf-8
Cryptographic Digest Of Compressed Payload: ['75c03228af86b5aa125966962a19ec402ab330054264f74a4d877dd357a46c26']
                  Payload Digest Algorithm: <FileDigestAlgorithm.SHA512: 8>
"""[1:-1].format(file_flags=file_flags, file_verification_flags=file_verification_flags, required_names_flags=required_names_flags),  # noqa: E501
            results
        )
