# Skill: Question Generation — Pass 2

## Mục tiêu
Đọc file `_theory.json` từ Pass 1 và sinh ra **hệ thống câu hỏi** bám sát lý thuyết đã trích xuất. KHÔNG thay đổi hay bổ sung lý thuyết.

---

## Đầu vào
- File `<chương>_theory.json` — output từ Pass 1

## Đầu ra
Một JSON object duy nhất, KHÔNG có markdown fence, KHÔNG có giải thích thêm — chỉ JSON thuần.

---

## Schema output

```json
{
  "meta": {
    "subject": "<lấy từ theory file>",
    "chapter": "<lấy từ theory file>",
    "theory_source": "<tên file theory, ví dụ chuong_1_theory.json>",
    "extracted_at": "<YYYY-MM-DD>",
    "extractor_model": "<tên model đang dùng>",
    "pass": "questions"
  },
  "topics": [
    {
      "id": "t01",
      "questions": [
        {
          "type": "quiz",
          "question": "<câu hỏi trắc nghiệm rõ ràng, không mơ hồ>",
          "options": ["<A>", "<B>", "<C>", "<D>"],
          "answer": "<đúng 1 trong 4 options, copy nguyên văn>",
          "explanation": "<giải thích tại sao đáp án đúng và tại sao các đáp án còn lại sai>"
        },
        {
          "type": "flashcard",
          "front": "<khái niệm hoặc câu hỏi ngắn>",
          "back": "<định nghĩa hoặc giải thích ngắn gọn, đủ để nhớ>"
        },
        {
          "type": "essay",
          "question": "<câu hỏi tự luận mở, yêu cầu phân tích hoặc so sánh>"
        }
      ]
    }
  ]
}
```

---

## Quy tắc bắt buộc

### Số lượng câu hỏi theo độ phức tạp của topic

**Quiz:**
- Topic đơn giản (định nghĩa, liệt kê): 2–3 câu
- Topic trung bình (nguyên lý, cơ chế hoạt động): 3–5 câu
- Topic phức tạp (so sánh, phân tích, có công thức): 5–7 câu

**Flashcard:**
- Không giới hạn cứng — mỗi `key_point` → 1 flashcard, mỗi thuật ngữ quan trọng trong `definition` / `explanation` → 1 flashcard
- Bám theo nội dung thực tế, không đếm số lượng cơ học

**Essay:**
- Luôn 1–2 câu, không phụ thuộc độ phức tạp
- Nếu topic có `related_topics` → ưu tiên tạo câu so sánh liên chủ đề

### Về câu hỏi quiz
- Chỉ có 1 đáp án đúng trong 4 options
- Các đáp án sai phải **hợp lý và dễ nhầm** — không được quá hiển nhiên
- `answer` phải copy nguyên văn từ một trong 4 options, không viết lại
- `explanation` giải thích cả đáp án đúng lẫn lý do đáp án sai

### Về flashcard
- `front` — một khái niệm, thuật ngữ, hoặc câu hỏi What/Why/How ngắn
- `back` — câu trả lời súc tích, không quá 3 câu

### Về essay
- Yêu cầu **phân tích, so sánh, hoặc ứng dụng** — không phải chỉ nhớ thuộc
- Tốt: "So sánh X và Y về...", "Phân tích ưu nhược điểm của...", "Trong tình huống ... nên dùng ... vì sao?"
- Không dùng: "X là gì?", "Liệt kê các thành phần của X"

### Về nội dung
- **Toàn bộ câu hỏi phải bám sát `theory` của topic** — không hỏi kiến thức ngoài file
- Ưu tiên khai thác `common_mistakes` để tạo quiz có đáp án sai hợp lý
- Ưu tiên khai thác `key_points` để tạo flashcard

### Về cấu trúc JSON
- Output là JSON object thuần — KHÔNG có markdown fence, KHÔNG có text thừa
- `id` của mỗi topic phải **khớp chính xác** với `id` trong file theory
- Không thêm, không bỏ topic so với file theory
