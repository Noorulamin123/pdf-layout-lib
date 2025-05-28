import json
from reportlab.platypus import SimpleDocTemplate
from table_template import build_table

def interpret_dsl(layout, filename="output.pdf"):
    doc = SimpleDocTemplate(filename)

    field_map = layout["field_map"]
    data_rows = layout["data_rows"]

    header_row_1 = []
    header_row_2 = []
    final_keys = []

    for item in field_map:
        if item.get("group"):
            header_row_1.append(item["label"])
            for child in item["children"]:
                header_row_2.append(child["label"])
                final_keys.append(child["key"])
        else:
            header_row_1.append(item["label"])
            header_row_2.append("")
            final_keys.append(item["key"])

    data = [header_row_1, header_row_2]
    for row in data_rows:
        data.append([row.get(k, "") for k in final_keys])

    table = build_table(data, layout)
    doc.build([table])
    print(f"✅ PDF generated: {filename}")

if __name__ == "__main__":
    with open("layout.json") as f:
        layout = json.load(f)
    with open("data.json") as f:
        data = json.load(f)
    layout["data_rows"] = data
    interpret_dsl(layout, "custom_headers_table.pdf")