from icalendar import Calendar
from datetime import datetime
from typing import Dict, List

class Event:
    def __init__(self, uid, start, end, summary, location):
        self.uid, self.start, self.end, self.summary, self.location = (
            uid, start, end, summary, location
        )

def parse_ics(path: str) -> Dict[str, Event]:
    with open(path, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    evs = {}
    for ve in cal.walk('VEVENT'):
        uid      = str(ve.get('UID'))
        start    = ve.decoded('DTSTART')
        end      = ve.decoded('DTEND')
        summary  = str(ve.get('SUMMARY'))
        location = str(ve.get('LOCATION', ''))
        evs[uid] = Event(uid, start, end, summary, location)
    return evs

def diff_events(old: Dict[str, Event], new: Dict[str, Event]):
    added, changed, removed = [], [], []
    for uid, e in new.items():
        if uid not in old:
            added.append(e)
        elif (e.start, e.end, e.location) != (old[uid].start, old[uid].end, old[uid].location):
            changed.append(e)
    for uid, e in old.items():
        if uid not in new:
            removed.append(e)
    return added, changed, removed
