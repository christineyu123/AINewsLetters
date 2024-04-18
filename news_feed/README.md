### Module Usage
#### Entrypoint
```python
from news_feed.application.ai_feed import main as rss_feed

## Option 1 Add a .env file to the root of the project
#### It may have the following variable NUM_DAYS_OLD=<Number of days prior to today from when to fetch articles>
documents_all = rss_feed()

## Option 2 Pass the number of days as an argument
documents_all = rss_feed(3) # This will fetch articles that are a maximum of 3 days old
```
`documents_all` is a list of `langchain_core.documents.base.Document` objects.   
Each document has the following attributes that are needed downstream:
- `metadata`: This is metadata about the page content, for example: title, source, etc.
- `page_content`: This is the string content of the page and contains the text of the article.

#### Example
```python
## Assuming the summary of the article is computed through a method called summarize()
for document in documents_all:
    summary = summarize(document.page_content)
    print(summary)
```