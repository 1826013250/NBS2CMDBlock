# NBS2CMDBlock
这个工具可以将你使用OpenNoteBlockStudio创作的工程文件导出为Minecraft中的结构NBT文件，并且可以使用结构方块读取

# 使用方式
使用如下命令安装第三方包
```commandline
python -m pip install pynbs amulet_nbt
```
将本项目克隆下来
```commandline
git clone https://github.com/1826013250/NBS2CMDBlock.git
cd NBS2CMDBlock
```
之后运行主程序
```commandline
python main.py
```

# 为什么会有这个工具
由于OpenNBS自身所携带的只有音符盒的结构导出方式，超音域的音符完全播放不了，而数据包的方式又有所偏离“红石音乐”的范畴。再者数据包本身的运作原理即为执行命令，那么完全可以使用命令方块代替，从而实现真正的红石音乐

# 局限性
- 目前有对自定义音色提供支持，但是支持度有待考证
- 不支持红石tick调整，所有中继器默认全部为1档（即1 红石刻（2 游戏刻）的延时），也就是对于OpenNBS中最佳兼容速度为10ticks/s。如需自定义游戏刻，此过程受到游戏自身的局限性，请使用Carpet等可以调整游戏刻的Mod实现

# 已完成功能
- 基本功能：导出和在游戏内使用，经测试所有原版音色在超音域并搭配OpenNBS导出的更多音符盒资源包可以正常播放（mcver1.20.1）
- 文件路径手动输入

# 待完成功能
*~~（又给自己挖坑是吧）~~*
- 选择游戏内呈现方式（目前仅会按照原音轨的样式布置方块矩阵）
- 更加人性化的TUI
- English Support

# 欢迎提出issue！
# 游戏内截屏
![screenshot0 - 在Minecraft内的截屏，展示了已经加载了两个结构的地图](./screenshot0.png)

# 特别感谢
[OpenNBS/PyNBS](https://github.com/OpenNBS/pynbs)
[Amulet-NBT](https://github.com/Amulet-Team/Amulet-NBT)