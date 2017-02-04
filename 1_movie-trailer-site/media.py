import fresh_tomatoes

class Movie():
    """This Movie class defines an object with the properties needed to display
    them in our movie trailer website.
    """
    def __init__(self, title, poster_image_url, trailer_youtube_url):
        """init's arguments are the movie's title, a link to the movie poster
        and a YouTube link to the trailer.
        """
        self.title = title
        self.poster_image_url = poster_image_url
        self.trailer_youtube_url = trailer_youtube_url
