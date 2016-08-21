23 - 下半场
24 - 半场
32 - 全场
35 - 上半场
40 - 黄牌
45 - 黄红牌
50 - 红牌

158 - 受伤
60 - 替补
90 - 伤停补时
168 - 伤后进场

110 - 控球时间
30 - 进球
150 - 任意球
151 - 球门球
152 - 界外球
153 - 越位
154 - 角球
155 - 射正
156 - 射偏
157 - goalkeeper save(守门员守住了)
161 - 给了点球
172 - 拦截
666 - 点球罚失

/* matchsituation 有3种，分别为
    'attack' - 抢攻
    'safe' - 安全区域
    'danger' - 危险进攻
    如果_typeid 为1103, 那么得判断字段situation, 值一定为'attack', 'safe', 
    'danger'中的一种
*/
1103 - matchsituation
    
1181 - players on pitch
1140 - pitch coordinates

1024 - 比赛即将开始
20 - 比赛结束
10 - 已开始
16 - 比赛继续

*****************************************************************************************

通过消息队列接受到的消息是一个字典，这个字典有两个键值，分别为'events',
'match'.

在interface.py文件中有两个class, 一个为Match, 一个为Event分别用来处理接受到的
字典。

在接受到字典以后可以这样使用:
1 调用interface.py 中的animation_actions函数，函数的参数应为接受到的字典，
    该函数返回一个字典，同样这个字典有两个键值：'events', 'match'.
    value分别为由Event对象组成的列表，Match对象
2 调用对象的函数得到你想要的字段

使用例子:
    import interface

    d = interface.animation_actions(data) ==> data为通过消息队列接受到的字典
    
    # 处理每个Event对象,每个event对象就是应该现实在动画上的信息
    for ev in d['events']:
        print ev.name(), ev.position(), ev.time(), ev.team()

如何接收到的事件为pitch coordinates(typeid=1140), 那么ev.position()返回的是
字典列表，字典由三个键值'X', 'Y', 'team'. 'team'可取'home', 'away'

例如： {'X': 40, 'Y': 36, 'team': 'away' or 'home'}

否则返回的是个元祖,例如（36， 22），
index 0 ==> x 坐标
inex 1 ==> y 坐标

如果这个事件没有坐标，就为('', '')
