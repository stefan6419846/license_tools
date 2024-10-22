# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

"""
Tools related to RPM files.
"""

from __future__ import annotations

import datetime
import logging
import stat
from enum import IntEnum, IntFlag
from pathlib import Path
from typing import Any, cast

import rpmfile  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)
del logging


# Docs: https://rpm-software-management.github.io/rpm/manual/tags.html
_VERBOSE_HEADER_NAMES = {
    # Known names: https://github.com/srossross/rpmfile/blob/4cd4ae2bd191d3489c95dfa540da14585670adb5/rpmfile/headers.py#L12-L363
    "headersignatures": "Header Signatures",
    "headerimmutable": "Unmodified, Original Header Image",
    "headeri18ntable": "Header Translation Locales",
    "sigsize": "Size Of Header + Payload",
    "sigmd5": "MD5 Digest Of Header + Payload",
    "sigpgp": "OpenPGP RSA Signature Of Header + Payload",
    "siggpg": "OpenPGP DSA Signature Of Header + Payload",
    "pubkeys": "Public PGP Keys",
    "signature": "OpenPGP DSA Signature Of Header",
    "rsaheader": "OpenPGP RSA Signature Of Header",
    "md5": "SHA1 Digest Of Header",  # Wrong name: https://github.com/srossross/rpmfile/issues/26
    "longsigsize": "Header + Payload Size when > 4 GB",
    "longarchivesize": "Uncompressed Payload Size when > 4 GB",
    "sha256": "SHA256 Digest Of Header",
    "veritysignatures": "fsverity Signature (Base64-encoded)",
    "veritysignaturealgo": "fsverity Signature Algorithm ID",
    "pgp": "PGP Signature From Signature Header",
    "pgp5": "PGP5 Signature From Signature Header",
    "gpg": "GPG Signature From Signature Header",
    "payloadsize": "Payload Size",
    "reservedspace": "Reserved Space",
    "name": "Package Name",
    "version": "Package Version",
    "release": "Package Release",
    "serial": "Package Epoch",
    "summary": "One-line Summary",
    "description": "Multi-line Description",
    "buildtime": "Package Build Time",
    "buildhost": "Hostname Of Build System",
    "installtime": "Package Installation Time",
    "size": "Installed Package Size",
    "distribution": "Distribution Name",
    "vendor": "Package Vendor",
    "copyright": "License Of Contents",
    "packager": "Packager",
    "group": "Package Group",
    "changelog": "Changelog",
    "source": "Source File Names",
    "patch": "Patch File Names",
    "url": "Upstream URL",
    "os": "Operating System",
    "arch": "Architecture",
    "prein": "Pre-installation Script",
    "postin": "Post-installation Script",
    "preun": "Pre-uninstallation Script",
    "postun": "Post-uninstallation Script",
    "filesizes": "File Sizes (when all < 4 GB)",
    "filestates": "Per-file Installation Status",
    "filemodes": "Unix Files Modes",
    "filerdevs": "Device IDs (of device files)",
    "filemtimes": "File Modification Timestamps",
    "filemd5s": "File Hash",
    "filelinktos": "File Symlink Targets",
    "fileflags": "File Flags",
    "fileusername": "File Unix Owner Names",
    "filegroupname": "File Unix Group Names",
    "sourcerpm": "Source RPM Filename",
    "fileverifyflags": "File Verification Flags",
    "archivesize": "Uncompressed Payload Size",
    "provides": "Provided Names",
    "requireflags": "Required Names (Flags)",
    "requirename": "Required Names",
    "requireversion": "Required Names (Versions)",
    "nosource": "Source Number Without Source",
    "nopatch": "Patch Number Without Source",
    "conflictflags": "Conflicting Names (Flags)",
    "conflictname": "Conflicting Names",
    "conflictversion": "Conflicting Names (Versions)",
    "excludearch": "Excluded Architecture",
    "excludeos": "Excluded Operating System",
    "exclusivearch": "Exclusive Architecture",
    "exclusiveos": "Exclusive Operating System",
    "rpmversion": "RPM Version For Building",
    "triggerscripts": "Trigger Scripts",
    "triggername": "Trigger Name",
    "triggerversion": "Trigger Version",
    "triggerflags": "Trigger Flags",
    "triggerindex": "Trigger Index",
    "verifyscript": "Verification Script",
    "changelogtime": "Changelog Timestamps",
    "authors": "Changelog Authors",
    "comments": "Changelog Texts",
    "preinprog": "Pre-installation Interpreter + Arguments",
    "postinprog": "Post-installation Interpreter + Arguments",
    "preunprog": "Pre-uninstallation Interpreter + Arguments",
    "postunprog": "Post-uninstallation Interpreter + Arguments",
    "buildarchs": "Possible Architectures",
    "obsoletes": "Obsolete Names",
    "verifyscriptprog": "Verification Interpreter + Arguments",
    "triggerscriptprog": "Trigger Script Interpreter + Arguments",
    "docdir": "Documentation Directory",
    "cookie": "Cookie For Build Operation",
    "filedevices": "File Devices",
    "fileinodes": "Abstract File Inode Numbers",
    "filelangs": "File Languages",
    "prefixes": "Relocatable Prefixes",
    "instprefixes": "Installation Prefixes",
    "sourcepackage": "Source RPM",
    "provideflags": "Provided Names (Flags)",
    "provideversion": "Provided Names (Versions)",
    "obsoleteflags": "Obsolete Names (Flags)",
    "obsoleteversion": "Obsolete Names (Versions)",
    "dirindexes": "Index Into Directory Names For Basenames",
    "basenames": "Basenames",
    "dirnames": "Directory Names",
    "origdirindexes": "Original Directory Indexes",
    "origbasenames": "Original Basenames",
    "origdirnames": "Original Directory Names",
    "optflags": "%{optflags} Value During Build",
    "disturl": "Distribution-specific URL",
    "archive_format": "Payload Format",
    "archive_compression": "Payload Compressor Name",
    "payloadflags": "Payload Compressor Level",
    "installcolor": "'Color' Of Package Installation Transaction",
    "installtid": "Package Installation Transaction ID",
    "target": "Package Platform",
    "filecolors": "File 'Color'",
    "fileclass": "Index Into Class Dictionary",
    "classdict": "Class Dictionary (File Class libmagic Entries)",
    "filedependsx": "Index Into File Dependencies Dictionary Denoting Start Of File's Dependencies",
    "filedependsn": "Number Of File Dependencies in Dependencies Dictionary",
    "dependsdict": "File Dependencies Dictionary",
    "sourcepkgid": "Source Package Identifier",
    "policies": "Policies",
    "pretrans": "Pre-transaction Script",
    "posttrans": "Post-transaction Script",
    "pretransprog": "Pre-transaction Interpreter + Arguments",
    "posttransprog": "Post-transaction Interpreter + Arguments",
    "disttag": "Distribution Acronym",
    "priority": "Priority",
    "cvsid": "CVS ID",
    "dbinstance": "Installed Package Header ID",
    "nvra": "Formatted name-version-release.arch Package String",
    "filenames": "Per File Paths Contained in the Package",
    "fileprovide": "Per File Dependency Capabilities Provided by the Files",
    "filerequire": "Per File Dependency Capabilities Required by the Files",
    "triggerconds": "Formatted Trigger Condition Information",
    "triggertype": "Formatted Trigger Type Information",
    "origfilenames": "Original Filenames (in relocated packages)",
    "longfilesizes": "File Size (when files > 4 GB)",
    "longsize": "Installed Package Size (when > 4 GB)",
    "filecaps": "Textual Representation of File Capabilities",
    "filedigestalgo": "File Digest Algorithm",
    "bugurl": "Bug Tracker URL",
    "evr": "Formatted epoch:version-release String",
    "nvr": "Formatted name-version-release String",
    "nevr": "Formatted name-epoch:version-release String",
    "nevra": "Formatted name-epoch:version-release.arch String",
    "headercolor": "Header 'Color' Calculated From File Colors",
    "verbose": "Verbose Mode",
    "epochnum": "Package Epoch (numeric)",
    "preinflags": "Pre-installation Flags",
    "postinflags": "Post-installation Flags",
    "preunflags": "Pre-uninstallation Flags",
    "postunflags": "Post-uninstallation Flags",
    "pretransflags": "Pre-transaction Flags",
    "posttransflags": "Post-transaction Flags",
    "verifyscriptflags": "Verification Script Flags",
    "triggerscriptflags": "Trigger Script Flags",
    "policynames": "Policy Names",
    "policytypes": "Policy Types",
    "policytypesindexes": "Policy Types Indexes",
    "policyflags": "Policy Flags",  # TODO: Provide IntFlag mapping.
    "vcs": "Upstream Source Code VCS Location",
    "ordername": "Order Names",
    "orderversion": "Order Names (Versions)",
    "orderflags": "Order Names (Flags)",
    "instfilenames": "Per File Paths Installed From The Package",
    "requirenevrs": "Formatted `name [op version]` Required Dependency Strings",
    "providenevrs": "Formatted `name [op version]` Provided Dependency Strings",
    "obsoletenevrs": "Formatted `name [op version]` Obsolete Dependency Strings",
    "conflictnevrs": "Formatted `name [op version]` Conflicting Dependency Strings",
    "filenlinks": "Per File Hardlink Number",
    "recommendname": "Recommended Names",
    "recommendversion": "Recommended Names (Versions)",
    "recommendflags": "Recommended Names (Flags)",
    "suggestname": "Suggested Names",
    "suggestversion": "Suggested Names (Versions)",
    "suggestflags": "Suggested Flags (Versions)",
    "supplementname": "Supplementary Names",
    "supplementversion": "Supplementary Names (Versions)",
    "supplementflags": "Supplementary Names (Flags)",
    "enhancename": "Enhancement Names",
    "enhanceversion": "Enhancement Names (Versions)",
    "enhanceflags": "Enhancement Names (Flags)",
    "recommendnevrs": "Formatted `name [op version]` Recommended Dependency Strings",
    "suggestnevrs": "Formatted `name [op version]` Suggested Dependency Strings",
    "supplementnevrs": "Formatted `name [op version]` Supplementary Dependency Strings",
    "enhancenevrs": "Formatted `name [op version]` Enhancement Dependency Strings",
    "encoding": "Header String Data Encoding",
    "filetriggerscripts": "File Trigger Scripts",
    "filetriggerscriptprog": "File Trigger Scripts Interpreters + Arguments",
    "filetriggerscriptflags": "File Trigger Scripts Flags",
    "filetriggername": "File Trigger Names",
    "filetriggerindex": "File Trigger Indexes",
    "filetriggerversion": "File Trigger Versions",
    "filetriggerflags": "File Trigger Flags",
    "transfiletriggerscripts": "Transaction File Trigger Scripts",
    "transfiletriggerscriptprog": "Transaction File Trigger Scripts Interpreters + Arguments",
    "transfiletriggerscriptflags": "Transaction File Trigger Flags",
    "transfiletriggername": "Transaction File Trigger Names",
    "transfiletriggerindex": "Transaction File Trigger Indexes",
    "transfiletriggerversion": "Transaction File Trigger Versions",
    "transfiletriggerflags": "Transaction File Trigger Flags",
    "filetriggerpriorities": "File Trigger Priorities",
    "transfiletriggerpriorities": "Transaction File Trigger Priorities",
    "filetriggerconds": "Formatted File Trigger Condition Information",
    "filetriggertype": "Formatted File Trigger Type Information",
    "transfiletriggerconds": "Formatted Transaction File Trigger Condition Information",
    "transfiletriggertype": "Formatted Transaction File Trigger Type Information",
    "filesignatures": "IMA Signatures (hex encoded)",
    "filesignaturelength": "IMA Signature Length",
    "payloaddigest": "Cryptographic Digest Of Compressed Payload",
    "payloaddigestalgo": "Payload Digest Algorithm",
    "modularitylabel": "Modularity Label",
    "payloaddigestalt": "Cryptographic Digest Of Uncompressed Payload",
    "archsuffix": "Package File Arch Suffix",
    "spec": "Expanded And Parsed Spec Contents",
    "translationurl": "URL Of Upstream Translation Service/Repository",
    "upstreamreleases": "URL To Check For Newer Upstream Releases",
    "loaddigestalt": "Cryptographic Digest Of Uncompressed Payload",
    "upstreamleases": "URL To Check For Newer Upstream Releases",
    "sourcelicense": "Source License",
    "sysusers": "Formatted systemd-sysusers Line",
    "preuntrans": "Pre-uninstallation-transaction Script",
    "postuntrans": "Post-uninstallation-transaction Script",
    "preuntransprog": "Pre-uninstallation-transaction Interpreter + Arguments",
    "postuntransprog": "Post-uninstallation-transaction Interpreter + Arguments",
    "preuntransflags": "Pre-uninstallation-transaction Flags",
    "postuntransflags": "Post-uninstallation-transaction Flags",
}

