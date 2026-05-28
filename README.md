# SyllaByte

Tool học tập cá nhân: trích xuất nội dung bài giảng (PDF / DOCX / PPTX) thành JSON, sau đó render thành web app tương tác để ôn lý thuyết và luyện tập.

Không cần cài thêm thư viện nào ngoài Python stdlib. Tất cả logic xử lý nằm trong `logic/`. Web app là một file HTML duy nhất, có thể host miễn phí trên GitHub Pages.

---

## Cấu trúc thư mục

```
SyllaByte/
  data/
    raw/
      <môn>/
        <chương>_theory.json
        <chương>_questions.json
    processed/
      subjects.json
      <môn>/
        index.json
        <chương>.json
  logic/
    main.py
    merge.py
    validate.py
  prompts/
    extraction_theory_skill.md
    extraction_questions_skill.md
  index.html
  README.md
```

---

## Luồng hoạt động

```
[File bài giảng: PDF / DOCX / PPTX]
        |
        | Bước 1 — Trích xuất lý thuyết
        v
Gemini + extraction_theory_skill.md
        |
        v
SyllaByte/data/raw/<môn>/<chương>_theory.json
        |
        | Bước 2 — Sinh câu hỏi
        v
Gemini + extraction_questions_skill.md   (input = theory JSON)
        |
        v
SyllaByte/data/raw/<môn>/<chương>_questions.json
        |
        | Bước 3 — Merge và validate
        v
python logic/main.py --subject <môn>
        |
        v
SyllaByte/data/processed/<môn>/index.json
SyllaByte/data/processed/<môn>/<chương>.json
        |
        | Bước 4 — Xem web app
        v
index.html   (đọc processed/ qua fetch, không cần server riêng)
```

---

## Hướng dẫn sử dụng

### Bước 1 — Trích xuất lý thuyết

Mở Gemini (hoặc bất kỳ model nào hỗ trợ file upload). Upload file bài giảng, sau đó dán toàn bộ nội dung file `prompts/extraction_theory_skill.md` vào prompt.

Model sẽ trả về một JSON. Lưu kết quả vào:

```
data/raw/<tên môn>/<tên chương>_theory.json
```

Ví dụ: `data/raw/mang_may_tinh/chuong_1_theory.json`

Tên thư mục môn dùng chữ thường, không dấu, thay khoảng trắng bằng dấu gạch dưới.


### Bước 2 — Sinh câu hỏi

Trong cùng cuộc hội thoại với Gemini (để giữ context về bài giảng), dán nội dung file `prompts/extraction_questions_skill.md` vào prompt, kèm theo nội dung của file theory JSON vừa tạo ở bước 1.

Lưu kết quả vào:

```
data/raw/<tên môn>/<tên chương>_questions.json
```

Ví dụ: `data/raw/mang_may_tinh/chuong_1_questions.json`

Lặp lại bước 1 và 2 cho từng chương của từng môn.


### Bước 3 — Merge và validate

Sau khi đã có đủ file theory và questions cho một môn, chạy lệnh sau từ thư mục gốc của project:

```bash
python logic/main.py --subject <tên môn>
```

Ví dụ:

```bash
python logic/main.py --subject mang_may_tinh
```

Script sẽ:
- Validate format của tất cả file raw JSON trong thư mục môn đó
- Merge theory và questions theo `topic.id`
- Ghi kết quả ra `data/processed/<môn>/index.json` và `data/processed/<môn>/<chương>.json`
- Tự động cập nhật `data/processed/subjects.json` bằng cách scan toàn bộ thư mục `processed/`

Nếu có lỗi validate, script sẽ in ra tên file và trường bị thiếu. Sửa trực tiếp trong file raw rồi chạy lại.

`subjects.json` không cần tạo tay — script sinh lại file này sau mỗi lần chạy, kể cả khi thêm môn mới.


### Bước 4 — Chạy web app

File `index.html` dùng `fetch()` để đọc JSON, nên cần chạy qua HTTP server. Không mở trực tiếp bằng `file://`.

**Local:**

```bash
cd SyllaByte
python -m http.server 8000
```

Sau đó mở trình duyệt tại `http://localhost:8000`.

**GitHub Pages:**

1. Push toàn bộ thư mục `SyllaByte/` lên repository GitHub.
2. Vào Settings > Pages > chọn source là thư mục gốc (`/ (root)`).
3. GitHub sẽ cấp một URL dạng `https://<username>.github.io/<repo>/`.

---

## Tính năng của web app

**Tab Lý thuyết** — hiển thị toàn bộ nội dung lý thuyết của mỗi topic: định nghĩa, giải thích, điểm quan trọng, công thức, sơ đồ Mermaid, ví dụ, lỗi thường gặp. Có nút đánh dấu đã ôn từng topic.

**Tab Luyện tập** — ba loại câu hỏi cho mỗi topic:
- Quiz: chọn đáp án, hiện giải thích sau khi trả lời
- Flashcard: lật thẻ để xem đáp án
- Tự luận: ô nhập câu trả lời tự do

**Tab Thống kê** — tổng quan số topic, câu hỏi, sơ đồ và phần trăm hoàn thành của chương đang xem.

Tiến độ được lưu vào `localStorage` của trình duyệt, không mất khi reload trang.

---

## Yêu cầu

- Python 3.8 trở lên (stdlib thuần, không cần cài thêm gì)
- Trình duyệt hiện đại (Chrome, Firefox, Edge, Safari)
- Tài khoản Gemini hoặc model AI có khả năng xử lý file