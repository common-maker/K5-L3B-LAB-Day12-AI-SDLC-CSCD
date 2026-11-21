# TEAM

**Tên nhóm:** CSCD  **Số người:** 5  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Lê Bảo | `LeBao403` | `sim/gather` (Lát 1, Contract) | Integrator (giữ `docs/contracts/`, gắn tag) | `LaanLee` |
| Lê Hải Lân | `LaanLee` | `sim/gather` (Lát 2, Đóng gói) | Scrum / Release (canh giờ, standup) | `LeBao403` |
| Nguyễn Đức Lâm | `TheDLCrimson` | `sim/quan` (Lát 3, Day/Shop) | PO (hỏi Anh Năm, giữ `docs/clarify.md`) | `baoduy2048` |
| Bảo Duy | `baoduy2048` | `sim/quan` (Lát 4, QA Bench/Soak) | Hỗ trợ lát chậm & kiểm thử | `TheDLCrimson` |
| Nguyễn Hậu | `common-maker` | `client/ui`, `qa` | QA Lead (HUD, Smoke, Verification) | cả nhóm |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: Nhóm chat lớp (Zalo/Discord).
- Khi bất đồng về thiết kế: Mỗi bên nói 2 phút, chưa xong thì Integrator (`LeBao403`) quyết và ghi lý do vào `docs/clarify.md`.
- Khi ai đó trễ hoặc vướng quá 10 phút: Báo ngay trong kênh để người dự phòng vào giúp.
- Giờ standup giữa phase: Phút 15–20 và 45 mỗi phase, cập nhật `docs/standup.md`.
- Cách đọc code của nhau (tùy chọn): Đọc diff/PR của lát mình dự phòng trước khi merge vào `main`.
- Cách làm việc với Git: Nhánh ngắn `p<phase>/<handle>/<viec>`, chạy test xanh trước khi mở PR, merge thường (không squash).
