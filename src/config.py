import configparser
import os


class GlobalConfig:
    # 定义默认值
    _default_values = {
        "DELAY_TIME": 100,
        "COLLECT_INSTA_DELAY_TIME": 3000,
        "LOG_FILE_GRANULARITY": 3,
        "CUSTOM_SAVE_PATH": os.path.join(os.path.dirname(os.path.abspath(__file__)), "气球塔防6脚本日志"),
        "REPEAT_TIMES": 1,
        "SELECTED_FILE": 0,
        "SELECTED_FILES": 0,
        "MIDDLE_POS_X": 558,
        "IF_SHOP_OPENED": 0,
        "IF_GERALDO_PLACED_LEFT": 0,
        "IF_AUTOSTART_NOW": -1,
        "GAME_SPEED": -1,
        "START_GAME_LEVEL": 0,
        "MAX_GAME_LEVEL": 0,
        "NOW_GAME_LEVEL": -1,
        "TEST_LEVEL": 1,
        "LEVELS_WITH_STOPS": [],
        "RETRY_TIMES": 0,
        "ALLOWED_RETRY_TIMES": 5,
        "FAIL_COUNT": 0,
        "STOP_HERE": 0,
        "NOW_DIFFICULTY": 'CHIMPS or Hard or else',
        "SCRIPT_STOP": 0,
        "WINDOWS_POSITION_X": 0,  # Not used
        "WINDOWS_POSITION_Y": 0,  # Not used
        "WINDOWS_OFFSET_CALCULATED_X": 0,
        "WINDOWS_OFFSET_CALCULATED_Y": 0,
        "CUSTOM_OFFSET_X": 0,
        "CUSTOM_OFFSET_Y": 0,
        "START_BUTTON_ONOFF": 0,
    }

    def __init__(self):
        # 初始化，将默认值设置为当前值
        self.reset()

    def reset(self):
        # 重置所有变量为默认值
        for key, value in list(self._default_values.items()):
            setattr(self, key, value)

    def new_game_reset(self):
        # 仅重置指定的属性
        keys_to_reset = [
            "IF_SHOP_OPENED",
            "IF_GERALDO_PLACED_LEFT",
            "GAME_SPEED",
            "START_GAME_LEVEL",
            "MAX_GAME_LEVEL",
            "NOW_GAME_LEVEL",
            "LEVELS_WITH_STOPS",
            "RETRY_TIMES",
            "STOP_HERE",
            "NOW_DIFFICULTY",
            "SCRIPT_STOP",
        ]
        for key in keys_to_reset:
            if key in self._default_values:
                setattr(self, key, self._default_values[key])


class KeybindConfig:
    # 定义默认键位映射 (如果 ini 文件中某些键缺失)
    _default_keybinds = {
        "开始脚本": "f10",
        "停止脚本": "f12",
        "飞镖猴": "q",
        "回旋镖猴": "w",
        "大炮": "e",
        "图钉塔": "r",
        "冰猴": "t",
        "胶水炮手": "y",
        "狙击手猴": "z",
        "猴子潜艇": "x",
        "海盗猴": "c",
        "皇家飞行员": "v",
        "直升机飞行员": "b",
        "迫击炮猴": "n",
        "机枪猴": "m",
        "法师猴": "a",
        "超猴侠": "s",
        "忍者猴": "d",
        "炼金术师": "f",
        "德鲁伊": "g",
        "人鱼猴子": "o",
        "香蕉农场": "h",
        "刺钉工厂": "j",
        "猴子村": "k",
        "工程师猴": "l",
        "野兽之主": "i",
        "英雄": "u",
        "升级路线1": ",",
        "升级路线2": ".",
        "升级路线3": "/",
        "更改目标": "tab",
        "特制猴子": "page_down",
        "特制猴子2": "page_up",
        "出售": "backspace",
        "播放/快进": "space",
        "暂停": "`",
        "激活技能1": "1",
        "激活技能2": "2",
        "激活技能3": "3",
        "激活技能4": "4",
        "激活技能5": "5",
        "激活技能6": "6",
        "激活技能7": "7",
        "激活技能8": "8",
        "激活技能9": "9",
        "激活技能10": "0",
    }

    def __init__(self, ini_file_path="custom_keybind.ini"):
        self.keybinds = {}
        self.ini_file_path = ini_file_path
        self._load_keybinds()

    def _load_keybinds(self):
        """从 ini 文件加载快捷键配置。如果缺失，则使用默认值。"""
        load_config = configparser.ConfigParser()

        # 检查 ini 文件是否存在
        if os.path.exists(self.ini_file_path):
            load_config.read(self.ini_file_path, encoding="utf-8-sig")
            if "Keybinds" in load_config:
                # 从 ini 文件中加载键位映射
                for key, default_value in self._default_keybinds.items():
                    self.keybinds[key] = load_config["Keybinds"].get(key, default_value)
            else:
                print(f"警告: ini 文件中未找到 [Keybinds] 部分，使用默认键位映射。")
                self.keybinds = self._default_keybinds.copy()
        else:
            print(f"警告: ini 文件 {self.ini_file_path} 不存在，使用默认键位映射。")
            self.keybinds = self._default_keybinds.copy()

    def reset_to_defaults(self):
        """将键位映射重置为默认值。"""
        self.keybinds = self._default_keybinds.copy()

    def get_key(self, action):
        """获取某个操作的快捷键。如果操作不存在，则返回 None。"""
        return self.keybinds.get(action, None)

    def set_key(self, action, key):
        """设置某个操作的快捷键。"""
        self.keybinds[action] = key

    def save_to_ini(self):
        """将当前键位映射保存到 ini 文件中。"""
        config2 = configparser.ConfigParser()
        config2["Keybinds"] = self.keybinds

        with open(self.ini_file_path, "w", encoding="utf-8-sig") as ini_file:
            config2.write(ini_file)


