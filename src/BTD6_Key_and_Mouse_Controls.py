import time
import pyautogui
import threading
from config import config, keybind_config
from pynput.keyboard import Controller, Key, Listener

pyautogui.PAUSE = 0  # 移除全局延迟
keyboard = Controller()


# 实现按方向键时微调鼠标位置功能
class ControlMouseUponKeyPress:
    def __init__(self):
        self.listener = None
        self.enabled = False
        self.lock = threading.Lock()

    def start_listen(self):
        """启动方向键监听"""
        with self.lock:
            if not self.listener or not self.listener.running:
                self.listener = Listener(on_press=self._handle_keys)
                self.listener.start()

    def stop_listen(self):
        """停止方向键监听"""
        with self.lock:
            if self.listener and self.listener.running:
                self.listener.stop()
                self.listener = None

    def enable_control(self, enable):
        """设置控制开关状态"""
        with self.lock:
            self.enabled = enable

    def _handle_keys(self, key):
        """处理方向键事件（系统级监听）"""
        with self.lock:
            if not self.enabled:
                return
        dx, dy = 0, 0
        try:
            if key == Key.left:
                dx = -1
            elif key == Key.right:
                dx = 1
            elif key == Key.up:
                dy = -1
            elif key == Key.down:
                dy = 1
            else:
                return
        except AttributeError:
            return
        pyautogui.move(dx, dy)


def delay(time_ms=config.DELAY_TIME):
    """
    在两步操作中带来 time 毫秒的延时。
    :param time_ms: 延时的时间（以毫秒为单位）
    """
    if config.SCRIPT_STOP == 1:
        return
    time.sleep(time_ms / 1000)  # 将毫秒转换为秒后再进行延时


def move2(pos_x, pos_y):
    """
    将鼠标指针移动到屏幕目标点 (posX, posY)。
    :param pos_x: 目标点的 X 坐标
    :param pos_y: 目标点的 Y 坐标
    """
    if config.SCRIPT_STOP == 1:
        return

    pyautogui.moveTo(pos_x + config.WINDOWS_OFFSET_CALCULATED_X, pos_y + config.WINDOWS_OFFSET_CALCULATED_Y)
    # 移动鼠标到指定坐标
    delay()


def left_click(times=1):
    """
    让鼠标左键点击指定次数。
    :param times: 点击的次数（默认为 1 次）
    """
    if config.SCRIPT_STOP == 1:
        return

    for _ in range(times):
        pyautogui.click()  # 模拟鼠标左键点击
        delay()  # 每次点击后稍作延迟，避免过快（可调整）


def scroll_up(times=1):
    """
    让鼠标滚轮向上滑动指定次数。
    :param times: 向上滑动的次数（默认为 1 次）
    """
    if config.SCRIPT_STOP == 1:
        return

    for _ in range(times):
        pyautogui.scroll(10)  # 正值表示向上滚动
        delay()


def scroll_down(times=1):
    """
    让鼠标滚轮向下滑动指定次数。
    :param times: 向下滑动的次数（默认为 1 次）
    """
    if config.SCRIPT_STOP == 1:
        return

    for _ in range(times):
        pyautogui.scroll(-10)  # 负值表示向下滚动
        delay()


