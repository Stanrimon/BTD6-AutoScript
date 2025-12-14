from config import config, keybind_config
import pyautogui
import numpy as np
from typing import Union
from BTD6_Key_and_Mouse_Controls import delay, left_click, move2, key_press
from BTD6_TraceLogs import write_game_log, save_screenshot


def resovle_keybind(key_name, default_key):
    resolved_key = keybind_config.get_key(key_name)
    if resolved_key:
        return resolved_key
    else:
        return default_key


def find_color_ex(pos_x1: int, pos_y1: int, pos_x2: int, pos_y2: int, target_color: str = 'F1F1F1',
                  color_search_mode: int = 0, find_color_similarity: float = 0.95) -> \
        Union[str, None]:
    """
    模糊找色功能的 Python 实现，返回颜色位置坐标。

    :param pos_x1: 窗口左上角 X 坐标
    :param pos_y1: 窗口左上角 Y 坐标
    :param pos_x2: 窗口右下角 X 坐标
    :param pos_y2: 窗口右下角 Y 坐标
    :param target_color: 目标颜色值（16 进制字符串，如 "FFFFFF"）
    :param color_search_mode: 查找方向 (0: 从左到右从上到下，1: 从中间向四周)
    :param find_color_similarity: 相似度 (0.1 - 1.0)，1.0 表示完全匹配
    :return: 如果找到颜色，返回 "X|Y" 坐标；否则返回 None
    """
    # 将16进制颜色转换为RGB元组
    target_color = tuple(int(target_color[i:i + 2], 16) for i in (0, 2, 4))

    # 截图指定区域
    screenshot = pyautogui.screenshot(region=(pos_x1 + config.WINDOWS_OFFSET_CALCULATED_X,
                                              pos_y1 + config.WINDOWS_OFFSET_CALCULATED_Y,
                                              pos_x2 - pos_x1,
                                              pos_y2 - pos_y1
                                              )
                                      )

    screenshot_np = np.array(screenshot)  # 转换为 NumPy 数组，方便操作

    # 获取截图的宽度和高度
    height, width, _ = screenshot_np.shape

    # 定义搜索顺序
    def generate_search_order():
        if color_search_mode == 0:  # 从左到右，从上到下
            return [(tmp_x, tmp_y) for tmp_y in range(height) for tmp_x in range(width)]
        elif color_search_mode == 1:  # 从中间向四周
            center_x, center_y = width // 2, height // 2
            return sorted(
                [(tmp_x, tmp_y) for tmp_y in range(height) for tmp_x in range(width)],
                key=lambda pos: abs(pos[0] - center_x) + abs(pos[1] - center_y)
            )
        else:
            raise ValueError("Invalid search_mode, must be 0 or 1.")

    # 搜索颜色
    search_order = generate_search_order()
    for x, y in search_order:
        pixel_color = screenshot_np[y, x]
        # print(pixel_color, 'Pixel')

        # 计算颜色相似度
        similarity_score = np.mean(np.abs(pixel_color - target_color) / 255.0)

        # print(similarity_score, 'similarity_score')
        if similarity_score <= (1 - find_color_similarity):  # 如果相似度符合要求
            return f"{x + pos_x1}|{y + pos_y1}"  # 返回相对于整个屏幕的坐标

    return None


# 示例调用
def idle_clicking():
    """
    Placeholder for the IdleClicking function.
    可以在这里定义实际的点击行为。
    """
    move2(50, 70)  # 左上角心形图案
    left_click()

    print("Performing idle clicking...")


