import pynbs
from amulet_nbt import CompoundTag as Compound, ListTag as List, IntTag as Int, StringTag as String
from os.path import splitext

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
            'Name': String("minecraft:air")
        }),
        Compound({
            'Name': String("minecraft:stone")
        }),
        Compound({
            'Name': String("minecraft:repeater"),
            'Properties': Compound({
                'delay': String("1"),
                'facing': String("west"),
                'powered': String("false"),
                'locked': String("false")
            })
        }),
        Compound({
            'Name': String("minecraft:command_block")
        })
    ])
})

filename = input("请输入文件路径: ")
nbs = pynbs.read(filename)

print("载入NBS内自定义音色")
for i in nbs.instruments:
    instruments[i.id] = i.file

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
zone = []  # y x z
for z in range(len(meta.keys()) * 2):
    zone.append([[], [], [], [], [], []])
    _progress_zone_setup += 6
    for x in range(nbs.header.song_length * 2 + 1):
        print("初始化方块矩阵...%d/%d" % (_progress_zone_setup,
              len(meta.keys()) * 2 * 6 * (nbs.header.song_length + 1) * 2), end="\r")
        if z % 2 == 0:
            if song.get(z // 2, False) and x // 2 < len(song[z // 2]):
                zone[z][0].append({'state': 1})
                _progress_zone_setup += 1
                if x % 2 == 0:
                    if song[z // 2][x // 2]:
                        zone[z][1].append({'state': 3, 'command':
                                           "execute as @a at @a run playsound "
                                           + instruments[song[z // 2][x // 2]['instrument']]
                                           + real_keys[song[z // 2][x // 2]['key']][0]
                                           + " block @s ~ ~ ~ "
                                           + str(song[z // 2][x // 2]['volume']) + " "
                                           + real_keys[song[z // 2][x // 2]['key']][1]})
                        _progress_zone_setup += 1
                    else:
                        zone[z][1].append({'state': 1})
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

print()
_progress_zone_fill = 0
for z in range(len(zone)):
    for y in range(len(zone[z])):
        for x in range(len(zone[z][y])):
            _progress_zone_fill += 1
            print("填充方块...%d/%d" % (_progress_zone_fill, len(zone) * len(zone[0]) * len(zone[0][0])), end="\r")
            block = Compound({
                'pos': List([Int(x), Int(y), Int(z)]),
                'state': Int(zone[z][y][x]['state']),
            })
            if zone[z][y][x].get('command', ''):
                block['nbt'] = Compound({'Command': String(zone[z][y][x].get('command', ''))})
            structure['blocks'].append(block)
print()
with open(splitext(filename)[0].lower().replace(' ', '_')+".nbt", 'wb') as f:
    print("正在写入文件...")
    structure.save_to(f)
print("完成！文件已保存在：\n%s" % splitext(filename)[0].lower().replace(' ', '_')+".nbt")