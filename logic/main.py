"""
Cách dùng:
  python logic/main.py
  python logic/main.py --subject mang_may_tinh
  python logic/main.py --validate-only
  python logic/main.py --subject mang_may_tinh --validate-only
"""
import argparse
import json
import sys
from pathlib import Path

# Đảm bảo import được khi chạy từ thư mục gốc dự án
sys.path.insert(0, str(Path(__file__).parent))

from validate import validate_subject_raw
from merge import merge_subject

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def get_subjects(subject_name=None):
    if subject_name:
        path = RAW_DIR / subject_name
        if not path.exists():
            print(f"Không tìm thấy: {path}")
            sys.exit(1)
        return [path]
    return sorted(p for p in RAW_DIR.iterdir() if p.is_dir())


def run_validate(subject_dirs):
    total_errors = 0
    for subject_dir in subject_dirs:
        print(f"\n── Validate: {subject_dir.name}")
        errors = validate_subject_raw(subject_dir)
        if not errors:
            print("  ✓ Không có lỗi")
        else:
            for filename, errs in errors.items():
                for e in errs:
                    print(f"  ✗ {e}")
                    total_errors += 1
    return total_errors


def run_merge(subject_dirs):
    for subject_dir in subject_dirs:
        print(f"\n── Merge: {subject_dir.name}")
        processed_subject_dir = PROCESSED_DIR / subject_dir.name
        merge_subject(subject_dir, processed_subject_dir)


def write_subjects_json():
    """
    Scan toàn bộ data/processed/<môn>/index.json và ghi lại
    data/processed/subjects.json — không cần tạo tay.
    """
    subjects = []
    for index_path in sorted(PROCESSED_DIR.glob("*/index.json")):
        try:
            with open(index_path, encoding="utf-8") as f:
                data = json.load(f)
            subject_id = data["meta"]["subject_id"]
            subject_name = data["meta"]["subject"]
            subjects.append({"id": subject_id, "name": subject_name})
        except Exception as e:
            print(f"  Bỏ qua {index_path}: {e}")

    out_path = PROCESSED_DIR / "subjects.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(subjects, f, ensure_ascii=False, indent=2)

    print(f"\n── subjects.json: {len(subjects)} môn")
    for s in subjects:
        print(f"  · {s['id']} — {s['name']}")


def main():
    parser = argparse.ArgumentParser(description="SyllaByte — Pipeline xử lý JSON")
    parser.add_argument("--subject", metavar="TÊN", help="Chỉ xử lý một môn cụ thể (mặc định: tất cả)")
    parser.add_argument("--validate-only", action="store_true", help="Chỉ validate, không merge")
    args = parser.parse_args()

    subject_dirs = get_subjects(args.subject)

    if not subject_dirs:
        print("Không tìm thấy môn học nào trong data/raw/")
        sys.exit(1)

    total_errors = run_validate(subject_dirs)

    if total_errors > 0:
        print(f"\n✗ Có {total_errors} lỗi — dừng lại, không merge.")
        print("  Sửa các file raw JSON và chạy lại.")
        sys.exit(1)

    if args.validate_only:
        print("\n✓ Validate xong, không merge (--validate-only).")
        return

    run_merge(subject_dirs)

    # Tự động cập nhật subjects.json sau mỗi lần merge
    write_subjects_json()

    print("\n✓ Hoàn tất.")


if __name__ == "__main__":
    main()