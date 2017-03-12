# Item Catalogue
This project creates a site that allows users to Create, Read, Update and Delete items in a catalogue. Users authenticate with a Google account using OAuth 2.0. It uses Python, Flask, Jinja2 templates, Bootstrap and an SQLite database.

## Installation
To access:
1. Install Vagrant and VirtualBox
1. Clone/copy this directory
1. Navigate to the `vagrant` directory where the `Vagrantfile` is located
1. Issue the following commands:
    * `vagrant up`
    * `vagrant ssh`
    * `cd /vagrant/catalog`
    * `python database_setup.py`
    * Populate with dummy data (optional): `python populate_db.py`
    * `python project.py`
1. If you get an error about something like `ImportError: No module named packaging.version`, you'll need to reinstall pip. Issue is described [here](https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1658844) and the solution in comments 12 and 14 on that page
1. Open a browser and go to: http://localhost:5000

## Usage
Get the VM installed and web server running as described above:
* Access the site and login using a Google account
* Create a category
* Click on that category and create items
* Open an item you created and edit or delete it
* Download a JSON of the whole catalogue by calling localhost:5000/rest/catalogue
* Log out or log in with a different Google account and note that you're not able to edit or delete items created previously