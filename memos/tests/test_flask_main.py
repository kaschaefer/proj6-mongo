"""
Nose tests for flask_main.py
"""
from flask_main import del_memo, get_memos, add_new_memo

import nose
import logging
import arrow

from nose.tools import *

logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

#Tests for del_memo
def test_delete_bad_memos():
    assert del_memo("") == 0
    assert del_memo("badMemoId") == 0

#Tests for add_memo
def test_add_memo():
    assert add_new_memo("dated_memo", "2017-11-08T16:42:28+00:00", "this is a test") == True

#different style of testing for memo added
def test_add_memo():
    records = get_memos()
    n = len(records)
    add_new_memo("dated_memo", "2017-11-08T16:42:28+00:00", "this is another test")
    records = get_memos()
    m = len(records)
    assert n == m-1

#Test that empty text raises error
@raises(ValueError)
def test_empty_memo():
    add_new_memo("dated_memo", "2017-11-08T16:42:28+00:00", "")

#Test that bad date raises error
@raises(ValueError)
def test_bad_date():
    add_new_memo("dated_memo", "this is not a date", "this is a test")

#Test listing of memos
"""
Test that get memos returns a list of memos by date
"""
def test_memo_sort():
    records = get_memos()
    n = len(records)
    result = True
    i = 1
    for memo in records:
        if memo['date'] > records[i]['date']:   #If the memo date at records[i] is later than date @ records[i+1]
            result = False                      #Then the list isn't sorted by date
        i = i+1
        if i == n:
            break
    assert result == True

