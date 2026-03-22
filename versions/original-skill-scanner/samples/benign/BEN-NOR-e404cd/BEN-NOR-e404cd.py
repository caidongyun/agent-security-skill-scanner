import csv
import json

def csv_to_json(input_file, output_file):
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    csv_to_json("input.csv", "output.json")
