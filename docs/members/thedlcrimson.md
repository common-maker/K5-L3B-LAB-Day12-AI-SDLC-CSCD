# TheDLCrimson - phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Lát 3 khách đến, giữ chỗ, kiên nhẫn ([e15f865](https://github.com/common-maker/K5-L3B-LAB-Day12-AI-SDLC-CSCD/commit/e15f865), test [a62e962](https://github.com/common-maker/K5-L3B-LAB-Day12-AI-SDLC-CSCD/commit/a62e962)).
  - Lọc món theo kế hoạch, kiểm khối `day` ([49c0eaf](https://github.com/common-maker/K5-L3B-LAB-Day12-AI-SDLC-CSCD/commit/49c0eaf)).
  - `DaySession` và Shop ([041314c](https://github.com/common-maker/K5-L3B-LAB-Day12-AI-SDLC-CSCD/commit/041314c)).
  - Giữ chỗ theo id cá thể khi hàng ươn ([63dd853](https://github.com/common-maker/K5-L3B-LAB-Day12-AI-SDLC-CSCD/commit/63dd853), test [2cbbbca](https://github.com/common-maker/K5-L3B-LAB-Day12-AI-SDLC-CSCD/commit/2cbbbca)).
  - PO: `docs/clarify.md`, 24 dòng. Phase 4: `DaySession` chạy quá 5 Ngày cho soak.
- Tôi đã review (kèm link): diff lát 4 của `baoduy2048` ([PR #3](https://github.com/common-maker/K5-L3B-LAB-Day12-AI-SDLC-CSCD/pull/3)). Tôi tìm xung đột với `main`, chạy 69 test trên bản gộp.
- AI sai ở đâu và tôi phát hiện thế nào:
  - AI làm lại hợp đồng v1.1 trùng nền của `LeBao403`, nên tôi đóng 3 PR (#5, #7, #9).
  - `DaySession` chỉ lập chỉ mục `day_plan[day - 1]`, vỡ ở Ngày 6. Soak 10 Ngày của `LeBao403` bắt được; tôi tái hiện bằng đúng lệnh đó, sửa bằng `% 5` kèm test.
- Điều tôi học được: đọc `main` và PR đang mở trước khi viết để khỏi làm trùng; chạy tích hợp thật vì test từng lát bỏ sót lỗi nhiều Ngày.
