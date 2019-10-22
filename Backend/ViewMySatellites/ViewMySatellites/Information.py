from requests import get
from contextlib import closing
from bs4 import BeautifulSoup


class Information:
    """
    Represents information of a satellite extracted from the www.n2yo.com website
    """

    # Code of the satellite
    code = ''

    # Launch date of the satellite
    launch_date = ''

    # Country of origin of the satellite
    source = ''

    # Launch site of the satellite
    launch_site = ''

    def __init__(self, code):
        """
        Creates an Information object from the given satellite code
        :param code: code of the satellite
        """

        # Appends the code to the url parameter
        url = 'https://www.n2yo.com/satellite/?s=' + code

        # Obtains the raw content from the website
        with closing(get(url, stream=True)) as resp:
            content_type = resp.headers['Content-Type'].lower()
            if resp.status_code == 200 and content_type is not None and content_type.find('html') > -1:
                response = resp.content
            else:
                response = None
                print("Error")

        # Parse the raw content in to a BeautifulSoup object
        html = BeautifulSoup(response, 'html.parser')

        # Find the date item
        date_item = html.find('a', {'class': 'showTip rcs'}).find_next('b').next_sibling.next_sibling

        # Obtain the text within the date item
        self.launch_date = date_item.text

        # Obtain the source item
        source_item = date_item.find_next('b')

        # Obtain and parse the text after the source item
        self.source = source_item.next_sibling.split(':')[1].strip()

        # Obtain and parse the text after the launch site item
        self.launch_site = source_item.find_next('b').next_sibling.split(':')[1].strip()

        # Store the code
        self.code = code

    def __str__(self):
        return 'Satellite code: ' + self.code + 'Launch date: ' + self.launch_date + '\nSource: ' \
                + self.source + '\nLaunch site: ' + self.launch_site
