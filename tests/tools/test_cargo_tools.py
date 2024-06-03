# Copyright (c) stefan6419846. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.

from __future__ import annotations

import re
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock, TestCase

from license_tools.tools import cargo_tools
from license_tools.tools.cargo_tools import PackageVersion
from license_tools.utils.download_utils import Download
from tests import get_from_url
from tests.data import BASE64__0_22_0__CARGO_TOML, CRYPTOGRAPHY__42_0_0__CARGO_LOCK


EXPECTED_METADATA = {
    "authors": ["Alice Maz <alice@alicemaz.com>", "Marshall Pierce <marshall@mpierce.org>"],
    "categories": ["encoding"],
    "description": "encodes and decodes base64 as bytes or utf8",
    "documentation": "https://docs.rs/base64",
    "edition": "2018",
    "keywords": ["base64", "utf8", "encode", "decode", "no_std"],
    "license": "MIT OR Apache-2.0",
    "metadata": {"docs": {"rs": {"rustdoc-args": ["--generate-link-to-definition"]}}},
    "name": "base64",
    "readme": "README.md",
    "repository": "https://github.com/marshallpierce/rust-base64",
    "rust-version": "1.48.0",
    "version": "0.22.0",
}


class ReadTomlTestCase(TestCase):
    def test_read_toml(self) -> None:
        with get_from_url(BASE64__0_22_0__CARGO_TOML) as path:
            result = cargo_tools.read_toml(path)
        self.assertEqual(
            {
                "bench": [{"harness": False, "name": "benchmarks", "required-features": ["std"]}],
                "dev-dependencies": {
                    "clap": {"features": ["derive"], "version": "3.2.25"},
                    "criterion": "0.4.0",
                    "once_cell": "1",
                    "rand": {"features": ["small_rng"], "version": "0.8.5"},
                    "rstest": "0.13.0",
                    "rstest_reuse": "0.6.0",
                    "strum": {"features": ["derive"], "version": "0.25"},
                },
                "example": [{"name": "base64", "required-features": ["std"]}],
                "features": {"alloc": [], "default": ["std"], "std": ["alloc"]},
                "package": EXPECTED_METADATA,
                "profile": {"bench": {"debug": True}, "test": {"opt-level": 3}},
                "test": [{"name": "tests", "required-features": ["alloc"]}, {"name": "encode", "required-features": ["alloc"]}],
            },
            result,
        )


class AnalyzeMetadataTestCase(TestCase):
    def test_path_is_cargo_toml(self) -> None:
        with get_from_url(BASE64__0_22_0__CARGO_TOML) as path, TemporaryDirectory() as directory:
            cargo_toml = Path(directory) / "Cargo.toml"
            cargo_toml.write_bytes(path.read_bytes())
            metadata = cargo_tools.analyze_metadata(cargo_toml)
        self.assertEqual(EXPECTED_METADATA, metadata)

    def test_path_is_parent_of_cargo_toml(self) -> None:
        with get_from_url(BASE64__0_22_0__CARGO_TOML) as path, TemporaryDirectory() as directory:
            cargo_toml = Path(directory) / "Cargo.toml"
            cargo_toml.write_bytes(path.read_bytes())
            metadata = cargo_tools.analyze_metadata(Path(directory))
        self.assertEqual(EXPECTED_METADATA, metadata)

    def test_path_is_grandparent_of_cargo_toml(self) -> None:
        with get_from_url(BASE64__0_22_0__CARGO_TOML) as path, TemporaryDirectory() as directory:
            cargo_toml = Path(directory) / "base64-0.22.1" / "Cargo.toml"
            cargo_toml.parent.mkdir()
            cargo_toml.write_bytes(path.read_bytes())
            metadata = cargo_tools.analyze_metadata(Path(directory))
            self.assertEqual(EXPECTED_METADATA, metadata)

            Path(directory, "another_directory").mkdir()
            with self.assertRaisesRegex(expected_exception=ValueError, expected_regex=rf"^No clear Cargo\.toml in {re.escape(directory)}\.$"):
                cargo_tools.analyze_metadata(Path(directory))


