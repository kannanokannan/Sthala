#!/usr/bin/env python3
"""Gate the structural invariants of the Sthala repository.

Run from the repository root:  python3 scripts/verify_structure.py
Exit 0 = every gate passed. Exit 1 = at least one gate failed.

This file exists because the 2026-09-03 structure salvage established a set of
invariants that nothing was checking. Nothing here checks style or content; it
checks only the properties that must hold for the repository to be coherent.
"""
import glob
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("FAIL  PyYAML is required:  pip install pyyaml")
    sys.exit(1)

FAIL = []
PASS = []
STAGES = ["ingest", "extract", "compute", "verify", "narrate", "egress"]
REQUIRED = ["profile.yaml", "run.sh", "docker-compose.yml", "README.md"]


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(("PASS  " if ok else "FAIL  ") + name + (("  -- " + detail) if detail else ""))


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def recipe_dirs():
    dirs = [d for d in glob.glob("recipes/*/*") if os.path.isdir(d)]
    if os.path.isdir("recipes/_template"):
        dirs.append("recipes/_template")
    return sorted(set(d for d in dirs if os.path.isfile(os.path.join(d, "profile.yaml"))))


# --- G1: no path renamed away by the 2026-09-03 salvage may reappear ---------
# profiles/ca-firm.yaml -> profiles/accounting-firm.yaml
# models/models.md      -> docs/models.md
# recipes/<name>/       -> recipes/<region>/<name>/
RETIRED = [
    "profiles/ca-firm.yaml",
    "models/models.md",
    "recipes/sales-trend-mining/",
    "recipes/tally-ca-copilot/",
    "STHALA_PROFILE=ca-firm",
]
TEXT = ("*.md", "*.yaml", "*.yml", "*.sh", "*.py", "*.txt")
files = []
for pat in TEXT:
    files += glob.glob("**/" + pat, recursive=True)
# The gate names the retired paths as literals, so it must exclude itself.
SELF = os.path.normpath(__file__).replace(os.sep, "/")
files = sorted(f for f in files
               if not f.startswith(".git")
               and not SELF.endswith(f.replace(os.sep, "/")))
for retired in RETIRED:
    hits = [f for f in files if retired in read(f)]
    check("G1 retired path absent: " + retired, not hits,
          "found in: " + ", ".join(hits) if hits else "")

# --- G2: every compose file is valid YAML -----------------------------------
composes = sorted(glob.glob("stack/**/docker-compose.yml", recursive=True) +
                  glob.glob("recipes/**/docker-compose.yml", recursive=True))
for path in composes:
    try:
        yaml.safe_load(read(path))
        check("G2 compose parses: " + path, True)
    except yaml.YAMLError as exc:
        check("G2 compose parses: " + path, False, str(exc).replace("\n", " ")[:120])

# --- G3: every recipe profile extends a file that exists ---------------------
for d in recipe_dirs():
    path = os.path.join(d, "profile.yaml")
    match = re.search(r"^extends:\s*(\S+)", read(path), re.MULTILINE)
    if not match:
        check("G3 extends resolves: " + path, False, "no extends: line")
        continue
    target = os.path.normpath(os.path.join(d, match.group(1)))
    check("G3 extends resolves: " + path, os.path.isfile(target),
          "" if os.path.isfile(target) else "missing: " + target)

# --- G4: every pipeline module compiles -------------------------------------
for path in sorted(glob.glob("recipes/**/*.py", recursive=True)):
    try:
        compile(read(path), path, "exec")
        check("G4 compiles: " + path, True)
    except SyntaxError as exc:
        check("G4 compiles: " + path, False, "line %s: %s" % (exc.lineno, exc.msg))

# --- G5: every recipe is structurally complete ------------------------------
for d in recipe_dirs():
    missing = [f for f in REQUIRED if not os.path.isfile(os.path.join(d, f))]
    missing += ["pipeline/%s.py" % s for s in STAGES
                if not os.path.isfile(os.path.join(d, "pipeline", "%s.py" % s))]
    check("G5 recipe complete: " + d, not missing, "missing: " + ", ".join(missing) if missing else "")

print()
print("%d passed, %d failed" % (len(PASS), len(FAIL)))
if FAIL:
    print()
    print("Failed gates:")
    for name in FAIL:
        print("  - " + name)
sys.exit(1 if FAIL else 0)
