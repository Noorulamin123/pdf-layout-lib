# PDF Template System Documentation

This system allows you to create dynamic PDF documents using a JSON-based template system. The template defines the layout and content of your PDF, while data is provided separately to populate the template.

## Basic Structure

A template file (`layout.json`) consists of a JSON object with the following structure:

```json
{
  "type": "column",
  "children": [
    // Layout blocks go here
  ]
}
```

## Layout Types

### 1. Column Layout
- Arranges elements vertically
- Default layout type
- Elements are stacked from top to bottom
- Example:
```json
{
  "type": "column",
  "children": [
    {
      "type": "variable",
      "label": "First Item",
      "key": "first"
    },
    {
      "type": "variable",
      "label": "Second Item",
      "key": "second"
    }
  ]
}
```

### 2. Row Layout
- Arranges elements horizontally
- Elements are placed side by side
- Useful for creating header sections or grouped information
- Example:
```json
{
  "type": "row",
  "children": [
    {
      "type": "variable",
      "label": "Left",
      "key": "left"
    },
    {
      "type": "separator",
      "direction": "vertical",
      "length": 100
    },
    {
      "type": "variable",
      "label": "Right",
      "key": "right"
    }
  ]
}
```

### 3. Grid Layout
- Arranges elements in a grid format
- Requires `columns` property to specify number of columns
- Elements flow from left to right, top to bottom
- Example:
```json
{
  "type": "grid",
  "columns": 2,
  "children": [
    {
      "type": "variable",
      "label": "Top Left",
      "key": "tl"
    },
    {
      "type": "variable",
      "label": "Top Right",
      "key": "tr"
    },
    {
      "type": "variable",
      "label": "Bottom Left",
      "key": "bl"
    },
    {
      "type": "variable",
      "label": "Bottom Right",
      "key": "br"
    }
  ]
}
```

## Block Types

### 1. Variable Block
Displays a single value with an optional label. Can handle multiple data keys and transformations.

```json
{
  "type": "variable",
  "label": "Price",
  "key": "price",
  "transform": "dollarize",
  "group_name": "stock_data"
}
```

Properties:
- `label`: Display label for the variable
- `key`: Data key to fetch the value. Can be a single key or multiple keys separated by pipes (e.g., "price|bid|ask")
- `transform`: Optional transform to apply to the value
- `group_name`: Optional group context to fetch data from

Multiple keys example:
```json
{
  "type": "variable",
  "label": "Price Range",
  "key": "bid|ask",
  "transform": "join_pipes",
  "group_name": "stock_data"
}
```

### 2. Table Block
Creates a data table with headers and rows. Supports complex column structures with grouped headers.

```json
{
  "type": "table",
  "field_map": [
    {
      "label": "Financial Data",
      "group": true,
      "children": [
        {
          "label": "Ticker\nSymbol",
          "key": "Ticker"
        },
        {
          "label": "Price",
          "group": true,
          "children": [
            {
              "label": "Ask\nPrice",
              "key": "Ask",
              "transform": "dollarize"
            },
            {
              "label": "Bid\nPrice",
              "key": "Bid",
              "transform": "dollarize"
            }
          ]
        }
      ]
    }
  ],
  "style": {
    "col_widths": [100, 100],
    "font_name": "Helvetica",
    "font_size": 10,
    "grid": true
  }
}
```

#### Complex Table Structures

1. **Grouped Headers**
   - Use the `group` property to create header groups
   - Nested groups create multi-level headers
   - Example:
   ```json
   {
     "label": "Financial Data",
     "group": true,
     "children": [
       {
         "label": "Price",
         "group": true,
         "children": [
           {"label": "Ask", "key": "ask"},
           {"label": "Bid", "key": "bid"}
         ]
       }
     ]
   }
   ```

2. **Multi-line Headers**
   - Use `\n` in labels to create multi-line headers
   - Example:
   ```json
   {
     "label": "Ticker\nSymbol",
     "key": "Ticker"
   }
   ```

3. **Multiple Fields in One Column**
   - Use pipe-separated keys with appropriate transforms
   - Example:
   ```json
   {
     "label": "Volume Data",
     "key": "Volume1|Volume2|Volume3",
     "transform": "join_lines"
   }
   ```

### 3. Separator Block
Creates a visual separator line with customizable properties.

