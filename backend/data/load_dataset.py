from sklearn.datasets import fetch_20newsgroups
from sklearn.datasets._twenty_newsgroups import strip_newsgroup_header, strip_newsgroup_footer, strip_newsgroup_quoting

def load_newsgroups_data(subset='train', categories=None):
    # Fetch raw data without slow stripping filters
    newsgroups = fetch_20newsgroups(
        subset=subset,
        categories=categories
    )

    # limit dataset first to reduce processing overhead and memory usage
    raw_data = newsgroups.data[:200]
    targets = newsgroups.target[:200]

    # Apply stripping filters only to the selected subset of documents
    processed_data = []
    for doc in raw_data:
        doc = strip_newsgroup_header(doc)
        doc = strip_newsgroup_quoting(doc)
        doc = strip_newsgroup_footer(doc)
        processed_data.append(doc)

    return processed_data, targets, newsgroups.target_names