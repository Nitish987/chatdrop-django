from bs4 import BeautifulSoup
from requests import get as get_request

class LinkPreviewService:
    def __init__(self, url):
        self.url = url

    def initialize(self):
        response = get_request(self.url)
        self.html = BeautifulSoup(response.content, 'html.parser')

    def __get_title(self):
        """Scrape page title."""
        title = None
        if self.html.title.string:
            title = self.html.title.string
        elif self.html.find("meta", property="og:title"):
            title = self.html.find("meta", property="og:title").get('content')
        elif self.html.find("meta", property="twitter:title"):
            title = self.html.find("meta", property="twitter:title").get('content')
        elif self.html.find("h1"):
            title = self.html.find("h1").string
        return title
    
    def __get_description(self):
        """Scrape page description."""
        description = None
        if self.html.find("meta", property="description"):
            description = self.html.find("meta", property="description").get('content')
        elif self.html.find("meta", property="og:description"):
            description = self.html.find("meta", property="og:description").get('content')
        elif self.html.find("meta", property="twitter:description"):
            description = self.html.find("meta", property="twitter:description").get('content')
        elif self.html.find("p"):
            description = self.html.find("p").contents
        return description
    
    def __get_image(self):
        """Scrape page image."""
        image = None
        if self.html.find("meta", property="image"):
            image = self.html.find("meta", property="image").get('content')
        elif self.html.find("meta", property="og:image"):
            image = self.html.find("meta", property="og:image").get('content')
        elif self.html.find("meta", property="twitter:image"):
            image = self.html.find("meta", property="twitter:image").get('content')
        elif self.html.find("img", src=True):
            image = self.html.find_all("img").get('src')
        return image

    @staticmethod
    def generate_link_preview(url: str) -> dict:
        link_preview = LinkPreviewService(url)
        link_preview.initialize()

        title = link_preview.__get_title()
        description = link_preview.__get_description()
        image = link_preview.__get_image()

        return {
            'title': title,
            'description': description,
            'image': image,
            'url': url,
        }