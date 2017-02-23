# Fancy Blog

This is an example of a basic blog built using Google AppEngine, Python, Jinja2 and Bootstrap. It's functionality includes:
* User creation
* Storing salted and hashed passwords
* Create new posts
* Uses cookies to identify user
* Commenting and liking
* Much, much more! (not really)

You can access by going here: [https://fancy-blog.appspot.com/blog](https://fancy-blog.appspot.com/blog)

To deploy and run yourself
0. Download the files in this folder (/3_blog_app)
0. Get a [Google Cloud Platform account](https://cloud.google.com/)
0. [Install the SDK](https://cloud.google.com/sdk/downloads) and follow the directions to initialise
0. To run locally, navigate to the directory with the files
..0. Run `dev_appserver.py .`
0. To deploy, create a Google Cloud project
0. Deploy using the command `gcloud app deploy`
0. Upload the index file manually to be sure: `gcloud app deploy index.yaml`
0. Open using the command `gcloud app browse`