def key_press(key, times=1):
    """
    模拟键盘按下指定按键数次。
    :param key: 键盘按键的字符或名称，例如 'a', 'enter', 'space' 等
    :param times: 按键的次数（默认为 1 次）
    """

    # 检查是否是特殊按键
    from pynput.keyboard import Key, KeyCode

    special_keys = {
        # =============== 核心控制键 ===============
        "enter": Key.enter,
        "esc": Key.esc,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "tab": Key.tab,
        "space": Key.space,
        "menu": Key.menu,
        "insert": Key.insert,

        # =============== 导航键簇 ===============
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "home": Key.home,
        "end": Key.end,
        "page_up": Key.page_up,
        "page_down": Key.page_down,

        # =============== 功能键 ===============
        "f1": Key.f1,
        "f2": Key.f2,
        "f3": Key.f3,
        "f4": Key.f4,
        "f5": Key.f5,
        "f6": Key.f6,
        "f7": Key.f7,
        "f8": Key.f8,
        "f9": Key.f9,
        "f10": Key.f10,
        "f11": Key.f11,
        "f12": Key.f12,

        # =============== 数字键盘 ===============
        "numpad0": KeyCode.from_vk(0x60),
        "numpad1": KeyCode.from_vk(0x61),
        "numpad2": KeyCode.from_vk(0x62),
        "numpad3": KeyCode.from_vk(0x63),
        "numpad4": KeyCode.from_vk(0x64),
        "numpad5": KeyCode.from_vk(0x65),
        "numpad6": KeyCode.from_vk(0x66),
        "numpad7": KeyCode.from_vk(0x67),
        "numpad8": KeyCode.from_vk(0x68),
        "numpad9": KeyCode.from_vk(0x69),
        "numpad_add": KeyCode.from_vk(0x6A),
        "numpad_subtract": KeyCode.from_vk(0x6D),
        "numpad_multiply": KeyCode.from_vk(0x6B),
        "numpad_divide": KeyCode.from_vk(0x6F),
        "numpad_decimal": KeyCode.from_vk(0x6E),

        # =============== 系统功能键 ===============
        "caps_lock": Key.caps_lock,
        "num_lock": Key.num_lock,
        "scroll_lock": Key.scroll_lock,
        "print_screen": Key.print_screen,
        "pause": Key.pause,

        # =============== 媒体控制键 ===============
        "media_volume_up": Key.media_volume_up,
        "media_volume_down": Key.media_volume_down,
        "media_volume_mute": Key.media_volume_mute,
        "media_play_pause": Key.media_play_pause,
        "media_next": Key.media_next,
        "media_previous": Key.media_previous,

        # =============== 修饰键 ===============
        "alt": Key.alt,
        "alt_gr": Key.alt_gr,
        "alt_l": Key.alt_l,
        "alt_r": Key.alt_r,
        "ctrl": Key.ctrl,
        "ctrl_l": Key.ctrl_l,
        "ctrl_r": Key.ctrl_r,
        "shift": Key.shift,
        "shift_r": Key.shift_r,

        # =============== 平台键 ===============
        "cmd": Key.cmd,
        "cmd_r": Key.cmd_r
    }

    # 处理组合键
    def parse_combo_key(key_str):
        keys = key_str.split('+')
        key_objs = []
        for k in keys:
            k = k.strip().lower()
            if k in special_keys:
                key_objs.append(special_keys[k])
            else:
                # 处理普通字符
                if len(k) == 1:
                    key_objs.append(k)
                else:
                    # 可能是操作名称，通过 keybind_config 获取对应的按键
                    resolved_key = keybind_config.get_key(k)
                    if resolved_key:
                        if resolved_key in special_keys:
                            key_objs.append(special_keys[resolved_key])
                        else:
                            key_objs.append(resolved_key)
                    else:
                        print(f"警告：无法识别按键或操作 '{k}'")
                        return None
        return key_objs

    # 如果输入的 key 是操作名称（如"飞镖猴"），通过 keybind_config 获取对应的按键
    if isinstance(key, str) and key not in special_keys and len(key) > 1 and '+' not in key:
        resolved_key = keybind_config.get_key(key)
        if resolved_key:
            key = resolved_key  # 将操作名称替换为对应的按键
        else:
            print(f"警告：无法找到操作 '{key}' 的对应按键映射。")
            return  # 未找到对应按键时直接返回
    for _ in range(times):
        if config.SCRIPT_STOP == 1:
            return
        delay(0.65 * config.DELAY_TIME)

        if isinstance(key, str) and '+' in key:
            # 处理组合键
            key_objs = parse_combo_key(key)
            if not key_objs:
                return

            # 按下所有修饰键
            for k in key_objs[:-1]:
                keyboard.press(k)
                delay(0.1 * config.DELAY_TIME)

            # 按下并释放主键
            main_key = key_objs[-1]
            keyboard.press(main_key)
            delay(0.35 * config.DELAY_TIME)
            keyboard.release(main_key)

            # 释放所有修饰键
            for k in reversed(key_objs[:-1]):
                keyboard.release(k)
                delay(0.1 * config.DELAY_TIME)

        elif isinstance(key, str) and key in special_keys:
            # 单个特殊按键
            keyboard.press(special_keys[key])
            delay(0.35 * config.DELAY_TIME)
            keyboard.release(special_keys[key])
        else:
            # 单个普通字符
            keyboard.press(key)
            delay(0.35 * config.DELAY_TIME)
            keyboard.release(key)
