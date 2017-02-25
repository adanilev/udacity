def basic_db_query:
    import sqlite3

    # Create connection
    db = sqlite3.connect("students")
    # Get the cursor so we can query and look at results
    c = db.cursor()
    # Define quert
    query = "select name, id from students;"
    # The cursor executes it
    c.execute(query)
    # Get the resulting table from the cursor
    rows = c.fetchall()

    # First, what data structure did we get?
    print "Row data:"
    print rows

    # And let's loop over it too:
    print
    print "Student names:"
    for row in rows:
      print "  ", row[0]

    # Execute an insert
    c.execute("insert into students values ('Jim Jones', '3838485') ")
    # Commit the transaction to the DB (not the cursor) for the insert to take
    # effect
    db.commit()

    db.close()
