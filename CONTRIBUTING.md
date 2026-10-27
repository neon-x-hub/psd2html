# Contributing to PSD2HTML

Thank you for your interest in contributing! This project started as a personal utility to bridge the gap between Photoshop layouts and clean code without bloated WYSIWYG markup or non-deterministic AI tools.

Contributions, suggestions, and feedback are very welcome.

---

## Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/psd2html.git
   cd psd2html
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies and package in editable mode:**
   ```bash
   pip install -e .
   ```

---

## Running Tests

Before submitting any changes, make sure all tests pass:

```bash
python -m unittest discover -s tests -v
```

If you add new syntax tokens or features, please include corresponding unit tests in `tests/`.

---

## Submitting Pull Requests

1. **Fork the repository** and create a feature branch (`git checkout -b feature/my-enhancement`).
2. **Keep it focused**: Small, clear PRs with clear explanations are easiest to review.
3. **Preserve determinism**: We intentionally avoid heuristic guessing or computer vision — layout resolution should remain predictable, explicit, and reproducible.
4. **Follow code style**: Keep code PEP 8 compliant, type-annotated, and well-documented.
5. **Open a PR**: Describe what changed and why, linking any relevant issues.

---

## Ideas & Feature Requests

Have an idea for:
- New metadata tokens (e.g. `z-index`, CSS grid template columns, border-radius)?
- Additional exporters (e.g. Tailwind CSS, React, Vue, Svelte)?
- Better handling of text layers and typography?

Feel free to open an issue or discussion on GitHub!
