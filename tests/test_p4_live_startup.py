"""Phase 4: `python3 -m chonoi.live` phải khởi động được khi stdout dùng bảng mã cp1252 (Windows, stdout là ống).

Lỗi gặp khi clone sạch: dòng in tiếng Việt lúc khởi động ném UnicodeEncodeError và máy chủ thoát ngay.
"""

import os
import subprocess
import sys
import time
import unittest

from helpers import ROOT


class LiveStartup(unittest.TestCase):
    def test_khoi_dong_voi_stdout_cp1252_khong_sap(self):
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        p = subprocess.Popen([sys.executable, "-m", "chonoi.live", "--mode", "gather", "--port", "0"], cwd=ROOT,
                             env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline and p.poll() is None:
                time.sleep(0.1)
            exited = p.poll()
        finally:
            if p.poll() is None:
                p.terminate()
            out, err = p.communicate(timeout=10)
        self.assertIsNone(exited, f"máy chủ thoát sớm, mã {exited}: {err.decode('utf-8', 'replace')[-300:]}")
        self.assertIn(b"http://", out)


if __name__ == "__main__":
    unittest.main()
