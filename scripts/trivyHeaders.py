import json
import argparse
import os

# Define the headers to be retained
HEADERS = {
    "SchemaVersion", "CreatedAt", "ArtifactName", "ArtifactType", 
    "Results", "Target", "Class", "Type", "Vulnerabilities", 
    "VulnerabilityID", "PkgName", "InstalledVersion", "FixedVersion", 
    "Status", "PrimaryURL", "Title", "Description", "Severity", 
    "PublishedDate"
}

def filter_dict(d, headers):
    """
    Recursively filter the dictionary to retain only the specified headers.
    """
    if isinstance(d, dict):
        return {k: filter_dict(v, headers) for k, v in d.items() if k in headers}
    elif isinstance(d, list):
        return [filter_dict(item, headers) for item in d]
    else:
        return d

def process_data(input_data):
    """
    Process the input data to retain only the specified headers.
    """
    return filter_dict(input_data, HEADERS)

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
    high_serverity = 0
    for result in input_data["Results"]:
        vulnerabilities = result["Vulnerabilities"]
        if vulnerabilities:
            severity = [SeverityMap[vuln["Severity"]] for vuln in vulnerabilities]
            local_max = max(severity)
            if local_max > high_serverity:
                high_serverity = local_max
    return list(SeverityMap.keys())[list(SeverityMap.values()).index(high_serverity)]

def main():
    parser = argparse.ArgumentParser(description='Process input JSON and output to specified JSON file with specific headers.')
    parser.add_argument('input_file', type=str, help='Input JSON file')
    parser.add_argument('output_file', type=str, help='Output JSON file')

    args = parser.parse_args()
    
    # Read the input JSON file
    with open(args.input_file, 'r') as infile:
        input_data = json.load(infile)
    
    # Process the data
    output_data = process_data(input_data)
    
    high_serverity = get_higher_severity(output_data)
    output_data["HighSeverity"] = high_serverity

    # Write the output JSON file
    output_file = os.path.expanduser(args.output_file)
    with open(output_file, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)
    
    print(f"Processed JSON saved to {output_file}")

if __name__ == '__main__':
    main()
