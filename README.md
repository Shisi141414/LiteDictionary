# 轻量级学科知识库

面向中国大学本科生的学科术语知识库。词条覆盖本科课程的核心概念、定理、方法、人物与学科总览，中英对照，释义原创（基于公开教材知识体系的学科标准术语组织，未包含受版权保护的材料）。

## 当前内容（21 个学科，3415 条）

| 数据库                       | 学科     | 词条数 | 内容构成                                                                                                                                                                                                                                                 |
| ---------------------------- | -------- | ------ |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `kb_math.sqlite`             | 数学     | 1065   | 数学分析、高等代数、解析几何、常微分方程、概率统计、复变函数（基础+深化）、张量分析（含恒等式与表示定理）、拓扑学、微分几何、泛函分析与变分法、偏微分方程、抽象代数、随机过程、实变函数、线性代数与数值代数、基础核心概念（裸概念+学科总览）、数学人物志 |
| `kb_physics.sqlite`          | 物理     | 424    | 力学、热学与分子动理论、电磁学（含边值问题与方法）、光学、近代物理、统计物理、量子力学、物理人物志                                                                                                                                                       |
| `kb_chemistry.sqlite`        | 化学     | 230    | 无机、反应原理、有机、分析与物化、化学人物志                                                                                                                                                                                                             |
| `kb_mechanics.sqlite`        | 力学     | 174    | 理论力学、分析力学与振动、材料力学基础、力学人物志                                                                                                                                                                                                       |
| `kb_biology.sqlite`          | 生物学   | 180    | 普通生物学、生化与分子生物学、核心概念补充、生物学人物志                                                                                                                                                                                                 |
| `kb_computer_science.sqlite` | 计算机   | 180    | 计算机基础与数据结构、操作系统网络数据库、程序设计软工与 AI、计算机人物志                                                                                                                                                                                |
| `kb_philosophy.sqlite`       | 哲学     | 140    | 哲学基础、核心概念补充（先验/后验/奥卡姆剃刀等）、哲学人物志（中西 40 人）                                                                                                                                                                               |
| `kb_aesthetics.sqlite`       | 美学     | 100    | 美学基础、核心概念补充（格式塔/通感/审美距离等）                                                                                                                                                                                                         |
| `kb_literature.sqlite`       | 文学     | 80     | 文学理论与文学史、文学人物志                                                                                                                                                                                                                             |
| `kb_economics.sqlite`        | 经济学   | 80     | 微观宏观核心、经济学人物志                                                                                                                                                                                                                               |
| `kb_history.sqlite`          | 历史学   | 80     | 史学理论、中国史与世界史、史学人物志                                                                                                                                                                                                                     |
| 其余 12 学科                 | 各 56–75 | 1011   | 地理、心理、政治、社会、语言、美术、音乐、舞蹈、热力学、材料学各含基础批+人物志                                                                                                                                                                          |

单库均 ≤1.5 MB（上限 30MB）。人物志已覆盖全部学科（每科 6–40 人）。

## 数据结构

主表 `kb_entries`：`id`、`term`（`中文|English`）、`aliases`（JSON 数组）、`definition_brief`、`definition_detail`、`subject`、`tags`（JSON 数组）。

### 概念词条格式

`definition_brief`（100~220 字符）：

```
**定义**：核心定义（含主公式）。
**性质**：要点1；要点2；要点3。
```

`definition_detail`（200~400 字）：

```
概念名：
**定义**：单句定义；多角度时用无序列表：
- 狭义：……；
- 广义：……。
**性质**：
1. ……；
2. ……；
3. ……。
```

### 人物词条格式

```
**人物中文全名**（English Name，生卒年），国籍，身份定位。
* **主要成果**：……；
* **主要著作**：《……》（年份）、……；
* **主要荣誉与影响**：……。
```

跨学科人物（如马克思、韦伯）按学科分库收录、定位语注明侧重。

完整规范见 `docs/格式规范.md`（v4）。

## 使用示例

```python
import sqlite3, json
conn = sqlite3.connect("kb_math.sqlite")
rows = conn.execute("SELECT term, definition_brief FROM kb_entries WHERE term LIKE '%收敛%'").fetchall()
term, brief, detail = conn.execute(
    "SELECT term, definition_brief, definition_detail FROM kb_entries WHERE term='极限|Limit'").fetchone()
```

检索提示：概念可用裸词命中（极限、收敛、积分、概率……均有伞形条目）；限定形态（数列的极限、条件收敛、二重积分）各有专条。

## 目录结构

```
轻量级学科知识库/
├── README.md、docs/格式规范.md
├── kb_<学科>.sqlite × 21        # 构建产物
├── scripts/                      # build_kb / validate_kb / debug_jsonl
└── data/<学科>/                  # JSONL 源数据（60+ 文件，3415 条）
```

## 扩展

加密流程：在 `data/<学科>/` 追加 `NN_主题.jsonl`（按 `docs/格式规范.md`）→ `python3 scripts/build_kb.py --subject <code> --src data/<code> --out /tmp/kb_<code>.sqlite` → `validate_kb.py` 终检 → 拷贝入库。注意 SQLite 需在本地磁盘构建后拷贝。

学科代码：math, physics, chemistry, mechanics, thermodynamics, materials_science, computer_science, economics, literature, philosophy, aesthetics, fine_arts, dance, music, psychology, biology, geography, politics, history, linguistics, sociology。
