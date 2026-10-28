# Industrial design

- **Status:** Draft. The maintainers' design direction (2026-10-22) for the physical case; materials, finishes and radii are to be confirmed on prototypes. Dimensions are not set here.
- **Date:** 2026-10-22
- **Scope:** materials and surface language, geometry, edges, finishes, physical controls as the case shapes them, and rendering rules for the physical product.
- **Related:** the [design system spec](https://github.com/opendap-project/blackbird/blob/main/ui/docs/specs/design-system.md) (the shared visual language, colour and tokens) and the [controls and status LED spec](https://github.com/opendap-project/t1/blob/main/docs/specs/controls-and-status-led.md) (button behaviour and physical control design).
- **Requirements:** CASE-020, CASE-021, CASE-022, CASE-024, CASE-025, CASE-028 here; T1-014, T1-015, T1-022, T1-059 in [`t1`](https://github.com/opendap-project/t1/blob/main/docs/requirements/README.md).

The T1 should feel like a carefully engineered instrument made for people: compact, durable and comfortable to hold, with the corner treatment of contemporary consumer electronics and a distinct identity as a dedicated audio player. It must stay credible as a manufacturable object.

## 1. Materials

A predominantly synthetic palette, matching CASE-020 (the first cases are polymer, PC or ABS) and CASE-021 (graphite polymer with a grip texture).

| Role | Materials | Notes |
|---|---|---|
| Primary | Textured polycarbonate, matte ABS, durable polymer blends | The body. PC and ABS are what CASE-020 confirms. |
| Secondary | Anodised aluminium for selected structural or tactile details; transparent or smoked acrylic for small windows and light guides; elastomer for grip zones and buttons | Each needs a function. |
| Later options | Crystal clear, carbon, anodised aluminium | CASE-022. |

Do not make the device look machined from metal unless the construction is metal.

### 1.1 Surface hierarchy

| Surface | Finish | Purpose |
|---|---|---|
| Main enclosure | Matte graphite polymer | Primary body |
| Grip or side zones | Fine synthetic texture | Tactility and handling |
| Faceplate surround | Smooth dark polymer | Visual continuity with the display |
| Selected accents | Satin or anodised | Limited contrast |
| Light guides (status LED, FPT-003) | Translucent polymer | Controlled illumination |
| Buttons | Volume and Main in silver-finished polymer (metallic paint under a satin clear coat); Action in the orange accent | Tactile differentiation (§3) |

### 1.2 Textures

Subtle, scaled to the material, and visible only where they improve perceived quality or mark a functional difference: fine polymer grain, very subtle directional variation, diffuse reflections, restrained microtexture in grip zones, slightly different roughness between adjacent parts.

Avoid decorative hexagonal grids, random scratches, carbon-fibre patterns as decoration, exaggerated machining marks, and anything that looks noisy at device scale. Details must convince at render scale and at real size.

## 2. Geometry

### 2.1 Overall shape

A rounded rectangular enclosure with comfortable corner radii; controlled transitions between front, sides and back; no unnecessarily sharp external edge; a balanced display and control area; distinct physical affordances for frequent controls. Compact and comfortable, not a miniature rack instrument.

### 2.2 Geometry families

Shared with the interface ([design system](https://github.com/opendap-project/blackbird/blob/main/ui/docs/specs/design-system.md)):

1. **Primary:** rounded rectangles and broad radii, for the enclosure and major surfaces.
2. **Control:** circles, capsules, segmented capsules and soft concave forms, for tactile input.
3. **Instrumentation:** fine lines, arcs and restrained markings, for secondary information.

Instrumentation geometry never overpowers the primary geometry.

### 2.3 Edges

Edges are softened by geometry, highlights and material transitions. No heavy bevels, bright outlines or exaggerated metallic chamfers; nothing that suggests a gaming accessory.

Physical radii are set here, by industrial design and manufacturing; the interface radius tokens do not apply to the case.

## 3. Physical controls

The button design in the [T1 concept art](https://github.com/opendap-project/t1/tree/main/docs/concept-art) governs (T1-059); this section describes it for the case. Other details in that concept art are stale (480 × 800 screen, 1.27 mm pins, earlier dimensions) and are not a source.

Seen from the front:

| Edge | Control | Form |
|---|---|---|
| Left, top | **Action** (T1-014, T1-022) | A round disc, subtly concave, with a defined tactile perimeter and no sharp rim. Deeper travel and a clearer click. The only control in the orange brand accent. |
| Left, below Action | **Volume +** and **Volume −** (T1-014) | Two half-capsules: together they form one capsule split across the middle, each half with a rounded outer end and a flat inner edge at the split, operated as two separate buttons. Not a rocker. |
| Right | **Main (power)** (T1-015) | A taller capsule with horizontal ribs for touch identification. |

Volume + / − and Main are silver-finished plastic: a metallic silver paint under a satin clear coat on the polymer cap, with the + and − reliefs in graphite (maintainers, 2026-10-23). Action stays in the orange accent; the body stays graphite.

### 3.1 Button groups

The volume pair is the reference instance of the **button group** pattern shared with the interface (DS-013): one capsule split into segments, rounded outer ends, flat inner edges at each split, every segment its own button, with a consistent gap or divider at each split. Any future physical button group on the case, a faceplate or a HAT case uses the same pattern.

### 3.2 Constraints for the case

- The Action disc's concavity is shallow: comfortable, with no depression that collects dirt.
- Controls are recognisable by touch alone: disc, split capsule and ribbed capsule differ in shape, position and texture.
- Button caps, travel and click are within the prototype fab's published processes (CASE-028); the Action button's deeper travel and click should come from a catalog switch rather than a custom mechanism (T1-010).
- The orange is validated against the design system's brand token under the same light, and is the same colour on every edition.

## 4. Manufacturability

Every material, finish and form in this document is chosen to be producible as a prototype within the prototype fab's published processes (CASE-028): CNC machining, 3D printing, injection moulding, anodising and other finishes.

| Element | Prototype route | Note |
|---|---|---|
| Graphite polymer body | 3D printing (early), CNC-machined PC or ABS, injection moulding | Colour and texture on 3D-printed parts differ from moulded parts; the reference is the moulded finish. |
| Grip texture | Moulded texture or bead blasting | Exact texture grades available are **UNVERIFIED**. |
| Orange Action button | Coloured polymer or painted cap | Colour match to the token is checked on a physical sample. |
| Aluminium details and the later aluminium option | CNC machining and anodising | CASE-022. |
| Light guides | Clear or translucent polymer | |

Snap-fit for the plain back cover (CASE-025) and screws for the faceplate, board and HAT device-side piece (CASE-024) are part of the visual language: visible fasteners appear only where they have a function, and are never added for effect.

## 5. Rendering rules

Product renders, previews and concept art follow the same design language as the interface (design system §16). They are built from components' `export/` with the [Blender library](https://github.com/opendap-project/blender-lib).

**Do:**

- Matte synthetic enclosure as the default, with realistic polymer roughness and reflections.
- Soft, controlled studio light; white highlights for contrast and material definition.
- Rounded edges with believable manufacturing transitions.
- Orange on the Action button, and sparingly elsewhere.
- Plasma effects only in display content, selected lighting or an explicit conceptual visualisation; thermal distortion only near an energetic source.
- Accurate proportions of the real controls and parts.

**Avoid:**

- Full-body metallic surfaces without a manufacturing reason.
- Extra orange trim, glowing seams, floating holographic interfaces.
- Mirror finishes on matte polymer.
- Decorative vents and fake technical details.
- Plasma that hides the product silhouette.

## 6. Open points

- Corner and edge radii, wall thickness and device thickness (open question in the requirements).
- Grip texture grade and where grip zones sit.
- The orange part's material and colour match on prototypes.