# These headers are of no real use (for now), not properly documented or deprecated.
_HEADERS_TO_OMIT = {
    "autoinstalled",
    "autoprov",
    "autoreq",
    "autoreqprov",
    "badsha1_1",
    "badsha1_2",
    "blinkhdrid",
    "blinknevra",
    "blinkpkgid",
    "buildcpuclock",
    "buildconflicts",
    "buildenhances",
    "buildmacros",
    "buildobsoletes",
    "buildplatforms",
    "buildprereq",
    "buildprovides",
    "buildrequires",
    "buildroot",
    "buildsuggests",
    "cachectime",
    "cachepkgmtime",
    "cachepkgpath",
    "cachepkgsize",
    "capability",
    "collections",
    "conflictattrsx",
    "defaultprefix",
    "depattrsdict",
    "exclude",
    "exclusive",
    "filecontexts",
    "filedigestalgos",
    "filegids",
    "filetriggerin",
    "filetriggerpostun",
    "filetriggerun",
    "fileuids",
    "filexattrsx",
    "flinkhdrid",
    "flinknevra",
    "flinkpgkid",
    "fscontexts",
    "fsnames",
    "fssizes",
    "gif",
    "headerimage",
    "headerregions",
    "icon",
    "identity",
    "installprefix",
    "keywords",
    "lemd5_2",
    "mssfdomain",
    "mssfmanifest",
    "obsoleteattrsx",
    "oldenhancesflags",
    "oldenhancesnames",
    "oldenhancesversion",
    "oldorigfilenames",
    "oldsuggestsflags",
    "oldsuggestsname",
    "oldsuggestsversion",
    "packagecolor",
    "packageorigin"
    "packageprefcolor",
    "patchesflags",
    "patchesname",
    "patchesversion",
    "prereq",
    "provideattrsx",
    "recontexts",
    "removepathpostfixes",
    "removetid",
    "repotag",
    "requireattrsx",
    "rhnplatform",
    "root",
    "scriptmetrics",
    "scriptstates",
    "sig_base",
    "siglemd5_1",
    "siglemd5_2",
    "sigpgp5",
    "transfiletriggerin",
    "transfiletriggerpostun",
    "transfiletriggerun",
    "triggerin",
    "triggerun",
    "triggerpostun",
    "triggerprein",
    "variants",
    "xattrsdict",
    "xmajor",
    "xminor",
    "xpm",
}


