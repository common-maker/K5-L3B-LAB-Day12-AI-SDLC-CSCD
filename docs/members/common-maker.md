# common-maker — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm:** HUD 2 buổi pixel art 60fps, vòng ngày `--mode day`, Quán 2.5D, HUD độ tươi v1.2, 3 cảnh báo + chế độ tương phản cao (`chonoi/web/index.html`, `chonoi/live.py`, PR #6, #23), render benchmark Tkinter 1280×720 (`chonoi/bench_render.py`, đạt 153 FPS), bộ skill QA (`smoke-p1`, `verify-ac`, `smoke-day`, `smoke-p3`), test QA (`test_e_qa_p1.py`, `test_p2_ui_qa.py`, `test_p3_hud_qa.py`), điền `TEAM.md` và gắn tag `phase-1`, `phase-2`.
- **Tôi đã review & kiểm chứng:** Rà toàn bộ 4 lát qua `unittest`, smoke tích hợp 2 tiến trình, smoke vòng ngày, bench 30s (`docs/proof/phase-4/bench.json`), chụp ảnh Edge headless xác nhận không lỗi JS/màn hình đen (`docs/proof/phase-1..4/`).
- **AI sai ở đâu và phát hiện thế nào:** AI viết `continue` trong `forEach` gây màn hình đen JS (phát hiện khi người dùng báo và mở Edge headless kiểm tra); viết test P1 cũ theo kho đếm làm đỏ khi bật v1.2/v1.3 (đã cập nhật kèm lý do trong commit).
- **Điều tôi học được:** Kiểm tra trực quan bằng ảnh chụp thật và giữ HUD đọc được cả schema cũ lẫn mới giúp tách biệt tiến độ, tránh chặn chéo giữa các lát.
