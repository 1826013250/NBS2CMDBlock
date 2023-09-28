import pynbs
from amulet_nbt import CompoundTag as Compound, ListTag as List, IntTag as Int, StringTag as String, ByteTag as Byte
from os.path import splitext, splitdrive

def wait_input(message, allow_empty=True, only_number=False, only_string=False, out_lowercase=False, strip="both",
               number_range=False):
    while True:
        temp = input(message)
        if not temp and allow_empty:
            return temp
        if only_number:
            try:
                int(temp)
            except ValueError:
                pass
            else:
                if number_range:
                    if number_range[0] <= int(temp) <= number_range[-1]:
                        return temp
                else:
                    return temp
        elif only_string and temp.isalpha():
            if out_lowercase:
                temp = temp.lower()
            if strip == "both":
                temp = temp.strip()
            elif strip == "left":
                temp = temp.lstrip()
            elif strip == "right":
                temp = temp.rstrip()
            else:
                raise Exception("无效的类型 %s" % strip)
            return temp
        elif not only_number and not only_string:
            return temp
        print("输入不合规!%s" % ("请输入数字!" if only_number else "请仅输入字母!"))

real_keys = {}
for i in range(9):
    real_keys[i] = ['', '0.000000']
for i in range(9, 33):
    real_keys[i] = ['_-1', "%.6f" % 2 ** ((-12 + i - 9) / 12)]
for i in range(33, 58):
    real_keys[i] = ['', "%.6f" % 2 ** ((-12 + i - 33) / 12)]
for i in range(58, 82):
    real_keys[i] = ['_1', "%.6f" % 2 ** ((-12 + i - 57) / 12)]
for i in range(82, 88):
    real_keys[i] = ['', '0.000000']

instruments = {
    0: "harp",
    1: "bass",
    2: "basedrum",
    3: "snare",
    4: "hat",
    5: "guitar",
    6: "flute",
    7: "bell",
    8: "chime",
    9: "xylophone",
    10: "iron_xylophone",
    11: "cow_bell",
    12: "didgeridoo",
    13: "bit",
    14: "banjo",
    15: "pling"
}
for k, v in instruments.items():
    instruments[k] = "minecraft:block.note_block." + v

structure = Compound({
    'size': List([Int(2), Int(2), Int(2)]),
    'entities': List([]),
    'blocks': List([]),
    'palette': List([
        Compound({
            'Name': String("minecraft:air")  # id: 0
        }),
        Compound({
            'Name': String("minecraft:stone")  # id: 1
        }),
        Compound({
            'Name': String("minecraft:repeater"),  # id: 2
            'Properties': Compound({
                'delay': String("1"),
                'facing': String("west"),
                'powered': String("false"),
                'locked': String("false")
            })
        }),
        Compound({
            'Name': String("minecraft:command_block"),  # id: 3
            'Properties': Compound({
                'facing': String("east")
            })
        }),
        Compound({
            'Name': String("minecraft:oak_sign"),  # id: 4
            'Properties': Compound({
                'rotation': String("4")
            })
        }),
        Compound({
            'Name': String("minecraft:stone_button"),  # id: 5
            'Properties': Compound({
                'facing': String("west"),
                'face': String("wall")
            })
        }),
        Compound({
            'Name': String("minecraft:redstone_lamp")  # id: 6
        })
    ])
})

filename = input("请输入文件路径: ")
nbs = pynbs.read(filename)

config_height = wait_input("请输入玩家悬浮高度(留空默认,默认为10): ", only_number=True)
if not config_height:
    config_height = 10

config_offset = wait_input("请输入玩家相对于当前播放进度位置的偏移格数(留空默认,默认为-5): ", only_number=True)
if not config_offset:
    config_offset = -5

config_play_location = wait_input("请选择播放时玩家位置:\n[1] 位于整个谱子正中间的上方\n[2] 位于最长轨道的上方\n> ",
                                  only_number=True, number_range=[1, 2])

print("载入NBS内自定义音色")
for i in nbs.instruments:
    instruments[16 + i.id] = i.file

print("载入NBS轨道...")
meta = {}  # layer, note
for x in nbs.layers:
    meta[x.id] = {'volume': x.volume, 'notes': []}

_progress_note = 0
for note in nbs.notes:
    _progress_note += 1
    print("载入NBS音符... %d/%d" % (_progress_note, len(nbs.notes)), end="\r")
    meta[note.layer]['notes'].append({'tick': note.tick, 'instrument': note.instrument, 'key': note.key,
                                      'volume': note.velocity * meta[note.layer]['volume'] / 10000})
print("\n删除空轨道...")
index = 0
cleaned = {}
for k, v in meta.items():
    if v['notes']:
        cleaned[index] = v
        index += 1

song = {}  # {layer: [tick for note]}
for layer_id, value in cleaned.items():
    song[layer_id] = []
    if value['notes']:
        for i in range(max([x['tick'] for x in value['notes']]) + 1):
            song[layer_id].append(None)
        for note in value['notes']:
            song[layer_id][note['tick']] = {'key': note['key'], 'instrument': note['instrument'],
                                            'volume': note['volume']}

