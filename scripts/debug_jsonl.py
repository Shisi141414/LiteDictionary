#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速诊断 JSONL: 打印总行数与每行首个字符/长度/解析错误。"""
import json
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    lines = f.readlines()
print(f"总行数: {len(lines)}")
for i, line in enumerate(lines, 1):
    s = line.rstrip("\n")
    try:
        obj = json.loads(s)
        keys = sorted(obj.keys())
        print(f"行{i}: len={len(s)} keys={keys}")
    except json.JSONDecodeError as e:
        print(f"行{i}: len={len(s)} JSON错误: {e} 首40字符={s[:40]!r}")
