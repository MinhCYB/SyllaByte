import json
from pathlib import Path
from datetime import date


def _load_json(filepath):
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def _save_json(data, filepath):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _chapter_key(filename):
    """Lấy chapter key từ tên file, bỏ _theory / _questions suffix."""
    name = Path(filename).stem
    for suffix in ("_theory", "_questions"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def merge_chapter(theory_path, questions_path):
    """
    Merge 1 cặp theory + questions thành processed chapter JSON.
    Trả về dict processed chapter hoặc raise nếu id không khớp.
    """
    theory = _load_json(theory_path)
    questions = _load_json(questions_path)

    # Index questions theo topic id
    questions_map = {t["id"]: t.get("questions", []) for t in questions["topics"]}

    topics_out = []
    for topic in theory["topics"]:
        tid = topic["id"]
        merged_topic = {
            "id": tid,
            "title": topic["title"],
            "theory": topic["theory"],
            "questions": questions_map.get(tid, []),
            "sources": [topic["source"]] if topic.get("source") else [],
            "is_extended": topic.get("is_extended", False),
            "extended_source_url": topic.get("extended_source_url"),
        }
        topics_out.append(merged_topic)

    meta = theory["meta"]
    return {
        "meta": {
            "subject": meta["subject"],
            "chapter_id": _chapter_key(theory_path),
            "title": meta["chapter"],
            "updated_at": str(date.today()),
        },
        "topics": topics_out,
    }


def merge_subject(raw_subject_dir, processed_subject_dir):
    """
    Merge toàn bộ các cặp theory/questions trong raw/<subject>/
    thành processed/<subject>/index.json + chuong_x.json
    """
    raw_subject_dir = Path(raw_subject_dir)
    processed_subject_dir = Path(processed_subject_dir)

    # Tìm tất cả theory files → xác định danh sách chapters
    theory_files = sorted(raw_subject_dir.glob("*_theory.json"))
    if not theory_files:
        print(f"  Không tìm thấy *_theory.json trong {raw_subject_dir}")
        return

    chapters_meta = []
    errors = []

    for theory_path in theory_files:
        chapter_key = _chapter_key(theory_path)
        questions_path = raw_subject_dir / f"{chapter_key}_questions.json"

        if not questions_path.exists():
            errors.append(f"  Thiếu questions file: {questions_path.name}")
            continue

        try:
            chapter_data = merge_chapter(theory_path, questions_path)
        except Exception as e:
            errors.append(f"  Lỗi merge {chapter_key}: {e}")
            continue

        # Lưu processed chapter
        out_path = processed_subject_dir / f"{chapter_key}.json"
        _save_json(chapter_data, out_path)

        topic_count = len(chapter_data["topics"])
        question_count = sum(len(t["questions"]) for t in chapter_data["topics"])
        chapters_meta.append({
            "id": chapter_key,
            "title": chapter_data["meta"]["title"],
            "file": f"{chapter_key}.json",
            "topic_count": topic_count,
            "question_count": question_count,
        })
        print(f"  ✓ {chapter_key} ({topic_count} topics, {question_count} câu hỏi)")

    if errors:
        for e in errors:
            print(e)

    if not chapters_meta:
        print(f"  Không có chapter nào được merge thành công.")
        return

    # Lấy subject name từ file theory đầu tiên
    first_theory = _load_json(theory_files[0])
    subject = first_theory["meta"]["subject"]
    subject_id = raw_subject_dir.name

    # Lưu index.json
    index_data = {
        "meta": {
            "subject": subject,
            "subject_id": subject_id,
            "updated_at": str(date.today()),
        },
        "chapters": chapters_meta,
    }
    _save_json(index_data, processed_subject_dir / "index.json")
    print(f"  ✓ index.json ({len(chapters_meta)} chapters)")
