import fresh_tomatoes

# This Movie class defines an object with the properties needed to display them
# in our movie trailer website
class Movie():
    
    # The constructor is the only function at the moment.
    def __init__(self, title, poster_image_url, trailer_youtube_url):
        self.title = title
        self.poster_image_url = poster_image_url
        self.trailer_youtube_url = trailer_youtube_url
