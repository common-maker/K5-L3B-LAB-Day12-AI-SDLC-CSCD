"""Phần VẼ của benchmark (Ticket-04 mục 1) — E viết bằng Tkinter chuẩn Python. Khung đo ở `chonoi/bench.py`.

Giao diện bench.py cần:
    r = Renderer()
    r.open(1280, 720)
    r.draw(snapshot) -> bool
    r.close()

Linux không có màn hình: chạy qua `xvfb-run python3 -m chonoi.bench ...`.
"""

import tkinter as tk


_KIND_COLOR = {
    "ca_linh": "#90caf9",
    "ca_loc": "#ffb74d",
    "ca_keo": "#ce93d8",
    "bong_dien_dien": "#ffee58",
    "bong_sung": "#f48fb1",
    "keo_neo": "#a5d6a7",
}


class Renderer:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.w = 1280
        self.h = 720
        self.closed = False

    def open(self, width, height):
        self.w = int(width)
        self.h = int(height)
        self.root = tk.Tk()
        self.root.title("Chợ Nổi — Benchmark Render (1280x720)")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h, bg="#0d2238", highlightthickness=0)
        self.canvas.pack()
        self.closed = False
        self.root.update()

    def _on_close(self):
        self.closed = True

    def _to_px(self, x, d, bounds):
        bx = bounds.get("x", [0, 100])
        bd = bounds.get("d", [0, 30])
        top = 110
        bottom = self.h - 90
        px = 40 + (x - bx[0]) / max(1e-6, (bx[1] - bx[0])) * (self.w - 80)
        py = top + (d - bd[0]) / max(1e-6, (bd[1] - bd[0])) * (bottom - top)
        return px, py

    def draw(self, snapshot) -> bool:
        if self.closed or self.root is None or self.canvas is None:
            return False
        c = self.canvas
        w, h = self.w, self.h
        bounds = snapshot.get("bounds") or {"x": [0, 100], "d": [0, 30]}
        try:
            c.delete("all")
            # Nền trời, mặt nước và vùng nước sâu
            c.create_rectangle(0, 0, w, 110, fill="#1a3b5c", outline="")
            c.create_rectangle(0, 110, w, h - 90, fill="#0d314f", outline="")
            c.create_line(0, 110, w, 110, fill="#64d8ff", width=3)

            # Bến (dock)
            dock_x, dock_y = self._to_px(2, 0, bounds)
            c.create_rectangle(dock_x - 28, dock_y - 18, dock_x + 36, dock_y + 6, fill="#8d6e63", outline="#4e342e", width=2)
            c.create_text(dock_x + 4, dock_y - 26, text="BẾN", fill="#ffe082", font=("sans-serif", 11, "bold"))

            # Nút hái
            for node in snapshot.get("nodes", []):
                nx, ny = self._to_px(node["pos"][0], node["pos"][1], bounds)
                ready = node.get("regrow_ticks", 0) == 0
                col = _KIND_COLOR.get(node["kind"], "#81c784") if ready else "#455a64"
                c.create_oval(nx - 10, ny - 10, nx + 10, ny + 10, fill=col, outline="#102027", width=2)

            # Đàn cá
            for f in snapshot.get("fish", []):
                fx, fy = self._to_px(f["pos"][0], f["pos"][1], bounds)
                col = _KIND_COLOR.get(f["kind"], "#80deea")
                c.create_oval(fx - 12, fy - 7, fx + 12, fy + 7, fill=col, outline="#0b1d2c", width=1)

            # Thủy quái (Cá Sấu / Rắn)
            for m in snapshot.get("monsters", []):
                mx, my = self._to_px(m["pos"][0], m["pos"][1], bounds)
                col = "#ff5252" if m.get("state") == "chase" else "#66bb6a"
                c.create_rectangle(mx - 16, my - 9, mx + 16, my + 9, fill=col, outline="#1b0000", width=2)

            # Út Sen
            p = snapshot.get("player") or {}
            p_pos = p.get("pos", [2, 0])
            px, py = self._to_px(p_pos[0], p_pos[1], bounds)
            c.create_oval(px - 12, py - 12, px + 12, py + 12, fill="#ffd54f", outline="#ffffff", width=2)

            # HUD trên: thời gian, oxy, máu
            c.create_rectangle(8, 8, w - 8, 66, fill="#101a24", outline="#4b6078", width=2)
            t_sec = max(0, round((snapshot.get("time_left_ticks") or 0) / 60))
            c.create_text(24, 37, anchor="w", text=f"Giờ: {t_sec // 60}:{t_sec % 60:02d}", fill="#ffe082", font=("sans-serif", 15, "bold"))
            oxy = p.get("oxygen_ticks", 0)
            oxy_max = max(1, p.get("oxygen_max_ticks", 1800))
            c.create_rectangle(170, 22, 390, 50, fill="#1c2c3c", outline="#4b6078", width=2)
            c.create_rectangle(172, 24, 172 + int(216 * max(0.0, min(1.0, oxy / oxy_max))), 48, fill="#38c6f4", outline="")
            c.create_text(280, 36, text=f"Oxy {round(oxy / 60)}s", fill="#ffffff", font=("sans-serif", 12, "bold"))
            c.create_text(430, 37, anchor="w", text=f"Máu: {p.get('hp', 0)}/{p.get('hp_max', 3)}", fill="#ff8fa3", font=("sans-serif", 15, "bold"))

            # HUD dưới: giỏ + độ tươi
            c.create_rectangle(8, h - 82, w - 8, h - 8, fill="#101a24", outline="#4b6078", width=2)
            hold = snapshot.get("hold") or []
            cap = snapshot.get("hold_capacity", 12)
            for i in range(cap):
                x0 = 20 + i * 48
                y0 = h - 72
                c.create_rectangle(x0, y0, x0 + 42, y0 + 48, fill="#172432", outline="#324152", width=1)
                if i < len(hold):
                    it = hold[i]
                    kind = it["kind"] if isinstance(it, dict) else it
                    fresh_v = it.get("fresh") if isinstance(it, dict) else None
                    c.create_oval(x0 + 9, y0 + 6, x0 + 33, y0 + 30, fill=_KIND_COLOR.get(kind, "#ffffff"), outline="")
                    if fresh_v is not None:
                        bar_col = "#ef5350" if fresh_v < 30 else ("#ffb74d" if fresh_v < 60 else "#66bb6a")
                        c.create_rectangle(x0 + 4, y0 + 38, x0 + 4 + int(34 * max(0.0, min(100.0, fresh_v)) / 100.0), y0 + 44, fill=bar_col, outline="")
            c.create_text(20 + cap * 48 + 16, h - 46, anchor="w", text=f"Giỏ: {len(hold)}/{cap}", fill="#f4eedc", font=("sans-serif", 14, "bold"))

            self.root.update()
            return not self.closed
        except tk.TclError:
            self.closed = True
            return False

    def close(self):
        if self.root is not None:
            try:
                self.root.destroy()
            except tk.TclError:
                pass
            self.root = None
            self.canvas = None
