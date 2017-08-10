import csv
import sys
import string
from fuzzywuzzy import fuzz

import pdb

# '/Users/208301/aggregate_property_contribs.csv'
# '/Users/208301/aggregate_property_contribs_matched.csv'
CONTRACTORS_FILE = '/Users/208301/property_contracts.csv'
def match_contractors(contractors_file, match_file, match_col, match_threshold):
    results = []

    with open(match_file, 'r') as f:
        with open(contractors_file, 'r') as g:
            contracts = []
            contribs_reader = csv.reader(f)
            contracts_reader = csv.reader(g)
            next(contracts_reader)
            for row in contracts_reader:
                contracts.append(row)

            header = next(contribs_reader)
            for row in contribs_reader:
                best_match = ''
                best_match_amount = -1
                best_score = 0
                for contract in contracts:
                    translator = str.maketrans('', '', string.punctuation)
                    contractor_name = contract[0].translate(translator).lower()
                    match_name = row[match_col].translate(translator).lower()
                    score = fuzz.ratio(match_name, contractor_name)
                    if score > best_score and score > match_threshold:
                        best_match = contract[0]
                        best_score = score
                        best_match_amount = contract[4]
                
                new_row = row + [best_match, best_match_amount]
                results.append(new_row)
    return results

def main():
    results = match_contractors(CONTRACTORS_FILE, sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    with open(sys.argv[4], 'w') as h:
        writer = csv.writer(h)
        writer.writerows(results)

if __name__=='__main__':
    main()