```json
{
  "type": "separator",
  "length": 400,
  "thickness": 2,
  "color": "blue",
  "direction": "horizontal",
  "margin_before": 20,
  "margin_after": 20,
  "dash": [3, 2]
}
```

Properties:
- `length`: Length of the separator in points
- `thickness`: Line thickness in points
- `color`: Color name (e.g., "blue", "red", "black")
- `direction`: "horizontal" or "vertical"
- `margin_before`: Space before the separator
- `margin_after`: Space after the separator
- `dash`: Optional array for dashed line pattern [dash_length, gap_length]

### 4. Group Block
Defines a data context for variables. Can filter data based on conditions.

```json
{
  "type": "group",
  "group_name": "stock_data",
  "filter": "RIC=GOOGL.O"
}
```

Properties:
- `group_name`: Unique identifier for the group
- `filter`: Simple filter condition in format "field=value" (exact match only)

### Group Data Sources

1. **Direct Data Injection**
   ```json
   {
     "type": "group",
     "group_name": "stock_data",
     "data": {
       "price": 150.25,
       "volume": 1000000,
       "change": 2.5
     }
   }
   ```

2. **Filtered Data from Array**
   ```json
   {
     "type": "group",
     "group_name": "stock_data",
     "filter": "RIC=GOOGL.O",
     "data": [
       {"RIC": "GOOGL.O", "price": 150.25},
       {"RIC": "AAPL.O", "price": 175.50}
     ]
   }
   ```

### Filter Limitations

The current implementation has the following limitations:

1. **Single Field Filtering**
   - Only one field can be filtered at a time
   - Format must be "field=value"
   - Example: `"filter": "RIC=GOOGL.O"`

2. **Exact Match Only**
   - Filters perform exact matching
   - No partial matches or pattern matching
   - No comparison operators (>, <, >=, <=)

3. **No Complex Conditions**
   - No support for AND/OR operations
   - No support for multiple conditions
   - No support for nested conditions

### Workarounds for Complex Filtering

If you need more complex filtering, consider these approaches:

1. **Pre-filter Data**
   ```python
   # Pre-filter your data before passing it to the template
   filtered_data = [item for item in raw_data 
                   if item.get("market") == "NYSE" 
                   and item.get("sector") == "tech"]
   
   group_data = {
       "type": "group",
       "group_name": "filtered_data",
       "data": filtered_data
   }
   ```

2. **Use Multiple Groups**
   ```json
   {
     "type": "column",
     "children": [
       {
         "type": "group",
         "group_name": "market_data",
         "filter": "market=NYSE"
       },
       {
         "type": "group",
         "group_name": "sector_data",
         "filter": "sector=tech"
       }
     ]
   }
   ```

3. **Transform Data Structure**
   ```json
   {
     "type": "group",
     "group_name": "combined_data",
     "data": {
       "market_sector": "NYSE_tech",
       "items": [...]
     }
   }
   ```

### Future Enhancements

The following features could be added to enhance filtering capabilities:

1. **Multiple Field Filtering**
   ```json
   {
     "filter": {
       "market": "NYSE",
       "sector": "tech"
     }
   }
   ```

2. **Comparison Operators**
   ```json
   {
     "filter": {
       "price": { ">": 100 },
       "volume": { "<=": 1000000 }
     }
   }
   ```

3. **Logical Operations**
   ```json
   {
     "filter": {
       "or": [
         { "market": "NYSE" },
         { "market": "NASDAQ" }
       ]
     }
   }
   ```

## Data Transforms

### Built-in Transforms

1. `dollarize`: Formats number as currency (e.g., "$100.00")
2. `price`: Formats price with 2 decimal places
3. `volume_millions`: Converts volume to millions format
4. `format_time_dd`: Formats timestamp as "HH:MM DD"
5. `dash_if_none`: Replaces None/null values with "-"
6. `join_lines`: Joins multiple values with newlines
7. `join_pipes`: Joins multiple values with " | "

### Adding Custom Transforms

To add custom transforms, modify the `transform_utils.py` file:

1. Define your transform function:
```python
def my_custom_transform(value):
    # Your transformation logic here
    return transformed_value
```

2. Add it to the TRANSFORMS dictionary:
```python
TRANSFORMS = {
    # ... existing transforms ...
    "my_custom_transform": my_custom_transform
}
```

Example of a custom transform:
```python
def format_percentage(value):
    return f"{float(value):.2f}%" if value is not None else "-"

TRANSFORMS = {
    # ... existing transforms ...
    "format_percentage": format_percentage
}
```