def extract(archive_path: Path, target_path: Path) -> None:
    """
    Extract the given RPM file.

    :param archive_path: The RPM file to unpack.
    :param target_path: The directory to unpack to.
    """
    target_path_str = str(target_path)

    # See `rpmfile.cli` for the `extract` option.
    # This is a pathlib-based approach of the original implementation.
    #
    # Upstream code:
    # https://github.com/srossross/rpmfile/blob/c0498cd5173afb6fb0af9ed5c7d61335b7c9af0e/rpmfile/cli.py
    #
    # Original copyright:
    #
    # -------------------------------------------------------------------------
    #
    # Copyright (c) 2015 Sean Ross-Ross
    #
    # MIT License
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in all
    # copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    # SOFTWARE.
    #
    # -------------------------------------------------------------------------
    #
    # The changed version can be used under either the MIT or the Apache-2.0 license,
    # depending on your preferences.
    with rpmfile.open(archive_path) as rpm_file:
        for rpm_info in rpm_file.getmembers():
            with rpm_file.extractfile(rpm_info.name) as file_object:
                directories = rpm_info.name.split("/")
                filename = directories.pop()
                if directories:
                    directories_path = target_path.joinpath(*directories).resolve()
                    if not str(directories_path).startswith(target_path_str):
                        raise ValueError(f"Attempted path traversal: {directories_path}")
                    if not directories_path.is_dir():
                        directories_path.mkdir(parents=True)
                else:
                    directories_path = target_path.resolve()
                target_file = directories_path / filename
                if not str(target_file).startswith(target_path_str):
                    raise ValueError(f"Attempted path traversal: {target_file}")
                target_file.write_bytes(file_object.read())


