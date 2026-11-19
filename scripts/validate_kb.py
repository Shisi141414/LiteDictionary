#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_kb.py — 知识库质量终检。

用法:
    python3 validate_kb.py kb_math.sqlite [--subject math]

检查项:
    1. 表结构完整 (kb_entries 及 6 个必需字段)
    2. subject 字段一致性
    3. term 非空且库内唯一
    4. term 含中英文 (含 "|" 分隔)
    5. aliases / tags 为合法 JSON 数组
    6. definition_brief ≤ 100 字
    7. definition_detail 非空且 ≥ 80 字
    8. LaTeX 定界符配对 ($ 偶数, $$ 成对)
    9. 文件大小 ≤ 30MB
"""
import argparse
import json
import os
import re
import sqlite3
import sys

REQUIRED_FIELDS = {"term", "aliases", "definition_brief",
                   "definition_detail", "subject", "tags"}


def check_delimiters(text: str) -> str | None:
    """检查 $ / $$ 定界符配对。"""
    n_dollar = text.count("$")
    if n_dollar % 2 != 0:
        return "$ 个数为奇数"
    # 把 $$ 对消耗掉后剩单 $ 应为偶数 (已由总数偶数保证)
    if text.count("$$") * 2 > n_dollar:
        return "$$ 配对异常"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--subject")
    args = ap.parse_args()

    errors, warns = [], []
    conn = sqlite3.connect(args.db)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(kb_entries)")}
    if not REQUIRED_FIELDS <= cols:
        print(f"[失败] 缺少必需字段: {REQUIRED_FIELDS - cols}")
        sys.exit(1)

    rows = conn.execute(
        "SELECT id, term, aliases, definition_brief, definition_detail, "
        "subject, tags FROM kb_entries").fetchall()
    seen_terms = {}
    for (rid, term, aliases, brief, detail, subject, tags) in rows:
        ctx = f"id={rid} [{term}]"
        if not term or not term.strip():
            errors.append(f"{ctx} term 为空")
            continue
        if "|" not in term:
            warns.append(f"{ctx} term 未含中英文分隔符 '|'")
        if term in seen_terms:
            errors.append(f"{ctx} term 重复 (首见 id={seen_terms[term]})")
        else:
            seen_terms[term] = rid
        for k, v in (("aliases", aliases), ("tags", tags)):
            try:
                parsed = json.loads(v)
                if not isinstance(parsed, list):
                    errors.append(f"{ctx} {k} 不是 JSON 数组")
            except json.JSONDecodeError as e:
                errors.append(f"{ctx} {k} JSON 解析失败: {e}")
        nb = len(brief or "")
        if nb == 0:
            errors.append(f"{ctx} brief 为空")
        elif nb > 100:
            warns.append(f"{ctx} brief 超长 ({nb} 字)")
        nd = len(detail or "")
        if nd < 80:
            warns.append(f"{ctx} detail 过短 ({nd} 字)")
        if args.subject and subject != args.subject:
            errors.append(f"{ctx} subject={subject!r} 与预期 {args.subject!r} 不符")
        d = check_delimiters(detail or "")
        if d:
            errors.append(f"{ctx} detail LaTeX {d}")

    size_mb = os.path.getsize(args.db) / 1024 / 1024
    print(f"条目总数: {len(rows)}")
    print(f"文件大小: {size_mb:.2f} MB (上限 30MB)")
    print(f"错误: {len(errors)}, 警告: {len(warns)}")
    for e in errors[:30]:
        print(f"  [E] {e}")
    for w in warns[:30]:
        print(f"  [W] {w}")
    if len(errors) > 30:
        print(f"  ... 其余 {len(errors)-30} 条错误省略")
    conn.close()
    sys.exit(1 if errors or size_mb > 30 else 0)


if __name__ == "__main__":
    main()
