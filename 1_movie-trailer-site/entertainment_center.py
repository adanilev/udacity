import media
import fresh_tomatoes

# This is the file that is run to launch the Movie Trailer site

# First, create all of the Movie instances and set their properties
# N.B. many of the links run across multiple lines so that they are all are <80
# characters as per Google's Python Style Guide
m1 = media.Movie('Star Trek: Generations',
    'http://cdn2us.denofgeek.com/sites/denofgeekus/files/'
    'generations_poster.jpg',
    'https://www.youtube.com/watch?v=MUieGh1fHSI')

m2 = media.Movie('Star Trek: First Contact',
    'http://www.megabearsfan.net/image.axd?picture=2011%2F5%2FSTFirstContact_po'
    'ster_540x768.jpg',
    'https://www.youtube.com/watch?v=YQ1eiEvefKI')

m3 = media.Movie('Star Trek: Insurrection',
    'https://upload.wikimedia.org/wikipedia/en/thumb/3/3c/Star_Trek_Insurrectio'
    'n.png/220px-Star_Trek_Insurrection.png',
    'https://www.youtube.com/watch?v=N1XmtdMZdL8')

m4 = media.Movie('Star Trek: Nemesis',
    'https://upload.wikimedia.org/wikipedia/en/9/9c/Star_Trek_Nemesis_poster'
    '.jpg',
    'https://www.youtube.com/watch?v=KFUjGFpW7OI')

# Now add them to an array so we can pass to a function.
movies = [m1,m2,m3,m4]

# Finally, pass the array to the function which will generate an HTML file
# and open it in your default browser. It creates a page that shows the list of
# movies we defined above.
fresh_tomatoes.open_movies_page(movies)
