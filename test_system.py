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

if __name__ == '__main__':
    unittest.main() 