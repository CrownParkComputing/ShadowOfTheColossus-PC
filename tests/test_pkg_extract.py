from paths import ROOT
from pathlib import Path
import mmap
import tempfile
import unittest

from pkg_extract import BytesImage, InodeImage, Pfs, Pkg, PkgError, extract_files


class StreamingExtractionTests(unittest.TestCase):
    def test_package_metadata_is_mapped_not_loaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'large.pkg'
            with path.open('wb') as package:
                package.write(b'\x7fCNT')
                package.truncate(8 * 1024**3)
            pkg = Pkg(path)
            try:
                self.assertIsInstance(pkg.data, mmap.mmap)
                self.assertEqual(len(pkg.data), 8 * 1024**3)
            finally:
                pkg.data.close()

    def test_fragmented_inode_reads_and_final_partial_block(self):
        pfs = Pfs.__new__(Pfs)
        pfs.block_size = 4
        pfs.image = BytesImage(b'aaaaBBBBccccDDDD')
        inode = dict(size=10, blocks=3, direct=[3, 1, 0], indirect=[])
        source = InodeImage(pfs, inode)
        self.assertEqual(source.read_at(2, 7), b'DDBBBBa')
        self.assertEqual(source.read_at(9, 100), b'a')
        self.assertEqual(source.read_at(10, 1), b'')

    def test_large_file_extraction_uses_bounded_reads(self):
        size = 3 * 1024**2 + 23

        class BoundedImage:
            def read_at(self, offset, length):
                if length > 1024**2:
                    raise AssertionError('unbounded read')
                return b'x' * length

        pfs = Pfs.__new__(Pfs)
        pfs.block_size = 65536
        pfs.image = BoundedImage()
        inode = dict(size=size, blocks=49, mode=0x8000,
                     direct=[0, 0xFFFFFFFF], indirect=[])
        pfs.inodes = [inode]
        pfs.directory = lambda _: [(b'asset.psarc', 0, 2)]
        with tempfile.TemporaryDirectory() as tmp:
            files = extract_files(pfs, {}, Path(tmp))
            self.assertEqual(files[0].stat().st_size, size)
            with files[0].open('rb') as output:
                output.seek(size - 23)
                self.assertEqual(output.read(), b'x' * 23)

    def test_truncated_inode_fails_instead_of_returning_short_data(self):
        pfs = Pfs.__new__(Pfs)
        pfs.block_size = 4
        pfs.image = BytesImage(b'abc')
        inode = dict(size=4, blocks=1, direct=[0] * 12, indirect=[])
        with self.assertRaisesRegex(PkgError, 'truncated file'):
            InodeImage(pfs, inode).read_at(0, 4)
