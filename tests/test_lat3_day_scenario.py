"""Lát 3 (C), Phase 2: kiểm scenario mode `day` (Test Contract v1.1 mục 4.3).

Gọi thẳng load_scenario vì `--mode day` của headless do lát `day` bật. Mâu thuẫn -> BadInput (mã 2).
"""

import json
import os
import unittest

from helpers import ROOT, Workdir, write_json
from chonoi.errors import BadInput
from chonoi.scenario import effective_day_plan, load_scenario

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    TUNING = json.load(f)["tuning"]


def load(data, mode="day"):
    with Workdir() as w:
        return load_scenario(write_json(w.path("sc.json"), data), mode, TUNING)


class DayScenario(unittest.TestCase):
    def test_vi_du_tren_board_hop_le(self):
        sc = load({"day": {"money": 200, "earned": 200},
                   "gather": {"hold": ["ca_loc", "bong_sung", "bong_sung"], "random_fish": False}})
        self.assertEqual(sc["day"], {"money": 200, "earned": 200})
        self.assertEqual(sc["gather"]["hold"], ["ca_loc", "bong_sung", "bong_sung"])
        self.assertEqual(sc["quan"], {})

    def test_cam_quan_stock_va_reputation(self):
        for key, val in (("stock", {"ca_loc": 1}), ("reputation", 4.0)):
            with self.subTest(key=key), self.assertRaises(BadInput):
                load({"quan": {key: val}})

    def test_quan_stock_van_hop_le_khi_chay_quan(self):
        self.assertEqual(load({"quan": {"stock": {"ca_keo": 2}}}, mode="quan"), {"stock": {"ca_keo": 2}})

    def test_tien_dau_ky(self):
        bad = [{"money": 100},                     # có tiền đầu kỳ mà không khai earned
               {"money": 300, "earned": 200},      # money > earned
               {"money": -1, "earned": 0},
               {"earned": 1.5}]
        for day in bad:
            with self.subTest(day=day), self.assertRaises(BadInput):
                load({"day": day})
        self.assertEqual(load({"day": {"earned": 500}})["day"], {"earned": 500})

    def test_uy_tin_trong_khoang(self):
        with self.assertRaises(BadInput):
            load({"day": {"reputation": 5.5}})
        self.assertEqual(load({"day": {"reputation": 0}})["day"]["reputation"], 0)

    def test_day_plan_tinh_lai_ingredients(self):
        sc = load({"day": {"day_plan": [{"day": 2, "dishes": {"ca_keo_nuong": 1, "lau_mam": 1}}]}})
        self.assertEqual(sc["day"]["day_plan"],
                         [{"day": 2, "dishes": {"ca_keo_nuong": 1, "lau_mam": 1},
                           "ingredients": {"bong_dien_dien": 1, "ca_keo": 3, "ca_linh": 2, "keo_neo": 1}}])

    def test_day_plan_sai_bao_loi(self):
        bad = [
            [{"day": 1, "dishes": {"ca_loc_nuong_trui": 1}, "ingredients": {"ca_loc": 2}}],  # khai sai tổng
            [{"day": 1, "dishes": {"pho": 1}}],                                             # món ngoài menu
            [{"day": 6, "dishes": {"ca_loc_nuong_trui": 1}}],                               # chỉ có 5 Ngày
            [{"day": 1, "dishes": {}}],
            [{"day": 1, "dishes": {"ca_loc_nuong_trui": 0}}],
            [{"day": 1, "dishes": {"ca_loc_nuong_trui": 1}}, {"day": 1, "dishes": {"goi_bong_sung": 1}}],
        ]
        for plan in bad:
            with self.subTest(plan=plan), self.assertRaises(BadInput):
                load({"day": {"day_plan": plan}})

    def test_khoi_la_va_truong_la(self):
        for data in ({"shop": {}}, {"day": {"gold": 1}}, {"day": {"upgrades": {"oxygen": -1}}}):
            with self.subTest(data=data), self.assertRaises(BadInput):
                load(data)

    def test_ke_hoach_hieu_luc_ghi_de_theo_ngay(self):
        sc = load({"day": {"day_plan": [{"day": 2, "dishes": {"goi_bong_sung": 1}}]}})
        plan = effective_day_plan(TUNING, sc["day"])
        self.assertEqual([p["day"] for p in plan], [1, 2, 3, 4, 5])
        self.assertEqual(plan[1]["dishes"], {"goi_bong_sung": 1})
        self.assertEqual(plan[0], TUNING["day_plan"][0])  # Ngày không ghi đè giữ preset


if __name__ == "__main__":
    unittest.main()