def get_headers(rpm_path: Path) -> dict[str, Any]:
    """
    Get the RPM headers.

    :param rpm_path: The RPM file to analyze.
    :return: The corresponding headers.
    """
    with rpmfile.open(rpm_path) as rpm_file:
        headers = rpm_file.headers
    return cast(dict[str, Any], headers)


class FileFlags(IntFlag):
    """
    Flags used to indicate the file types.
    """
    # https://refspecs.linuxbase.org/LSB_3.1.0/LSB-Core-generic/LSB-Core-generic/pkgformat.html, section 22.2.4.3.1
    # https://github.com/eclipse/packager/blob/e481c63dd76b112b3924d93e39ab6e791e60a41b/rpm/src/main/java/org/eclipse/packager/rpm/FileFlags.java
    CONFIG = 1 << 0
    DOC = 1 << 1
    DO_NOT_USE = 1 << 2
    MISSING_OK = 1 << 3
    NO_REPLACE = 1 << 4
    SPECFILE = 1 << 5
    GHOST = 1 << 6
    LICENSE = 1 << 7
    README = 1 << 8
    EXCLUDE = 1 << 9
    IGNORE = 1 << 10
    PUBKEY = 1 << 11
    ARTIFACT = 1 << 12


class VerifyFlags(IntFlag):
    """
    Flags used to indicate how to verify the file.
    """
    # https://github.com/eclipse/packager/blob/e481c63dd76b112b3924d93e39ab6e791e60a41b/rpm/src/main/java/org/eclipse/packager/rpm/VerifyFlags.java
    MD5 = 1 << 0
    SIZE = 1 << 1
    LINK_TO = 1 << 2
    USER = 1 << 3
    GROUP = 1 << 4
    MTIME = 1 << 5
    MODE = 1 << 6
    RDEV = 1 << 7
    CAPS = 1 << 8


