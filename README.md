# psd2html

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-psd--tools-orange.svg)](https://github.com/psd-tools/psd-tools)
[![Build Status](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)]()

> A lightweight, deterministic Photoshop (`.psd`) to semantic HTML/CSS and structured JSON layout compiler, driven by simple layer naming utility conventions.

---

## Why psd2html?

I originally built this utility for my own daily workflows. I love using Photoshop for fast visual mockups, but converting layouts into code usually involves two frustrating extremes:
1. **Traditional export / slicing tools**: Produce rigid pixel-absolute coordinate soup or unmaintainable, bloated HTML.
2. **AI & computer vision converters**: Non-deterministic, prone to hallucinating dimensions, and lack precise control over box model rules.

**`psd2html` takes a deterministic approach:** your Photoshop file is the ground truth. By simply adding short utility tokens to your layer names (like `w-rel h-abs left-abs top-rel`), `psd2html` resolves true parent-relative percentages, bounding boxes, and vector fills into **clean, human-readable HTML5 + modern CSS** and **structured JSON**.

I decided to open-source it in case anyone else with a designer-developer workflow finds it useful!

---

## Features

- ** 100% Deterministic**: No heuristic guessing, computer vision, or black-box AI. Photoshop layer bounds and naming tokens dictate the structure.
- ** Fluid & Absolute Positioning**: Mix pixel dimensions (`w-abs`, `h-abs`) and responsive parent-relative percentages (`w-rel`, `h-rel`, `left-rel`, `top-rel`) effortlessly.
- ** The `#` Container Convention**: A child shape named `#` automatically sets the parent group's bounds, background color, and coordinate space.
- ** Vector Style Extraction**: Automatically extracts solid RGB fills (`background-color`) and border strokes from Photoshop vector rectangle layers.
- ** Semantic HTML5**: Automatically maps layer names like `Navbar`, `Sidebar`, `Header`, or `Main` to `<nav>`, `<aside>`, `<header>`, and `<main>` tags (or explicitly specify with `tag-*`).
- ** Dual Canvas Modes**:
  - `viewport` (default): Fluid, responsive width (`100%`) matching browser viewports.
  - `fixed`: Pixel-perfect canvas locked to the exact PSD artboard dimensions.
- ** Multiple Exporters**: Generates standalone HTML previews, clean external stylesheets (`styles.css`), and structured JSON trees.
- ** CLI & Python API**: Usable as a command-line tool or importable directly into Python build pipelines.

---

## How It Works

```
Photoshop (.psd)
  ├── Groups & Layer Hierarchy
  ├── Bounding Boxes & Vector Fills
  └── Utility Layer Names (e.g., "Navbar | w-rel h-abs left-abs top-abs")
          │
          ▼
      [psd2html]
     ├── PSD Extractor (psd-tools)
     ├── Metadata Parser
     └── Layout & Coordinate Resolver
          │
          ├──► index.html   (Semantic HTML5)
          ├──► styles.css   (Modern, clean CSS)
          └──► layout.json  (Framework-agnostic tree)
```

---

## Quickstart

### 1. Installation

Ensure you have **Python 3.10+** installed:

```bash
# Clone the repository
git clone https://github.com/neon-x-hub/psd2html.git
cd psd2html

# Install in editable mode
python -m pip install -e .

# Or install dependencies directly
python -m pip install -r requirements.txt
```

### 2. Convert a PSD

Run the CLI on the included sample PSD:

```bash
# Viewport mode (fluid responsive layout)
psd2html example/1.psd -o dist/

# Fixed mode (exact artboard pixel bounds)
psd2html example/1.psd -o dist/fixed/ -m fixed
```

Generated output in `dist/`:
- `index.html`: Complete standalone preview page.
- `styles.css`: External clean stylesheet.
- `1.layout.json`: Structured JSON containing raw bounding boxes, computed coordinates, and styling trees.

---

## Layer Naming Notation

Layer names follow a simple pipe-delimited format:

```txt
[Layer or Group Name] | [tokens ...]
```

### Reference Cheat Sheet

| Token Category | Token | Meaning | Generated CSS / Output |
| :--- | :--- | :--- | :--- |
| **Width** | `w-abs` | Absolute width | `width: <layer_width>px` |
| | `w-rel` | Relative width (% of parent) | `width: (<w> / <parent_w>) * 100%` |
| **Height** | `h-abs` | Absolute height | `height: <layer_height>px` |
| | `h-rel` | Relative height (% of parent) | `height: (<h> / <parent_h>) * 100%` |
| **X-Position** | `left-abs`, `x-abs` | Distance from parent left | `left: <offset>px` |
| | `left-rel`, `x-rel` | % offset from parent left | `left: <offset_pct>%` |
| | `right-abs` | Distance from parent right | `right: <offset>px` |
| | `right-rel` | % offset from parent right | `right: <offset_pct>%` |
| **Y-Position** | `top-abs`, `y-abs` | Distance from parent top | `top: <offset>px` |
| | `top-rel`, `y-rel` | % offset from parent top | `top: <offset_pct>%` |
| | `bottom-abs` | Distance from parent bottom | `bottom: <offset>px` |
| | `bottom-rel` | % offset from parent bottom | `bottom: <offset_pct>%` |
| **Positioning** | `pos-rel` | Relative positioning | `position: relative` |
| | `pos-abs` | Absolute positioning (default) | `position: absolute` |
| **Display** | `flex` | Flexbox container | `display: flex` |
| | `flex-row` | Row direction | `display: flex; flex-direction: row` |
| | `flex-col` | Column direction | `display: flex; flex-direction: column` |
| | `grid`, `block` | Grid / Block display | `display: grid` / `display: block` |
| **Alignment** | `items-center` | Align items center | `align-items: center` |
| | `justify-between` | Space between items | `justify-content: space-between` |
| | `justify-center` | Center items | `justify-content: center` |
| | `gap-16` | Container gap | `gap: 16px` |
| **Tags & Classes** | `tag-article` | Override HTML element | `<article ...>` |
| | `.custom-class` | Add custom CSS class | `class="... custom-class"` |

---

### The `#` Container Trick

In Photoshop, a group folder doesn't have an intrinsic background color or fill. To give a container group dimensions, position, and background color:

1. Create a vector rectangle layer inside your group.
2. Name that layer `#` (or `# | w-rel h-abs left-abs top-abs`).
3. `psd2html` merges the `#` shape's bounds and background color directly into the parent group!

```txt
Page
├── Navbar                         <-- HTML <nav class="navbar">
│   ├── # | w-rel h-abs left-abs   <-- Background fill & geometry for Navbar
│   ├── Logo | w-abs h-abs         <-- Placed inside Navbar
│   └── Nav Options | w-abs h-abs  <-- Placed inside Navbar
└── Main                           <-- HTML <main class="main">
    ├── Sidebar | w-abs h-rel
    └── Content | w-rel h-rel
```

---

## CLI Usage

```bash
psd2html [-h] [-o OUTPUT_DIR] [-m {viewport,fixed}] [-f {all,html,json}]
         [--no-vector-geom] [--no-clamp] [-v] [--version]
         psd_path
```

### Options

| Flag | Description | Default |
| :--- | :--- | :--- |
| `psd_path` | Path to the source Photoshop (`.psd`) file | *(Required)* |
| `-o`, `--out` | Directory to save generated files | `dist` |
| `-m`, `--mode` | Sizing mode: `viewport` (fluid) or `fixed` (exact PSD pixels) | `viewport` |
| `-f`, `--format` | Output format: `all`, `html`, or `json` | `all` |
| `--no-vector-geom` | Use raster bounding boxes instead of vector origination shapes | `False` |
| `--no-clamp` | Allow negative coordinate offsets without clamping to 0 | `False` |
| `-v`, `--verbose` | Print detailed step-by-step processing output | `False` |
| `--version` | Show program version and exit | |

---

## Python API

You can also use `psd2html` programmatically in your own build scripts or tools:

```python
from psd2html import (
    PSDParser,
    LayoutResolver,
    HTMLCSSGenerator,
    JSONExporter,
    CanvasMode,
)

# 1. Parse the PSD file
parser = PSDParser(use_vector_geometry=True)
canvas_bbox, raw_root = parser.parse_file("example/1.psd")

# 2. Resolve layout tree and compute coordinates
resolver = LayoutResolver(canvas_mode=CanvasMode.VIEWPORT)
document = resolver.resolve(canvas_bbox, raw_root)

# 3. Export to JSON
json_exporter = JSONExporter(indent=2)
json_exporter.export_file(document, "dist/layout.json")

# 4. Export to semantic HTML & CSS
html_gen = HTMLCSSGenerator(include_comments=True)
html_file, css_file = html_gen.export_files(document, "dist/", standalone=True)

print(f"Generated: {html_file} and {css_file}")
```

---

## Running Tests

A complete automated unit and integration test suite is included:

```bash
python -m unittest discover -s tests -v
```

All tests run across Python 3.10–3.13 on Linux, macOS, and Windows via GitHub Actions.

---

## Roadmap & Ideas

- [ ] Export to Tailwind CSS utility classes
- [ ] Export directly to React / JSX components
- [ ] Typography and text layer extraction (font-family, font-size, line-height, text color)
- [ ] CSS Grid template area declarations
- [ ] Exporting sliced image assets for raster layers

If there's a feature or layer syntax token you'd love to see, feel free to [open an issue](https://github.com/neon-x-hub/psd2html/issues) or submit a pull request!

---

## License

This project is licensed under the [MIT License](LICENSE).
