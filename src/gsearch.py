from googlesearch import search

def Gsearch(query):
    try:
        url = ""
        url_list = []
        for i in search(query,lang="en", num_results=10):
            url_list.append(i)

        #store stackoverflow URL
        for u in url_list:
            if "stackoverflow" in u:
                url = u

        url_list.clear()
        return url
    except Exception as e:
            raise RuntimeError(f"API request failed: {str(e)}")
