#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_kb.py — 将 JSONL 源数据打包为单文件 SQLite 知识库。

用法:
    python3 build_kb.py --subject math --src data/math --out kb_math.sqlite

JSONL 每行一个对象, 字段:
    term               中英文术语, 格式 "中文|English"
    aliases            JSON 数组 (别名/缩写/常见误写)
    definition_brief   简明释义, ≤100 字
    definition_detail  完整解释, 可含 LaTeX $..$ / $$..$$
    tags               JSON 数组

产物表结构 (kb_entries):
    id, term, aliases, definition_brief, definition_detail, subject, tags
附加:
    fts_entries (FTS5 全文索引, 若可用) — 支持高效中文/英文检索
"""
import argparse
import json
import os
import sqlite3
import sys

SCHEMA = """
CREATE TABLE IF NOT EXISTS kb_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    aliases TEXT NOT NULL,
    definition_brief TEXT NOT NULL,
    definition_detail TEXT NOT NULL,
    subject TEXT NOT NULL,
    tags TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_kb_subject ON kb_entries(subject);
CREATE INDEX IF NOT EXISTS idx_kb_term ON kb_entries(term);
"""


def parse_line(line: str, src: str, lineno: int):
    """解析并预校验一行 JSONL; 返回 tuple 或抛异常。"""
    obj = json.loads(line)
    missing = [k for k in
               ("term", "aliases", "definition_brief",
                "definition_detail", "tags")
               if k not in obj]
    if missing:
        raise ValueError(f"缺少字段: {missing}")
    if not str(obj["term"]).strip():
        raise ValueError("term 为空")
    for k in ("aliases", "tags"):
        if not isinstance(obj[k], list):
            obj[k] = json.loads(obj[k])  # 允许已字符串化的数组
    return (obj["term"].strip(),
            json.dumps(obj["aliases"], ensure_ascii=False),
            obj["definition_brief"].strip(),
            obj["definition_detail"].strip(),
            json.dumps(obj["tags"], ensure_ascii=False))


def build_fts(conn: sqlite3.Connection) -> bool:
    """尝试创建 FTS5 全文索引; 不可用时返回 False。"""
    try:
        conn.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_entries USING fts5(
            term, aliases, brief, detail, tags,
            content='kb_entries', content_rowid='id',
            tokenize='unicode61'
        );
        """)
        conn.execute("""
        INSERT INTO fts_entries(fts_entries)
        VALUES('rebuild');
        """)
        return True
    except sqlite3.OperationalError:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True,
                    help="学科代码, 如 math/physics/mechanics")
    ap.add_argument("--src", required=True, help="JSONL 目录")
    ap.add_argument("--out", required=True, help="输出 sqlite 路径")
    args = ap.parse_args()

    if os.path.exists(args.out):
        os.remove(args.out)

    files = sorted(f for f in os.listdir(args.src) if f.endswith(".jsonl"))
    if not files:
        print(f"[错误] {args.src} 下没有 .jsonl 文件", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(args.out)
    conn.executescript(SCHEMA)

    total, bad = 0, 0
    for fn in files:
        path = os.path.join(args.src, fn)
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = parse_line(line, fn, lineno)
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"[跳过] {fn}:{lineno} — {e}", file=sys.stderr)
                    bad += 1
                    continue
                conn.execute(
                    "INSERT INTO kb_entries"
                    "(term,aliases,definition_brief,definition_detail,"
                    "tags,subject) VALUES (?,?,?,?,?,?)",
                    row + (args.subject,))
                total += 1
    conn.commit()

    fts_ok = build_fts(conn)
    conn.commit()
    try:
        conn.execute("VACUUM")
    except sqlite3.OperationalError:
        pass
    conn.close()

    size_mb = os.path.getsize(args.out) / 1024 / 1024
    print(f"[完成] {args.out}: {total} 条入库, {bad} 条格式错误被跳过, "
          f"文件 {size_mb:.2f} MB, FTS5={'启用' if fts_ok else '不可用'}")
    if size_mb > 30:
        print("[警告] 超过 30MB 上限!", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
