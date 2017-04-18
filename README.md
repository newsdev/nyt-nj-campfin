# nyt-nj-campfin
Scrapers for NJ campaign finance data

Currently just listing filings by candidates who have filed for governor in 2017.

## Usage
Dump JSON with info about governor's election filings:
```
get_filing_list > filings.json
```

This command produces JSON of the following format:

```
[{"name" : candidate_name,
  "date" : filing_date,
  "form" : form_type,
  "period" : filing_period,
  "amendment" : amendment_number,
  "doc_id" : document_id_from_download_url
  }
  ...]

```

For example:

```
[
    {"date": "01/18/2017",
    "period": "0",
    "form": "D-1",
    "amendment": "1",
    "doc_id": "lRTrsnVg6%2b4%3d",
    "name": "LESNIAK, RAYMOND J"},
    {"date": "01/06/2017",
    "period": "0",
    "form": "D-1",
    "amendment": "0",
    "doc_id": "a9HjeNwNbRQ%3d",
    "name": "LESNIAK, RAYMOND J"},
    {"date": "01/12/2017",
    "period": "0",
    "form": "D-1",
    "amendment": "0",
    "doc_id": "plBeOeEX704%3d",
    "name": "GUADAGNO, KIMBERLY"},
    {"date": "01/12/2017",
    "period": "0",
    "form": "DX",
    "amendment": "0",
    "doc_id": "%2bna3eeIdDWs%3d",
    "name": "GUADAGNO, KIMBERLY"}
]

```

## Heads up
The website does not do well under load, I recommend against running this script frequently.
