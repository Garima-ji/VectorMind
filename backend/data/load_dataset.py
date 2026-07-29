from sklearn.datasets import fetch_20newsgroups
from sklearn.datasets._twenty_newsgroups import strip_newsgroup_header, strip_newsgroup_footer, strip_newsgroup_quoting

def load_newsgroups_data(subset='train', categories=None):
    """
    Load the 20 Newsgroups dataset and pre-process documents.
    
    JUSTIFICATION FOR PRE-PROCESSING DECISIONS:
    The 20 Newsgroups dataset contains email headers (e.g., subject, sender, organization), 
    quoting signatures, and reply headers which are extremely noisy. If not discarded, 
    the model might align queries with email addresses, headers, or repeated reply quotes 
    rather than the actual message contents. To enforce clean semantic search on primary texts,
    we use scikit-learn's standard filters to strip headers, quotes, and footers.
    """
    newsgroups = fetch_20newsgroups(
        subset=subset,
        categories=categories
    )

    raw_data = newsgroups.data
    targets = newsgroups.target

    # Apply stripping filters to all loaded documents
    processed_data = []
    for doc in raw_data:
        doc = strip_newsgroup_header(doc)
        doc = strip_newsgroup_quoting(doc)
        doc = strip_newsgroup_footer(doc)
        processed_data.append(doc)

    return processed_data, targets, newsgroups.target_names