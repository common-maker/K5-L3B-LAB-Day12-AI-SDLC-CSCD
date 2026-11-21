# LaanLee — phản tư cá nhân (≤ 200 từ)

> Bản nháp do AI soạn từ những gì có trong repo. LaanLee đọc lại, sửa theo trải nghiệm thật và điền thêm link review nếu có.

- Tôi đã làm (kèm link commit): Phase 1, lát 2 gather: hái nút, bắt cá, giỏ đầy, kho cuối buổi (`55a0033`, PR #4). Phase 2, lát cá: bơi, phản xạ mép, đổi hướng theo seed, sinh cá theo lịch (`10f565d`, PR #14) và 30 test `tests/test_p2_fish.py` (`aef4fad`, PR #17, #19). Phase 3, giỏ cá thể và độ tươi: `_decay_hold`, `_add_to_hold`, 24 test `tests/test_p3_gather_fresh.py`, chuyển test lát 2 và test cá chạy được ở cả v1.1 và v1.2 (`725f767`, PR #24). Làm vai Scrum (standup, nhắc mốc, dẫn retro).
- Tôi đã review (kèm link): rà `_pick_spawn` và `_initial_fish` của LeBao403 (phần cá thuộc B sở hữu), không phải sửa. *(Điền thêm PR hoặc diff khác đã đọc nếu có.)*
- AI sai ở đâu và tôi phát hiện thế nào: bản cá đầu viết theo nền v1.0 nên phải viết lại khi nền v1.1 gộp, phát hiện khi đọc `main` mới; AI quên đẩy file test lên cùng PR code, phát hiện khi kiểm lại `main`. Khi thêm hao tươi, một test của LeBao403 đỏ vì kỳ vọng viết lúc hao còn TODO; test headless của tôi lệch vì snapshot JSONL làm tròn 3 chữ số còn file kho thì không. Test xanh ngay lần đầu nên luôn phá thử code để chắc test bắt được lỗi.
- Điều tôi học được: nền chung của người khác đổi dưới chân mình nên phải fetch trước khi viết tiếp và kiểm lại `main` sau khi gộp PR; đổi schema kho nên làm theo kiểu hai phiên bản để `main` luôn xanh; ghi giả định luật vào `docs/clarify.md` thay vì tự tin là đúng.
