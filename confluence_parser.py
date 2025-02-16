from html.parser import HTMLParser

class ConfluenceParser(HTMLParser):
    def __init__(self, base_href=''):
        super().__init__()
        self.base_href = base_href
        self.content = ""
        self.ignore_data = False
        self.href = None
        self.depth = 0
        self.new_line = False
        self.bold = False
        self.heading_level = 0
        self.table_row = -1
        self.table_column = -1
        self.table_header_row = False
        self.display_table_label = False
        self.display_table_row = False
        self.display_table_body = False
    
    def feed(self, data):
        self.content = ""
        super().feed(data)
        return self.content

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag, attrs)
        attrsDict = dict(attrs)
        match tag:
            case "style":
                self.ignore_data = True
                pass
            case "br":
                self.new_line = True
            case "p":
                self.new_line = True
            case "ul":
                self.depth += 1
            case "li":
                self.new_line = True
            case "strong":
                self.bold = True
            case "b":
                self.bold = True
            case "a":
                if "href" in attrsDict:
                    self.href = attrsDict["href"]
            case "h1":
                self.heading_level = 1
                self.new_line = True
            case "h2":
                self.heading_level = 2
                self.new_line = True
            case "h3":
                self.heading_level = 3
                self.new_line = True
            case "h4":
                self.heading_level = 4
                self.new_line = True
            case "h5":
                self.heading_level = 5
                self.new_line = True
            case "h6":
                self.heading_level = 6
                self.new_line = True
            case "table":
                self.display_table_label = True
            case "tr":
                self.table_row += 1
                self.table_column = -1
                self.new_line = True
                self.display_table_row = True
            case "td":
                self.table_column += 1
                self.display_table_body = True
                self.new_line = True
            case "th":
                self.table_column += 1
                self.display_table_body = True
                self.new_line = True
            case "thead":
                self.table_header_row = True
                self.table_row = -1
                self.table_column = -1
            case "tbody":
                self.table_header_row = False
                self.table_row = 0
                self.table_column = -1
            case _:
                pass


    def handle_endtag(self, tag):
        self.ignore_data = False
        if tag == "ul":
            self.depth -= 1

    def handle_data(self, data):
        if self.ignore_data:
            return
        
        depth_prefix = "-" * self.depth
        display_href = None
        if self.href and self.href != data:
            if self.href.startswith("http"):
                display_href = self.href
            else:
                display_href = self.base_href + self.href
            self.href = None
        if self.new_line:
            self.content += "\n" + depth_prefix
            self.new_line = False
        if self.heading_level:
            self.content += "#" * self.heading_level + " "
            self.heading_level = 0
        if self.display_table_label:
            self.content += f"Table:\n{depth_prefix}"
            self.display_table_label = False
        if self.display_table_row:
            if self.table_header_row:
                self.content += f"Headings:\n{depth_prefix}"
                self.table_header_row = False
            else:
                self.content += f"Row {self.table_row}:\n{depth_prefix}"
            self.display_table_row = False
        if self.display_table_body:
            self.content += f"Column {self.table_column}: "
            self.display_table_body = False
        if self.bold:
            self.content += "**"
        if display_href:
            self.content += '['
        self.content += data.strip().replace("\n", f"\n{depth_prefix}")
        if self.bold:
            self.content += "**"
            self.bold = False
        if display_href:
            self.content += f']({display_href})'
        self.content += " "