class CheckMetadataTestCase(TestCase):
    def test_check_metadata(self) -> None:
        with get_from_url(BASE64__0_22_0__CARGO_TOML) as path, TemporaryDirectory() as directory:
            cargo_toml = Path(directory) / "Cargo.toml"
            cargo_toml.write_bytes(path.read_bytes())
            metadata = cargo_tools.check_metadata(cargo_toml)
        self.assertEqual(
            """
        Name: base64
     Version: 0.22.0
     Authors:
               * Alice Maz <alice@alicemaz.com>
               * Marshall Pierce <marshall@mpierce.org>
 Description: encodes and decodes base64 as bytes or utf8
      README: README.md
  Repository: https://github.com/marshallpierce/rust-base64
     License: MIT OR Apache-2.0
    Keywords:
               * base64
               * decode
               * encode
               * no_std
               * utf8
  Categories: encoding
"""[
                1:-1
            ],
            metadata,
        )


class PackageVersionTestCase(TestCase):
    def test_to_download(self) -> None:
        package_version = PackageVersion(name="autocfg", version="1.1.0", checksum="d468802bab17cbc0cc575e9b053f41e72aa36bfa6b7f55e3529ffa43161b97fa")
        self.assertEqual(
            Download(
                url="https://crates.io/api/v1/crates/autocfg/1.1.0/download",
                filename="autocfg_1.1.0.crate",
                sha256="d468802bab17cbc0cc575e9b053f41e72aa36bfa6b7f55e3529ffa43161b97fa",
            ),
            package_version.to_download(),
        )


