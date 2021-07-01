import time
import uuid

import analytics


analytics.write_key = 'qmnxrkhf17A0cNnXkwSf0ZnoJKcjzeZ7'  # dev
analytics.debug = True
analytics.on_error = print

user_id = None
context = None
session = None


def get_user_id():
    global user_id
    if user_id is None:
        user_id = uuid.getnode()
    return user_id


def get_context():
    global context
    if context is None:
        context = {
            "app": {
                "name": 'Insights v4',
                "version": '4.0.0-b1',
            }
        }
    return context


def get_session():
    global session
    if session is None:
        session = time.time()
    return session


def track(event, **details):
    details["session_id"] = get_session()
    analytics.track(
        anonymous_id=get_user_id(),
        event=event,
        properties=details,
        context=get_context()
    )
