# Retro nhóm

## Phase 2 (nhanh)
- Điều tốt: Nền v1.1 của `LeBao403` vào `main` sớm nên `LaanLee`, `TheDLCrimson`, `baoduy2048` và `common-maker` làm song song trên cùng khung không phải sửa luật của nhau. Test sinh ra theo từng lát (213 test xanh) giúp phát hiện lỗi tích hợp rất nhanh. Smoke tích hợp `gather` -> `quan` và `--mode day` chạy dưới 1 giây, có bằng chứng trong `docs/proof/phase-2/`.
- Điều tệ: (1) 3 PR đầu của `TheDLCrimson` bị trùng với nền v1.1 của `LeBao403` (cùng làm lại hợp đồng) nên phải đóng và dựng lại. (2) `test_e_qa_p1` của `common-maker` đỏ trên `main` sau khi nền v1.1 vào vì còn đòi `contract_version` 1.0, và `common-maker` sửa chậm. (3) Tag `phase-1`, `phase-2` không được gắn đúng hạn (đến Phase 3 vẫn chưa có tag nào trên `origin`) và `TEAM.md` vẫn là bản mẫu. (4) Client web có lỗi cú pháp `continue` trong `forEach` làm màn hình đen cả hai chế độ, test Python không bắt được vì không có test chạy JS.
- 1 hành động cho Phase 3: **`common-maker`** thêm kiểm tra cú pháp JS cho `index.html` vào smoke (chạy trang bằng trình duyệt headless và đọc lỗi console) trước mỗi lần báo "xong HUD"; **`LeBao403`** gắn và đẩy tag `phase-1`, `phase-2` ngay đầu Phase 3 (đã ghi trong `PHAN-CONG-PHASE-3.md`); **cả nhóm** điền `TEAM.md` bằng tên thật trước khi gắn `phase-3`.

