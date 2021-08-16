import os
import time
import uuid

import analytics
from requests.exceptions import ConnectionError

SEGMENT_ENABLED = os.getenv("MOSAIC_STREAMLIT_SEGMENT_ENABLED", "false") == "true"
if SEGMENT_ENABLED:
    analytics.write_key = "qmnxrkhf17A0cNnXkwSf0ZnoJKcjzeZ7"  # dev
analytics.debug = True
analytics.on_error = print
analytics.sync_mode = True

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
                "name": "Insights v4",
                "version": "4.0.0-b1",
            }
        }
    return context


def get_session():
    global session
    if session is None:
        session = time.time()
    return session


# FIXME: streamlit needs a standard lifecycle events which currently don't exist
_track_only_once = ["Application Launched", "Application Closed"]
_already_tracked_events = []


def track(event, **details):
    if not SEGMENT_ENABLED:
        return

    if event in _track_only_once and event in _already_tracked_events:
        return

    _already_tracked_events.append(event)
    details["session_id"] = get_session()
    try:
        analytics.track(anonymous_id=get_user_id(), event=event, properties=details, context=get_context())
    except ConnectionError:
        # required for offline mode
        pass
