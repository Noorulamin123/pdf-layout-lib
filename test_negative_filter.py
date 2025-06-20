#!/usr/bin/env python3

import json
from layout_lib.filter_utils import apply_filter

# Test data
test_data = [
    {"RIC": "AAPL.O", "Ticker": "AAPL", "Price": 175.22},
    {"RIC": "MSFT.O", "Ticker": "MSFT", "Price": 420.08},
    {"RIC": "GOOGL.O", "Ticker": "GOOGL", "Price": 180.48},
    {"RIC": "TSLA.O", "Ticker": "TSLA", "Price": 185.68}
]

# Test negative filter
negative_filters = ["RIC=GOOGL.O"]

print("🔍 Testing Negative Filter Logic")
print("=" * 50)
print(f"📊 Original data ({len(test_data)} objects):")
for i, obj in enumerate(test_data):
    print(f"  {i}: {obj['RIC']} - {obj['Ticker']}")

print(f"\n🔍 Negative filters: {negative_filters}")
print("\n🔍 Processing each negative filter:")

excluded_indices = set()

for filter_condition in negative_filters:
    print(f"\n  Processing: {filter_condition}")
    filtered_data = apply_filter(test_data, filter_condition)
    print(f"  Objects matching this filter: {len(filtered_data)}")
    
    for i, obj in enumerate(test_data):
        if obj in filtered_data:
            excluded_indices.add(i)
            print(f"    → Excluding object {i}: {obj['RIC']}")

print(f"\n🔍 Excluded indices: {excluded_indices}")

# Keep only objects that were NOT excluded
remaining_data = [obj for i, obj in enumerate(test_data) if i not in excluded_indices]

print(f"\n📋 Remaining data ({len(remaining_data)} objects):")
for i, obj in enumerate(remaining_data):
    print(f"  {i}: {obj['RIC']} - {obj['Ticker']}")

print("\n✅ Test completed!") 