def check_if_next_level_available() -> int:
    """
    判断是否可以进入下一关的逻辑。

    :return: 1 表示可以进入下一关，0 表示不能进入下一关。
    """
    # 初始状态，默认不可进入下一关
    next_level_available_flag = 0

    # 第一次查找 "下一关" 按钮
    check_result1 = find_color_ex(1215, 690, 1220, 695, "FFFFFF", 0, 0.9)
    if check_result1:  # 如果找到按钮可以点击
        
        check_result2 = find_color_ex(1240, 100, 1245, 105, "946336", 0, 0.9)
        # 二次判断防止误识别，此处识别猴子名称框中的棕色
        if check_result2:

            # 为了防止关末升级卡住，等待一段时间。默认500 毫秒
            # 此延时可自定义修改，为0则不判断，但可能由于升级带来失误
            delay(config.ENTER_NEXT_LEVEL_DELAY_TIME)

            # 三次判断防止升级卡住，“下一关”按钮可点击，即此时为关末
            check_result3 = find_color_ex(1215, 690, 1220, 695, "FFFFFF", 0, 0.95)
            if check_result3:
                # "下一关" 按钮可点击
                next_level_available_flag = 1
            else:
                # "下一关" 按钮不可点击，执行点击以防止卡住
                for _ in range(5):
                    delay()  # 延迟时间，可以根据需要调整
                    idle_clicking()
                delay(500)

    return next_level_available_flag


class GameRestartException(Exception):
    """表示需要重试整个游戏的异常"""
    pass


class LevelRetryException(Exception):
    """表示需要重试当前关卡的异常"""
    pass


def change_game_speed(target_speed):
    
    current_speed = config.GAME_SPEED  # 获取当前游戏速度
    key_play_start = resovle_keybind("播放/快进", 'space')
    
    if target_speed == 1:
        if current_speed == -1:
            key_press(key_play_start, 1)
            print("-1按一下开始键，改为1倍速")
        elif current_speed == -3:
            key_press(key_play_start, 2)
            print("-3按两下开始键，改为1倍速")
        elif current_speed == 3:
            key_press(key_play_start, 1)
            print("3按一下开始键，改为1倍速")
        # 当已经是1时不需要操作

    elif target_speed == 3:
        if current_speed == -1:
            key_press(key_play_start, 2)
            print("-1按两下开始键，改为3倍速")
        elif current_speed == -3:
            key_press(key_play_start, 1)
            print("-3按一下开始键，改为3倍速")
        elif current_speed == 1:
            key_press(key_play_start, 1)
            print("1按一下开始键，改为3倍速")
        # 当已经是3时不需要操作

    config.GAME_SPEED = target_speed


