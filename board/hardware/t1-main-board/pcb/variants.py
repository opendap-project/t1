"""KiCad 10 design-variant data on the board, copied from the schematic (pure Python).

The generator writes each part's per-variant data into its schematic symbol instances
(`(variant (name "production") (dnp yes) (field (name "Value") (value "0 Ω")) …)`, from
../variants/*.toml). KiCad keeps the same data on the board: a `(variants …)` list at the root and
the same `(variant …)` entries inside each footprint, so `kicad-cli … --variant <name>` fab outputs
read the variant's population. build.py runs this after the board is written; the board takes
exactly the schematic's data, so a rerun with the same inputs writes the same bytes."""

from __future__ import annotations

import glob
import os
import re


def _close(text, i):
    """Index just past the S-expression that opens at text[i] == '('."""
    depth, j, quoted = 0, i, False
    while j < len(text):
        c = text[j]
        if quoted:
            if c == "\\":
                j += 1
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError("unbalanced S-expression at %d" % i)


REF_RE = re.compile(r'\(reference "([^"]+)"\)')


def sch_variants(texts):
    """ref -> {variant name: entry text} from the instance paths of schematic texts. A multi-unit
    part carries the same entry on every unit; the first one read is kept."""
    out = {}
    for text in texts:
        for m in REF_RE.finditer(text):
            ref = m.group(1)
            if ref.startswith("#"):
                continue
            path_open = text.rfind("(path ", 0, m.start())
            end = _close(text, path_open)
            i = m.end()
            while True:
                k = text.find("(variant ", i, end)
                if k < 0:
                    break
                e = _close(text, k)
                entry = text[k:e]
                name = re.match(r'\(variant \(name "([^"]+)"\)', entry).group(1)
                out.setdefault(ref, {}).setdefault(name, entry)
                i = e
    return out


def write_pcb(text, data, descriptions):
    """The board text with the variants of `data` (ref -> {name: entry}): the root list (one entry
    per variant name, with its description) and each footprint's entries, sorted by name. Earlier
    variant data on the board is replaced."""
    text = re.sub(r"\n\t\(variants\n(?:\t\t\(variant [^\n]*\n)*\t\)", "", text)
    text = re.sub(r"\n\t\t\(variant \(name [^\n]*", "", text)
    names = sorted({n for v in data.values() for n in v})
    edits = []
    for m in re.finditer(r'\n\t\(footprint "', text):
        start = m.start() + 1
        end = _close(text, start + 1)
        if text[end - 2:end] != "\t)":
            raise ValueError("unexpected footprint layout at %d" % start)
        ref = re.search(r'\(property "Reference" "([^"]+)"', text[start:end])
        if ref and ref.group(1) in data:
            v = data[ref.group(1)]
            edits.append((end - 2, "".join("\t\t%s\n" % v[n] for n in sorted(v))))
    if names:
        first = re.search(r'\n\t\(footprint "', text)
        at = first.start() + 1 if first else text.rstrip().rfind(")")
        edits.append((at, "\t(variants\n" + "".join('\t\t(variant (name "%s") (description "%s"))\n'
                                                     % (n, descriptions.get(n, "").replace('"', '\\"')) for n in names)
                      + "\t)\n"))
    for at, add in sorted(edits, reverse=True):
        text = text[:at] + add + text[at:]
    return text


def apply(pcb_path, project_dir, descriptions):
    texts = []
    for p in sorted(glob.glob(os.path.join(project_dir, "*.kicad_sch"))):
        with open(p, encoding="utf-8") as fh:
            texts.append(fh.read())
    data = sch_variants(texts)
    with open(pcb_path, encoding="utf-8") as fh:
        text = fh.read()
    new = write_pcb(text, data, descriptions)
    with open(pcb_path, "w", encoding="utf-8") as fh:
        fh.write(new)
    return {"parts": len(data), "variants": sorted({n for v in data.values() for n in v})}