## Phase 3 (nhanh)
- Điều tốt: cách "hai phiên bản, manifest để 1.1 tới khi mọi lát chuyển xong" của `LeBao403` cho phép các lát chuyển sang kho cá thể song song; fixture của từng lát được chuyển và kiểm bằng lệnh headless thật (`docs/proof/phase-3/`).
- Điều tệ: PR bật `contract_version` 1.2 (#22) vào `main` trước khi B, D, E chuyển xong, nên `main` đỏ 47 test trong một khoảng (danh sách trong `docs/proof/phase-3/bat-v12.txt`) và `phase-3` phải đợi tới khi các lát sửa xong.
- Điều rút ra từ lần đổi kho đếm thành kho cá thể (`common-maker` ghi tạm, cả nhóm bổ sung): đổi schema kho ảnh hưởng mọi lát cùng lúc nên cách làm "hai phiên bản, manifest để 1.1 tới khi mọi lát chuyển xong" của `LeBao403` giữ `main` luôn chạy được. HUD đọc được cả hai dạng kho nên không bị chặn bởi tiến độ của lát khác. Test bàn giao v1.2 để dạng bỏ qua có điều kiện thay vì báo xanh giả khi sim chưa có độ tươi.
- 1 hành động cho Phase 4: bật manifest mới chỉ sau khi các chủ lát báo đã chuyển xong và `main` xanh. Phase 4 làm đúng như vậy với v1.3: `main` giữ xanh (294 test) tới lúc gắn tag.

## Phase 4 (cuối)
- Rà lại hành động Phase 2 (`TheDLCrimson` tổng hợp từ `main` và `origin` lúc 2:40, chưa có kiểm chứng riêng của chủ việc):
  - `common-maker` thêm kiểm tra cú pháp JS cho `index.html` vào smoke: chưa thấy. Tìm trong `tests/` không có test chạy JS hay đọc console trình duyệt, nên lỗi kiểu `continue` trong `forEach` vẫn có thể lọt lại.
  - `LeBao403` gắn và đẩy tag `phase-1`, `phase-2`: lúc `TheDLCrimson` viết (2:40) chưa làm, `origin` chưa có tag nào. Sau đó đã gắn trễ: `phase-1` `759caeb`, `phase-2` `72f1f29`, `phase-3` `0ad4c08`, `phase-4` và `v1.0.0` `fd4df05`.
  - Cả nhóm điền `TEAM.md`: lúc 2:40 chưa làm. Sau đó đã điền và `tools/check_team.py` báo `OK: 5 thành viên`. Còn hai lỗi dữ liệu được rà ở bước audit: handle của B ghi `LaanLee` (tài khoản này không tồn tại, tài khoản thật là `laaaaanleeeee`) và tên của C ghi sai; đã sửa trong PR audit.
  - Vì sao: ba việc này không thuộc lát của ai và không có người kiểm cuối giờ. Chúng nằm giữa Integrator, QA và Scrum, đều đã ghi vào phân công nhưng không ai bị nhắc đúng lúc. Phần lý do là nhận định của `TheDLCrimson`, cần chủ việc xác nhận.
- Điều tốt:
  - Nền hợp đồng v1.1, v1.2 và v1.3 của `LeBao403` vào `main` sớm, các lát làm song song được. Cách "hai phiên bản, manifest để nguyên tới khi mọi lát chuyển xong" giữ `main` chạy được khi đổi schema kho.
  - Test theo từng lát và bằng chứng headless trong `docs/proof/` cho phép kiểm tích hợp bằng lệnh thật, không bằng lời.
  - Soak 10 Ngày của `LeBao403` bắt được lỗi mà test từng lát không thấy (xem mục AI sai).
- Điều tệ:
  - Việc chung (tag, `TEAM.md`) bị bỏ sót suốt cả 4 phase.
  - Các lát đụng chung `quan.py` và `scenario.py` nên có PR trùng việc và phải đóng (3 PR đầu của `TheDLCrimson`).
  - Một số commit đẩy lên nhánh sau khi PR đã merge nên không vào `main` (commit nhật ký và standup Phase 3 của `TheDLCrimson`), cần mở PR bù.
- Số liệu (commit không tính merge trên `main`, đếm lúc 2:40): `LeBao403` 19, `common-maker` 17, `TheDLCrimson` 16, `baoduy2048` 8, `LaanLee` 5 (`laaaaanleeeee` ký commit bằng tên `LaanLee`, cần chắc email đã gắn với tài khoản). 9 commit của `Hai Duong` là starter của giảng viên. PR đã mở: `TheDLCrimson` 12, `LeBao403` 6, `laaaaanleeeee` 5, `common-maker` 2, `baoduy2048` 2.
  - Cách đọc code của nhau: `TheDLCrimson` đọc diff lát 4 của `baoduy2048` (PR #3) và tìm ra xung đột với `main` trước khi gộp. Các cặp còn lại chưa có bằng chứng review trên GitHub, cần chủ cặp bổ sung.
  - Token theo người (từ `docs/ai-usage-log.md`, đếm khác nhau nên chỉ so sánh thô): `LeBao403` khoảng 3,7M (P1), 12,5M (P2), 17,3M (P3), 7,9M (P4); `TheDLCrimson` khoảng 5,9M (P1), 22,9M (P2), 23,2M (P3). `common-maker` chỉ ước tính. `LaanLee` và `baoduy2048` chưa ghi token.
- Một lần AI sai và cách nhóm phát hiện: `DaySession` do AI viết chỉ lập chỉ mục `day_plan[day - 1]`, nên vỡ `IndexError` ở Ngày 6. Test từng lát chỉ chạy tối đa 2 Ngày nên không thấy. Soak `--days 10` của `LeBao403` cho `days_completed` 5 và `crashes` 1. `TheDLCrimson` tái hiện bằng đúng lệnh đó, sửa bằng `(day - 1) % 5`, thêm test Ngày 6-7 lặp kế hoạch D1-D2, và chạy lại soak ra 10 Ngày, 0 lỗi (`docs/proof/phase-4/lat3-soak-10-ngay.json`).
- Nếu làm lại, đổi gì:
  - Ngay phút đầu của phase đầu: điền `TEAM.md` và giao tag cho một người cụ thể, có hạn.
  - Trước khi viết hợp đồng hay khung, đọc `main` và các PR đang mở để không làm trùng.
  - Chạy một smoke nhiều Ngày sớm hơn, không đợi tới Phase 4.