def wait_level(level: int):
    """
    循环等待进入指定关卡，同时处理本关重试和本局重试逻辑。
    如果需要重试当前关卡或整个游戏，则抛出相应的异常。

    :param level: 希望等待的目标关卡号
    :raises LevelRetryException: 如果需要重试当前关卡
    :raises GameRestartException: 如果需要重试整个游戏
    """

    while config.NOW_GAME_LEVEL != level:

        if config.SCRIPT_STOP == 1:
            return
        
        # 延迟 100 毫秒，控制识别频率
        delay(config.CHECK_NEXT_LEVEL_DELAY_TIME)

        # 检查当前关卡是否结束
        level_end_flag = check_if_next_level_available()

        if level_end_flag == 1:  # "下一关"按钮可用，关卡成功结束

            config.GAME_SPEED = -abs(config.GAME_SPEED)  # 游戏速度由之前的速度转变为暂停，用负数代表
            print(f"关卡结束，速度变为{config.GAME_SPEED}")


            if level not in config.LEVELS_WITH_STOPS:  # 如果下一关没有“关前停顿”指令，则可以三倍速进入下一关
                change_game_speed(3)  

            config.NOW_GAME_LEVEL += 1  # 正常游戏，关卡计数器 +1
            config.RETRY_TIMES = 0  # 成功进入下一关，重置重试次数
            
            # 记录日志
            if config.LOG_FILE_GRANULARITY >= 2:
                write_game_log(f"进入关卡 {config.NOW_GAME_LEVEL}", config.CUSTOM_SAVE_PATH)

        # 如果找不到下一关按钮，则检查当前关卡是否失败
        check_fail_result = find_color_ex(400, 500, 405, 505, "3C6091", 0, 0.95)
        if check_fail_result:  # 找到了失败框的蓝色
            # 二次判断，识别猴子名称框中的棕色
            check_fail_result2 = find_color_ex(1240, 110, 1245, 115, "946336", 0, 0.9)
            if not check_fail_result2:  # 猴子名称框中的棕色找不到，证明此时的确在中断状态，关卡失败

                config.FAIL_COUNT += 1  # 增加全局失败统计
                config.GAME_SPEED = -1  # 此时游戏是暂停的，且会变为一倍速
                print(f"关卡失败，速度变为{config.GAME_SPEED}")
                delay()

                # 进行重试
                if config.RETRY_TIMES < config.ALLOWED_RETRY_TIMES \
                        and config.NOW_DIFFICULTY == "点击" \
                        and config.NOW_GAME_LEVEL > config.START_GAME_LEVEL:
                    # 重试次数允许、难度为点击且不在开局失败（在脚本多处有难度判断，维护时请搜config.NOW_DIFFICULTY）

                    config.RETRY_TIMES += 1  # 增加重试次数
                    print("难度为点击且不在开局失败,移动到重试按钮位置")

                    move2(860, 560)  # 移动到重试按钮位置
                    delay()
                    left_click()  # 点击重试
                    delay()
                    move2(750, 500)  # 确定
                    delay()
                    left_click()
                    delay(500)
                    if config.NOW_GAME_LEVEL not in config.LEVELS_WITH_STOPS:  # 如果本关没有“关前停顿”指令，则可以三倍速进入
                        change_game_speed(3)  # 三倍速进入重试这关

                    if config.LOG_FILE_GRANULARITY >= 1:
                        write_game_log(f"第 {config.RETRY_TIMES} 次自动重试本关，全局失败次数{config.FAIL_COUNT}",
                                       config.CUSTOM_SAVE_PATH
                                       )

                    raise LevelRetryException(f"关卡 {config.NOW_GAME_LEVEL} 失败，准备重试")

                else:
                    # 失败超过3次，重试本局
                    move2(425, 560)  # 移动到回到主菜单位置
                    if config.NOW_DIFFICULTY == "点击" \
                            and config.NOW_GAME_LEVEL == config.START_GAME_LEVEL:
                        move2(500, 560)  # 点击模式下第六关失败时，主菜单按钮的位置
                    delay()
                    left_click()  # 点击
                    delay(3000)

                    if config.LOG_FILE_GRANULARITY >= 1:
                        write_game_log("不允许重试关卡，重开本局游戏", config.CUSTOM_SAVE_PATH)

                    raise GameRestartException("不允许重试关卡，准备重试整局游戏")

        else:  # 未找到失败框。如果识别不到猴子名称框中的棕色，可能是账号升级，或是游戏已成功

            check_brown_result = find_color_ex(1240, 100, 1245, 105, "946336", 0, 0.9)  # 寻找猴子名称框中的棕色

            if not check_brown_result:  # 找不到猴子名称框中的棕色，证明此时游戏有弹出界面，判断是什么

                check_success_result = find_color_ex(370, 150, 375, 155, "FFFFFF", 0, 0.9)  # 寻找成功界面左上角星星
                if check_success_result:
                    check_success_result2 = find_color_ex(700, 500, 705, 505, "3C6091", 0, 0.9)  # 二次判断蓝框
                    if check_success_result2:
                        print("判断游戏已成功")
                        config.NOW_GAME_LEVEL = level
                    pass
                else:
                    print("可能升级卡住，尝试鼠标点击")
                    for _ in range(3):
                        delay()  # 延迟时间，可以根据需要调整
                        idle_clicking()
                    delay(500)
            pass


