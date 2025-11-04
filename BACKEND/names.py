import csv
with open("data/essential_data.csv", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader)
print(headers)
