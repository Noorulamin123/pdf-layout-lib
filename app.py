import json
from reportlab.platypus import SimpleDocTemplate
from renderer import interpret_layout

def interpret_dsl(layout, filename="output.pdf"):
    doc = SimpleDocTemplate(filename)
    data_rows = layout.get("data_rows", [])
    layout_tree = {
        "type": layout.get("type", "column"),
        "children": layout.get("children", layout.get("layout", [])),
        "columns": layout.get("columns", 2)
    }
    flowables = interpret_layout(layout_tree, data_rows)
    doc.build(flowables)
    print(f"✅ PDF generated: {filename}")

if __name__ == "__main__":
    with open("layout.json") as f:
        layout = json.load(f)
    with open("data.json") as f:
        data = json.load(f)
    layout["data_rows"] = data
    interpret_dsl(layout, "custom_headers_table.pdf")