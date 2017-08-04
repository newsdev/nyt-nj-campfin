import csv
from fuzzywuzzy import fuzz

results = []

with open('/Users/208301/aggregate_property_contribs.csv', 'r') as f:
    with open('/Users/208301/property_contracts.csv', 'r') as g:
        contracts = []
        contribs_reader = csv.reader(f)
        contracts_reader = csv.reader(g)
        next(contracts_reader)
        for row in contracts_reader:
            contracts.append(row)

        next(contribs_reader)
        for row in contribs_reader:
            best_match = ''
            best_match_amount = -1
            best_score = 0
            for contract in contracts:
                score = fuzz.ratio(row[0], contract[0])
                if score > best_score and score > 75:
                    best_match = contract[0]
                    best_score = score
                    best_match_amount = contract[4]

            new_row = row + [best_match, best_match_amount]
            results.append(new_row)

with open('/Users/208301/aggregate_property_contribs_matched.csv', 'w') as h:
    writer = csv.writer(h)
    writer.writerows(results)