def toggle_autostart(on_or_off):
    if on_or_off == 0:  # 关闭自动开始
        if config.IF_AUTOSTART_NOW != 0:  # 仅自动开始未关闭（或不知是否关闭）时执行
            key_press("esc")  # 模拟按键 "Esc"
            delay(500)

            # 查找颜色，判断自动开始是否为开启状态
            find_color = find_color_ex(900, 230, 905, 235, "00DCFF", 0, 0.9)
            if find_color:
                int_x, int_y = map(int, find_color.split("|"))

                if int_x > 0 and int_y > 0:  # 判断此时自动开始为开启状态，手动关闭
                    move2(880, 235)
                    left_click()

            delay(200)
            key_press("esc")
            config.IF_AUTOSTART_NOW = 0

            if config.LOG_FILE_GRANULARITY >= 1:  # 记录日志
                write_game_log("自动开始已关闭", config.CUSTOM_SAVE_PATH)

    elif on_or_off == 1:  # 开启自动开始
        if config.IF_AUTOSTART_NOW != 1:  # 仅自动开始未开启（或不知是否开启）时执行
            key_press("esc")
            delay(500)

            # 查找颜色，判断自动开始是否为关闭状态
            find_color = find_color_ex(900, 230, 905, 235, "371F0F", 0, 0.9)
            if find_color:
                int_x, int_y = map(int, find_color.split("|"))

                if int_x > 0 and int_y > 0:  # 判断此时自动开始为关闭状态，手动开启
                    move2(880, 235)
                    left_click()

            delay(200)
            key_press("esc")
            config.IF_AUTOSTART_NOW = 1

            if config.LOG_FILE_GRANULARITY >= 1:  # 记录日志
                write_game_log("自动开始已开启", config.CUSTOM_SAVE_PATH)

    delay(500)


def return_to_menu():
    """
    函数名称：return_to_menu()
    函数功能：在一局游戏的所有操作结束后，等待判断结算框并回到主菜单。
    """

    if config.SCRIPT_STOP == 1:
        return

    # 标志变量，用于控制循环的退出
    break_flag = 0

    # 在结算框出现前不断检测
    while break_flag == 0:

        # 延迟一定时间，避免过于频繁的检测
        delay()

        # 检查当前关卡是否为第100关
        if config.NOW_GAME_LEVEL == 100:  # 如果是第100关结束，有 insta 猴奖励

            # 检测猴子名称框中棕色是否改变，如改变证明有insta猴
            find_result = find_color_ex(1240, 110, 1245, 115, "946336", 0, 0.9)
            if find_result is None:
                # 如果没有检测到颜色，说明关卡结束。再次延迟 1000 毫秒（1 秒），以确保insta弹出
                print("Game Complete & Insta Detected")
                delay(1000)

                # 检查日志文件的详细等级，如果需要截图，则进行截图
                if config.LOG_FILE_GRANULARITY >= 2:
                    # 截图保存指定区域，并保存到自定义路径
                    save_screenshot(424, 204, 863, 607, config.CUSTOM_SAVE_PATH)

                # 调用函数进行空闲点击，清除 insta 猴奖励
                idle_clicking()
                delay(1000)
                idle_clicking()
                # 延迟 2000 毫秒（2 秒），准备点击结算框
                delay(2000)

                # 设置退出循环的标志
                break_flag = 1

        else:  # 如果关卡不足 100，则没有 insta 猴奖励

            # 检测猴子名称框中棕色是否改变，如改变证明已结束
            find_result = find_color_ex(1240, 110, 1245, 115, "946336", 0, 0.9)
            if find_result is None:
                # 如果检测到结算框颜色，直接退出循环
                print("Game Complete")

                break_flag = 1

        # 再次延迟一段时间，避免过于频繁的检测
        delay()

    # 循环结束，延迟 500 毫秒，确保稳定
    delay(500)

    # 移动鼠标到 "下一页" 按钮的坐标并点击
    move2(630, 630)
    delay()
    left_click()

    # 延迟 500 毫秒，确保操作生效
    delay(500)

    # 移动鼠标到 "主页" 按钮的坐标并点击
    move2(480, 600)
    delay()
    left_click()

    # 最后延迟 3000 毫秒（3 秒），确保主菜单加载完成
    delay(3000)
    print("Returned to menu")


