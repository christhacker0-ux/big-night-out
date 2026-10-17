#!/usr/bin/env python3
"""Checks World/*.json against Dialogue/*.yarn without opening Unity.

Run from the repo root: python3 tools/check_world.py
Reports missing Yarn nodes, unknown items or rooms in commands, duplicate names,
unbalanced <<if>>/<<endif>>, and items nobody can ever get.
"""
import glob, json, os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "Assets", "_Project")
errors, warnings = [], []

items, combos, rooms = {}, [], {}
for path in sorted(glob.glob(os.path.join(ROOT, "World", "*.json"))):
    data = json.load(open(path))
    for it in data.get("items", []):
        if it["id"] in items: errors.append(f"{path}: item '{it['id']}' defined twice")
        items[it["id"]] = it
    combos += data.get("combinations", [])
    for r in data.get("rooms", []):
        if r["id"] in rooms: errors.append(f"{path}: room '{r['id']}' defined twice")
        rooms[r["id"]] = r

nodes, bodies = {}, {}
for path in sorted(glob.glob(os.path.join(ROOT, "Dialogue", "*.yarn"))):
    text = open(path).read()
    for m in re.finditer(r"^title:\s*(\S+)\s*\n(?:.*\n)*?---\n(.*?)^===", text, re.M | re.S):
        name = m.group(1)
        if name in nodes: errors.append(f"{os.path.basename(path)}: node '{name}' also in {nodes[name]}")
        nodes[name] = os.path.basename(path)
        bodies[name] = m.group(2)

def need(node, where):
    if node and node not in nodes: errors.append(f"{where}: Yarn node '{node}' does not exist")

scenes = set()
for r in rooms.values():
    if r["scene"] in scenes: errors.append(f"room {r['id']}: scene name '{r['scene']}' used twice")
    scenes.add(r["scene"])
    need(r.get("onEnter"), f"room {r['id']} onEnter")
    slugs = set()
    for h in r.get("hotspots", []):
        where = f"room {r['id']} hotspot '{h['name']}'"
        need(h.get("look"), where); need(h.get("use"), where)
        for i in h.get("items", []):
            if i["item"] not in items: errors.append(f"{where}: unknown item '{i['item']}'")
            need(i["node"], where)
        for k in ("feet", "size"):
            if len(h.get(k, [])) != 2: errors.append(f"{where}: '{k}' must be [x, y]")
for c in combos:
    need(c["node"], f"combination {c['a']}+{c['b']}")
    for k in ("a", "b"):
        if c[k] not in items: errors.append(f"combination: unknown item '{c[k]}'")
for i in items:
    need(f"Item_{i}_Look", f"item {i}")

given = set()
for name, body in bodies.items():
    depth = 0
    for line in body.splitlines():
        s = line.strip()
        if re.match(r"<<if\b", s): depth += 1
        elif re.match(r"<<endif>>", s): depth -= 1
        if depth < 0: errors.append(f"node {name}: <<endif>> without <<if>>"); depth = 0
    if depth: errors.append(f"node {name}: {depth} unclosed <<if>>")
    for m in re.finditer(r"<<(give|take)\s+(\w+)>>", body):
        if m.group(2) not in items: errors.append(f"node {name}: <<{m.group(1)} {m.group(2)}>> unknown item")
        if m.group(1) == "give": given.add(m.group(2))
    for m in re.finditer(r"<<go\s+(\w+)\s+(\w+)>>", body):
        room, entry = m.groups()
        if room not in rooms: errors.append(f"node {name}: <<go {room}>> unknown room")
        elif entry not in [e["name"] for e in rooms[room].get("entries", [])]:
            errors.append(f"node {name}: room {room} has no entry '{entry}'")
    for m in re.finditer(r"<<jump\s+(\w+)>>", body):
        need(m.group(1), f"node {name} jump")
    for m in re.finditer(r"<<(\w+)", body):
        if m.group(1) not in {"if", "elseif", "else", "endif", "give", "take", "flag", "unflag", "add", "act", "go", "jump", "set", "declare", "stop", "wait"}:
            errors.append(f"node {name}: unknown command <<{m.group(1)}>>")
for i in items:
    if i not in given: warnings.append(f"item '{i}' is never given")

for w in warnings: print("warning:", w)
for e in errors: print("ERROR:", e)
print(f"{len(rooms)} rooms, {len(items)} items, {len(nodes)} nodes, {len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
