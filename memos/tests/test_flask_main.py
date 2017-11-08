"""
Nose tests for flask_main.py
"""
from flask_main import del_memo, get_memos, add_new_memo

import nose
import logging
import arrow

logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

#Tests for del_memo
def test_delete_bad_memos():
    assert del_memo("") == 0
    assert del_memo("badMemoId") == 0

#
