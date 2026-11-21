"""Test QA (Người E) cho Phase 1: kiểm tra dải game.contract.json, smoke 2 tiến trình mở rộng, và HUD/assets chonoi.live."""

import json
import math
import os
import unittest
import urllib.error
import urllib.request

from chonoi import fresh
from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer
from helpers import ROOT, Workdir, read_jsonl, run_headless, snapshots, write_json


class ContractTuningRangesTest(unittest.TestCase):
    def test_contract_v10_required_fields_and_ranges(self):
        with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
            c = json.load(f)
        self.assertEqual(c["contract_version"], "1.3")
        self.assertTrue(c.get("bench_cmd"))
        self.assertTrue(c.get("soak_cmd"))
        self.assertTrue(isinstance(c["team_size"], int) and not isinstance(c["team_size"], bool))
        self.assertTrue(4 <= c["team_size"] <= 6)

        t = c["tuning"]
        self.assertEqual(t["tick_hz"], 60)
        g = t["gather"]
        self.assertTrue(60 <= g["duration_s"] <= 600)
        self.assertTrue(4 <= g["hold_capacity"] <= 30)
        for rkey in ("dock_radius", "interact_radius", "catch_radius"):
            self.assertTrue(0.5 <= g[rkey] <= 5, rkey)
        self.assertTrue(1 <= g["swim_speed"] <= 10)
        self.assertTrue(0 <= g["catch_cooldown_s"] <= 10)
        self.assertTrue(10 <= g["oxygen_max_s"] <= 120)
        self.assertTrue(isinstance(g["ramp_max_ticks"], int) and not isinstance(g["ramp_max_ticks"], bool))
        self.assertTrue(0 <= g["ramp_max_ticks"] <= 6)
        self.assertGreater(int(round(g["regrow_s"] * 60)), 0)

        q = t["quan"]
        self.assertTrue(60 <= q["duration_s"] <= 600)
        self.assertTrue(20 <= q["patience_s"] <= 180)
        self.assertTrue(0.5 <= q["interact_radius"] <= 5)
        self.assertTrue(1 <= q["walk_speed"] <= 10)
        self.assertTrue(isinstance(q["ramp_max_ticks"], int) and not isinstance(q["ramp_max_ticks"], bool))
        self.assertTrue(0 <= q["ramp_max_ticks"] <= 6)
        self.assertTrue(isinstance(q["first_customer_tick"], int) and not isinstance(q["first_customer_tick"], bool))
        self.assertTrue(0 < q["first_customer_tick"] < int(round(q["duration_s"] * 60)))
        self.assertGreater(int(round(q["eat_s"] * 60)), 0)
        self.assertGreater(int(round(q["customer_interval_s"] * 60)), 0)
        self.assertIsNone(q["burn_s"])
        self.assertGreater(q["tip_rate"], 0)
        self.assertTrue(0 < q["tip_min_patience_ratio"] <= 1)
        self.assertGreater(q["tip_reputation"], 0)
        self.assertLess(q["left_reputation_delta"], 0)

        expected_recipes = {
            "ca_loc_nuong_trui": {"ca_loc": 1},
            "goi_bong_sung": {"bong_sung": 2},
            "lau_ca_linh_dien_dien": {"ca_linh": 3, "bong_dien_dien": 1},
            "canh_chua_ca_loc": {"ca_loc": 1, "bong_dien_dien": 1},
            "ca_keo_nuong": {"ca_keo": 2},
            "lau_mam": {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1},
        }
        menu = t["menu"]
        self.assertEqual(set(menu.keys()), set(expected_recipes.keys()))
        for dish_id, recipe in expected_recipes.items():
            spec = menu[dish_id]
            self.assertEqual(spec["recipe"], recipe)
            self.assertTrue(isinstance(spec["price"], int) and not isinstance(spec["price"], bool))
            self.assertGreater(spec["price"], 0)
            self.assertGreater(int(round(spec["cook_s"] * 60)), 0)

        self.assertEqual([s["id"] for s in q["stoves"]], ["B1", "B2"])
        self.assertEqual([tb["id"] for tb in q["tables"]], ["T1", "T2", "T3", "T4"])
        self.assertTrue({"bong_dien_dien", "bong_sung", "keo_neo"}.issubset({n["kind"] for n in g["nodes"]}))
        self.assertTrue(all(n["pos"][1] == 0 for n in g["nodes"]))
        self.assertEqual(g["fish_initial"], 8)
        self.assertEqual(set(g["fish_depths"].keys()), {"ca_linh", "ca_loc", "ca_keo"})
        self.assertTrue(all(0 < lo < hi for lo, hi in g["fish_depths"].values()))


