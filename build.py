import json
from collections import Counter

CLASSES = {'1': '幼稚園生', '2': '8才以下', '3': '9〜10才', '4': '11才以上'}
RELAY_CLASS = {'8歳以下': '2', '9～10歳': '3', '11歳以上': '4'}
# 要項の種目表の順。板キック・背面キックは申込一覧で「200m」と表示されている
EVENTS = [
    ('板キック', '25m', '自由形', '200m'), ('背面キック', '25m', '背泳ぎ', '200m'),
    ('自由形', '25m'), ('自由形', '50m'), ('背泳ぎ', '25m'), ('背泳ぎ', '50m'),
    ('平泳ぎ', '25m'), ('平泳ぎ', '50m'), ('バタフライ', '25m'), ('バタフライ', '50m'),
    ('個人メドレー', '100m'),
]
EVENT_KEY = {(e[2], e[3]) if len(e) > 2 else e: i for i, e in enumerate(EVENTS)}
# 開門・ウォーミングアップは2組に分かれる
B_TEAMS = ['原田学園SS', 'ジェル鹿児島']


def seconds(t):
    m, _, s = t.rpartition(':')
    return round((int(m) if m else 0) * 60 + float(s), 2)


people = {}
for line in open('entries.tsv', encoding='utf-8'):
    no, name, kana, team, team_kana, grade, age, gender, stroke, dist, cls, time = line.rstrip('\n').split('\t')
    if no not in people:
        people[no] = dict(no=int(no), name=name, kana=kana, team=team, teamKana=team_kana, grade=grade,
                          age=int(age), gender='女子' if gender == '女' else '男子', entries=[])
    p = people[no]
    assert (p['name'], p['team'], p['grade']) == (name, team, grade), no
    p['entries'].append(dict(ev=EVENT_KEY[(stroke, dist)], cls=cls, time=time, sec=seconds(time)))
rows = sorted(people.values(), key=lambda p: p['no'])
for r in rows:
    r['entries'].sort(key=lambda e: e['ev'])

relays = []
for line in open('relays.tsv', encoding='utf-8'):
    no, team, team_kana, cls, event, dist, gender, time = line.rstrip('\n').split('\t')
    relays.append(dict(no=int(no), team=team, teamKana=team_kana, cls=RELAY_CLASS[cls],
                       event='フリーリレー' if event == 'リレー' else event, dist=dist,
                       gender=gender, time=time, sec=seconds(time)))

teams = Counter(r['team'] for r in rows)
data = dict(
    classes=CLASSES,
    events=[dict(name=e[0], dist=e[1]) for e in EVENTS],
    bTeams=B_TEAMS,
    rows=rows,
    relays=relays,
    teams=[dict(name=t, people=n, group='B' if t in B_TEAMS else 'A') for t, n in teams.most_common()],
    stats=dict(people=len(rows), entries=sum(len(r['entries']) for r in rows), relays=len(relays),
               teams=len(teams), male=sum(r['gender'] == '男子' for r in rows),
               female=sum(r['gender'] == '女子' for r in rows)),
)
assert all(t in teams for t in B_TEAMS)

tpl = open('template.html', encoding='utf-8').read()
out = tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
open('index.html', 'w', encoding='utf-8').write(out)
print(data['stats'])
print(Counter(EVENTS[e['ev']][0] + EVENTS[e['ev']][1] for r in rows for e in r['entries']))
