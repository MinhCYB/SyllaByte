# Skill: Theory Extraction — Pass 1

## Mục tiêu
Đọc toàn bộ nội dung file bài giảng (PDF, DOCX, PPTX) và trích xuất **phần lý thuyết** ra JSON theo schema chuẩn. KHÔNG tạo câu hỏi ở pass này.

---

## Đầu vào
- Một hoặc nhiều file bài giảng cùng chương (PDF / DOCX / PPTX)
- Tên môn học
- Tên / số chương

## Đầu ra
Một JSON object duy nhất, KHÔNG có markdown fence, KHÔNG có giải thích thêm — chỉ JSON thuần.

---

## Schema output

```json
{
  "meta": {
    "subject": "<tên môn học>",
    "chapter": "<tên hoặc số chương>",
    "source_files": ["<tên file 1>", "<tên file 2>"],
    "extracted_at": "<YYYY-MM-DD>",
    "extractor_model": "<tên model đang dùng>",
    "pass": "theory"
  },
  "topics": [
    {
      "id": "t01",
      "title": "<tên topic ngắn gọn>",
      "theory": {
        "definition": "<1 câu định nghĩa súc tích>",
        "explanation": "<giải thích đầy đủ 1-3 đoạn văn, viết lại từ nội dung slide, KHÔNG copy nguyên văn>",
        "examples": [
          "<ví dụ thực tế cụ thể liên quan đến topic>"
        ],
        "formulas": [
          {
            "name": "<tên công thức>",
            "expression": "<công thức dạng text thuần hoặc LaTeX inline>",
            "note": "<giải thích ý nghĩa các biến và khi nào dùng>"
          }
        ],
        "diagrams": [
          {
            "id": "d01",
            "title": "<tiêu đề diagram>",
            "type": "mermaid",
            "content": "<mermaid syntax hợp lệ, đã validate>",
            "source_page": 0,
            "caption": "<mô tả ngắn diagram thể hiện điều gì>"
          }
        ],
        "key_points": [
          "<điểm quan trọng cần ghi nhớ — mỗi điểm 1 câu>"
        ],
        "common_mistakes": [
          "<lỗi hay nhầm lẫn phổ biến của người học về topic này>"
        ],
        "related_topics": ["<id của topic liên quan, ví dụ t02>"]
      },
      "source": {
        "file": "<tên file chứa nội dung chính của topic này>",
        "page": 0
      },
      "is_extended": false,
      "extended_source_url": null
    }
  ]
}
```

---

## Quy tắc bắt buộc

### Về nội dung
- `definition` — đúng 1 câu, đủ để hiểu topic mà không cần đọc thêm
- `explanation` — viết lại bằng ngôn ngữ tự nhiên, dễ hiểu hơn slide gốc. KHÔNG copy nguyên văn từ slide
- `examples` — ưu tiên ví dụ thực tế, nếu slide không có thì tự suy luận từ context. Để array rỗng `[]` nếu không có ví dụ phù hợp
- `formulas` — chỉ điền nếu topic thực sự có công thức. Để array rỗng `[]` nếu không có
- `key_points` — tối thiểu 2, tối đa 5 điểm. Mỗi điểm là 1 câu hoàn chỉnh
- `common_mistakes` — suy luận từ nội dung và các điểm dễ nhầm lẫn. Để array rỗng `[]` nếu không xác định được
- `related_topics` — chỉ điền id của topic **trong cùng file output này**. Để array rỗng `[]` nếu chưa rõ

### Về diagrams
- Chỉ tạo diagram khi nội dung slide có sơ đồ, flowchart, hoặc quan hệ rõ ràng giữa các thành phần
- Ưu tiên `type: "mermaid"`. Dùng `type: "svg"` chỉ khi Mermaid không thể biểu diễn được
- **Validate Mermaid syntax trước khi output** — đảm bảo không có lỗi cú pháp
- Mermaid types được phép dùng: `flowchart`, `sequenceDiagram`, `erDiagram`, `classDiagram`, `timeline`
- `source_page` — điền số trang nếu biết, để `0` nếu không xác định được
- Để `diagrams: []` nếu không có sơ đồ phù hợp

### Về cấu trúc JSON
- Output là JSON object thuần — KHÔNG có markdown fence, KHÔNG có text giải thích trước hoặc sau
- Mỗi topic có `id` dạng `t01`, `t02`, ... theo thứ tự xuất hiện trong tài liệu
- `related_topics` chỉ tham chiếu `id` đã tồn tại trong cùng output
- Nếu tài liệu không đủ thông tin để điền một field, để giá trị rỗng (`""`, `[]`, `null`) — KHÔNG bịa thêm

### Về `is_extended`
- `false` — nội dung hoàn toàn từ file bài giảng
- `true` — có bổ sung kiến thức ngoài file (KHÔNG làm ở pass này, để `false` toàn bộ)