_progress_zone_setup = 6
_progress_zone_setup_max = len(cleaned.keys()) * 2 * 6 * (nbs.header.song_length + 1) * 2
zone = []  # z y x， z//2代表轨道
for z in range(len(cleaned.keys()) * 2):
    zone.append([[], [], [], [], [], []])
    for x in range((nbs.header.song_length + 1) * 2):
        print("初始化方块矩阵...%d/%d" % (_progress_zone_setup, _progress_zone_setup_max), end="\r")
        if z % 2 == 0:
            if song.get(z // 2, False) and x // 2 < len(song[z // 2]):
                zone[z][0].append({'state': 1})
                _progress_zone_setup += 1
                if x % 2 == 1:
                    if song[z // 2][x // 2]:
                        zone[z][1].append({'state': 3, 'command':
                                           "execute as @a at @a run playsound "
                                           + instruments[song[z // 2][x // 2]['instrument']]
                                           + real_keys[song[z // 2][x // 2]['key']][0]
                                           + " block @s ~1 ~ ~ "
                                           + str(song[z // 2][x // 2]['volume']) + " "
                                           + real_keys[song[z // 2][x // 2]['key']][1]})
                        _progress_zone_setup += 1
                    else:
                        zone[z][1].append({'state': 6})
                        _progress_zone_setup += 1
                else:
                    zone[z][1].append({'state': 2})
                    _progress_zone_setup += 1
            else:
                zone[z][0].append({'state': 0})
                zone[z][1].append({'state': 0})
                _progress_zone_setup += 2
        else:
            zone[z][0].append({'state': 0})
            zone[z][1].append({'state': 0})
            _progress_zone_setup += 2
        zone[z][2].append({'state': 0})
        zone[z][3].append({'state': 0})
        zone[z][4].append({'state': 0})
        zone[z][5].append({'state': 0})
        _progress_zone_setup += 4

print("\n寻找最长轨道便于放置传送用命令方块")
longest = None
for i in range(len(zone)):
    if zone[i][0][-1] != {'state': 0}:
        longest = i
if not longest:
    print("出现错误！将不会创建传送用的命令方块轨道")
else:
    _progress_teleport_commandblock = 0
    _progress_teleport_commandblock_max = len(zone[longest][0]) // 2
    for i in range(len(zone[longest][0])):
        if i % 2 == 1:
            _progress_teleport_commandblock += 1
            print("正在放置...%d/%d\r" % (_progress_teleport_commandblock, _progress_teleport_commandblock_max), end='')
            zone[longest][0][i] = {
                'state': 3,
                'command': f"tp @a ~{config_offset} ~{config_height} ~%s" % (
                    "" if config_play_location == '2' else f"{-longest + len(zone)//2 -1}"
                )
            }

print("\n进行零碎方块放置")
if len(zone) < 5:
    while len(zone) < 5:
        zone.append([[{'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}],
                     [{'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}],
                     [{'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}],
                     [{'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}],
                     [{'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}, {'state': 0}]])
for z in range(5):  # 布置小平台
    for x in range(5):
        zone[z][2][x] = {'state': 1}
finalz = -2 + len(zone)
zone[2][3][2] = {  # 放置启动用命令方块
    'state': 3,
    'command': "fill ~-3 ~-2 ~-2 ~-3 ~-2 ~%d minecraft:redstone_block" % finalz
}
zone[2][3][1] = {'state': 5}  # 放置启动按钮
zone[1][1][0] = {  # 放置清除红石块的命令方块
    'state': 3,
    'command': "fill ~-1 ~ ~-1 ~-1 ~ ~%d minecraft:air" % (finalz + 1)
}
zone[2][4][2] = {
    'state': 4,
    'sign': True,
    'glow': True,
    'color': "black",
    'message1': splitdrive(filename)[-1],
    'message2': nbs.header.description,
    'message3': f"红石刻速度: {nbs.header.tempo}tick/s",
    'message4': f"推荐游戏刻{nbs.header.tempo * 2}"
}


print()
_progress_zone_fill = 0
_progress_zone_fill_max = len(zone) * len(zone[0]) * len(zone[0][0])
for z in range(len(zone)):
    for y in range(len(zone[z])):
        for x in range(len(zone[z][y])):
            _progress_zone_fill += 1
            print("填充方块...%d/%d" % (_progress_zone_fill, _progress_zone_fill_max), end="\r")
            block = Compound({
                'pos': List([Int(x), Int(y), Int(z)]),
                'state': Int(zone[z][y][x]['state']),
            })
            if zone[z][y][x].get('command'):
                block['nbt'] = Compound({'Command': String(zone[z][y][x]['command'])})
            if zone[z][y][x].get('sign'):
                block['nbt'] = Compound({
                    'is_waxed': Byte(1),
                    'front_text': Compound({
                        'has_glowing_text': Byte(zone[z][y][x]['glow']),
                        'color': String(zone[z][y][x]['color']),
                        'messages': List([
                            String(zone[z][y][x].get('message1', '{"text":""}')),
                            String(zone[z][y][x].get('message2', '{"text":""}')),
                            String(zone[z][y][x].get('message3', '{"text":""}')),
                            String(zone[z][y][x].get('message4', '{"text":""}'))
                        ])
                    })
                })
            structure['blocks'].append(block)
print()
filename = splitext(filename)[0].lower().replace(' ', '_').replace("'", '_') + ".nbt"
with open(filename, 'wb') as f:
    print("正在写入文件...")
    structure.save_to(f)
print("完成！文件保存在：\n%s" % filename)
print("本歌曲采用的红石刻速度为%d tick/s, 请在游戏内做适当调整" % nbs.header.tempo)