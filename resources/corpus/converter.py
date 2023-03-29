import argparse
import json
import yaml

# create argument parser for input and output files
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True, help='Input file in YAML format')
parser.add_argument('-o', '--output', required=True, help='Output file in JSON format')
args = parser.parse_args()

# open input file and load YAML data
with open(args.input, 'r') as f:
    yaml_data = yaml.safe_load(f)

# convert YAML data to JSON format
json_data = json.dumps(yaml_data)

# write JSON data to output file
with open(args.output, 'w') as f:
    f.write(json_data)
