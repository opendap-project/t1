# Renders

Tool: [Blender](https://www.blender.org) 5.2.

## Layout

- `<scene>/`: one folder per scene, holding `<scene>.blend`. Import geometry from the STEP exports of the mechanical parts.
- `<scene>/out/`: rendered images, not committed. Images used in documentation are copied to `docs/`.

Blender backups (`*.blend1`) are not committed.

## Web

- `web/`: standalone HTML previews (three.js), for product-side views that do not need Blender. `web/concept.html` is the source of the concept-art cover in [`docs/concept-art/`](../docs/concept-art/README.md); open it in a browser and capture the 1920 × 1080 frame.
