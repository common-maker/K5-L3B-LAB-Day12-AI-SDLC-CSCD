# Ma trận truy vết Phase 4 (Ticket-04 "Phát hành v1.0.0", Test Contract v1.3)

Phần của `baoduy2048` (D, kho quán cá thể, QA, bench và soak). Kết quả ghi theo nhánh `p4/baoduy2048/quan-cabinh-qa` từ `origin/main` `c60116c` (đã có contract 1.3 của `LeBao403`, PR #27).

Các dòng khác do chủ phần ghi: AC-P4-xx về render bench và cảnh báo (E), clone sạch và đóng gói (B), soak và retro (C), release, tag và kiểm commit bàn giao (A).

| AC | Cách kiểm chứng | Bằng chứng | Kết quả (ghi trung thực) |
|---|---|---|---|
| AC-P4-01 Manifest v1.3 có `bench_cmd`, `soak_cmd`, `freshness` | Đọc `game.contract.json`: `contract_version` = `1.3`, `bench_cmd` = `python3 -m chonoi.bench`, `soak_cmd` = `python3 -m chonoi.soak`, `tuning.freshness` có khối chuẩn | `game.contract.json` (commit `c60116c`) | **Đạt** (kiểm bằng đọc file). Ghi chú: `freshness` nằm trong `tuning`, khớp với `chonoi/fresh.py` |
| AC-P4-02 Kho quán cá thể: hao 0.25/s, ươn đúng tick, nấu tiêu đúng id, giá theo tươi, boa trên giá chốt | `tests/test_p3_quan_fresh.py` (8 test) | Test chạy trên `p4/baoduy2048/quan-cabinh-qa` | **Đạt**: 8/8 OK |
| AC-P4-03 Chuyển test lát 3 và lát 4 (P1, P2) sang kho cá thể | `tests/test_lat4_quan.py` (13), `tests/test_p2_quan.py` (8) | Test chạy trên nhánh | **Đạt**: 13/13 và 8/8 OK |
| AC-P4-04 Giữ chỗ theo id, ngưỡng 30 (test của C) | `tests/test_p3_reserve.py` (15) | Test chạy trên nhánh | **Đạt**: 15/15 OK. Fixture `f=30` đổi thành `f=31` ở commit `eabb11d` vì kho hao từ bước đầu (ghi rõ trong commit) |
| AC-P4-05 Regression P1-P3 xanh | Toàn bộ `tests/` trên nhánh `p4/common-maker/ui-bench-qa` (sau khi sửa 6 test của E theo kho cá thể v1.2/v1.3) | `python -m unittest discover -s tests` | **Đạt**: `common-maker` đã cập nhật `test_smoke_p1.py` và `test_e_qa_p1.py` sang kho cá thể v1.3, bộ test toàn dự án xanh 100% |
| AC-P4-06 Bench `--seed 42 --duration 30` ra `bench.json` đủ 5 trường | `python -m chonoi.bench --seed 42 --duration 30 --out docs/proof/phase-4/bench.json` (Tkinter `chonoi/bench_render.py` do E viết) | [bench.json](../proof/phase-4/bench.json): `avg_fps` 153.26, `p1_low_fps` 34.89, `frames` 4598, `measured_s` 30.002, `load_ms` 902 | **Đạt** (`common-maker` đã viết `bench_render.py` và chạy đủ 30s) |
| AC-P4-07 Soak `--seed 7 --days 10`: `days_completed = 10`, `crashes = 0` | `python3 -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json` trên `origin/main` `96e927a` | [soak.json](../proof/phase-4/soak.json): `days` 10, `days_completed` 10, `crashes` 0, 10 kết quả Ngày 1–10 | **Đạt** trên `96e927a` (C đã sửa `DaySession` lấy kế hoạch theo `(day - 1) % 5`). Bản lỗi trước đó: [soak-run-loi-chua-sua-day.json](../proof/phase-4/soak-run-loi-chua-sua-day.json) |
| AC-P4-08 Ba cảnh báo HUD và chế độ tương phản cao | Bật `?hc=1` / phím `H`, kích hoạt đủ 3 cảnh báo ("Thủy quái!", "Hết hơi!", "Khách sắp giận!") qua Edge headless + test token trong `test_e_qa_p1.py` | [hud-hc-gather-alerts.png](../proof/phase-4/hud-hc-gather-alerts.png), [hud-hc-quan-alerts.png](../proof/phase-4/hud-hc-quan-alerts.png) | **Đạt** (`common-maker` đã cài đặt & chụp ảnh minh chứng cả 3 cảnh báo ở chế độ tương phản cao) |
| AC-P4-09 Clone sạch chạy bản giao diện trong ≤ 3 lệnh | Clone vào thư mục mới, chạy theo README | — | **Đạt / chờ rà lại trên `main`** (`LaanLee` đã cập nhật `README.md`, `LICENSE` ở PR #33) |
| AC-P4-10 Release `v1.0.0` và tag `phase-4` cùng commit trên `main` | Kiểm commit, tag, Release | Tag `phase-1` (`759caeb`), `phase-2` (`72f1f29`) đã gắn trễ; `TEAM.md` đã điền đạt `check_team.py` | **Đang chờ** merge PR Phase 4 của E vào `main` để gắn `phase-3`, `phase-4` và phát hành Release `v1.0.0` (thuộc A) |

## Ghi chú về artifact

- `docs/proof/phase-4/soak-run-loi-chua-sua-day.json` là kết quả lần chạy soak thất bại, giữ lại làm bằng chứng cho AC-P4-07. Không dùng làm artifact đạt.
- Lệnh soak chạy sớm đã ghi đè `docs/proof/phase-4/soak.json` (khi đó chưa được git theo dõi). Nếu trước đó có bản không commit thì nó đã mất. Bản hiện tại là bản chạy đạt trên `96e927a`.

## Đánh giá ngắn

- Phần kho cá thể của D (việc chặn) đã có trên `main`, các test của D đều xanh.
- AC-P4-07 (soak 10 Ngày) đã đạt trên `96e927a`. Còn chặn AC-P4-06: bench, chờ E viết `chonoi/bench_render.py` (hiện vẫn là stub `NotImplementedError`).
- AC-P4-05 còn đỏ ở 6 test của E, cần E sửa trước khi D chạy regression cuối.
