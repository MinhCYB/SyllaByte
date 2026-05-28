import json
from pathlib import Path


THEORY_REQUIRED = {"meta", "topics"}
QUESTIONS_REQUIRED = {"meta", "topics"}
META_THEORY_REQUIRED = {"subject", "chapter", "source_files", "extracted_at", "pass"}
META_QUESTIONS_REQUIRED = {"subject", "chapter", "theory_source", "extracted_at", "pass"}
TOPIC_THEORY_REQUIRED = {"id", "title", "theory", "source"}
TOPIC_QUESTIONS_REQUIRED = {"id", "questions"}
THEORY_FIELDS_REQUIRED = {"definition", "explanation", "key_points"}
QUESTION_TYPES = {"quiz", "flashcard", "essay"}


def _err(path, msg):
    return f"[{path}] {msg}"


def validate_theory(data, filepath):
    errors = []
    fp = str(filepath)

    missing = THEORY_REQUIRED - data.keys()
    if missing:
        errors.append(_err(fp, f"Thiếu field gốc: {missing}"))
        return errors

    meta = data["meta"]
    missing_meta = META_THEORY_REQUIRED - meta.keys()
    if missing_meta:
        errors.append(_err(fp, f"meta thiếu: {missing_meta}"))
    if meta.get("pass") != "theory":
        errors.append(_err(fp, f"meta.pass phải là 'theory', hiện là '{meta.get('pass')}'"))

    if not isinstance(data["topics"], list) or len(data["topics"]) == 0:
        errors.append(_err(fp, "topics phải là array và không rỗng"))
        return errors

    ids_seen = set()
    for i, topic in enumerate(data["topics"]):
        prefix = f"topics[{i}]"
        missing_topic = TOPIC_THEORY_REQUIRED - topic.keys()
        if missing_topic:
            errors.append(_err(fp, f"{prefix} thiếu: {missing_topic}"))
            continue

        tid = topic["id"]
        if tid in ids_seen:
            errors.append(_err(fp, f"{prefix} id trùng: '{tid}'"))
        ids_seen.add(tid)

        theory = topic.get("theory", {})
        missing_theory = THEORY_FIELDS_REQUIRED - theory.keys()
        if missing_theory:
            errors.append(_err(fp, f"{prefix}.theory thiếu: {missing_theory}"))

        if not isinstance(theory.get("key_points", []), list):
            errors.append(_err(fp, f"{prefix}.theory.key_points phải là array"))

        for j, d in enumerate(theory.get("diagrams", [])):
            if d.get("type") not in ("mermaid", "svg", None):
                errors.append(_err(fp, f"{prefix}.theory.diagrams[{j}].type không hợp lệ"))
            if not d.get("content"):
                errors.append(_err(fp, f"{prefix}.theory.diagrams[{j}].content rỗng"))

    return errors


def validate_questions(data, filepath):
    errors = []
    fp = str(filepath)

    missing = QUESTIONS_REQUIRED - data.keys()
    if missing:
        errors.append(_err(fp, f"Thiếu field gốc: {missing}"))
        return errors

    meta = data["meta"]
    missing_meta = META_QUESTIONS_REQUIRED - meta.keys()
    if missing_meta:
        errors.append(_err(fp, f"meta thiếu: {missing_meta}"))
    if meta.get("pass") != "questions":
        errors.append(_err(fp, f"meta.pass phải là 'questions', hiện là '{meta.get('pass')}'"))

    if not isinstance(data["topics"], list) or len(data["topics"]) == 0:
        errors.append(_err(fp, "topics phải là array và không rỗng"))
        return errors

    for i, topic in enumerate(data["topics"]):
        prefix = f"topics[{i}]"
        missing_topic = TOPIC_QUESTIONS_REQUIRED - topic.keys()
        if missing_topic:
            errors.append(_err(fp, f"{prefix} thiếu: {missing_topic}"))
            continue

        for j, q in enumerate(topic.get("questions", [])):
            qprefix = f"{prefix}.questions[{j}]"
            qtype = q.get("type")
            if qtype not in QUESTION_TYPES:
                errors.append(_err(fp, f"{qprefix}.type không hợp lệ: '{qtype}'"))
                continue

            if qtype == "quiz":
                if not q.get("question"):
                    errors.append(_err(fp, f"{qprefix} thiếu question"))
                opts = q.get("options", [])
                if not isinstance(opts, list) or len(opts) != 4:
                    errors.append(_err(fp, f"{qprefix} options phải có đúng 4 phần tử"))
                if q.get("answer") not in opts:
                    errors.append(_err(fp, f"{qprefix} answer không khớp với options"))

            elif qtype == "flashcard":
                if not q.get("front") or not q.get("back"):
                    errors.append(_err(fp, f"{qprefix} thiếu front hoặc back"))

            elif qtype == "essay":
                if not q.get("question"):
                    errors.append(_err(fp, f"{qprefix} thiếu question"))

    return errors


def validate_file(filepath):
    filepath = Path(filepath)
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [_err(str(filepath), f"JSON không hợp lệ: {e}")]
    except FileNotFoundError:
        return [_err(str(filepath), "File không tồn tại")]

    pass_type = data.get("meta", {}).get("pass")
    if pass_type == "theory":
        return validate_theory(data, filepath)
    elif pass_type == "questions":
        return validate_questions(data, filepath)
    else:
        return [_err(str(filepath), f"meta.pass không xác định: '{pass_type}'")]


def validate_subject_raw(raw_subject_dir):
    raw_subject_dir = Path(raw_subject_dir)
    all_errors = {}
    for f in sorted(raw_subject_dir.glob("*.json")):
        errors = validate_file(f)
        if errors:
            all_errors[f.name] = errors
    return all_errors