class DependencyFlags(IntFlag):
    """
    Flags used to indicate how to handle dependency relationships.
    """
    # https://refspecs.linuxbase.org/LSB_3.1.0/LSB-Core-generic/LSB-Core-generic/pkgformat.html, section 22.2.4.4.2
    # https://github.com/rpm-software-management/rpm/blob/f1b68c9e7672a2af8251d611f61c4ab17fcd3ea8/include/rpm/rpmds.h#L22-L53
    ANY = 0
    LESS = 1 << 1
    GREATER = 1 << 2
    EQUAL = 1 << 3
    UNUSED4 = 1 << 4
    POSTTRANS = 1 << 5
    PREREQ = 1 << 6
    PRETRANS = 1 << 7
    INTERP = 1 << 8
    SCRIPT_PRE = 1 << 9
    SCRIPT_POST = 1 << 10
    SCRIPT_PREUN = 1 << 11
    SCRIPT_POSTUN = 1 << 12
    SCRIPT_VERIFY = 1 << 13
    FIND_REQUIRES = 1 << 14
    FIND_PROVIDES = 1 << 15
    TRIGGERIN = 1 << 16
    TRIGGERUN = 1 << 17
    TRIGGERPOSTUN = 1 << 18
    MISSINGOK = 1 << 19
    PREUNTRANS = 1 << 20
    POSTUNTRANS = 1 << 21
    UNUSED22 = 1 << 22
    UNUSED23 = 1 << 23
    RPMLIB = 1 << 24
    TRIGGERPREIN = 1 << 25
    KEYRING = 1 << 26
    UNUSED27 = 1 << 27
    CONFIG = 1 << 28
    META = 1 << 29