def get_insta_map_name() -> str:
    """
    进入关卡选择页面，获取当前奖励地图的名称之后回到主页面。

    :return: 地图名称的字符串，如果未找到匹配的地图则返回 "Unknown"
    """

    debug_flag = 0

    if debug_flag == 1:
        delay(5000)
    else:
        move2(640, 660)  # 开始
        delay(200)
        left_click(1)
        delay()
        move2(53, 138)  # 搜索
        delay(1500)
        left_click(1)
        delay()
        move2(910, 55)  # insta
        delay(2000)
        left_click(1)
        delay(500)

    # 初始化地图名称为 "Unknown"
    map_name = "Unknown"

    # 检查 TrickyTracks
    tricky_tracks_check_result = find_color_ex(267, 408, 272, 413, "FFFFF7", 0, 0.97)
    if tricky_tracks_check_result:
        map_name = "棘手的轨道"

    # 检查 GlacialTrail
    glacial_trail_check_result = find_color_ex(285, 497, 290, 502, "10AAC6", 0, 0.97)
    if glacial_trail_check_result:
        map_name = "冰河之径"

    # 检查 DarkDungeons
    dark_dungeons_check_result = find_color_ex(281, 491, 286, 496, "5A5D52", 0, 0.97)
    if dark_dungeons_check_result:
        dark_dungeons_second_check_result = find_color_ex(292, 465, 297, 470, "4D1913", 0, 0.97)
        if dark_dungeons_second_check_result:
            map_name = "黑暗地下城"
            print(f"insta关卡识别结果: {map_name}")

    # 检查 Sanctuary
    sanctuary_check_result = find_color_ex(283, 451, 288, 456, "7B7529", 0, 0.97)
    if sanctuary_check_result:
        map_name = "避难所"
        print(f"insta关卡识别结果: {map_name}")

    # 检查 Ravine
    ravine_check_result = find_color_ex(285, 482, 290, 487, "797C2D", 0, 0.97)
    if ravine_check_result:
        map_name = "峡谷"
        print(f"insta关卡识别结果: {map_name}")

    # 检查 FloodedValley
    flooded_valley_check_result = find_color_ex(397, 490, 402, 495, "39A6CE", 0, 0.97)
    if flooded_valley_check_result:
        map_name = "水淹山谷"
        print(f"insta关卡识别结果: {map_name}")

    # 检查 Infernal
    infernal_check_result = find_color_ex(276, 458, 281, 463, "C61426", 0, 0.97)
    if infernal_check_result:
        map_name = "炼狱"
        print(f"insta关卡识别结果: {map_name}")

    # 检查 BloodyPuddles
    bloody_puddles_check_result = find_color_ex(282, 475, 287, 480, "4A2F3F", 0, 0.97)
    if bloody_puddles_check_result:
        map_name = "血腥水坑"
        print(f"insta关卡识别结果: {map_name}")

    # 检查 Workshop
    workshop_check_result = find_color_ex(261, 484, 266, 489, "2E5A47", 0, 0.97)
    if workshop_check_result:
        map_name = "工坊"
        print(f"insta关卡识别结果: {map_name}")

    # 检查 Quad
    quad_check_result = find_color_ex(279, 466, 284, 471, "E6DEBF", 0, 0.97)
    if quad_check_result:
        map_name = "方院"
        print(f"insta关卡识别结果: {map_name}")

    # 检查 DarkCastle
    dark_castle_check_result = find_color_ex(306, 425, 311, 430, "868923", 0, 0.97)
    if dark_castle_check_result:
        map_name = "黑暗城堡"
        print(f"insta关卡识别结果: {map_name}")

    # 检查 MuddyPuddles
    muddy_puddles_check_result = find_color_ex(318, 452, 323, 457, "945539", 0, 0.97)
    if muddy_puddles_check_result:
        muddy_puddles_second_check_result = find_color_ex(338, 410, 343, 415, "814831", 0, 0.97)
        if muddy_puddles_second_check_result:
            map_name = "泥泞的水坑"
            print(f"insta关卡识别结果: {map_name}")

    # 检查 Ouch
    ouch_check_result = find_color_ex(270, 440, 275, 445, "756B6D", 0, 0.97)
    if ouch_check_result:
        map_name = "#哎哟"
        print(f"insta关卡识别结果: {map_name}")

    # 打印最终识别结果
    print(f"最终insta关卡识别结果: {map_name}")

    # 返回主页面
    move2(55, 55)  # 返回
    delay()
    left_click(1)
    delay()

    return map_name