class GetPackageVersionsTestCase(TestCase):
    def test_get_package_versions(self) -> None:
        with get_from_url(CRYPTOGRAPHY__42_0_0__CARGO_LOCK) as path:
            with mock.patch.object(cargo_tools.logger, "warning") as warning_mock:
                package_versions = list(cargo_tools.get_package_versions(path))
        self.assertEqual(
            [
                PackageVersion(name="asn1", version="0.15.5", checksum="ae3ecbce89a22627b5e8e6e11d69715617138290289e385cde773b1fe50befdb"),
                PackageVersion(name="asn1_derive", version="0.15.5", checksum="861af988fac460ac69a09f41e6217a8fb9178797b76fcc9478444be6a59be19c"),
                PackageVersion(name="autocfg", version="1.1.0", checksum="d468802bab17cbc0cc575e9b053f41e72aa36bfa6b7f55e3529ffa43161b97fa"),
                PackageVersion(name="base64", version="0.21.7", checksum="9d297deb1925b89f2ccc13d7635fa0714f12c87adce1c75356b39ca9b7178567"),
                PackageVersion(name="bitflags", version="1.3.2", checksum="bef38d45163c2f1dde094a7dfd33ccf595c92905c8f8f4fdc18d06fb1037718a"),
                PackageVersion(name="bitflags", version="2.4.2", checksum="ed570934406eb16438a4e976b1b4500774099c13b8cb96eec99f620f05090ddf"),
                PackageVersion(name="cc", version="1.0.83", checksum="f1174fb0b6ec23863f8b971027804a42614e347eafb0a95bf0b12cdae21fc4d0"),
                PackageVersion(name="cfg-if", version="1.0.0", checksum="baf1de4339761588bc0619e3cbc0120ee582ebb74b53b4efbf79117bd2da40fd"),
                PackageVersion(name="foreign-types", version="0.3.2", checksum="f6f339eb8adc052cd2ca78910fda869aefa38d22d5cb648e6485e4d3fc06f3b1"),
                PackageVersion(name="foreign-types-shared", version="0.1.1", checksum="00b0228411908ca8685dba7fc2cdd70ec9990a6e753e89b6ac91a84c40fbaf4b"),
                PackageVersion(name="heck", version="0.4.1", checksum="95505c38b4572b2d910cecb0281560f54b440a19336cbbcb27bf6ce6adc6f5a8"),
                PackageVersion(name="indoc", version="2.0.4", checksum="1e186cfbae8084e513daff4240b4797e342f988cecda4fb6c939150f96315fd8"),
                PackageVersion(name="libc", version="0.2.152", checksum="13e3bf6590cbc649f4d1a3eefc9d5d6eb746f5200ffb04e5e142700b8faa56e7"),
                PackageVersion(name="lock_api", version="0.4.11", checksum="3c168f8615b12bc01f9c17e2eb0cc07dcae1940121185446edc3744920e8ef45"),
                PackageVersion(name="memoffset", version="0.9.0", checksum="5a634b1c61a95585bd15607c6ab0c4e5b226e695ff2800ba0cdccddf208c406c"),
                PackageVersion(name="once_cell", version="1.19.0", checksum="3fdb12b2476b595f9358c5161aa467c2438859caa136dec86c26fdd2efe17b92"),
                PackageVersion(name="openssl", version="0.10.63", checksum="15c9d69dd87a29568d4d017cfe8ec518706046a05184e5aea92d0af890b803c8"),
                PackageVersion(name="openssl-macros", version="0.1.1", checksum="a948666b637a0f465e8564c73e89d4dde00d72d4d473cc972f390fc3dcee7d9c"),
                PackageVersion(name="openssl-sys", version="0.9.99", checksum="22e1bf214306098e4832460f797824c05d25aacdf896f64a985fb0fd992454ae"),
                PackageVersion(name="parking_lot", version="0.12.1", checksum="3742b2c103b9f06bc9fff0a37ff4912935851bee6d36f3c02bcc755bcfec228f"),
                PackageVersion(name="parking_lot_core", version="0.9.9", checksum="4c42a9226546d68acdd9c0a280d17ce19bfe27a46bf68784e4066115788d008e"),
                PackageVersion(name="pem", version="3.0.3", checksum="1b8fcc794035347fb64beda2d3b462595dd2753e3f268d89c5aae77e8cf2c310"),
                PackageVersion(name="pkg-config", version="0.3.29", checksum="2900ede94e305130c13ddd391e0ab7cbaeb783945ae07a279c268cb05109c6cb"),
                PackageVersion(name="proc-macro2", version="1.0.78", checksum="e2422ad645d89c99f8f3e6b88a9fdeca7fabeac836b1002371c4367c8f984aae"),
                PackageVersion(name="pyo3", version="0.20.2", checksum="9a89dc7a5850d0e983be1ec2a463a171d20990487c3cfcd68b5363f1ee3d6fe0"),
                PackageVersion(name="pyo3-build-config", version="0.20.2", checksum="07426f0d8fe5a601f26293f300afd1a7b1ed5e78b2a705870c5f30893c5163be"),
                PackageVersion(name="pyo3-ffi", version="0.20.2", checksum="dbb7dec17e17766b46bca4f1a4215a85006b4c2ecde122076c562dd058da6cf1"),
                PackageVersion(name="pyo3-macros", version="0.20.2", checksum="05f738b4e40d50b5711957f142878cfa0f28e054aa0ebdfc3fd137a843f74ed3"),
                PackageVersion(name="pyo3-macros-backend", version="0.20.2", checksum="0fc910d4851847827daf9d6cdd4a823fbdaab5b8818325c5e97a86da79e8881f"),
                PackageVersion(name="quote", version="1.0.35", checksum="291ec9ab5efd934aaf503a6466c5d5251535d108ee747472c3977cc5acc868ef"),
                PackageVersion(name="redox_syscall", version="0.4.1", checksum="4722d768eff46b75989dd134e5c353f0d6296e5aaa3132e776cbdb56be7731aa"),
                PackageVersion(name="scopeguard", version="1.2.0", checksum="94143f37725109f92c262ed2cf5e59bce7498c01bcc1502d7b9afe439a4e9f49"),
                PackageVersion(name="self_cell", version="1.0.3", checksum="58bf37232d3bb9a2c4e641ca2a11d83b5062066f88df7fed36c28772046d65ba"),
                PackageVersion(name="smallvec", version="1.13.1", checksum="e6ecd384b10a64542d77071bd64bd7b231f4ed5940fba55e98c3de13824cf3d7"),
                PackageVersion(name="syn", version="2.0.48", checksum="0f3531638e407dfc0814761abb7c00a5b54992b849452a0646b7f65c9f770f3f"),
                PackageVersion(name="target-lexicon", version="0.12.13", checksum="69758bda2e78f098e4ccb393021a0963bb3442eac05f135c30f61b7370bbafae"),
                PackageVersion(name="unicode-ident", version="1.0.12", checksum="3354b9ac3fae1ff6755cb6db53683adb661634f67557942dea4facebec0fee4b"),
                PackageVersion(name="unindent", version="0.2.3", checksum="c7de7d73e1754487cb58364ee906a499937a0dfabd86bcb980fa99ec8c8fa2ce"),
                PackageVersion(name="vcpkg", version="0.2.15", checksum="accd4ea62f7bb7a82fe23066fb0957d48ef677f6eeb8215f372f52e48bb32426"),
                PackageVersion(name="windows-targets", version="0.48.5", checksum="9a2fa6e2155d7247be68c096456083145c183cbbbc2764150dda45a87197940c"),
                PackageVersion(name="windows_aarch64_gnullvm", version="0.48.5", checksum="2b38e32f0abccf9987a4e3079dfb67dcd799fb61361e53e2882c3cbaf0d905d8"),
                PackageVersion(name="windows_aarch64_msvc", version="0.48.5", checksum="dc35310971f3b2dbbf3f0690a219f40e2d9afcf64f9ab7cc1be722937c26b4bc"),
                PackageVersion(name="windows_i686_gnu", version="0.48.5", checksum="a75915e7def60c94dcef72200b9a8e58e5091744960da64ec734a6c6e9b3743e"),
                PackageVersion(name="windows_i686_msvc", version="0.48.5", checksum="8f55c233f70c4b27f66c523580f78f1004e8b5a8b659e05a4eb49d4166cca406"),
                PackageVersion(name="windows_x86_64_gnu", version="0.48.5", checksum="53d40abd2583d23e4718fddf1ebec84dbff8381c07cae67ff7768bbf19c6718e"),
                PackageVersion(name="windows_x86_64_gnullvm", version="0.48.5", checksum="0b7b52767868a23d5bab768e390dc5f5c55825b6d30b86c844ff2dc7414044cc"),
                PackageVersion(name="windows_x86_64_msvc", version="0.48.5", checksum="ed94fce61571a4006852b7389a063ab983c02eb1bb37b47f8272ce92d06d9538"),
            ],
            package_versions,
        )

        warning_mock.assert_has_calls(
            [
                mock.call('Skipping %s', {'name': 'cryptography-cffi', 'version': '0.1.0', 'dependencies': ['cc', 'openssl-sys', 'pyo3']}),
                mock.call(
                    'Skipping %s',
                    {'name': 'cryptography-key-parsing', 'version': '0.1.0', 'dependencies': ['asn1', 'cfg-if', 'cryptography-x509', 'openssl', 'openssl-sys']}
                ),
                mock.call(
                    'Skipping %s',
                    {'name': 'cryptography-openssl', 'version': '0.1.0', 'dependencies': ['foreign-types', 'foreign-types-shared', 'openssl', 'openssl-sys']}
                ),
                mock.call(
                    'Skipping %s',
                    {
                        'name': 'cryptography-rust', 'version': '0.1.0',
                        'dependencies': [
                            'asn1', 'cc', 'cfg-if', 'cryptography-cffi', 'cryptography-key-parsing', 'cryptography-openssl', 'cryptography-x509',
                            'cryptography-x509-verification', 'foreign-types-shared', 'once_cell', 'openssl', 'openssl-sys', 'pem', 'pyo3', 'self_cell'
                        ]
                    }
                ),
                mock.call('Skipping %s', {'name': 'cryptography-x509', 'version': '0.1.0', 'dependencies': ['asn1']}),
                mock.call(
                    'Skipping %s',
                    {'name': 'cryptography-x509-verification', 'version': '0.1.0', 'dependencies': ['asn1', 'cryptography-x509', 'once_cell', 'pem']}
                )
            ],
            any_order=False
        )
        self.assertEqual(6, warning_mock.call_count, warning_mock.call_args_list)


class DownloadFromLockFileTestCase(TestCase):
    def test_download_from_lock_file(self) -> None:
        package_versions = [
            PackageVersion(name="lock_api", version="0.4.11", checksum="3c168f8615b12bc01f9c17e2eb0cc07dcae1940121185446edc3744920e8ef45"),
            PackageVersion(name="memoffset", version="0.9.0", checksum="5a634b1c61a95585bd15607c6ab0c4e5b226e695ff2800ba0cdccddf208c406c"),
            PackageVersion(name="once_cell", version="1.19.0", checksum="3fdb12b2476b595f9358c5161aa467c2438859caa136dec86c26fdd2efe17b92"),
        ]
        lock_path = Path("/path/to/Cargo.lock")
        with mock.patch.object(cargo_tools, "get_package_versions", return_value=package_versions), \
                mock.patch("license_tools.utils.download_utils.download_one_file_per_second") as download_mock, \
                TemporaryDirectory() as directory:
            cargo_tools.download_from_lock_file(lock_path=lock_path, target_directory=directory)
        download_mock.assert_called_once_with(
            downloads=[package.to_download() for package in package_versions],
            directory=Path(directory)
        )
