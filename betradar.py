# coding: utf-8

import requests
import json
import threading
import time
from logging import config
import logging
import sys

timeline_base_url = 'https://ls.sportradar.com/ls/feeds/?/betradar/en/Europe:Berlin/gismo/match_timelinedelta/'
LOGGER = logging.getLogger(__name__)

COMPETITION_STATUS_NOT_START = 0
COMPETITION_STATUS_END = 100
COMPETITION_STATUS_CANCEL = 70
COMPETITION_STATUS_DELAY = 60
COMPETITION_STATUS_AP = 120

EVENT_TYPID_ALREADY_START = 10
EVENT_TYPID_ABOUT_TO_START = 1024

SOCCER_SID = 1


headers = {
    'Accept-Language': 'zh-CN;q=0.6',
}


def data(url, headers=headers):
    while True:
        try:
            r = requests.get(url, headers=headers)
        except:
            LOGGER.warning('request failed will try again')
            time.sleep(1)
            continue
        if r.text == '':
            continue
        else:
            break
    try:
        data = json.loads(r.text)
    except:
        sys.exit(1)
    return data


def get_events():
    url = 'https://ls.sportradar.com/ls/feeds/?/betradar/en/Europe:Berlin/gismo/event_fullfeed/0/24'
    return data(url)


def get_data(events):
    return events['doc'][0]['data']


def soccer_tournaments():

    soccer = get_data(soccer_events())[0]
    assert soccer['_doc'] == 'sport'
    assert soccer['name'] == 'Soccer'
    assert soccer['_id'] == 1

    tournaments = []
    for realcategory in soccer['realcategories']:
        for tournament in realcategory['tournaments']:
            tournaments.append(tournament)
    return tournaments


def soccer_matches():

    matches = []
    for tournament in soccer_tournaments():
        for match in tournament['matches']:
            matches.append(match)

    return matches


def soccer_ids():
    ids = []
    for match in soccer_matches():
        ids.append(match['_id'])
    return ids


def soccer_events():
    return get_events()


def ongoing_match_ids():
    return [mt['_id'] for mt in soccer_matches() if mt['status']['_id'] != COMPETITION_STATUS_END
            and mt['status']['_id'] != COMPETITION_STATUS_NOT_START
            and mt['status']['_id'] != COMPETITION_STATUS_CANCEL and mt['status']['_id'] != COMPETITION_STATUS_DELAY
            and mt['status']['_id'] != COMPETITION_STATUS_AP]



def live_data(data):
    d = {}
    d.update(live_events(data))
    d.update(live_match(data))

    return d


def live_match(d):
    da = dict()
    da['match'] =  {k: d['match'].get(k) for k in ['_id', '_sid', 'result', 'status', 'teams']
                    if k in d['match']}
    if 'status' in da['match']:
        del da['match']['status']['_doc']
    if 'teams' in da['match']:
        dl = ['cc', '_doc', 'mediumname', 'virtual', 'iscountry', 'abbr', 'uid', '_id']
        for tm_tp in ['home', 'away']:
            if tm_tp in da['match']['teams']:
                for k in dl:
                    if k in da['match']['teams'][tm_tp]:
                        del da['match']['teams'][tm_tp][k]

        if '_doc' in da['match']['teams']:
            del da['match']['teams']['_doc']
    return da


def live_events(d):
    da = []
    dic = {}
    for event in d['events']:
        l = []
        for k in ['_id', 'updated_uts','matchid', 'minutes', 'X', 'Y', 'coordinates', '_typeid', 'playerin',
                  'playerout', 'shirtnumbers', 'coordinates', 'player', 'side'
                  'minutes', 'periodname', 'result', 'situation',
                  'team', 'time', 'name']:
            if k in event:
                l.append((k, int(event[k]) if isinstance(event[k], unicode) and
                          event[k].isdigit() else event[k]))
        da.append(dict(l))
    dic['events'] = da

    return dic


def send_timelinedelta_for(id):
        p = threading.Thread(target=timelinedelta, args=(id, ))
        p.start()
        LOGGER.warning('开启了一个线程处理id: %s' % id)


def transfor(d):
    # 排除有限报道的情况
    da = live_data(d)
    if da['events']:
        return da
    else:
        return None


def timelinedelta(id):
    from onemq.onemq import OneMQ
    import interface

    prev_events = []
    oneMq = OneMQ()
    while True:
            da = get_data(data('https://ls.sportradar.com/ls/feeds/?/betradar/zh/Europe:Berlin/gismo/match_timelinedelta/%s' % id))

            if da['match']['status']['_id'] == COMPETITION_STATUS_END:
                LOGGER.warning('比赛: %s已结束，线程将退出' % id)
                break
            if da['match']['status']['_id'] == COMPETITION_STATUS_CANCEL:
                LOGGER.warning('比赛: %s被取消, 线程将退出' % id)
                break
            d = transfor(da)
            if d is not None:
                dt = interface.animation_actions(d, prev_events)
                if dt:
                    for ev in dt['events']:
                        LOGGER.warning(json.dumps(d, indent=1, ensure_ascii=False, encoding='utf-8'))
                        oneMq.send_msg('betradar', json.dumps(d))
            time.sleep(1)


def get_soccer_events():
    url = 'https://ls.sportradar.com/ls/feeds/?/betradar/zh/Europe:Berlin/gismo/event_get'
    return [ev for ev in get_data(data(url)) if int(ev['_sid']) == SOCCER_SID]


def new_match_start():
    while True:
        LOGGER.warning('准备检查有没有新开始的比赛......')
        ets = get_soccer_events()
        for soccer_ev in ets:
            if int(soccer_ev['_typeid']) == EVENT_TYPID_ALREADY_START:
                LOGGER.warning('比赛: %s 已经开始' % soccer_ev['matchid'])
                send_timelinedelta_for(int(soccer_ev['matchid']))
        time.sleep(60)


def initialize():

    p2 = threading.Thread(target=new_match_start)
    p2.start()


if __name__  == '__main__':
    config.fileConfig('logger.conf', disable_existing_loggers=False)
    initialize()

    while True:
        ids = ongoing_match_ids()
        for ongoing_match_id in ids:
            send_timelinedelta_for(ongoing_match_id)
        if not ids:
            LOGGER.warning('现在没有比赛.....')
            LOGGER.warning('30秒后重新检查')
            time.sleep(30)
        else:
            break
