from config import config

from pywinauto import application
from pywinauto.findwindows import ElementNotFoundError
import pygetwindow as gw  # 如果未安装，请使用 pip install PyGetWindow


def find_and_focus_window():
    """
    查找并激活 BloonsTD6 游戏窗口。
    """
    # btd6_window = None
    # app = None

    try:
        # 尝试查找 Steam 版本窗口
        btd6_window = gw.getWindowsWithTitle("BloonsTD6")[0]
    except IndexError:
        try:
            # 如果未找到 Steam 版本，尝试查找 Epic 版本窗口
            btd6_window = gw.getWindowsWithTitle("BloonsTD6-Epic")[0]
        except IndexError:
            try:
                # 如果两种窗口标题都未找到，尝试通过进程名查找（UnityWndClass 窗口）
                app = application.Application().connect(path="BloonsTD6.exe")
                btd6_window = app.top_window()
            except Exception as e:
                print(f"未找到游戏窗口，请确保游戏正在运行。错误信息: {e}")
                return

    if btd6_window:
        try:
            # 如果通过 pygetwindow 找到了窗口，获取窗口句柄
            window_handle = btd6_window._hWnd   # noqa _hWnd被视为“受保护的成员”，对它们的访问通常被视为违反封装原则

            # 使用 pywinauto 连接并激活窗口
            app = application.Application().connect(handle=window_handle)
            app_dialog = app.window(handle=window_handle)

            # 设置焦点并恢复窗口
            app_dialog.restore()  # 如果窗口最小化，则恢复窗口
            app_dialog.set_focus()  # 设置窗口焦点

            # 获取窗口位置
            left, top, right, bottom = btd6_window.left, btd6_window.top, btd6_window.right, btd6_window.bottom
            print(f"当前窗口位置: 左上角({left}, {top}), 右下角({right}, {bottom})")

            # 计算全局窗口偏移
            config.WINDOWS_OFFSET_CALCULATED_X = right - 1289 + config.CUSTOM_OFFSET_X
            config.WINDOWS_OFFSET_CALCULATED_Y = bottom - 759 + config.CUSTOM_OFFSET_Y

            # print(config.WINDOWS_OFFSET_CALCULATED_X)
            # print(config.WINDOWS_OFFSET_CALCULATED_Y)

            # （可选）移动窗口到目标位置
            # 如果需要将窗口移动到特定位置，可以取消注释以下代码
            # target_x = config.WINDOWS_POSITION_X
            # target_y = config.WINDOWS_POSITION_Y
            # app_dialog.move_window(target_x, target_y)
            # print(f"窗口已移动到新位置: 左上角({target_x}, {target_y})")

        except ElementNotFoundError:
            print("无法连接到窗口，请确保窗口未被关闭或隐藏。")
        except Exception as e:
            print(f"设置窗口焦点时发生错误: {e}")
    else:
        print("未找到游戏窗口，请确保游戏正在运行。")


if __name__ == "__main__":
    find_and_focus_window()
