"""Lát 3 (C), Phase 2: khách chọn món theo kế hoạch Ngày, 6 món, 4 bàn.

Gọi thẳng QuanSim (như test lát 4) để truyền `plan_dishes` giống mode `day` sẽ làm.
"""

import json
import os
import unittest

from helpers import ROOT
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    TUNING = json.load(f)["tuning"]

PLAN = {p["day"]: p for p in TUNING["day_plan"]}


class Idle:
    move = (0.0, 0.0)

    def pressed(self, name):
        return False


def make(stock, plan_dishes=None, seed=1):
    return QuanSim(TUNING, {"stock": dict(stock)}, Streams(seed), IdAllocator(), plan_dishes=plan_dishes)


def run(sim, ticks):
    out = []
    for _ in range(ticks):
        out += sim.step(Idle())
    return out


def arrived(events):
    return [d for n, d in events if n == "customer_arrived"]


class PlanDishes(unittest.TestCase):
    def test_quan_rieng_dung_ca_6_mon(self):
        # Chỉ có cá kèo: món mới ca_keo_nuong phải gọi được khi quán chạy riêng.
        ev = run(make({"ca_keo": 2}), 120)
        self.assertEqual([d["dish_id"] for d in arrived(ev)], ["ca_keo_nuong"])

    def test_loc_theo_ke_hoach_truoc_kho(self):
        # Kho đủ cả ca_keo_nuong lẫn ca_loc_nuong_trui, nhưng Ngày 1 chỉ có ca_loc_nuong_trui và goi_bong_sung.
        ev = run(make({"ca_keo": 2, "ca_loc": 1}, plan_dishes=PLAN[1]["dishes"]), 120)
        self.assertEqual([d["dish_id"] for d in arrived(ev)], ["ca_loc_nuong_trui"])

    def test_mon_ngoai_ke_hoach_khong_cuu_no_dish(self):
        # Ngày 3 không có ca_loc_nuong_trui; chỉ có ca_loc thì không món nào của kế hoạch đủ -> no_dish.
        ev = run(make({"ca_loc": 1}, plan_dishes=PLAN[3]["dishes"]), 120)
        self.assertEqual(arrived(ev), [])
        self.assertEqual([n for n, _ in ev], ["no_dish"])

    def test_khong_gioi_han_so_suat(self):
        # Ngày 1 dự kiến 3 suất ca_loc_nuong_trui; đủ nguyên liệu thì khách thứ 4 vẫn gọi được.
        ev = run(make({"ca_loc": 10}, plan_dishes=PLAN[1]["dishes"]), 120 + 3 * 900)
        got = arrived(ev)
        self.assertEqual([d["dish_id"] for d in got], ["ca_loc_nuong_trui"] * 4)
        self.assertEqual([d["table_id"] for d in got], ["T1", "T2", "T3", "T4"])  # bàn trống id nhỏ nhất

    def test_ke_hoach_co_mon_ngoai_menu_bao_loi(self):
        with self.assertRaises(BadInput):
            make({}, plan_dishes={"pho": 1})


if __name__ == "__main__":
    unittest.main()
