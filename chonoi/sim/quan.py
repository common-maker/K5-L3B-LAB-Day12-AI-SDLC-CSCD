"""Buổi tối — Mở Quán. KHUNG: đi lại, chặn biên, đồng hồ, kho nạp từ file/scenario.

Nhóm viết tiếp (PRD-0 mục F, Quán):
  Lát 3 (C): khách đến theo lịch, chọn món nấu được, giữ chỗ nguyên liệu, kiên nhẫn,
             bỏ đi (customer_left), no_dish, vòng đời khách.
  TODO(nhóm, lát 4): interact tại bếp/bàn (cook_started, dish_ready, dish_picked, served),
                     ăn xong trả tiền (paid), boa, uy tín, hết ca (quan_end).
"""

import math

from ..ids import id_key, sort_by_id
from .ramp import ramp_velocity

TICK = 60.0


def _ticks(seconds):
    return int(round(seconds * 60))


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None, plan_dishes=None):
        """`plan_dishes`: id món trong kế hoạch Ngày (mode `day` truyền `day_plan[i].dishes`).
        None = quán chạy riêng, khách chọn trong cả menu (Test Contract v1.1 mục 2)."""
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        if plan_dishes is None:
            self.dish_ids = sorted(self.menu)
        else:
            unknown = sorted(set(plan_dishes) - set(self.menu))
            if unknown:
                from ..errors import BadInput
                raise BadInput(f"kế hoạch Ngày có món ngoài menu: {unknown}")
            self.dish_ids = sorted(set(plan_dishes))
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", _ticks(t["duration_s"]))
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.random_customers = scenario.get("random_customers", True)
        self.phase_tick = 0
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.customers = [self._customer_from_scenario(c) for c in scenario.get("customers", [])]
        for e in self.customers:
            ids.reserve(e["id"])
        self._check_reserved_fits_stock()
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                from ..errors import BadInput
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    # ---- Lát 3: dữ liệu khách -------------------------------------------------

    def _customer_from_scenario(self, c):
        """Khách dựng sẵn: điền mặc định theo hợp đồng; đơn reserved thiếu `reserved` thì cấp theo công thức."""
        dish_id = c.get("dish_id")
        status = c.get("order_status", "reserved")
        if "reserved" in c:
            reserved = dict(c["reserved"])
        elif status == "reserved" and dish_id in self.menu:
            reserved = dict(self.menu[dish_id]["recipe"])
        else:
            reserved = {}
        price = self.menu[dish_id]["price"] if dish_id in self.menu else 0
        return {
            "id": c["id"],
            "table_id": c["table_id"],
            "dish_id": dish_id,
            "order_tick": c.get("order_tick", 0),
            "state": c.get("state", "waiting"),
            "patience_ticks_left": c.get("patience_ticks_left", _ticks(self.t["patience_s"])),
            "eat_ticks_left": c.get("eat_ticks_left", 0),
            "order_status": status,
            "reserved": reserved,
            "base_price": c.get("base_price", price),
            "tip": c.get("tip", 0),
        }

    def _reserved_total(self):
        total = {}
        for c in self.customers:
            for k, n in c["reserved"].items():
                total[k] = total.get(k, 0) + n
        return total

    def _check_reserved_fits_stock(self):
        # Phải kiểm ở đây vì kho có thể đến từ --inventory (scenario.py không thấy file kho).
        from ..errors import BadInput
        for k, n in self._reserved_total().items():
            if n > self.stock.get(k, 0):
                raise BadInput(f"khách giữ {n} {k} nhưng kho chỉ có {self.stock.get(k, 0)}")

    def available_stock(self):
        """Kho khả dụng = tồn kho trừ phần các khách đang giữ."""
        held = self._reserved_total()
        return {k: self.stock[k] - held.get(k, 0) for k in self.stock}

    # ---- snapshot / step ------------------------------------------------------

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
        }

    def step(self, inp):
        events = []
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self._tick_timers()                 # C (kiên nhẫn) + D (nấu, ăn)
        self._stoves_ready(events)          # D
        self._move(inp)
        self._interact(inp, events)         # D
        self._settle_customers(events)      # C (bỏ đi) + D (trả tiền); chốt hết ca
        self._spawn_customer(events)        # C
        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        return events

    def _tick_timers(self):
        # C: kiên nhẫn giảm 1 mỗi bước cho khách đang chờ (khách mới sinh cuối bước trước nên giảm từ bước này).
        for c in self.customers:
            if c["state"] == "waiting":
                c["patience_ticks_left"] = max(0, c["patience_ticks_left"] - 1)
        # D: nấu và ăn. Món đã ready từ đầu bước mới tăng ready_ticks.
        for s in self.stoves:
            if s["state"] == "cooking" and s["cook_ticks_left"] > 0:
                s["cook_ticks_left"] -= 1
            elif s["state"] == "ready":
                s["ready_ticks"] += 1
        for c in self.customers:
            if c["state"] == "eating" and c["eat_ticks_left"] > 0:
                c["eat_ticks_left"] -= 1

    # ---- Lát 4: bếp, bưng, phục vụ, trả tiền ----------------------------------

    def _stoves_ready(self, events):
        for s in self.stoves:  # đã sort_by_id
            if s["state"] == "cooking" and s["cook_ticks_left"] <= 0:
                s["state"], s["ready_ticks"] = "ready", 0
                d = s["dish"]
                events.append(("dish_ready", {"stove_id": s["id"], "order_id": d["order_id"],
                                              "dish_id": d["dish_id"]}))

    def _interact(self, inp, events):
        """Tối đa MỘT đối tượng: gần nhất trong interact_radius; hòa thì bếp trước bàn, rồi theo id."""
        if not inp.pressed("interact"):
            return
        r = self.t["interact_radius"]
        cands = []
        for s in self.stoves:
            d = math.dist(self.pos, s["pos"])
            if d <= r:
                cands.append((d, 0, id_key(s["id"]), s))
        for tb in self.tables:
            d = math.dist(self.pos, tb["pos"])
            if d <= r:
                cands.append((d, 1, id_key(tb["id"]), tb))
        if not cands:
            return
        _, kind, _, obj = min(cands, key=lambda x: x[:3])
        if kind == 0:
            self._use_stove(obj, events)
        else:
            self._use_table(obj, events)

    def _use_stove(self, s, events):
        if s["state"] == "idle":
            order = self._oldest_reserved()
            if order is None:
                return
            dish = self.menu[order["dish_id"]]
            items = sorted(k for k, n in order["reserved"].items() for _ in range(n))
            for k, n in order["reserved"].items():  # tiêu đúng phần đã giữ
                self.stock[k] = self.stock.get(k, 0) - n
            order["reserved"] = {}
            order["order_status"] = "assigned"
            order["base_price"] = dish["price"]  # chốt giá khi bắt đầu nấu
            s.update(state="cooking", cook_ticks_left=_ticks(dish["cook_s"]), ready_ticks=0,
                     dish={"order_id": order["id"], "dish_id": order["dish_id"], "base_price": dish["price"]})
            events.append(("cook_started", {"stove_id": s["id"], "order_id": order["id"],
                                            "dish_id": order["dish_id"], "items": items,
                                            "base_price": dish["price"]}))
        elif s["state"] == "ready":
            if self.hand is not None:
                return
            d = s["dish"]
            self.hand = dict(d)
            s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)
            events.append(("dish_picked", {"stove_id": s["id"], "order_id": d["order_id"],
                                           "dish_id": d["dish_id"]}))
        # bếp đang nấu: không làm gì

    def _oldest_reserved(self):
        """Đơn reserved cũ nhất theo order_tick, hòa thì id bàn."""
        waiting = [c for c in self.customers if c["order_status"] == "reserved"]
        if not waiting:
            return None
        return min(waiting, key=lambda c: (c["order_tick"], id_key(c["table_id"])))

    def _use_table(self, tb, events):
        if self.hand is None:
            return
        cust = next((c for c in self.customers if c["table_id"] == tb["id"]), None)
        if (cust is None or cust["state"] != "waiting" or cust["order_status"] != "assigned"
                or cust["id"] != self.hand["order_id"]):
            return
        full = _ticks(self.t["patience_s"])
        ratio = cust["patience_ticks_left"] / full
        tip = math.floor(cust["base_price"] * self.t["tip_rate"]) if ratio >= self.t["tip_min_patience_ratio"] else 0
        cust.update(state="eating", order_status="served", eat_ticks_left=_ticks(self.t["eat_s"]), tip=tip)
        events.append(("served", {"order_id": cust["id"], "table_id": tb["id"], "dish_id": cust["dish_id"],
                                  "patience_ticks_left": cust["patience_ticks_left"],
                                  "base_price": cust["base_price"], "tip": tip}))
        self.hand = None

    def _settle_customers(self, events):
        # Hết ca: khách đang ăn trả tiền trước (D), rồi khách đang chờ rời với closing (C), rồi quan_end.
        self._pay_customers(events)         # D
        closing = self.time_left_ticks <= 0
        for c in self._by_table([c for c in self.customers if c["state"] == "waiting"]):
            if closing:
                self._customer_leaves(c, "closing", events)
            elif c["patience_ticks_left"] <= 0:
                lo, hi = self.t["reputation_min"], self.t["reputation_max"]
                self.reputation = min(hi, max(lo, self.reputation + self.t["left_reputation_delta"]))
                self._customer_leaves(c, "patience", events)

    def _pay_customers(self, events):
        """Khách ăn xong trả tiền và rời bàn. Hết ca: khách còn ăn trả ngay với closing."""
        closing = self.time_left_ticks <= 0
        for c in sort_by_id(self.customers):
            if c["state"] != "eating":
                continue
            done_eating = c["eat_ticks_left"] <= 0
            if not (done_eating or closing):
                continue
            amount = c["base_price"] + c["tip"]
            self.money += amount
            self.earned += amount
            self.shift_earned += amount
            if c["tip"] > 0:
                lo, hi = self.t["reputation_min"], self.t["reputation_max"]
                self.reputation = min(hi, max(lo, self.reputation + self.t["tip_reputation"]))
            events.append(("paid", {"order_id": c["id"], "table_id": c["table_id"],
                                    "base_price": c["base_price"], "tip": c["tip"], "amount": amount,
                                    "reason": "finished_eating" if done_eating else "closing"}))
            self.customers.remove(c)

    def _drop_order(self, order_id):
        """Khách rời mà chưa trả tiền: bỏ món của đơn trên tay hoặc trên bếp. Nguyên liệu đã dùng không hoàn lại."""
        if self.hand is not None and self.hand["order_id"] == order_id:
            self.hand = None
        for s in self.stoves:
            if s["dish"] is not None and s["dish"]["order_id"] == order_id:
                s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)

    def _by_table(self, customers):
        order = [tb["id"] for tb in self.tables]  # self.tables đã sort_by_id
        return sorted(customers, key=lambda c: order.index(c["table_id"]))

    def _customer_leaves(self, c, reason, events):
        """Khách rời: nhả `reserved` (nằm trên chính khách, bỏ khách là nhả), D dọn món của đơn."""
        self.customers.remove(c)
        self._drop_order(c["id"])
        events.append(("customer_left", {"order_id": c["id"], "table_id": c["table_id"],
                                         "reason": reason, "reputation": self.reputation}))

    def _spawn_customer(self, events):
        if not self.random_customers or self.time_left_ticks <= 0:
            return
        first = self.t["first_customer_tick"]
        every = _ticks(self.t["customer_interval_s"])
        pt = self.phase_tick
        if pt < first or (pt - first) % every != 0:
            return
        occupied = {c["table_id"] for c in self.customers}
        free = [tb for tb in self.tables if tb["id"] not in occupied]  # self.tables đã sort_by_id
        if not free:
            return
        avail = self.available_stock()
        # Lọc theo kế hoạch trước (self.dish_ids), rồi theo kho khả dụng. Không giới hạn số suất:
        # bán đủ số suất dự kiến rồi khách vẫn gọi tiếp được nếu đủ nguyên liệu.
        dishes = [d for d in self.dish_ids
                  if all(avail.get(k, 0) >= n for k, n in self.menu[d]["recipe"].items())]
        if not dishes:
            events.append(("no_dish", {}))
            return
        dish_id = dishes[self.rng.get("customers").randrange(len(dishes))]
        dish = self.menu[dish_id]
        c = {
            "id": self.ids.new("C"),
            "table_id": free[0]["id"],
            "dish_id": dish_id,
            "order_tick": pt,
            "state": "waiting",
            "patience_ticks_left": _ticks(self.t["patience_s"]),
            "eat_ticks_left": 0,
            "order_status": "reserved",
            "reserved": dict(dish["recipe"]),
            "base_price": dish["price"],
            "tip": 0,
        }
        self.customers.append(c)
        events.append(("customer_arrived", {"order_id": c["id"], "table_id": c["table_id"], "dish_id": dish_id}))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
