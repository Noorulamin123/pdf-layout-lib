import json
import unittest
from reportlab.platypus import SimpleDocTemplate
from layout_lib.renderer import interpret_layout
from layout_lib.filter_utils import FilterEvaluator

class TestPDFTemplateSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load test data
        with open("data/data.json") as f:
            cls.test_data = json.load(f)
        with open("data/group_data2.json") as f:
            cls.group_data = json.load(f)
        
        # Initialize filter evaluator with test data
        cls.filter_evaluator = FilterEvaluator(cls.test_data)

    def test_simple_filter(self):
        """Test basic filtering functionality"""
        # Test legacy format
        filter_legacy = "RIC=GOOGL.O"
        result = self.filter_evaluator.filter(filter_legacy)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["RIC"], "GOOGL.O")

        # Test new format
        filter_new = {"RIC": "GOOGL.O"}
        result = self.filter_evaluator.filter(filter_new)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["RIC"], "GOOGL.O")

    def test_complex_filters(self):
        """Test complex filter conditions"""
        # Test AND condition with actual data fields
        filter_and = {
            "and": [
                {"Exchange": "NASDAQ"},
                {"Currency": "USD"}
            ]
        }
        result = self.filter_evaluator.filter(filter_and)
        self.assertTrue(len(result) > 0)
        for item in result:
            self.assertEqual(item["Exchange"], "NASDAQ")
            self.assertEqual(item["Currency"], "USD")

        # Test OR condition
        filter_or = {
            "or": [
                {"Exchange": "NASDAQ"},
                {"Exchange": "COMEX"}
            ]
        }
        result = self.filter_evaluator.filter(filter_or)
        self.assertTrue(len(result) > 0)
        for item in result:
            self.assertIn(item["Exchange"], ["NASDAQ", "COMEX"])

    def test_comparison_operators(self):
        """Test numeric comparison operators"""
        # Test greater than
        filter_gt = {"Ask": {">": 100}}
        result = self.filter_evaluator.filter(filter_gt)
        self.assertTrue(len(result) > 0)
        for item in result:
            if item.get("Ask") is not None:
                self.assertGreater(item["Ask"], 100)

        # Test less than or equal
        filter_lte = {"Volume1": {"<=" : 1000000}}
        result = self.filter_evaluator.filter(filter_lte)
        self.assertTrue(len(result) > 0)
        for item in result:
            if item.get("Volume1") is not None:
                self.assertLessEqual(item["Volume1"], 1000000)

    def test_string_operations(self):
        """Test string operations in filters"""
        # Test contains
        filter_contains = {"RIC": {"contains": "O"}}
        result = self.filter_evaluator.filter(filter_contains)
        self.assertTrue(len(result) > 0)
        for item in result:
            self.assertIn("O", item["RIC"])

        # Test starts with
        filter_starts = {"RIC": {"starts_with": "GOOG"}}
        result = self.filter_evaluator.filter(filter_starts)
        self.assertTrue(len(result) > 0)
        for item in result:
            self.assertTrue(item["RIC"].startswith("GOOG"))

    def test_layout_rendering(self):
        """Test complete layout rendering"""
        layout = {
            "type": "column",
            "children": [
                {
                    "type": "group",
                    "group_name": "company_info",
                    "filter": {
                        "and": [
                            {"market": "NASDAQ"},
                            {"sector": "tech"}
                        ]
                    }
                },
                {
                    "type": "variable",
                    "label": "Company",
                    "key": "name",
                    "group_name": "company_info"
                },
                {
                    "type": "separator",
                    "direction": "vertical",
                    "length": 100,
                    "thickness": 2,
                    "color": "blue",
                    "margin_before": 10,
                    "margin_after": 10
                },
                {
                    "type": "table",
                    "field_map": [
                        {
                            "label": "Market Data",
                            "group": True,
                            "children": [
                                {
                                    "label": "Ticker",
                                    "key": "RIC"
                                },
                                {
                                    "label": "Price",
                                    "key": "price",
                                    "transform": "dollarize"
                                }
                            ]
                        }
                    ],
                    "style": {
                        "col_widths": [80, 100],
                        "font_name": "Helvetica",
                        "font_size": 10,
                        "grid": True
                    }
                }
            ]
        }

        # Test PDF generation
        doc = SimpleDocTemplate("test_output.pdf")
        flowables = interpret_layout(layout, self.test_data)
        doc.build(flowables)

    def test_error_conditions(self):
        """Test error handling"""
        # Test invalid filter (should just return empty list)
        result = self.filter_evaluator.filter({"invalid": {"$invalid": "value"}})
        self.assertEqual(result, [])

        # Test missing data (should just return empty list)
        empty_evaluator = FilterEvaluator([])
        result = empty_evaluator.filter({"RIC": "GOOGL.O"})
        self.assertEqual(result, [])

        # Test missing required fields in layout
        invalid_layout = {
            "type": "column",
            "children": [
                {
                    "type": "group",
                    "group_name": "test_group",
                    "data": []  # Empty data list without filter
                }
            ]
        }
        with self.assertRaises(ValueError):
            interpret_layout(invalid_layout, self.test_data)

    def test_grid_layout(self):
        """Test grid layout with data"""
        layout = {
            "type": "grid",
            "columns": 3,
            "children": [
                {
                    "type": "variable",
                    "label": "Ticker",
                    "key": "RIC"
                },
                {
                    "type": "variable",
                    "label": "Price",
                    "key": "Last",
                    "transform": "dollarize"
                },
                {
                    "type": "variable",
                    "label": "Volume",
                    "key": "Volume1",
                    "transform": "volume_millions"
                }
            ]
        }

        # Test PDF generation
        doc = SimpleDocTemplate("test_grid.pdf")
        flowables = interpret_layout(layout, self.test_data)
        doc.build(flowables)

    def test_transforms(self):
        """Test different transform approaches"""
        layout = {
            "type": "column",
            "children": [
                {
                    "type": "variable",
                    "label": "Price (Predefined)",
                    "key": "Last",
                    "transform": "dollarize"
                },
                {
                    "type": "variable",
                    "label": "Price (Lambda)",
                    "key": "Last",
                    "transform": "lambda x: f'${float(x):,.2f}' if x else '-'"
                },
                {
                    "type": "variable",
                    "label": "Volume (Predefined)",
                    "key": "Volume1",
                    "transform": "volume_millions"
                },
                {
                    "type": "variable",
                    "label": "Volume (Lambda)",
                    "key": "Volume1",
                    "transform": "lambda x: f'{float(x)/1000000:.2f}M' if x else '-'"
                }
            ]
        }

        # Test PDF generation
        doc = SimpleDocTemplate("test_transforms.pdf")
        flowables = interpret_layout(layout, self.test_data)
        doc.build(flowables)

    def test_table_single_level(self):
        """Test table with single-level headers."""
        layout = {
            "type": "column",
            "children": [
                {
                    "type": "table",
                    "field_map": [
                        {"label": "Ticker", "key": "Ticker"},
                        {"label": "RIC", "key": "RIC"},
                        {"label": "Price", "key": "Last", "transform": "dollarize"},
                        {"label": "Volume", "key": "Volume1", "transform": "volume_millions"}
                    ],
                    "style": {
                        "col_widths": [80, 80, 80, 80],
                        "grid": True
                    }
                }
            ]
        }
        data = [
            {"Ticker": "AAPL", "RIC": "AAPL.O", "Last": 175.22, "Volume1": 12500000},
            {"Ticker": "MSFT", "RIC": "MSFT.O", "Last": 420.08, "Volume1": 8900000}
        ]
        layout["data_rows"] = data
        doc = SimpleDocTemplate("single_level_table.pdf")
        flowables = interpret_layout(layout, data)
        doc.build(flowables)
        print("✅ Single-level table test completed")

    def test_table_multi_level(self):
        """Test table with multi-level headers and nested groups."""
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
                                {"label": "Ticker", "key": "Ticker"},
                                {"label": "RIC", "key": "RIC"},
                                {
                                    "label": "Price",
                                    "group": True,
                                    "children": [
                                        {"label": "Ask", "key": "Ask", "transform": "dollarize"},
                                        {"label": "Bid", "key": "Bid", "transform": "dollarize"},
                                        {"label": "Last", "key": "Last", "transform": "dollarize"}
                                    ]
                                },
                                {"label": "Volume", "key": "Volume1", "transform": "volume_millions"},
                                {"label": "Exchange", "key": "Exchange"}
                            ]
                        }
                    ],
                    "style": {
                        "col_widths": [80, 80, 80, 80, 80, 80],
                        "grid": True
                    }
                }
            ]
        }
        data = [
            {"Ticker": "AAPL", "RIC": "AAPL.O", "Ask": 175.25, "Bid": 175.20, "Last": 175.22, "Volume1": 12500000, "Exchange": "NASDAQ"},
            {"Ticker": "MSFT", "RIC": "MSFT.O", "Ask": 420.10, "Bid": 420.05, "Last": 420.08, "Volume1": 8900000, "Exchange": "NASDAQ"}
        ]
        layout["data_rows"] = data
        doc = SimpleDocTemplate("multi_level_table.pdf")
        flowables = interpret_layout(layout, data)
        doc.build(flowables)
        print("✅ Multi-level table test completed")

    def test_table_with_transforms(self):
        """Test table with various transforms applied."""
        layout = {
            "type": "column",
            "children": [
                {
                    "type": "table",
                    "field_map": [
                        {"label": "Ticker", "key": "Ticker"},
                        {"label": "RIC", "key": "RIC"},
                        {"label": "Price", "key": "Last", "transform": "dollarize"},
                        {"label": "Volume", "key": "Volume1|Volume2", "transform": "join_pipes"}
                    ],
                    "style": {
                        "col_widths": [80, 80, 80, 80],
                        "grid": True
                    }
                }
            ]
        }
        data = [
            {"Ticker": "AAPL", "RIC": "AAPL.O", "Last": 175.22, "Volume1": 12500000, "Volume2": 12500000},
            {"Ticker": "MSFT", "RIC": "MSFT.O", "Last": 420.08, "Volume1": 8900000, "Volume2": 8900000}
        ]
        layout["data_rows"] = data
        doc = SimpleDocTemplate("table_with_transforms.pdf")
        flowables = interpret_layout(layout, data)
        doc.build(flowables)
        print("✅ Table with transforms test completed")

if __name__ == '__main__':
    unittest.main() 