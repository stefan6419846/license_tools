# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import TestCase

from license_tools.utils import archive_utils
from license_tools.utils.path_utils import get_files_from_directory
from tests import get_from_url
from tests.data import (
    BASE64__0_22_0__CRATE, JSON__20231013__JAR, LIBAIO1__0_3_109_1_25__RPM, LIBAIO1__0_3_109_1_25__SRC_RPM, TYPING_EXTENSION_4_8_0__SOURCE_FILES,
    TYPING_EXTENSION_4_8_0__WHEEL_FILES, TYPING_EXTENSIONS__4_8_0__SDIST, TYPING_EXTENSIONS__4_8_0__WHEEL,
)


class ArchiveUtilsTestCase(TestCase):
    def test_jar(self) -> None:
        with get_from_url(JSON__20231013__JAR) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            self.assertTrue(archive_utils.can_extract(path))
            archive_utils.extract(archive_path=path, target_directory=directory)
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(
                [
                    "META-INF/MANIFEST.MF",
                    "META-INF/maven/org.json/json/pom.properties",
                    "META-INF/maven/org.json/json/pom.xml",
                    "org/json/CDL.class",
                    "org/json/Cookie.class",
                    "org/json/CookieList.class",
                    "org/json/HTTP.class",
                    "org/json/HTTPTokener.class",
                    "org/json/JSONArray.class",
                    "org/json/JSONException.class",
                    "org/json/JSONML.class",
                    "org/json/JSONMLParserConfiguration.class",
                    "org/json/JSONObject$1.class",
                    "org/json/JSONObject$Null.class",
                    "org/json/JSONObject.class",
                    "org/json/JSONPointer$Builder.class",
                    "org/json/JSONPointer.class",
                    "org/json/JSONPointerException.class",
                    "org/json/JSONPropertyIgnore.class",
                    "org/json/JSONPropertyName.class",
                    "org/json/JSONString.class",
                    "org/json/JSONStringer.class",
                    "org/json/JSONTokener.class",
                    "org/json/JSONWriter.class",
                    "org/json/ParserConfiguration.class",
                    "org/json/Property.class",
                    "org/json/XML$1$1.class",
                    "org/json/XML$1.class",
                    "org/json/XML.class",
                    "org/json/XMLParserConfiguration.class",
                    "org/json/XMLTokener.class",
                    "org/json/XMLXsiTypeConverter.class",
                ],
                actual,
            )

    def test_wheel(self) -> None:
        with get_from_url(TYPING_EXTENSIONS__4_8_0__WHEEL) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            self.assertTrue(archive_utils.can_extract(path))
            archive_utils.extract(archive_path=path, target_directory=directory)
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(TYPING_EXTENSION_4_8_0__WHEEL_FILES, actual)

    def test_rpm_file(self) -> None:
        with get_from_url(LIBAIO1__0_3_109_1_25__RPM) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            self.assertTrue(archive_utils.can_extract(path))
            archive_utils.extract(archive_path=path, target_directory=directory)
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(
                [
                    "lib64/libaio.so.1.0.1",
                    "usr/share/doc/packages/libaio1/COPYING",
                    "usr/share/doc/packages/libaio1/TODO",
                ],
                actual,
            )

    def test_tar_gz(self) -> None:
        with get_from_url(TYPING_EXTENSIONS__4_8_0__SDIST) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            self.assertTrue(archive_utils.can_extract(path))
            archive_utils.extract(archive_path=path, target_directory=directory)
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(TYPING_EXTENSION_4_8_0__SOURCE_FILES, actual)

    def test_rust_crate(self) -> None:
        with get_from_url(BASE64__0_22_0__CRATE) as path, TemporaryDirectory() as tempdir:
            directory = Path(tempdir)
            self.assertTrue(archive_utils.can_extract(path))
            archive_utils.extract(archive_path=path, target_directory=directory)
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(
                [
                    "base64-0.22.0/.cargo_vcs_info.json",
                    "base64-0.22.0/.circleci/config.yml",
                    "base64-0.22.0/.github/ISSUE_TEMPLATE/general-purpose-issue.md",
                    "base64-0.22.0/.gitignore",
                    "base64-0.22.0/Cargo.lock",
                    "base64-0.22.0/Cargo.toml",
                    "base64-0.22.0/Cargo.toml.orig",
                    "base64-0.22.0/LICENSE-APACHE",
                    "base64-0.22.0/LICENSE-MIT",
                    "base64-0.22.0/README.md",
                    "base64-0.22.0/RELEASE-NOTES.md",
                    "base64-0.22.0/benches/benchmarks.rs",
                    "base64-0.22.0/clippy.toml",
                    "base64-0.22.0/examples/base64.rs",
                    "base64-0.22.0/icon_CLion.svg",
                    "base64-0.22.0/src/alphabet.rs",
                    "base64-0.22.0/src/chunked_encoder.rs",
                    "base64-0.22.0/src/decode.rs",
                    "base64-0.22.0/src/display.rs",
                    "base64-0.22.0/src/encode.rs",
                    "base64-0.22.0/src/engine/general_purpose/decode.rs",
                    "base64-0.22.0/src/engine/general_purpose/decode_suffix.rs",
                    "base64-0.22.0/src/engine/general_purpose/mod.rs",
                    "base64-0.22.0/src/engine/mod.rs",
                    "base64-0.22.0/src/engine/naive.rs",
                    "base64-0.22.0/src/engine/tests.rs",
                    "base64-0.22.0/src/lib.rs",
                    "base64-0.22.0/src/prelude.rs",
                    "base64-0.22.0/src/read/decoder.rs",
                    "base64-0.22.0/src/read/decoder_tests.rs",
                    "base64-0.22.0/src/read/mod.rs",
                    "base64-0.22.0/src/tests.rs",
                    "base64-0.22.0/src/write/encoder.rs",
                    "base64-0.22.0/src/write/encoder_string_writer.rs",
                    "base64-0.22.0/src/write/encoder_tests.rs",
                    "base64-0.22.0/src/write/mod.rs",
                    "base64-0.22.0/tests/encode.rs",
                    "base64-0.22.0/tests/tests.rs",
                ],
                actual
            )

    def test_zip(self) -> None:
        with TemporaryDirectory() as source, TemporaryDirectory() as tempdir, NamedTemporaryFile() as zip_file:
            zip_path = Path(f"{zip_file.name}.zip")
            self.addCleanup(zip_path.unlink)
            source_path = Path(source)
            directory = Path(tempdir)
            source_path.joinpath("test.txt").write_text("abc")
            source_path.joinpath("directory1").mkdir()
            source_path.joinpath("directory2").mkdir()
            source_path.joinpath("directory2", "README").write_text("Hello World")
            shutil.make_archive(
                base_name=zip_file.name,
                format="zip",
                root_dir=source_path.parent,
                base_dir=source_path.name,
            )

            self.assertTrue(archive_utils.can_extract(zip_path))
            archive_utils.extract(archive_path=zip_path, target_directory=directory)
            actual = [x[1] for x in get_files_from_directory(directory)]
            self.assertEqual(
                [
                    f"{source_path.name}/directory2/README",
                    f"{source_path.name}/test.txt",
                ],
                actual,
            )
            self.assertEqual(
                {"directory1", "directory2", "test.txt"},
                {x.name for x in directory.joinpath(source_path.name).glob("*")},
            )

    def test_unknown(self) -> None:
        self.assertFalse(archive_utils.can_extract(Path("/home/bin/run.exe")))

    def test_nested(self) -> None:
        with get_from_url(LIBAIO1__0_3_109_1_25__SRC_RPM) as path:
            with TemporaryDirectory() as tempdir:
                directory = Path(tempdir)
                self.assertTrue(archive_utils.can_extract(path))
                archive_utils.extract(
                    archive_path=path,
                    target_directory=directory,
                    recurse=True,
                )
                actual = [x[1] for x in get_files_from_directory(directory)]
                self.assertEqual(
                    [
                        "00_arches.patch",
                        "00_arches_sh.patch",
                        "01_link_libgcc.patch",
                        "02_libdevdir.patch",
                        "03_man_errors.patch",
                        "baselibs.conf",
                        "libaio-0.3.109.tar.bz2",
                        "libaio-0.3.109/.version",
                        "libaio-0.3.109/COPYING",
                        "libaio-0.3.109/ChangeLog",
                        "libaio-0.3.109/INSTALL",
                        "libaio-0.3.109/Makefile",
                        "libaio-0.3.109/TODO",
                        "libaio-0.3.109/harness/Makefile",
                        "libaio-0.3.109/harness/README",
                        "libaio-0.3.109/harness/attic/0.t",
                        "libaio-0.3.109/harness/attic/1.t",
                        "libaio-0.3.109/harness/cases/10.t",
                        "libaio-0.3.109/harness/cases/11.t",
                        "libaio-0.3.109/harness/cases/12.t",
                        "libaio-0.3.109/harness/cases/13.t",
                        "libaio-0.3.109/harness/cases/14.t",
                        "libaio-0.3.109/harness/cases/15.t",
                        "libaio-0.3.109/harness/cases/16.t",
                        "libaio-0.3.109/harness/cases/2.t",
                        "libaio-0.3.109/harness/cases/3.t",
                        "libaio-0.3.109/harness/cases/4.t",
                        "libaio-0.3.109/harness/cases/5.t",
                        "libaio-0.3.109/harness/cases/6.t",
                        "libaio-0.3.109/harness/cases/7.t",
                        "libaio-0.3.109/harness/cases/8.t",
                        "libaio-0.3.109/harness/cases/aio_setup.h",
                        "libaio-0.3.109/harness/cases/common-7-8.h",
                        "libaio-0.3.109/harness/ext2-enospc.img",
                        "libaio-0.3.109/harness/main.c",
                        "libaio-0.3.109/harness/runtests.sh",
                        "libaio-0.3.109/libaio.spec",
                        "libaio-0.3.109/man/aio.3",
                        "libaio-0.3.109/man/aio_cancel.3",
                        "libaio-0.3.109/man/aio_cancel64.3",
                        "libaio-0.3.109/man/aio_error.3",
                        "libaio-0.3.109/man/aio_error64.3",
                        "libaio-0.3.109/man/aio_fsync.3",
                        "libaio-0.3.109/man/aio_fsync64.3",
                        "libaio-0.3.109/man/aio_init.3",
                        "libaio-0.3.109/man/aio_read.3",
                        "libaio-0.3.109/man/aio_read64.3",
                        "libaio-0.3.109/man/aio_return.3",
                        "libaio-0.3.109/man/aio_return64.3",
                        "libaio-0.3.109/man/aio_suspend.3",
                        "libaio-0.3.109/man/aio_suspend64.3",
                        "libaio-0.3.109/man/aio_write.3",
                        "libaio-0.3.109/man/aio_write64.3",
                        "libaio-0.3.109/man/io.3",
                        "libaio-0.3.109/man/io_cancel.1",
                        "libaio-0.3.109/man/io_cancel.3",
                        "libaio-0.3.109/man/io_destroy.1",
                        "libaio-0.3.109/man/io_fsync.3",
                        "libaio-0.3.109/man/io_getevents.1",
                        "libaio-0.3.109/man/io_getevents.3",
                        "libaio-0.3.109/man/io_prep_fsync.3",
                        "libaio-0.3.109/man/io_prep_pread.3",
                        "libaio-0.3.109/man/io_prep_pwrite.3",
                        "libaio-0.3.109/man/io_queue_init.3",
                        "libaio-0.3.109/man/io_queue_release.3",
                        "libaio-0.3.109/man/io_queue_run.3",
                        "libaio-0.3.109/man/io_queue_wait.3",
                        "libaio-0.3.109/man/io_set_callback.3",
                        "libaio-0.3.109/man/io_setup.1",
                        "libaio-0.3.109/man/io_submit.1",
                        "libaio-0.3.109/man/io_submit.3",
                        "libaio-0.3.109/man/lio_listio.3",
                        "libaio-0.3.109/man/lio_listio64.3",
                        "libaio-0.3.109/src/Makefile",
                        "libaio-0.3.109/src/compat-0_1.c",
                        "libaio-0.3.109/src/io_cancel.c",
                        "libaio-0.3.109/src/io_destroy.c",
                        "libaio-0.3.109/src/io_getevents.c",
                        "libaio-0.3.109/src/io_queue_init.c",
                        "libaio-0.3.109/src/io_queue_release.c",
                        "libaio-0.3.109/src/io_queue_run.c",
                        "libaio-0.3.109/src/io_queue_wait.c",
                        "libaio-0.3.109/src/io_setup.c",
                        "libaio-0.3.109/src/io_submit.c",
                        "libaio-0.3.109/src/libaio.h",
                        "libaio-0.3.109/src/libaio.map",
                        "libaio-0.3.109/src/raw_syscall.c",
                        "libaio-0.3.109/src/syscall-alpha.h",
                        "libaio-0.3.109/src/syscall-arm.h",
                        "libaio-0.3.109/src/syscall-i386.h",
                        "libaio-0.3.109/src/syscall-ia64.h",
                        "libaio-0.3.109/src/syscall-ppc.h",
                        "libaio-0.3.109/src/syscall-s390.h",
                        "libaio-0.3.109/src/syscall-x86_64.h",
                        "libaio-0.3.109/src/syscall.h",
                        "libaio-0.3.109/src/vsys_def.h",
                        "libaio-aarch64-support.diff",
                        "libaio-generic-arch.diff",
                        "libaio-optflags.diff",
                        "libaio.spec",
                    ],
                    actual,
                )

            with TemporaryDirectory() as tempdir, TemporaryDirectory() as tempdir2:
                directory = Path(tempdir)
                tar_bz2_directory = Path(tempdir2)
                self.assertTrue(archive_utils.can_extract(path))
                archive_utils.extract(
                    archive_path=path,
                    target_directory=directory,
                    recurse=False,
                )
                actual = [x[1] for x in get_files_from_directory(directory)]
                self.assertEqual(
                    [
                        "00_arches.patch",
                        "00_arches_sh.patch",
                        "01_link_libgcc.patch",
                        "02_libdevdir.patch",
                        "03_man_errors.patch",
                        "baselibs.conf",
                        "libaio-0.3.109.tar.bz2",
                        "libaio-aarch64-support.diff",
                        "libaio-generic-arch.diff",
                        "libaio-optflags.diff",
                        "libaio.spec",
                    ],
                    actual,
                )

                archive_utils.extract(
                    archive_path=directory / "libaio-0.3.109.tar.bz2",
                    target_directory=tar_bz2_directory,
                    recurse=False,
                )
                actual = [
                    x[1] for x in get_files_from_directory(tar_bz2_directory)
                ]
                self.assertEqual(
                    [
                        "libaio-0.3.109/.version",
                        "libaio-0.3.109/COPYING",
                        "libaio-0.3.109/ChangeLog",
                        "libaio-0.3.109/INSTALL",
                        "libaio-0.3.109/Makefile",
                        "libaio-0.3.109/TODO",
                        "libaio-0.3.109/harness/Makefile",
                        "libaio-0.3.109/harness/README",
                        "libaio-0.3.109/harness/attic/0.t",
                        "libaio-0.3.109/harness/attic/1.t",
                        "libaio-0.3.109/harness/cases/10.t",
                        "libaio-0.3.109/harness/cases/11.t",
                        "libaio-0.3.109/harness/cases/12.t",
                        "libaio-0.3.109/harness/cases/13.t",
                        "libaio-0.3.109/harness/cases/14.t",
                        "libaio-0.3.109/harness/cases/15.t",
                        "libaio-0.3.109/harness/cases/16.t",
                        "libaio-0.3.109/harness/cases/2.t",
                        "libaio-0.3.109/harness/cases/3.t",
                        "libaio-0.3.109/harness/cases/4.t",
                        "libaio-0.3.109/harness/cases/5.t",
                        "libaio-0.3.109/harness/cases/6.t",
                        "libaio-0.3.109/harness/cases/7.t",
                        "libaio-0.3.109/harness/cases/8.t",
                        "libaio-0.3.109/harness/cases/aio_setup.h",
                        "libaio-0.3.109/harness/cases/common-7-8.h",
                        "libaio-0.3.109/harness/ext2-enospc.img",
                        "libaio-0.3.109/harness/main.c",
                        "libaio-0.3.109/harness/runtests.sh",
                        "libaio-0.3.109/libaio.spec",
                        "libaio-0.3.109/man/aio.3",
                        "libaio-0.3.109/man/aio_cancel.3",
                        "libaio-0.3.109/man/aio_cancel64.3",
                        "libaio-0.3.109/man/aio_error.3",
                        "libaio-0.3.109/man/aio_error64.3",
                        "libaio-0.3.109/man/aio_fsync.3",
                        "libaio-0.3.109/man/aio_fsync64.3",
                        "libaio-0.3.109/man/aio_init.3",
                        "libaio-0.3.109/man/aio_read.3",
                        "libaio-0.3.109/man/aio_read64.3",
                        "libaio-0.3.109/man/aio_return.3",
                        "libaio-0.3.109/man/aio_return64.3",
                        "libaio-0.3.109/man/aio_suspend.3",
                        "libaio-0.3.109/man/aio_suspend64.3",
                        "libaio-0.3.109/man/aio_write.3",
                        "libaio-0.3.109/man/aio_write64.3",
                        "libaio-0.3.109/man/io.3",
                        "libaio-0.3.109/man/io_cancel.1",
                        "libaio-0.3.109/man/io_cancel.3",
                        "libaio-0.3.109/man/io_destroy.1",
                        "libaio-0.3.109/man/io_fsync.3",
                        "libaio-0.3.109/man/io_getevents.1",
                        "libaio-0.3.109/man/io_getevents.3",
                        "libaio-0.3.109/man/io_prep_fsync.3",
                        "libaio-0.3.109/man/io_prep_pread.3",
                        "libaio-0.3.109/man/io_prep_pwrite.3",
                        "libaio-0.3.109/man/io_queue_init.3",
                        "libaio-0.3.109/man/io_queue_release.3",
                        "libaio-0.3.109/man/io_queue_run.3",
                        "libaio-0.3.109/man/io_queue_wait.3",
                        "libaio-0.3.109/man/io_set_callback.3",
                        "libaio-0.3.109/man/io_setup.1",
                        "libaio-0.3.109/man/io_submit.1",
                        "libaio-0.3.109/man/io_submit.3",
                        "libaio-0.3.109/man/lio_listio.3",
                        "libaio-0.3.109/man/lio_listio64.3",
                        "libaio-0.3.109/src/Makefile",
                        "libaio-0.3.109/src/compat-0_1.c",
                        "libaio-0.3.109/src/io_cancel.c",
                        "libaio-0.3.109/src/io_destroy.c",
                        "libaio-0.3.109/src/io_getevents.c",
                        "libaio-0.3.109/src/io_queue_init.c",
                        "libaio-0.3.109/src/io_queue_release.c",
                        "libaio-0.3.109/src/io_queue_run.c",
                        "libaio-0.3.109/src/io_queue_wait.c",
                        "libaio-0.3.109/src/io_setup.c",
                        "libaio-0.3.109/src/io_submit.c",
                        "libaio-0.3.109/src/libaio.h",
                        "libaio-0.3.109/src/libaio.map",
                        "libaio-0.3.109/src/raw_syscall.c",
                        "libaio-0.3.109/src/syscall-alpha.h",
                        "libaio-0.3.109/src/syscall-arm.h",
                        "libaio-0.3.109/src/syscall-i386.h",
                        "libaio-0.3.109/src/syscall-ia64.h",
                        "libaio-0.3.109/src/syscall-ppc.h",
                        "libaio-0.3.109/src/syscall-s390.h",
                        "libaio-0.3.109/src/syscall-x86_64.h",
                        "libaio-0.3.109/src/syscall.h",
                        "libaio-0.3.109/src/vsys_def.h",
                    ],
                    actual,
                )