class FileColor(IntEnum):
    """
    Enumeration of file "color"/types.
    """
    ELF_32_BIT = 1
    ELF_64_BIT = 2
    OTHER = 0


class FileDigestAlgorithm(IntEnum):
    """
    Enumeration of allowed file digest algorithms.
    """
    # https://docs.rs/rpm-rs/latest/rpm/enum.FileDigestAlgorithm.html
    MD5 = 0
    SHA1 = 1
    MD2 = 2
    HAVAL_5_160 = 3
    RIPEMD160 = 4
    TIGER_192 = 5
    SHA256 = 6
    SHA384 = 7
    SHA512 = 8
    SHA224 = 9


class FileModes(IntEnum):
    """
    Enumeration of known file modes.
    """
    # File types.
    IS_DIRECTORY = stat.S_IFDIR
    IS_CHARACTER_DEVICE = stat.S_IFCHR
    IS_BLOCK_DEVICE = stat.S_IFBLK
    IS_REGULAR_FILE = stat.S_IFREG
    IS_FIFO_NAMED_PIPE = stat.S_IFIFO
    IS_SYMBOLIC_LINK = stat.S_IFLNK
    IS_SOCKET_FILE = stat.S_IFSOCK

    # Permissions.
    SET_UID_BIT = stat.S_ISUID
    SET_GID_BIT = stat.S_ISGID  # The same as file locking enforcement.
    STICKY_BIT = stat.S_ISVTX
    READ_BY_OWNER_ALTERNATIVE = stat.S_IREAD
    WRITE_BY_OWNER_ALTERNATIVE = stat.S_IWRITE
    EXECUTE_BY_OWNER_ALTERNATIVE = stat.S_IEXEC
    READ_WRITE_EXECUTE_BY_OWNER = stat.S_IRWXU
    READ_BY_OWNER = stat.S_IRUSR
    WRITE_BY_OWNER = stat.S_IWUSR
    EXECUTE_BY_OWNER = stat.S_IXUSR
    READ_WRITE_EXECUTE_BY_GROUP = stat.S_IRWXG
    READ_BY_GROUP = stat.S_IRGRP
    WRITE_BY_GROUP = stat.S_IWGRP
    EXECUTE_BY_GROUP = stat.S_IXGRP
    READ_WRITE_EXECUTE_BY_OTHERS = stat.S_IRWXO
    READ_BY_OTHERS = stat.S_IROTH
    WRITE_BY_OTHERS = stat.S_IWOTH
    EXECUTE_BY_OTHERS = stat.S_IXOTH

    @classmethod
    def make_verbose(cls, mode: int) -> list[str]:
        """
        Convert the given mode value into a verbose representation.

        :param mode: The mode to convert.
        :return: The corresponding named constants matching the given mode.
        """
        st_type = stat.S_IFMT(mode)
        st_mode = stat.S_IMODE(mode)

        result = []
        for name, value in cls.__members__.items():
            if name.startswith("IS_"):
                if st_type == value:
                    result.append(name)
            else:
                if st_mode & value == value:
                    result.append(name)
        return result