def collect_insta():
    print("开始执行 collect_insta 函数")
    delay(config.COLLECT_INSTA_DELAY_TIME)

    while True:
        print("查找‘收集’按钮")
        color_pos = find_color_ex(685, 494, 690, 499, "3CD500", 0, 0.9)
        if color_pos:
            intX, intY = map(int, color_pos.split('|'))
            if intX > 0 and intY > 0:  # “收集”按钮可用
                print("找到‘收集’按钮，点击")
                move2(685, 494)
                delay()
                left_click(1)
                delay(3000)

                print("查找 insta 猴")
                color_pos = find_color_ex(544, 378, 549, 383, "FFFFFF", 0, 0.8)
                if color_pos: # 只有两个 insta 猴
                    print("找到两个 insta 猴")
                    delay()
                    move2(544, 378)
                    delay()
                    left_click(1)
                    delay(1500)
                    if config.LOG_FILE_GRANULARITY >= 3:  # 截图 insta 猴保存
                        print("截图保存 insta 猴")
                        save_screenshot(424, 204, 863, 607, config.CUSTOM_SAVE_PATH)
                    left_click(1)
                    delay(1500)
                    move2(744, 378)
                    delay()
                    left_click(1)
                    delay(1500)
                    if config.LOG_FILE_GRANULARITY >= 3:  # 截图 insta 猴保存
                        print("截图保存 insta 猴")
                        save_screenshot(424, 204, 863, 607, config.CUSTOM_SAVE_PATH)
                    left_click(1)
                    delay(1500)
                    if config.LOG_FILE_GRANULARITY >= 1:  # 记录日志
                        print("记录日志：收集到 Insta 猴 x 2")
                        write_game_log("收集到Insta猴 x 2", config.CUSTOM_SAVE_PATH)

                else:  # 有三个 insta 猴
                    print("找到三个 insta 猴")
                    delay()
                    move2(444, 378)
                    delay()
                    left_click(1)
                    delay(1500)
                    if config.LOG_FILE_GRANULARITY >= 3:  # 截图 insta 猴保存
                        print("截图保存 insta 猴")
                        save_screenshot(424, 204, 863, 607, config.CUSTOM_SAVE_PATH)
                    left_click(1)
                    delay(1500)
                    move2(644, 378)
                    delay()
                    left_click(1)
                    delay(1500)
                    if config.LOG_FILE_GRANULARITY >= 3:  # 截图 insta 猴保存
                        print("截图保存 insta 猴")
                        save_screenshot(424, 204, 863, 607, config.CUSTOM_SAVE_PATH)
                    left_click(1)
                    delay(1500)
                    move2(844, 378)
                    delay()
                    left_click(1)
                    delay(1500)
                    if config.LOG_FILE_GRANULARITY >= 3:  # 截图 insta 猴保存
                        print("截图保存 insta 猴")
                        save_screenshot(424, 204, 863, 607, config.CUSTOM_SAVE_PATH)
                    left_click(1)
                    delay(1500)
                    if config.LOG_FILE_GRANULARITY >= 1:  # 记录日志
                        print("记录日志：收集到 Insta 猴 x 3")
                        write_game_log("收集到Insta猴 x 3", config.CUSTOM_SAVE_PATH)

                print("点击‘继续’按钮")
                move2(685, 707)  # 继续
                delay(1500)
                left_click(1)
                delay(1500)

                print("判断礼物是否开完")
                color_pos = find_color_ex(34, 75, 39, 80, "00CAF8", 0, 0.9)  # BGR "F8CA00" -> RGB "00CAF8"
                if color_pos:
                    intX, intY = map(int, color_pos.split('|'))
                    if intX > 0 and intY > 0:  # 判断礼物是否开完
                        print("礼物已开完，返回")
                        delay()
                        move2(50, 65)  # 礼物开完，返回
                        delay()
                        left_click(1)
                        break
                else:
                    print("礼物未开完，继续查找‘收集’按钮")
                    continue
        else:
            print("未找到‘收集’按钮，退出")
            break
