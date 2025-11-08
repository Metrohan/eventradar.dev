import dateparser

test_dates = [
    "19/11/2025",
    "23/10/2025",
    "10/9/2025",
    "15.12.2025",
]

print("=== Dateparser Test ===")
for date_str in test_dates:
    parsed = dateparser.parse(str(date_str), languages=['tr', 'en'])
    print(f"'{date_str}' -> {parsed} (tür: {type(parsed)})")
