# Linux Server Configuration

This project was to set up a LAPP stack (Linux, Apache, PostgreSQL, Python) and deploy an application previously developed for a different environment. It uses the following technologies:
* Ubuntu Linux
* Amazon Lightsail
* Apache HTTP Server + mod_wsgi
* Python
* PostgreSQL
* tmux

I configured a few things to make this setup more secure including:
* Disabled root login
* SSH over non-standard ports
* SSH using keys only
* Setup Postgres role with limited privileges
* OS firewall rules using `ufw`

# Usage
* Navigate to http://184.72.188.160
* Login using Google credentials
* Use the catalogue! More details [here](https://github.com/adanilev/udacity/tree/master/4_item_catalogue)

*NOTE:* The IP address above is temporary and the server will be shutdown once this assignment is marked. Cheers - Alex (8 April 2017)
