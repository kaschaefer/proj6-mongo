"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates: 
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will 
   - User input/output is in local (to the server) time.  
"""

import flask
from flask import g
from flask import render_template
from flask import request
from flask import url_for
from bson.objectid import ObjectId

import json
import logging

import sys

# Date handling 
import arrow   
from dateutil import tz  # For interpreting local times

# Mongo database
from pymongo import MongoClient

import config
CONFIG = config.configuration()


MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    CONFIG.DB_USER,
    CONFIG.DB_USER_PW,
    CONFIG.DB_HOST, 
    CONFIG.DB_PORT, 
    CONFIG.DB)


print("Using URL '{}'".format(MONGO_CLIENT_URL))


###
# Globals
###

app = flask.Flask(__name__)
app.secret_key = CONFIG.SECRET_KEY

####
# Database connection per server process
###

try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, str(CONFIG.DB))
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)



###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Main page entry")
  g.memos = get_memos()
  for memo in g.memos: 
      app.logger.debug("Memo: " + str(memo))
  return flask.render_template('index.html')


# We don't have an interface for creating memos yet
@app.route("/create")
def create():
    app.logger.debug("Create")
    return flask.render_template('create.html')

@app.route("/add_memo")
def add_memo():
    """
    Take inputs from create page and generate new DB entry
    """
    app.logger.debug("Creating a new memo")
    rslt = add_new_memo("dated_memo", request.args.get('date', type=str), memo_text = request.args.get('memo_text', type=str))
    return flask.jsonify(result=rslt)

def add_new_memo(memo_type, memo_date, memo_text):
    """
    Helper function to create new memo
    """
    record = { "type": memo_type,
        "date": memo_date,
        "text": memo_text
    }
    try:
        inserted = collection.insert_one(record)
        _id = inserted.inserted_id.valueOf()
        rslt = True
    except:
        app.logger.debug("Deletion of memo failed")
        _id = "0"
        rslt = False
    return {"result": rslt, "id": _id}

@app.route("/delete_memo")
def delete_memo():
    """
    Takes memo ID from client and deletes that DB entry
    """
    app.logger.debug("Deleting a memo")
    num_deleted = del_memo(request.args.get('memo_id'))
    return flask.jsonify(result=num_deleted)

def del_memo(id):
    """
    Helper function to delete a memo
    """
    _id = id
    app.logger.debug("Deleting memo with id: " + _id)
    try:
        reslt = collection.delete_one({'_id': ObjectId(_id)})
        num_deleted = reslt.deleted_count   #deleted_count will = 1 if memo was deleted
    except:
        app.logger.debug("Memo was not deleted")
        num_deleted = 0
    return num_deleted
    


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#################
#
# Functions used within the templates
#
#################


@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case. 
    """
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        if then.date() == now.date():
            human = "Today"
        else: 
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except: 
        human = date
    return human


#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
    Returns all memos in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    for record in collection.find( { "type": "dated_memo" } ):
        record['date'] = arrow.get(record['date']).isoformat()
        records.append(record)
    app.logger.debug(records)
    sorted_records = sorted(records, key=lambda k: k['date'])
    app.logger.debug(sorted_records)
    return sorted_records


if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT,host="0.0.0.0")

    
