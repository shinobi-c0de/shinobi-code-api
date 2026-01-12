from googlesearch import search


def Gsearch(query: str) -> str | None:
    try:
        results = [str(url) for url in search(query, lang="en", num_results=10)]
        stackoverflow_urls = [url for url in results if "stackoverflow" in url]
        return stackoverflow_urls[0] if stackoverflow_urls else None
    except Exception as e:
        raise RuntimeError(f"API request failed: {str(e)}")
