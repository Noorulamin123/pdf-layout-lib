# PDF Template System

A flexible framework for generating PDF documents with dynamic content, supporting various layout components, data transformations, and filtering capabilities.

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
4. [Layout Components](#layout-components)
5. [Layout Types](#layout-types)
6. [Data Handling](#data-handling)
7. [Transforms](#transforms)
8. [Filters](#filters)
9. [Advanced Features](#advanced-features)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)
13. [Contributing](#contributing)
14. [License](#license)

## Overview

The PDF Template System is a flexible framework for generating PDF documents with dynamic content. It supports various layout components, data transformations, and filtering capabilities.

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-template
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Example
```python
from reportlab.platypus import SimpleDocTemplate
from layout_lib.renderer import interpret_layout
import json

# Load layout and data
with open("layout.json") as f:
    layout = json.load(f)
with open("data/data.json") as f:
    data = json.load(f)

# Generate PDF
layout["data_rows"] = data
doc = SimpleDocTemplate("output.pdf")
flowables = interpret_layout(layout, data)
doc.build(flowables)
```

## Core Concepts

### Data Structure
The system works with two main types of data:
1. Table Data: List of objects for tabular display
2. Group Data: Can be either a single object or a list of objects. When a list is provided, the filter will select one object for use.

### Layout System
- JSON-based layout definition
- Component-based architecture
- Support for nested layouts
- Dynamic data binding

### Components
- Variable: Display single values
- Table: Display tabular data
- Group: Group related data
- Separator: Visual separation

## Layout Components

### 1. Group Component
Groups are one of the fundamental data containers in the system. They hold a single object of data and can be filtered. Other components (like variables) must reference a group to access its data.

#### Basic Usage
```json
{
  "type": "group",
  "group_name": "stock_data",
  "filter": "RIC=GOOGL.O"
}
```

#### Advanced Usage with Multiple Filters
```json
{
  "type": "group",
  "group_name": "stock_data",
  "filter": {
    "and": [
      {"RIC": "GOOGL.O"},
      {"Price": {">": 100}},
      {"Volume": {">": 1000000}}
    ]
  }
}
```

### 2. Variable Component
Variables display values from a group's data. They must be associated with a group using the `group_name` field to access the data.

#### Basic Usage
```json
{
  "type": "variable",
  "label": "Price",
  "key": "price",
  "group_name": "stock_data",  // References the group above
  "transform": "dollarize"
}
```

#### Advanced Usage with Multiple Fields
```json
{
  "type": "variable",
  "label": "Volume Data",
  "key": "Volume1|Volume2|Volume3",  // Multiple fields separated by pipe
  "group_name": "stock_data",  // References the group above
  "transform": "join_lines"  // Combines multiple fields with line breaks
}
```

### Example: Group with Variables
```json
{
  "type": "column",
  "children": [
    {
      "type": "group",
      "group_name": "stock_data",
      "filter": "RIC=GOOGL.O"
    },
    {
      "type": "variable",
      "label": "Price",
      "key": "price",
      "group_name": "stock_data",  // References the group above
      "transform": "dollarize"
    },
    {
      "type": "variable",
      "label": "Volume",
      "key": "volume",
      "group_name": "stock_data",  // References the same group
      "transform": "volume_millions"
    }
  ]
}
```

### 3. Table Component
Displays data in a tabular format with support for multi-level headers.

#### Basic Structure
```json
{
  "type": "table",
  "field_map": [...],
  "style": {...}
}
```

#### Multi-level Headers
```json
{
  "field_map": [
    {
      "label": "Financial Data",
      "group": true,
      "children": [
        {
          "label": "Price Information",
          "group": true,
          "children": [
            {"label": "Current", "key": "current_price", "transform": "dollarize"},
            {"label": "Previous", "key": "previous_price", "transform": "dollarize"}
          ]
        }
      ]
    }
  ]
}
```

#### Style Options
```json
{
  "style": {
    "col_widths": [80, 80, 80],  // Optional: If not provided, widths are calculated automatically based on content
    "font_name": "Helvetica",
    "font_size": 9,
    "font_style": "bold-italic",
    "body_font_size": 9,
    "grid": true,
    "header_background": "grey",
    "header_text_color": "whitesmoke",
    "body_background": "beige",
    "alternate_row_colors": ["white", "lightgrey"],
    "header_height": 30,
    "row_height": 25
  }
}
```

> **Note:** The `col_widths` field is optional. When not provided, the table automatically calculates column widths based on the content:
> - Each column's width is determined by the maximum width needed for its content
> - Width calculation takes into account the specified font and text content
> - A small padding (10 units) is added to ensure text doesn't touch cell borders
> - This automatic calculation ensures all content is properly displayed without manual configuration

### 4. Separator Component
Creates visual separators in the document.

#### Basic Usage
```json
{
  "type": "separator",
  "length": 400,
  "thickness": 2,
  "color": "blue",
  "direction": "horizontal"
}
```

#### Advanced Usage with Styling
```json
{
  "type": "separator",
  "length": 400,
  "thickness": 2,
  "color": "blue",
  "direction": "horizontal",
  "margin_before": 20,
  "margin_after": 20,
  "dash": [3, 2],
  "style": {
    "opacity": 0.5,
    "line_cap": "round"
  }
}
```

## Layout Types

### 1. Column Layout
Arranges elements vertically, stacking them from top to bottom.

#### Key Features
- Vertical arrangement of elements
- Default layout type
- Supports nested layouts
- Automatic spacing between elements
- Flexible width management

#### Basic Example
```json
{
  "type": "column",
  "children": [
    {
      "type": "group",
      "group_name": "data_group"
    },
    {
      "type": "variable",
      "label": "First Item",
      "key": "first",
      "group_name": "data_group"
    },
    {
      "type": "variable",
      "label": "Second Item",
      "key": "second",
      "group_name": "data_group"
    }
  ]
}
```

### 2. Row Layout
Arranges elements horizontally, placing them side by side.

#### Key Features
- Horizontal arrangement of elements
- Automatic width distribution
- Support for flexible spacing
- Alignment options
- Nested component support

#### Basic Example
```json
{
  "type": "row",
  "children": [
    {
      "type": "group",
      "group_name": "data_group"
    },
    {
      "type": "variable",
      "label": "Left",
      "key": "left",
      "group_name": "data_group"
    },
    {
      "type": "separator",
      "direction": "vertical",
      "length": 100
    },
    {
      "type": "variable",
      "label": "Right",
      "key": "right",
      "group_name": "data_group"
    }
  ]
}
```

### 3. Grid Layout
Arranges elements in a grid format, flowing from left to right and top to bottom.

#### Key Features
- Grid-based arrangement
- Configurable number of columns
- Automatic row wrapping
- Equal or custom column widths
- Flexible cell sizing

#### Basic Example
```json
{
  "type": "grid",
  "columns": 2,
  "children": [
    {
      "type": "group",
      "group_name": "data_group"
    },
    {
      "type": "variable",
      "label": "Top Left",
      "key": "tl",
      "group_name": "data_group"
    },
    {
      "type": "variable",
      "label": "Top Right",
      "key": "tr",
      "group_name": "data_group"
    },
    {
      "type": "variable",
      "label": "Bottom Left",
      "key": "bl",
      "group_name": "data_group"
    },
    {
      "type": "variable",
      "label": "Bottom Right",
      "key": "br",
      "group_name": "data_group"
    }
  ]
}
```

## Data Handling

### 1. Data Structure Examples

#### Table Data (List of Objects)
```python
table_data = [
    {
        "Ticker": "AAPL",
        "RIC": "AAPL.O",
        "Ask": 175.25,
        "Bid": 175.20,
        "Last": 175.22,
        "Volume1": 12500000,
        "Exchange": "NASDAQ"
    },
    {
        "Ticker": "MSFT",
        "RIC": "MSFT.O",
        "Ask": 420.10,
        "Bid": 420.05,
        "Last": 420.08,
        "Volume1": 8900000,
        "Exchange": "NASDAQ"
    }
]
```

#### Group Data Examples

##### Single Object
```python
group_data = {
    "RIC": "GOOGL.O",
    "Price": 180.50,
    "Volume": 7200000,
    "Exchange": "NASDAQ",
    "Currency": "USD"
}
```

##### List of Objects
```python
group_data = [
    {
        "RIC": "GOOGL.O",
        "Price": 180.50,
        "Volume": 7200000,
        "Exchange": "NASDAQ",
        "Currency": "USD"
    },
    {
        "RIC": "AAPL.O",
        "Price": 175.22,
        "Volume": 12500000,
        "Exchange": "NASDAQ",
        "Currency": "USD"
    }
]
```

### 2. Programmatic Data Passing

#### Group Data Injection
```python
# Load group data (can be either single object or list of objects)
with open("data/group_data.json") as f:
    group_data = json.load(f)

# Inject group data into layout
for block in layout.get("children", []):
    if block.get("type") == "group":
        group_name = block.get("group_name")
        filter_condition = block.get("filter")
        # If group_data is a list, the filter will select one object
        # If group_data is a single object, it will be used as is
        block["data"] = group_data
```

#### Table Data Injection
```python
# Load table data (list of objects)
with open("data/data.json") as f:
    table_data = json.load(f)  # List of objects

# Inject table data into layout
for block in layout.get("children", []):
    if block.get("type") == "table":
        block["data"] = table_data
```

> **Important Notes:**
> - Variables must always be associated with a group using the `group_name` field
> - Group data can be either a single object or a list of objects
> - When group data is a list, the filter will select one object for use
> - Table data must be a list of objects, where each object represents a row
> - Never use variables without a group association

## Transforms

Transforms are functions that modify the display of data values. The system comes with some basic transforms, but you can easily create your own custom transforms.

### Basic Transforms

```json
{
  "type": "variable",
  "label": "Price",
  "key": "price",
  "transform": "dollarize"  // Formats as currency
}
```

### Custom Transforms

You can create custom transforms in two ways:

1. Using Lambda Functions (Inline):
```json
{
  "type": "variable",
  "label": "Custom Price",
  "key": "price",
  "transform": "lambda x: f'Price: ${x:.2f}'"
}
```

2. Using Python Functions (Defined in your code):
```python
# Create a new file: my_transforms.py
from layout_lib.transform_utils import TRANSFORMS

# Define your transform functions
def format_currency(value):
    return f"${value:,.2f}"

def format_percentage(value):
    return f"{value:.1f}%"

def format_phone(value):
    return f"({value[:3]}) {value[3:6]}-{value[6:]}"

# Register your transforms
TRANSFORMS.update({
    "format_currency": format_currency,
    "format_percentage": format_percentage,
    "format_phone": format_phone
})

# In your main script (e.g., app.py)
import my_transforms  # This will register your transforms

# Now you can use them in your layout
layout = {
    "type": "variable",
    "label": "Price",
    "key": "price",
    "transform": "format_currency"  // Use the registered transform name
}
```

> **Note:** Each field can only have one transform applied. If you need multiple transformations, create a custom transform function that combines them.

## Filters

### 1. Basic Filters

#### Simple Equality
```json
{
  "type": "group",
  "group_name": "stocks",
  "filter": "RIC=GOOGL.O"
}
```

#### Multiple Conditions
```json
{
  "type": "group",
  "group_name": "stocks",
  "filter": "RIC=GOOGL.O AND Price>100"
}
```

### 2. Advanced Filters

#### Complex Conditions
```json
{
  "type": "group",
  "group_name": "stocks",
  "filter": {
    "and": [
      {"RIC": "GOOGL.O"},
      {"Price": {">": 100}},
      {"Volume": {">": 1000000}}
    ]
  }
}
```

#### Nested Conditions
```json
{
  "type": "group",
  "group_name": "stocks",
  "filter": {
    "or": [
      {
        "and": [
          {"RIC": "GOOGL.O"},
          {"Price": {">": 100}}
        ]
      },
      {
        "and": [
          {"RIC": "AAPL.O"},
          {"Price": {">": 150}}
        ]
      }
    ]
  }
}
```

### 3. Conditional Filtering

#### Dynamic Filters
```python
def create_dynamic_filter(min_price, max_volume):
    return {
        "and": [
            {"Price": {">": min_price}},
            {"Volume": {"<": max_volume}}
        ]
    }

# Use in layout
layout = {
    "type": "group",
    "group_name": "stocks",
    "filter": create_dynamic_filter(100, 1000000)
}
```

## Advanced Features

### 1. Nested Layouts
Combine different layout types for complex arrangements:
```json
{
  "type": "column",
  "children": [
    {
      "type": "group",
      "group_name": "data_group"
    },
    {
      "type": "row",
      "children": [
        {
          "type": "variable",
          "label": "Left",
          "key": "left",
          "group_name": "data_group"
        },
        {
          "type": "variable",
          "label": "Right",
          "key": "right",
          "group_name": "data_group"
        }
      ]
    },
    {
      "type": "table",
      "field_map": [...]
    }
  ]
}
```

### 2. Conditional Data Display
Use group filters to show different data based on conditions:
```json
{
  "type": "column",
  "children": [
    {
      "type": "group",
      "group_name": "googl_data",
      "filter": "RIC=GOOGL.O"
    },
    {
      "type": "variable",
      "label": "Google Price",
      "key": "price",
      "group_name": "googl_data"
    }
  ]
}
```

### 3. Multiple Fields in One Column
Use pipe-separated keys with appropriate transforms:
```json
{
  "type": "group",
  "group_name": "data_group"
},
{
  "type": "variable",
  "label": "Volume Data",
  "key": "Volume1|Volume2|Volume3",
  "transform": "join_lines",
  "group_name": "data_group"
}
```

### 4. Multi-line Headers
Use `\n` in labels to create multi-line headers:
```json
{
  "type": "group",
  "group_name": "data_group"
},
{
  "type": "variable",
  "label": "Ticker\nSymbol",
  "key": "Ticker",
  "group_name": "data_group"
}
```

## Examples

### 1. Table Examples

#### Basic Single-Level Table
```json
{
  "type": "table",
  "field_map": [
    {"label": "Ticker", "key": "Ticker"},
    {"label": "RIC", "key": "RIC"},
    {"label": "Price", "key": "Last", "transform": "dollarize"},
    {"label": "Volume", "key": "Volume1", "transform": "volume_millions"}
  ],
  "style": {
    "grid": true,
    "header_background": "grey",
    "header_text_color": "whitesmoke"
  }
}
```

#### Multi-Level Table with Nested Groups
```json
{
  "type": "table",
  "field_map": [
    {
      "label": "Financial Data",
      "group": true,
      "children": [
        {"label": "Ticker\nSymbol", "key": "Ticker"},
        {"label": "RIC\nCode", "key": "RIC"},
        {
          "label": "Price\nData",
          "group": true,
          "children": [
            {"label": "Ask\nPrice", "key": "Ask", "transform": "dollarize"},
            {"label": "Bid\nPrice", "key": "Bid", "transform": "dollarize"},
            {"label": "Last\nPrice", "key": "Last", "transform": "dollarize"}
          ]
        },
        {"label": "Volume\nTraded", "key": "Volume1|Volume2", "transform": "join_lines"},
        {"label": "Exchange\nName", "key": "Exchange"}
      ]
    }
  ],
  "style": {
    "font_name": "Helvetica",
    "font_size": 9,
    "font_style": "bold-italic",
    "body_font_size": 9,
    "grid": true,
    "header_background": "grey",
    "header_text_color": "whitesmoke",
    "body_background": "beige",
    "alternate_row_colors": ["white", "lightgrey"]
  }
}
```

#### Table with Multiple Fields in One Column
```json
{
  "type": "table",
  "field_map": [
    {"label": "Ticker", "key": "Ticker"},
    {"label": "RIC", "key": "RIC"},
    {
      "label": "Volume Data",
      "key": "Volume1|Volume2|Volume3",
      "transform": "join_lines"
    },
    {"label": "Exchange", "key": "Exchange"}
  ],
  "style": {
    "grid": true,
    "header_background": "grey",
    "header_text_color": "whitesmoke"
  }
}
```

#### Complete Example with Data
```python
# Create layout with multi-level headers
layout = {
    "type": "column",
    "children": [
        {
            "type": "table",
            "field_map": [
                {
                    "label": "Financial Data",
                    "group": True,
                    "children": [
                        {"label": "Ticker\nSymbol", "key": "Ticker"},
                        {"label": "RIC\nCode", "key": "RIC"},
                        {
                            "label": "Price\nData",
                            "group": True,
                            "children": [
                                {"label": "Ask\nPrice", "key": "Ask", "transform": "dollarize"},
                                {"label": "Bid\nPrice", "key": "Bid", "transform": "dollarize"},
                                {"label": "Last\nPrice", "key": "Last", "transform": "dollarize"}
                            ]
                        },
                        {"label": "Volume\nTraded", "key": "Volume1|Volume2", "transform": "join_lines"},
                        {"label": "Exchange\nName", "key": "Exchange"}
                    ]
                }
            ],
            "style": {
                "font_name": "Helvetica",
                "font_size": 9,
                "font_style": "bold-italic",
                "body_font_size": 9,
                "grid": true,
                "header_background": "grey",
                "header_text_color": "whitesmoke",
                "body_background": "beige",
                "alternate_row_colors": ["white", "lightgrey"]
            }
        }
    ]
}

# Prepare data
data = [
    {
        "Ticker": "AAPL",
        "RIC": "AAPL.O",
        "Ask": 175.25,
        "Bid": 175.20,
        "Last": 175.22,
        "Volume1": 12500000,
        "Volume2": 12500000,
        "Exchange": "NASDAQ"
    },
    {
        "Ticker": "MSFT",
        "RIC": "MSFT.O",
        "Ask": 420.10,
        "Bid": 420.05,
        "Last": 420.08,
        "Volume1": 8900000,
        "Volume2": 8900000,
        "Exchange": "NASDAQ"
    }
]

# Generate PDF
layout["data_rows"] = data
doc = SimpleDocTemplate("financial_table.pdf")
flowables = interpret_layout(layout, data)
doc.build(flowables)
```

> **Table Features Summary:**
> - Single and multi-level headers using `group: true`
> - Multi-line headers using `\n` in labels
> - Multiple fields in one column using pipe-separated keys
> - Transforms for data formatting (e.g., `dollarize`, `volume_millions`, `join_lines`)
> - Customizable styling (fonts, colors, grid, etc.)
> - Automatic column width calculation when `col_widths` is not specified
> - Support for nested groups and complex data structures

### 2. Group with Filter Example
```python
# Create layout with group and filter
layout = {
    "type": "column",
    "children": [
        {
            "type": "group",
            "group_name": "stock_data",
            "filter": "RIC=GOOGL.O"
        },
        {
            "type": "variable",
            "label": "Price",
            "key": "Price",
            "transform": "dollarize",
            "group_name": "stock_data"
        }
    ]
}

# Load and inject group data (single object)
with open("data/group_data.json") as f:
    group_data = json.load(f)  # Should be a single object

for block in layout["children"]:
    if block["type"] == "group":
        block["data"] = group_data  # Single object

# Generate PDF
doc = SimpleDocTemplate("group_example.pdf")
flowables = interpret_layout(layout, [])
doc.build(flowables)
```

## Troubleshooting

### Common Issues

1. **Variable Not Found**
   - Ensure the variable is associated with a group using `group_name`
   - Check that the group data contains the specified key
   - Verify the group filter is correctly matching data

2. **Table Rendering Issues**
   - Check that data rows match the field map structure
   - Verify all required fields are present in the data
   - Ensure transforms are properly defined for custom formatting

3. **Filter Not Working**
   - Verify the filter syntax matches the supported format
   - Check that the data structure matches the filter conditions
   - Ensure group data is properly injected into the layout

4. **Transform Errors**
   - Verify transform function exists in TRANSFORMS dictionary
   - Check that input data matches transform function requirements
   - Ensure proper error handling in custom transforms

### Debug Tips

1. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Data Flow**
   - Print group data after filtering
   - Verify table data structure
   - Check transform function outputs

3. **Validate Layout**
   - Test components individually
   - Verify group associations
   - Check filter conditions

4. **Common Solutions**
   - Use proper group associations for variables
   - Ensure data structure matches layout requirements
   - Implement proper error handling in transforms
   - Validate filter conditions before use

## Best Practices

### 1. Layout Design
- Keep layouts modular and reusable
- Use consistent naming conventions
- Document complex layouts
- Use appropriate spacing and margins

### 2. Data Organization
- Structure data consistently
- Use meaningful field names
- Group related data together
- Validate data before rendering

### 3. Performance
- Minimize nested structures
- Use efficient filters
- Cache frequently used data
- Optimize transform functions

### 4. Maintenance
- Keep documentation updated
- Version control your layouts
- Test with various data sets
- Monitor error logs

## Contributing

### Development Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd pdf-template
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Tests**
   ```bash
   python -m unittest discover tests
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Write unit tests for new features

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- ReportLab for the PDF generation capabilities
- Contributors and maintainers of the project 