import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_PATH = str(ROOT_DIR / "app.py")
STREAMLIT_APP_PATH = str(ROOT_DIR / "streamlit_app.py")

class TestDeploymentNavigation(unittest.TestCase):
    def test_app_py_navigation(self):
        """Verifikasi bahwa app.py dapat berpindah semua menu tanpa blank dan tanpa exception."""
        at = AppTest.from_file(APP_PATH)
        at.run(timeout=30)
        self.assertGreater(len(at.sidebar.radio), 0)
        options = at.sidebar.radio[0].options
        for opt in options:
            at.sidebar.radio[0].set_value(opt)
            at.run(timeout=30)
            self.assertGreater(len(at.sidebar.radio), 0, f'Sidebar blank on {opt}')
            self.assertGreater(len(at.main), 0, f'Main blank on {opt}')
            self.assertEqual(len(at.exception), 0, f'Exception on {opt}: {at.exception}')

    def test_streamlit_app_navigation(self):
        """Verifikasi bahwa streamlit_app.py dapat berpindah semua menu tanpa blank."""
        at = AppTest.from_file(STREAMLIT_APP_PATH)
        at.run(timeout=30)
        self.assertGreater(len(at.sidebar.radio), 0)
        options = at.sidebar.radio[0].options
        for opt in options:
            at.sidebar.radio[0].set_value(opt)
            at.run(timeout=30)
            self.assertGreater(len(at.sidebar.radio), 0, f'Sidebar blank on {opt}')
            self.assertGreater(len(at.main), 0, f'Main blank on {opt}')
            self.assertEqual(len(at.exception), 0, f'Exception on {opt}: {at.exception}')

if __name__ == '__main__':
    unittest.main()
