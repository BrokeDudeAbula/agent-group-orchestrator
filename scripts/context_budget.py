#!/usr/bin/env python3
"""热记忆和 worker 输出的共享上限。

校验脚本用这些上限拒绝超长文件。归档脚本用更低的滚动阈值，
使 ledger 在触达校验上限之前就被收成摘要加近期尾部。
"""

from __future__ import annotations


WORKER_OUTPUT_MAX_LINES = 120
WORKER_OUTPUT_MAX_CHARS = 6000

STATE_MAX_LINES = 80
STATE_MAX_CHARS = 4000

PROJECT_FACTS_MAX_LINES = 80
PROJECT_FACTS_MAX_CHARS = 4000

LEDGER_INDEX_MAX_LINES = 40
LEDGER_INDEX_MAX_CHARS = 2500

# 校验允许的热 ledger 上限。超过后 strict 校验失败。
LEDGER_HOT_MAX_LINES = 80
LEDGER_HOT_MAX_CHARS = 6000

# compact_memory.py 开始滚动的阈值，低于校验上限。
LEDGER_ROLL_LINES = 48
LEDGER_ROLL_CHARS = 3500
LEDGER_RECENT_ROWS = 8
LEDGER_RECENT_SECTIONS = 4
LEDGER_SUMMARY_MAX_LINES = 8

LEDGER_NAMES = (
    "TASK_LEDGER.md",
    "PROGRESS_LEDGER.md",
    "DECISIONS.md",
    "RISKS.md",
)
