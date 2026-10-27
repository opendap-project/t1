# Mechanics

Tool: [FreeCAD](https://www.freecad.org) 1.1.

## Layout

- `<part>/`: one folder per part, holding `<part>.FCStd`.
- `<part>/exports/`: STEP (and STL where the part is printed) exported from FreeCAD, committed so the part can be used without FreeCAD.

`.FCStd` files are binary archives; git stores them whole. FreeCAD backups (`*.FCBak`, `*.FCStd1`) are not committed.
