import http.client
import json
import os
import datetime
import re
import traceback
from markitdown import MarkItDown

class ConfluenceClient():
    def __init__(self, base_url, api_key, debug=False):
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
        self.debug = debug
        self.markdown = MarkItDown()
    
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
    
    def get_page_content(self, page: str) -> str:
        if self.debug:
            print(f"Getting content for page {page}")
        page_id = page

        if page.startswith(self.base_url):
            self.connection.request("GET", page.removeprefix(self.base_url), headers=self.headers)
            response = self.connection.getresponse()
            if response.status != 200:
                return f"Failed to get content for page {page}"
            data = json.loads(response.read())
            pattern = r'<meta\s+[^>]*name=["\']ajs-page-id["\'][^>]*content=["\'](\d+)["\']'
            page_id = re.search(pattern, data["body"]["export_view"]["value"])
        
        self.connection.request("GET", f'/rest/api/content/{page_id}?expand=body.export_view', headers=self.headers)
        response = self.connection.getresponse()
        if response.status != 200:
            return f"Failed to get content for page {page_id}"
        data = json.loads(response.read())
        content = self._markdown(data["body"]["export_view"]["value"])
        
        if self.debug:
            print(f"Content for page {page}: {content}")
        return f'# Title\n{data["title"]}\n# Content\n{content}'
    
    def get_page_children(self, page: str):
        if self.debug:
            print(f"Getting children for page {page}")
        page_id = page

        if page.startswith(self.base_url):
            self.connection.request("GET", page.removeprefix(self.base_url), headers=self.headers)
            response = self.connection.getresponse()
            if response.status != 200:
                return f"Failed to get children for page {page}"
            data = response.read()
            pattern = r'<meta\s+[^>]*name=["\']ajs-page-id["\'][^>]*content=["\'](\d+)["\']'
            page_id = re.search(pattern, data)

        self.connection.request("GET", f'/rest/api/content/{page_id}/child/page', headers=self.headers)
        response = self.connection.getresponse()
        if response.status != 200:
            return f"Failed to get children for page {page}"
        data_raw = response.read()
        data = json.loads(data_raw)
        children = []
        for item in data["results"]:
            children.append((item["title"], item["id"]))
        
        if self.debug:
            print(f"Children for page {page}: {children}")

        return children
    
    def _markdown(self, html):
        if html.strip() == "":
            return "This page is empty."
        
        try:
            page = f'{datetime.datetime.now().microsecond}.html'
            with open(f'/tmp/{page}', 'w+') as file:
                file.write(html)
            content = self.markdown.convert(f'/tmp/{page}').text_content
            os.remove(f'/tmp/{page}')
            return content
        except Exception as e:
            return f"{traceback.format_exc()}: Failed to convert content to markdown."