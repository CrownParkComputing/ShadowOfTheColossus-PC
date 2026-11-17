from paths import ROOT
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('sotc_runner', ROOT / 'sotc.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    @unittest.skipIf(os.name == 'nt', 'POSIX console handling')
    def test_no_console_needs_no_windows_api(self):
        self.assertEqual(runner.no_console(), 0)

    @unittest.skipIf(os.name == 'nt', 'POSIX native executable')
    def test_finds_native_linux_probe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'out').mkdir()
            probe = root / 'out' / 'bb-probe'
            probe.touch()
            with patch.object(runner, 'PORT', root):
                self.assertEqual(runner.find_probe(), probe)

    def test_install_dispatches_before_requiring_a_game(self):
        args = ['sotc.py', '--install-pkg', 'game.pkg', '--out', 'game']
        with patch.object(runner, 'load_ini'), patch.object(runner.sys, 'argv', args), \
                patch.object(runner, 'run_script') as install:
            self.assertEqual(runner.main(), 0)
        install.assert_called_once_with('pkg_extract.py', 'game.pkg', '--out', 'game')


class PrecacheTests(unittest.TestCase):
    def test_budget_reserves_memory_for_game_and_caps_at_half_ram(self):
        memory = 'MemTotal: 33554432 kB\nMemAvailable: 25165824 kB\n'
        with patch.object(Path, 'read_text', return_value=memory):
            self.assertEqual(runner.precache_budget(), 16 * 1024**3)

    def test_low_or_unknown_available_memory_disables_warmup(self):
        for memory in ('MemTotal: 33554432 kB\nMemAvailable: 4194304 kB\n',
                       'MemTotal: 33554432 kB\n'):
            with self.subTest(memory=memory), patch.object(Path, 'read_text', return_value=memory):
                self.assertEqual(runner.precache_budget(), 0)

    def test_overlay_archives_replace_base_case_insensitively(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, update = Path(tmp) / 'base', Path(tmp) / 'update'
            base.mkdir()
            update.mkdir()
            (base / 'pakN.psarc').write_bytes(b'old archive')
            (base / 'small.psarc').write_bytes(b'common')
            (base / 'eboot.bin').write_bytes(b'not an archive')
            (update / 'pakn.PSARC').write_bytes(b'updated archive')
            opened = []
            original = Path.open

            def record(path, *args, **kwargs):
                opened.append(path)
                return original(path, *args, **kwargs)

            with patch.dict(os.environ, SOTC_PREFETCH='1'), \
                    patch.object(runner.sys, 'platform', 'linux'), \
                    patch.object(runner, 'precache_budget', return_value=1024**3), \
                    patch.object(Path, 'open', record), patch('sys.stdout', new=io.StringIO()):
                runner.precache_game_data(base, update)
            self.assertEqual(opened, [base / 'small.psarc', update / 'pakn.PSARC'])

    def test_disabled_or_over_budget_does_not_read_archives(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'pak.psarc').write_bytes(b'game')
            for enabled, budget in (('0', 100), ('1', 3)):
                with self.subTest(enabled=enabled), patch.dict(os.environ, SOTC_PREFETCH=enabled), \
                        patch.object(runner.sys, 'platform', 'linux'), \
                        patch.object(runner, 'precache_budget', return_value=budget), \
                        patch.object(Path, 'open') as opened, patch('sys.stdout', new=io.StringIO()):
                    runner.precache_game_data(root)
                    opened.assert_not_called()