Usage in template:
```json
{
  "type": "variable",
  "label": "Growth",
  "key": "growth_rate",
  "transform": "format_percentage"
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
      "type": "row",
      "children": [
        {
          "type": "variable",
          "label": "Left",
          "key": "left"
        },
        {
          "type": "variable",
          "label": "Right",
          "key": "right"
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

## Group Layout System

The group system provides a powerful way to organize and filter data for display. It allows you to create data contexts that can be referenced by variables and other components.

### Group Block Structure

```json
{
  "type": "group",
  "group_name": "stock_data",
  "filter": "RIC=GOOGL.O",
  "data": {
    // Optional direct data injection
  }
}
```

Properties:
- `group_name`: Unique identifier for the group
- `filter`: Simple filter condition in format "field=value" (exact match only)
- `data`: Optional direct data injection (can be object or array)

### Group Data Sources

1. **Direct Data Injection**
   ```json
   {
     "type": "group",
     "group_name": "stock_data",
     "data": {
       "price": 150.25,
       "volume": 1000000,
       "change": 2.5
     }
   }
   ```

2. **Filtered Data from Array**
   ```json
   {
     "type": "group",
     "group_name": "stock_data",
     "filter": "RIC=GOOGL.O",
     "data": [
       {"RIC": "GOOGL.O", "price": 150.25},
       {"RIC": "AAPL.O", "price": 175.50}
     ]
   }
   ```

### Group-Variable Interaction

Variables can reference group data using the `group_name` property. This creates a powerful data binding system.

1. **Basic Group-Variable Binding**
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
         "label": "Stock Price",
         "key": "price",
         "group_name": "stock_data"
       }
     ]
   }
   ```