class GlobalText:
    # 定义默认值
    _default_values = {
        "TEXT_NOW_COMMAND": ""
    }

    def __init__(self):
        # 初始化，将默认值设置为当前值
        self.command_history = []  # 新增指令历史记录列表
        self.TEXT_NOW_COMMAND = None
        self.reset()

    def reset(self):
        # 重置所有变量为默认值
        self.command_history.clear()
        for key, value in list(self._default_values.items()):
            setattr(self, key, value)

    def renew(self):

        if not self.TEXT_NOW_COMMAND:
            return  # 如果为空行（None 或空字符串），直接返回，不更新

        # 插入到历史记录最前面（保持最新在最上方）
        self.TEXT_NOW_COMMAND = ', '.join(value for value in self.TEXT_NOW_COMMAND.values() if value)
        self.command_history.insert(0, self.TEXT_NOW_COMMAND)
        self.TEXT_NOW_COMMAND = ""  # 重置当前指令


KEY_OPTIONS = [
    # 基础字符键
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
    "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
    "u", "v", "w", "x", "y", "z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    ",", ".", "/", ";", "\"",
    "`", "\\", "-", "=",
    "[", "]",

    # 功能键
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
    "f9", "f10", "f11", "f12",

    # 核心控制键
    "enter", "esc", "backspace", "delete",
    "tab", "space", "menu", "insert",

    # 导航键簇
    "up", "down", "left", "right",
    "home", "end", "page_up", "page_down",

    # 数字键盘
    "numpad0", "numpad1", "numpad2", "numpad3", "numpad4",
    "numpad5", "numpad6", "numpad7", "numpad8", "numpad9",
    "numpad_add", "numpad_subtract", "numpad_multiply",
    "numpad_divide", "numpad_decimal",

    # 系统功能键
    "caps_lock", "num_lock", "scroll_lock",
    "print_screen", "pause",

    # 媒体控制键
    "media_volume_up", "media_volume_down", "media_volume_mute",
    "media_play_pause", "media_next", "media_previous",

    # 修饰键
    "alt", "alt_gr", "alt_l", "alt_r",
    "ctrl", "ctrl_l", "ctrl_r",
    "shift", "shift_r",

    # 平台键
    "cmd", "cmd_r"
]


# 默认键位配置
DEFAULT_KEY_MAPPING = [
    ("开始脚本", "f10"),
    ("停止脚本", "f12"),
    ("飞镖猴", "q"),
    ("回旋镖猴", "w"),
    ("大炮", "e"),
    ("图钉塔", "r"),
    ("冰猴", "t"),
    ("胶水炮手", "y"),
    ("狙击手猴", "z"),
    ("猴子潜艇", "x"),
    ("海盗猴", "c"),
    ("皇家飞行员", "v"),
    ("直升机飞行员", "b"),
    ("迫击炮猴", "n"),
    ("机枪猴", "m"),
    ("法师猴", "a"),
    ("超猴侠", "s"),
    ("忍者猴", "d"),
    ("炼金术师", "f"),
    ("德鲁伊", "g"),
    ("人鱼猴子", "o"),
    ("香蕉农场", "h"),
    ("刺钉工厂", "j"),
    ("猴子村", "k"),
    ("工程师猴", "l"),
    ("野兽之主", "i"),
    ("英雄", "u"),
    ("升级路线1", ","),
    ("升级路线2", "."),
    ("升级路线3", "/"),
    ("更改目标", "tab"),
    ("特制猴子", "page_down"),
    ("特制猴子2", "page_up"),
    ("出售", "backspace"),
    ("播放/快进", "space"),
    ("暂停", "`"),
    ("激活技能1", "1"),
    ("激活技能2", "2"),
    ("激活技能3", "3"),
    ("激活技能4", "4"),
    ("激活技能5", "5"),
    ("激活技能6", "6"),
    ("激活技能7", "7"),
    ("激活技能8", "8"),
    ("激活技能9", "9"),
    ("激活技能10", "0")
]

# 实例化一个全局配置对象
config = GlobalConfig()

# 实例化一个全局键位配置对象
keybind_config = KeybindConfig()

global_text = GlobalText()

# 示例：获取某个操作的快捷键
# print("飞镖猴的快捷键是:", keybind_config.get_key("飞镖猴"))

# 示例：修改快捷键并保存到 ini 文件
# keybind_config.set_key("飞镖猴", "p")  # 将飞镖猴快捷键设置为 "p"
# keybind_config.save_to_ini()  # 保存修改到 ini 文件
