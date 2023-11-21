import requests
from bs4 import BeautifulSoup, NavigableString


def parse_html(url):
    """
    parse the html using the url, and return the content with relevant information and mark-ups
    :param url: str
    :return: str
    """
    # print(url)
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    output = ""

    page_title = process_text(html.title.text)
    output += f"<title> {page_title}\n"
    page_descr = html.find(class_="va-introtext")
    if page_descr:
        page_descr = process_text(html.find(class_="va-introtext").text)
        output += f"<descriptor> {page_descr}\n"

    if html.find('table'):
        print("TABLE!!")
        table_content = parse_table(html)
        for row in table_content:
            output += f"<content> {row}\n"

        for tab in html.select('table'):
            tab.extract()

    h2_headers = html.select('h2')
    if len(h2_headers) == 0:
        return output

    if len(h2_headers) > 1:
        h2_pairs = [(h2_headers[i].text, h2_headers[i+1].text) for i in range(len(h2_headers)-1)]

        for header1, header2 in h2_pairs:
            processed_header = process_text(header1)
            output += f"<topic> {processed_header}\n"
            text_inbetween = ' '.join(text for text in between_h2(html.find("h2", string=header1), html.find("h2", string=header2)))
            output += f"<content> {text_inbetween}\n"

    if h2_headers:
        processed_header = process_text(h2_headers[-1].text)
        output += f"<topic> {processed_header}\n"
        cur = html.find('h2', string=h2_headers[-1].text).next_sibling
        if not isinstance(cur.next_element, str):
            text_last = cur.next_element.text
            text_last = process_text(text_last)
            output += f"<content> {text_last}\n\n"

    return output


def between_h2(cur, end):
    while cur and cur != end:
        if isinstance(cur, NavigableString):
            text = cur.strip()
            if len(text):
                yield text
        cur = cur.next_element


def parse_table(html):
    table_content = []
    for tr in html.find('table').find_all('tr'):
        row = [td.text.strip() for td in tr.find_all("dfn")]
        if len(row) > 0:
            table_content.append(" ".join(row))
    return table_content


def process_text(text):
    return text.strip().replace('\n', ' ')  # may need additional processing. But should be good for now
