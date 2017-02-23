# Fancy Blog

This is an example of a basic blog built using Google AppEngine, Python, Jinja2 and Bootstrap. Functionality includes:
* User creation
* Storing salted and hashed passwords
* Create new posts
* Uses cookies to identify user
* Commenting and liking
* Much, much more! (not really)

You can check it out here: [https://fancy-blog.appspot.com/blog](https://fancy-blog.appspot.com/blog)
* **Note** You may have to tell your browser to load unsafe scripts. That's because JavaScript files are required for some animations and the site isn't really https.

To deploy and run yourself:
* Download the files in this folder (/3_blog_app)
* Get a [Google Cloud Platform account](https://cloud.google.com/)
* [Install the SDK](https://cloud.google.com/sdk/downloads) and follow the directions to initialise
* To run locally, navigate to the directory with the files
  * Run `dev_appserver.py .`
* To deploy, create a Google Cloud project
  * Deploy using the command `gcloud app deploy`
  * Upload the index file manually to be sure: `gcloud app deploy index.yaml`
  * Open using the command `gcloud app browse`
