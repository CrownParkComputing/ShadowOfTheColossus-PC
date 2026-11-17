from paths import ROOT
from pathlib import Path
import struct
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import content_profile

EXE=ROOT/'out/content-test'

class ProfileTests(unittest.TestCase):
    def test_sfo_parameters_and_explicit_trial_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'sce_sys').mkdir();(p/'sce_sys/param.sfo').write_bytes(b'fixture')
            with patch.object(content_profile,'sfo',return_value={'USER_DEFINED_PARAM_1':13,'USER_DEFINED_PARAM_4':0xffffffff}):
                content_profile.prepare(p,p,'trial')
            self.assertEqual(struct.unpack('<8s5I',(p/'content.bin').read_bytes()),(b'BBCONT01',1,13,0,0,0xffffffff))

    def test_invalid_sfo_parameter_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'sce_sys').mkdir();(p/'sce_sys/param.sfo').write_bytes(b'fixture')
            with patch.object(content_profile,'sfo',return_value={'USER_DEFINED_PARAM_1':'13'}):
                with self.assertRaisesRegex(ValueError,'invalid user-defined'):
                    content_profile.prepare(p,p)

@unittest.skipUnless(EXE.exists(),'run bash build.sh --test first')
class ContentTests(unittest.TestCase):
    def run_case(self,*args):
        return subprocess.run([str(EXE.resolve()),*args],capture_output=True,text=True,timeout=5)

    def test_lifecycle_and_output_boundaries(self):
        r=self.run_case();self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_missing_profile_does_not_report_loaded(self):
        r=self.run_case('--missing');self.assertEqual(r.returncode,21)
        self.assertIn('needs --content-profile',r.stderr)

    def test_other_modules_are_counted_independently(self):
        r=self.run_case('--unknown');self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_pkg_dlc_filters_region_type_and_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            entries=[
                ('bow.pkg','CUSA08034','ANCIENTBOW0000000',0x1b),
                ('bow-copy.pkg','CUSA08034','ANCIENTBOW0000000',0x1b),
                ('sword.PKG','CUSA08034','LIFESWORD0000000',0x1b),
                ('eu.pkg','CUSA08809','EUONLY0000000000',0x1b),
                ('game.pkg','CUSA08034','NOTDLC0000000000',0x1a),
            ]
            for name,title,label,kind in entries:
                data=bytearray(0x80)
                data[:4]=b'\x7fCNT'
                content=f'UP9000-{title}_00-{label}'.encode()
                data[0x40:0x40+len(content)]=content
                struct.pack_into('>I',data,0x74,kind)
                (folder/name).write_bytes(data)
            (folder/'truncated.pkg').write_bytes(b'\x7fCNT')
            result=subprocess.run([str(EXE),'--addons','2'],capture_output=True,text=True,
                                  env={**os.environ,'SOTC_DLC_DIR':str(folder)},timeout=5)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
