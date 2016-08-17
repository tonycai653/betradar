# coding: utf-8
import betradar
import time

while True:
    for ev in betradar.get_soccer_events():
        print '_id: %s, _typeid: %s, _matchid: %s, _eventname: %s, _matchstatusid: %s, _matchstatusname: %s' % \
        (ev['_id'], ev['_typeid'], ev['matchid'], ev['name'], ev['match']['status']['_id'], ev['match']['status']['name'])
    else:
        print '没有关于足球的事件发生'

    time.sleep(2)