2. **Multiple Variables in Same Group**
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
         "group_name": "stock_data"
       },
       {
         "type": "variable",
         "label": "Volume",
         "key": "volume",
         "group_name": "stock_data"
       }
     ]
   }
   ```

3. **Nested Group Contexts**
   ```json
   {
     "type": "column",
     "children": [
       {
         "type": "group",
         "group_name": "market_data",
         "filter": "market=NYSE"
       },
       {
         "type": "group",
         "group_name": "stock_data",
         "filter": "RIC=GOOGL.O"
       },
       {
         "type": "variable",
         "label": "Market",
         "key": "market",
         "group_name": "market_data"
       },
       {
         "type": "variable",
         "label": "Stock Price",
         "key": "price",
         "group_name": "stock_data"
       }
     ]
   }
   ```

### Group Data Flow

1. **Data Resolution Process**
   - When a group block is encountered, the system:
     1. Checks for direct data injection
     2. If filter is present, applies it to array data
     3. Stores resolved data in group context
   - When a variable references a group:
     1. Looks up data in group context
     2. Applies any specified transforms
     3. Renders the result

2. **Data Inheritance**
   ```json
   {
     "type": "column",
     "children": [
       {
         "type": "group",
         "group_name": "parent_data",
         "data": {"common": "value"}
       },
       {
         "type": "group",
         "group_name": "child_data",
         "data": {"specific": "value"}
       },
       {
         "type": "variable",
         "label": "Common Value",
         "key": "common",
         "group_name": "parent_data"
       },
       {
         "type": "variable",
         "label": "Specific Value",
         "key": "specific",
         "group_name": "child_data"
       }
     ]
   }
   ```

### Advanced Group Features

1. **Multiple Filters**
   ```json
   {
     "type": "group",
     "group_name": "filtered_data",
     "filter": "market=NYSE&sector=tech"
   }
   ```

2. **Dynamic Group Names**
   ```json
   {
     "type": "variable",
     "label": "Dynamic Group",
     "key": "group_name",
     "group_name": "config"
   }
   ```

3. **Group Data Transformation**
   ```json
   {
     "type": "group",
     "group_name": "transformed_data",
     "data": {
       "raw": [1, 2, 3],
       "transformed": "1|2|3"
     }
   }
   ```

### Best Practices for Groups

1. **Naming Conventions**
   - Use descriptive group names
   - Follow consistent naming patterns
   - Avoid reserved names

2. **Data Organization**
   - Group related data together
   - Keep group data structures consistent
   - Use appropriate data types

3. **Filter Usage**
   - Keep filters simple and clear
   - Use meaningful field names
   - Handle edge cases in filters

4. **Performance Considerations**
   - Minimize number of groups
   - Use efficient filter conditions
   - Cache frequently used group data

5. **Error Handling**
   - Handle missing group data gracefully
   - Provide fallback values
   - Log group resolution errors

## Best Practices

1. **Data Organization**
   - Use groups to organize related data
   - Keep data structures consistent
   - Use meaningful group names

2. **Layout Design**
   - Use nested layouts for complex arrangements
   - Keep table column widths reasonable
   - Use separators to visually divide sections
   - Maintain consistent spacing

3. **Transforms**
   - Apply appropriate transforms for data formatting
   - Create custom transforms for repeated formatting patterns
   - Handle null/empty values appropriately

4. **Performance**
   - Keep template structure clean and organized
   - Avoid deeply nested structures when possible
   - Use appropriate data types for values

5. **Maintenance**
   - Document custom transforms
   - Use consistent naming conventions
   - Keep templates modular and reusable

### Advanced Filtering System

The template system now supports a powerful filtering system that can handle complex conditions. Filters can be specified in two formats:

1. **Simple Format** (Legacy)
   ```json
   {
     "filter": "field=value"
   }
   ```

2. **Advanced Format**
   ```json
   {
     "filter": {
       "field": "value"
     }
   }
   ```

#### Comparison Operators

The following comparison operators are supported:

```json
{
  "filter": {
    "price": { ">": 100 },
    "volume": { "<=": 1000000 },
    "status": { "!=": "inactive" }
  }
}
```

Available operators:
- `=`: Equal to
- `!=`: Not equal to
- `>`: Greater than
- `>=`: Greater than or equal to
- `<`: Less than
- `<=`: Less than or equal to
- `in`: Value is in list
- `not_in`: Value is not in list
- `contains`: String contains value
- `starts_with`: String starts with value
- `ends_with`: String ends with value

#### Logical Operations

1. **AND Operation**
   ```json
   {
     "filter": {
       "and": [
         { "market": "NYSE" },
         { "sector": "tech" },
         { "price": { ">": 100 } }
       ]
     }
   }
   ```

2. **OR Operation**
   ```json
   {
     "filter": {
       "or": [
         { "market": "NYSE" },
         { "market": "NASDAQ" }
       ]
     }
   }
   ```

3. **NOT Operation**
   ```json
   {
     "filter": {
       "not": {
         "status": "inactive"
       }
     }
   }
   ```

4. **Combined Operations**
   ```json
   {
     "filter": {
       "and": [
         {
           "or": [
             { "market": "NYSE" },
             { "market": "NASDAQ" }
           ]
         },
         { "sector": "tech" }
       ]
     }
   }
   ```

#### String Operations

```json
{
  "filter": {
    "name": { "contains": "tech" },
    "ticker": { "starts_with": "GOOG" },
    "description": { "ends_with": "Inc." }
  }
}
```

#### List Operations

```json
{
  "filter": {
    "sectors": { "in": ["tech", "finance"] },
    "exchanges": { "not_in": ["OTC"] }
  }
}
```

#### Examples

1. **Complex Market Filter**
   ```json
   {
     "filter": {
       "and": [
         {
           "or": [
             { "market": "NYSE" },
             { "market": "NASDAQ" }
           ]
         },
         { "sector": "tech" },
         { "price": { ">": 100 } },
         { "volume": { ">=": 1000000 } }
       ]
     }
   }
   ```

2. **Status and Type Filter**
   ```json
   {
     "filter": {
       "and": [
         { "status": "active" },
         {
           "or": [
             { "type": "stock" },
             { "type": "etf" }
           ]
         }
       ]
     }
   }
   ```

3. **Text Search Filter**
   ```json
   {
     "filter": {
       "and": [
         { "name": { "contains": "tech" } },
         { "description": { "contains": "software" } }
       ]
     }
   }
   ```

#### Best Practices for Filtering

1. **Performance**
   - Use simple filters when possible
   - Avoid deeply nested conditions
   - Consider pre-filtering large datasets

2. **Readability**
   - Use meaningful field names
   - Break complex filters into logical groups
   - Add comments for complex conditions

3. **Error Handling**
   - Handle missing fields gracefully
   - Use appropriate data types
   - Validate filter conditions

4. **Maintenance**
   - Keep filters modular
   - Document complex conditions
   - Use consistent naming conventions 