# Swiss Tournament Database & Functions

These files construct a database to store players and the results of matches they've played. It also provides functions to run a swiss-style tournament by giving the players current standings and a list of the pairings for the next round. Uses:
* PostgreSQL
* Python

## The files
* `tournament.py` is where all the python functions to manipulate the DB live
* `tournament_test.py` is where some test functions live
* `tournament.sql` is where the commands to destroy and re-create the DB live. Running this will *wipe* any existing data and build a blank DB.

## To run
* Setup VirtualBox and Vagrant
* Install the VM in this parent's parent (grandparent?) folder `FSND-Virtual-Machine`
* Start and login to the VM
* Navigate to the project's directory
  * `cd /vagrant/tournament`
* Open PostgreSQL and setup the database and tables
  * `psql`
  * `\i tournament.sql`
* Quit psql (or login in a different session) and run the test suite
  * `\q`
  * `python tournament_test.py`
* Or read and play with all the functions used to manipulate the DB which are located in `tournament.py`
