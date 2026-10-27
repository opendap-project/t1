"""Minimal S-expression reader and number/string formatting for KiCad files."""

from __future__ import annotations

import re

_TOKEN = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)


def parse(text):
    """Parse one S-expression into nested lists of strings (quoted strings unescaped)."""
    stack, cur, pos = [], [], 0
    while True:
        m = _TOKEN.match(text, pos)
        if not m:
            if text[pos:].strip():
                raise ValueError(f"unreadable S-expression at offset {pos}")
            break
        pos = m.end()
        if m.group(1):
            stack.append(cur)
            cur = []
        elif m.group(2):
            done, cur = cur, stack.pop()
            cur.append(done)
        elif m.group(3) is not None:
            cur.append(m.group(3).replace('\\"', '"').replace("\\\\", "\\"))
        else:
            cur.append(m.group(4))
    return cur[0]


def kids(node, name):
    return [k for k in node[1:] if isinstance(k, list) and k and k[0] == name]


def kid(node, name):
    for k in node[1:]:
        if isinstance(k, list) and k and k[0] == name:
            return k
    return None


def val(node, name, default=None):
    k = kid(node, name)
    return k[1] if k is not None and len(k) > 1 else default


def balanced(text, start):
    """Return the end index (exclusive) of the S-expression that opens at text[start]."""
    depth, i, instr = 0, start, False
    while i < len(text):
        c = text[i]
        if instr:
            if c == "\\":
                i += 1
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced S-expression")


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def n(v):
    v = round(float(v), 4)
    if v == 0:
        return "0"
    return f"{v:g}" if v != int(v) else str(int(v))
