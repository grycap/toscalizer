import json
import argparse
import os


def get_higher_severity(input_data):
    """
    Get the highest severity of the vulnerabilities.
    """
    SeverityMap = {
        "CRITICAL": 5,
        "HIGH": 4,
        "MEDIUM": 3,
        "LOW": 2,
        "UNKNOWN": 1,
        "N/A": 0
    }
    severity = [SeverityMap[vuln] for vuln in input_data]
    high_serverity = max(severity)
    return list(SeverityMap.keys())[list(SeverityMap.values()).index(high_serverity)]

def main():
    parser = argparse.ArgumentParser(description='Process input JSON and output to specified JSON file with the highest severity.')
    parser.add_argument('input_file', type=str, help='Input JSON files', nargs='+')
    parser.add_argument('output_file', type=str, help='Output JSON file')

    args = parser.parse_args()
    
    # Read the input JSON files
    severities = []
    for input_file in args.input_file:
        with open(input_file, 'r') as infile:
            severities.append(json.load(infile)['HighSeverity'])
    high_serverity = get_higher_severity(severities)
    output_data = {"HighSeverity": high_serverity}
    # Write the output JSON file
    output_file = os.path.expanduser(args.output_file)
    with open(output_file, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)

if __name__ == '__main__':
    main()
