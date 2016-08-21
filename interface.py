# coding: utf-8


def prev_event_of_id(id, prev_events):
    for evt in prev_events:
        if evt.id() == id:
            return evt
    return None


def present(d):
    pass


def get_match_details():
    u = 'https://ls.sportradar.com/ls/feeds/?/betradar/zh/Europe:Berlin/gismo/match_detailsextended/9672675'
    import betradar

    data = betradar.get_data(betradar.data(u))
    for typ in data['types']:
        pass


def animation_actions(data_of_dict, prev_events):
    ''' data_of_dict 有两个key, 第一个为"events", 第二个为"match"
        "events" 是个由字典组成的list, 其中每个字典都是一个事件，比如任意球，
        角球等。
        "match" 是关于比赛的信息 ==> 主客队名称，比分，上下半场等等
    '''
    ret = []
    temp = []
    for ev in data_of_dict['events']:
        evt = Event(ev)
        prev_evt = prev_event_of_id(evt.id(), prev_events)
        if (prev_evt and prev_evt.updatetime() >= evt.updatetime()):
            return dict()
        if prev_evt:
            if evt.typeid() == 24:
                present(get_match_details())
            else:
                ret.append(evt)
        else:
            ret.append(evt)

        temp.append(evt)
    del prev_events[:]
    prev_events += temp

    return dict(match=Match(data_of_dict['match']), events=ret)


class Match(object):
    def __init__(self, match):
        self.match = match

    def id(self):
        return self.match['_id']

    def homeName(self):
        '''主队名称'''
        return self.match['teams']['home']['name']

    def awayName(self):
        '''客队名称'''
        return self.match['teams']['away']['name']

    def result(self):
        ''' 返回值是个字典，有三个key,分别为"home", "away", "winner"
            value代表比分'''
        return self.match['result']

    def status(self):
        '''比赛的状态，上半场，下半场等'''
        return self.match['status']['name']


class Event(object):
    '''应该显示在动画上的信息'''
    def __init__(self, event_data):
        self.event_data = event_data


    def typeid(self):
        return int(self.event_data['_typeid'])


    def updatetime(self):
        return self.event_data['updated_uts']


    def id(self):
        return self.event_data['_id']


    def time(self):
        '''event发生的时间，比如任意球发生的时间'''
        return self.event_data['time']


    def team(self):
        '''动作的执行者, 主队，客队'''
        return self.event_data['team'] if 'team' in self.event_data else ''

    def result(self):
        '''发生这个动作后，当前比赛的比分, 返回值是个字典
        该字典由三个键值: "home", "away", "winner"
        {'home': 3, 'away':2 , 'winner': 'null'} 表示3-2
        'winner'可以去两个值'home', 'away'表示谁赢了比赛
        '''
        return self.event_data['result']

    def matchId(self):
        return self.event_data['matchid']

    def name(self):
        '''返回值可能由3种: "attack", "danger", "safe"
        attack - 表示抢攻
        danger - 表示危险进攻
        safe -  表示区域安全'''
        return  self.event_data['situation'] if self.event_data['name'] == 'matchsituation' else self.event_data['name']


    def positions(self):
        return self.event_data['coordinates'] if self.typeid() == 1140 else (self.event_data.get('X', ''), self.event_data.get('Y', ''))
