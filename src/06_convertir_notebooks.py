"""
Better script to convert .py files to .ipynb notebooks.
- Separates imports into their own cell
- Converts section comments into markdown cells
- Splits code blocks at logical boundaries
"""

import nbformat
import re


def py_to_ipynb_better(py_file, ipynb_file):
    with open(py_file, "r") as f:
        content = f.read()

    nb = nbformat.v4.new_notebook()

    # Extract docstring for title
    title_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if title_match:
        docstring = title_match.group(1).strip()
        nb.cells.append(nbformat.v4.new_markdown_cell(docstring))
        content = content[title_match.end() :]

    lines = content.split("\n")
    cells = []
    current_code = []
    current_md = []
    in_section = False
    imports_extracted = False

    for line in lines:
        stripped = line.strip()

        # Detect section separators
        if re.match(r"^#\s*=+\s*$", stripped):
            if not in_section:
                # End of code, start section
                if current_code:
                    code = "\n".join(current_code).strip()
                    if code:
                        cells.append(("code", code))
                    current_code = []
                in_section = True
                current_md = []
            else:
                # End of section, create markdown
                md_lines = []
                for l in current_md:
                    if re.match(r"^#\s*=+\s*$", l.strip()):
                        continue
                    clean = l.replace("# ", "").replace("#", "").strip()
                    if clean:
                        md_lines.append(clean)
                if md_lines:
                    cells.append(("markdown", "\n".join(md_lines)))
                current_md = []
                in_section = False
            continue

        if in_section:
            current_md.append(line)
        else:
            # Check if this is an import line
            if stripped.startswith("import ") or stripped.startswith("from "):
                if not imports_extracted:
                    # Start new imports cell if we haven't extracted yet
                    if current_code:
                        code = "\n".join(current_code).strip()
                        if code:
                            cells.append(("code", code))
                        current_code = []
                    imports_extracted = True
                current_code.append(line)
            elif imports_extracted and stripped == "":
                # End of imports block
                code = "\n".join(current_code).strip()
                if code:
                    cells.append(("code", code))
                current_code = []
                imports_extracted = False
            else:
                current_code.append(line)

    # Flush remaining
    if current_code:
        code = "\n".join(current_code).strip()
        if code:
            cells.append(("code", code))

    # Build notebook
    for cell_type, content in cells:
        if cell_type == "code":
            nb.cells.append(nbformat.v4.new_code_cell(content))
        else:
            nb.cells.append(nbformat.v4.new_markdown_cell(content))

    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }

    with open(ipynb_file, "w") as f:
        nbformat.write(nb, f)

    n_code = sum(1 for c in nb.cells if c.cell_type == "code")
    n_md = sum(1 for c in nb.cells if c.cell_type == "markdown")
    print(f"Converted {py_file} -> {ipynb_file}")
    print(f"  {len(nb.cells)} cells: {n_code} code, {n_md} markdown")


if __name__ == "__main__":
    py_to_ipynb_better("src/model_building.py", "src/01_model_building.ipynb")
    py_to_ipynb_better("src/competitor_analysis.py", "src/02_competitor_analysis.ipynb")
