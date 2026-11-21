# Quán Ăn Chợ Nổi v1.0.0 (nhóm CSCD)

Game 2D về Út Sen ở chợ nổi Rạch Sen. Buổi sáng em lặn bắt cá, hái rau trên sông Chín Khúc. Buổi tối em nấu và phục vụ khách trên nhà bè của Má Tư, rồi dùng tiền mua nâng cấp cho lần lặn sau. Một lượt chơi chuẩn kéo dài 5 Ngày. Bản này chạy theo Test Contract v1.3.

- Commit bàn giao: `fd4df05` (tag `phase-4` và `v1.0.0`)
- Đóng gói: `choi-noi-v1.0.0.zip` (đính kèm trong GitHub Release `v1.0.0`)

## Điểm mới theo từng phase

**Phase 1: hai buổi chơi nối nhau qua file kho**
- Buổi sáng: bơi trong mặt cắt sông, oxy giảm khi lặn và hồi khi nổi, ngạt thì mất Máu, hết Máu thì ngất. Hái nút ở mặt nước, bắt đàn cá bằng `catch`. Cập bến hoặc hết giờ thì giỏ thành kho.
- Buổi tối: khách đến theo lịch, giữ nguyên liệu khi gọi món. Người chơi nấu, bưng, phục vụ. Khách trả tiền và boa; khách hết kiên nhẫn làm giảm uy tín.

**Phase 2: một vòng ngày trọn vẹn**
- Số liệu chuẩn, 6 nguyên liệu (thêm cá kèo, kèo nèo) và 6 món, 2 bếp, 4 bàn.
- Đàn cá bơi và sinh thêm theo lịch. Cá Sấu Năm Chèo tuần tra, đuổi, cắn làm mất Máu và rơi nửa giỏ.
- Vòng ngày DayIntro → lặn → quán → kết quả → Shop, kế hoạch món D1 đến D5 do Má Tư công bố, Shop nâng cấp bình oxy và áo phao, tạm dừng, menu.
- Mở rộng **Rắn Hổ Mây** (`snake`): con quái thứ hai từ Ngày 1, đuổi nhanh hơn Cá Sấu và hoạt động ở vùng nước nông hơn.

**Phase 3: Mùa Nước Nổi**
- Mỗi nguyên liệu là một cá thể có id và độ tươi. Hàng hao 0.5/s trong giỏ, 0.25/s trong kho quán; dưới 30 là hàng ươn, không nấu được.
- Khách giữ những cá thể tươi nhất. Hàng đang giữ mà ươn thì giữ lại một lần, không đủ thì đơn không làm được.
- Giá món tính theo độ tươi trung bình lúc bắt đầu nấu. HUD hiện độ tươi và hàng ươn.

**Phase 4: phát hành**
- Benchmark có render (`bench_cmd`) và soak headless 10 Ngày (`soak_cmd`).
- Cảnh báo bằng chữ và biểu tượng cho thủy quái gần (`"Thủy quái!"`), oxy sắp hết (`"Hết hơi!"`), khách sắp giận (`"Khách sắp giận!"`), kèm chế độ tương phản cao (`[H]` / `?hc=1`).
- Đóng gói chạy từ clone sạch.

## Cách chạy

Yêu cầu: Python 3.10 trở lên, chỉ dùng thư viện chuẩn, không cần cài gói ngoài. Chơi trên trình duyệt.

```bash
git clone https://github.com/common-maker/K5-L3B-LAB-Day12-AI-SDLC-CSCD.git
cd K5-L3B-LAB-Day12-AI-SDLC-CSCD
python3 -m chonoi.live --mode day
```

Mở địa chỉ in ra (mặc định `http://127.0.0.1:8000/`). Trên Windows, nếu không có lệnh `python3` thì dùng `python`.

| Phím | Tác dụng |
|---|---|
| WASD / mũi tên | Bơi, đi lại |
| E | Cập bến, hái; nấu, bưng, phục vụ |
| Space | Bắt cá (khi đang lặn) |
| Esc / P | Tạm dừng |
| 1 / 2 / Enter | Shop: mua bình oxy / áo phao / đóng Shop |
| R | Chơi lại |

Lệnh cho kiểm thử và chấm:

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests        # test
python3 -m chonoi.headless --mode day --seed 1 --days 1 --ticks 22200 --out day.jsonl
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json  # cần màn hình; Linux không màn hình: xvfb-run
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

## Kết quả đo

| Hạng mục | Kết quả | Bằng chứng |
|---|---|---|
| Soak 10 Ngày, seed 7 | `days_completed` 10, `crashes` 0 | `docs/proof/phase-4/soak.json` |
| Benchmark seed 42, 30 s, 1280×720 | avg 153.26 FPS, 1% low 34.89 FPS, load 902 ms | `docs/proof/phase-4/bench.json` |
| Test tự động | 297/297 đạt (3 skipped có điều kiện) | `docs/verification/phase-4.md` |

## Giới hạn đã biết

- Bot của soak chỉ hái ở mặt nước và phục vụ khách theo luật sẵn có, không lặn bắt cá, nên điểm soak thấp. Ticket-04 chỉ chấm `days_completed` và `crashes`.
- Chọn vị trí 8 đàn cá đầu ca, quãng lùi của quái (`recoil_dist` là tổng 2 m) và ngưỡng độ sâu của quái (`depths[0]` của loài) là giả định của nhóm, ghi trong `docs/clarify.md` và `docs/contracts/README.md` mục 5.6.
- Benchmark mở cửa sổ thật bằng Tkinter (`chonoi/bench_render.py`) nên cần màn hình (Linux không màn hình chạy qua `xvfb-run`).
- Mở rộng của Phase 3 (dòng nước lũ, khách đặt trước) và Phase 4 (bảng xếp hạng, phụ đề SFX) chưa làm.
- Phản tư cá nhân của `baoduy2048` (`docs/members/baoduy2048.md`) và nguồn gói ảnh `assets/fish/` trong `CREDITS.md` đang chờ bổ sung.

## Ghi nguồn

Tài sản ngoài và công cụ AI đã dùng: xem `CREDITS.md`. Giấy phép: `LICENSE` (MIT). Cách nhóm làm việc, quyết định kỹ thuật và nhật ký dùng AI: `docs/adr/`, `docs/contracts/README.md`, `docs/retro.md`, `docs/ai-usage-log.md`, `docs/members/`.