def _convert_header_value(key: str, value: Any) -> Any:
    """
    Convert the given header value to the appropriate type.

    :param key: The header key.
    :param value: The header value.
    :return: The converted value.
    """
    # Attempt to decode bytes.
    if isinstance(value, bytes):
        try:
            value = value.decode("UTF-8")
        except UnicodeDecodeError:
            pass

    # Do not differentiate between lists and tuples.
    if isinstance(value, tuple):
        value = list(value)

    # Attempt to decode lists of strings.
    if isinstance(value, list) and value and isinstance(value[0], bytes):
        try:
            value = [entry.decode("UTF-8") for entry in value]
        except UnicodeDecodeError:
            pass

    # Convert UTC timestamps.
    if key == "buildtime":
        assert isinstance(value, int)
        return datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
    if key == "installtime":
        if isinstance(value, int):
            return datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
        return None
    if key in {"filemtimes", "changelogtime"}:
        return [datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc) for mtime in value]

    # Convert flags/enums.
    if key == "fileflags":
        return [FileFlags(flags) for flags in value]
    if key == "fileverifyflags":
        return [VerifyFlags(flags) for flags in value]
    if key in {"requireflags", "provideflags", "conflictflags", "obsoleteflags"}:
        if isinstance(value, int):
            return DependencyFlags(value)
        return [DependencyFlags(flags) for flags in value]
    if key == "filecolors":
        return [FileColor(color) for color in value]
    if key in {"filedigestalgo", "payloaddigestalgo"}:
        return FileDigestAlgorithm(value)
    if key == "filemodes":
        # Emulate the regular enumeration display.
        return ["<FileModes." + "|".join(FileModes.make_verbose(mode)) + f": {mode}>" for mode in value]

    # TODO: These are just null bytes. Is this value correct?
    if key == 'reservedspace':
        return len(value)

    # Keep the value without further conversion.
    return value


def get_nice_headers(rpm_path: Path) -> dict[str, Any]:
    """
    Get the RPM headers, but with nicer values and verbose names as keys.

    :param rpm_path: The RPM file to analyze.
    :return: The corresponding headers.
    """
    result: dict[str, Any] = {}
    for key, value in get_headers(rpm_path).items():
        if key in _HEADERS_TO_OMIT:
            logger.warning("Omitting key %s ...", key)
            continue
        if key not in _VERBOSE_HEADER_NAMES:
            logger.warning("Detected unknown key %s. Skipping it ...", key)
            continue
        verbose_key = _VERBOSE_HEADER_NAMES[key]
        transformed_value = _convert_header_value(key, value)
        result[verbose_key] = transformed_value
    return result


def check_rpm_headers(path: Path) -> str | None:
    """
    Render the relevant header details for the given RPM.

    :param path: The RPM path.
    :return: `None` if no results could be determined, otherwise the rendered
             dictionary-like representation of the header section which usually
             holds the copyright data.
    """
    header_data = get_nice_headers(path)
    if not header_data:
        return None
    maximum_length = max(map(len, header_data.keys()))

    def display(v: Any) -> str:
        if isinstance(v, (IntEnum, IntFlag, datetime.datetime)):
            return repr(v)
        return str(v)

    rendered = "\n".join(
        f"{key:>{maximum_length}}: {display(value)}" for key, value in header_data.items()
    )
    return rendered