class SmokeTwoProcessExtraTest(unittest.TestCase):
    def test_two_process_all_four_kinds_and_score_formula(self):
        with Workdir() as w:
            kinds = ["ca_loc", "ca_linh", "ca_linh", "ca_linh", "bong_dien_dien", "bong_sung", "bong_sung"]
            hold = [{"id": f"I{i}", "kind": k, "fresh": 100} for i, k in enumerate(kinds, 1)]
            sc = write_json(w.path("sc.json"), {"gather": {"hold": hold}})
            inp = write_json(w.path("in.json"), {"frames": [{"tick": 0, "interact": True}]})
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "gather", "--seed", "42", "--scenario", sc, "--inputs", inp,
                                     "--ticks", "1", "--out", w.path("g.jsonl"), "--inventory-out", inv)
            self.assertEqual(code, 0, err)
            with open(inv, encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual([it["id"] for it in saved["items"]], [f"I{i}" for i in range(1, 8)])
            self.assertEqual([it["kind"] for it in saved["items"]], kinds)

            code, err = run_headless("--mode", "quan", "--seed", "42", "--inventory", inv,
                                     "--ticks", "0", "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("q.jsonl"))
            snap = snapshots(rows)[0]
            self.assertEqual([(x["id"], x["kind"]) for x in snap["stock"]],
                             [(x["id"], x["kind"]) for x in saved["items"]])
            for a, b in zip(snap["stock"], saved["items"]):
                self.assertAlmostEqual(a["fresh"], b["fresh"], places=3)
            self.assertEqual(snap["score"], snap["earned"] + 100 * math.floor(snap["reputation"]))

    def test_two_process_empty_hold_and_quan_determinism(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"hold": []}})
            inp = write_json(w.path("in.json"), {"frames": [{"tick": 0, "interact": True}]})
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "gather", "--seed", "42", "--scenario", sc, "--inputs", inp,
                                     "--ticks", "1", "--out", w.path("g.jsonl"), "--inventory-out", inv)
            self.assertEqual(code, 0, err)
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": []})

            for i in (1, 2):
                code, err = run_headless("--mode", "quan", "--seed", "42", "--inventory", inv,
                                         "--ticks", "60", "--out", w.path(f"q{i}.jsonl"))
                self.assertEqual(code, 0, err)
            with open(w.path("q1.jsonl"), "rb") as a, open(w.path("q2.jsonl"), "rb") as b:
                self.assertEqual(a.read(), b.read())


class LiveHudAndAssetsTest(unittest.TestCase):
    def test_live_serves_updated_hud_quan_state_and_fish_assets(self):
        tuning = load_contract()["tuning"]
        inv_items = [{"id": "I1", "kind": "ca_loc", "fresh": 100}, {"id": "I2", "kind": "ca_loc", "fresh": 100}]
        server = LiveServer(LiveGame("quan", tuning, {}, 1, inventory=[fresh.from_public(it) for it in inv_items]), port=0)
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            with urllib.request.urlopen(base + "/", timeout=5) as r:
                self.assertEqual(r.status, 200)
                html = r.read()
            for token in (b"drawGather", b"drawQuan", b"computeAvailableStock", b"dishName", "Kho khả dụng".encode("utf-8")):
                self.assertIn(token, html)

            with urllib.request.urlopen(base + "/state", timeout=5) as r:
                self.assertEqual(r.status, 200)
                st = json.loads(r.read())
            self.assertEqual(st["mode"], "quan")
            self.assertEqual([(x["id"], x["kind"]) for x in st["stock"]], [("I1", "ca_loc"), ("I2", "ca_loc")])
            for x in st["stock"]:
                self.assertTrue(99.0 <= x["fresh"] <= 100.0, x)
            for k in ("stoves", "tables", "reputation", "score"):
                self.assertIn(k, st)

            for asset_path in (
                "/assets/fish/Ictaluridae/Catfish/channel_catfish.png",
                "/assets/fish/Cenrarchidae/Panfish/bluegill_panfish.png",
            ):
                with urllib.request.urlopen(base + asset_path, timeout=5) as r:
                    self.assertEqual(r.status, 200)
                    self.assertIn("image/png", r.headers.get("Content-Type", ""))

            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(base + "/assets/%2e%2e/game.contract.json", timeout=5)
            self.assertEqual(ctx.exception.code, 404)
            ctx.exception.close()
        finally:
            server.stop()

    def test_hud_has_three_alerts_and_high_contrast(self):
        with open(os.path.join(ROOT, "chonoi", "web", "index.html"), encoding="utf-8") as f:
            html = f.read()
        for token in ("Thủy quái!", "Hết hơi!", "Khách sắp giận!", "highContrast", "[H] Tương phản"):
            self.assertIn(token, html)

    def test_bench_renderer_interface(self):
        from chonoi.bench_render import Renderer
        r = Renderer()
        for method in ("open", "draw", "close"):
            self.assertTrue(callable(getattr(r, method, None)), method)


if __name__ == "__main__":
    unittest.main()
