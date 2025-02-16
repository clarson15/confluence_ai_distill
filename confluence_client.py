import http.client
import json
from confluence_parser import ConfluenceParser

class ConfluenceClient():
    def __init__(self, base_url, api_key):
        if not base_url:
            raise ValueError("base_url is required")
        if not api_key:
            raise ValueError("api_key is required")
        
        self.base_url = base_url
        self.api_key = api_key
        self.connection = http.client.HTTPSConnection(base_url)
        self.headers = {
            'Authorization': f'Bearer {api_key}'
        }
        self.parser = ConfluenceParser(base_url)
    
    def get_pages_in_space(self, space):
        pages = []
        nextPage = f'/rest/api/space/{space}/content/page'
        while nextPage:
            self.connection.request("GET", nextPage, headers=self.headers)
            response = self.connection.getresponse()
            data_raw = response.read()
            data = json.loads(data_raw)
            nextPage = data["_links"]["next"] if "_links" in data and "next" in data["_links"] else None
            for item in data["results"]:
                if item["type"] == "page":
                    pages.append((item["title"], item["id"]))    
        return pages
    
    def get_page_content(self, page_id):
        self.connection.request("GET", f'/rest/api/content/{page_id}?expand=body.styled_view', headers=self.headers)
        response = self.connection.getresponse()
        data_raw = response.read()
        data = json.loads(data_raw)
        return f'# {data["title"]}\n{self.parser.feed(data["body"]["styled_view"]["value"])}'
    
