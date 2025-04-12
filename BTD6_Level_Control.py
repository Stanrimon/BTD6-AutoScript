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


def see_if_next_level_available() -> int:
    """
    判断是否可以进入下一关的逻辑。

    :return: 1 表示可以进入下一关，0 表示不能进入下一关。
    """
    # 初始状态，默认不可进入下一关
    check_if_next_level_available = 0

    # 第一次查找 "下一关" 按钮
    check_result = find_color_ex(1215, 690, 1220, 695, "FFFFFF", 0, 0.9)
    if check_result:  # 如果找到按钮可以点击
        # print('check 1')
        int_x0, int_y0 = map(int, check_result.split("|"))
        if int_x0 > 0 and int_y0 > 0:  # 二次判断防止误识别，此处识别猴子名称框中的棕色
            check_result = find_color_ex(1240, 100, 1245, 105, "946336", 0, 0.9)
            if check_result:
                # print('check 2')
                int_x1, int_y1 = map(int, check_result.split("|"))
                if int_x1 > 0 and int_y1 > 0:
                    # 等待 500 毫秒
                    delay(500)

                    # 三次判断防止升级卡住，“下一关”按钮可点击，即此时为关末
                    check_result = find_color_ex(1215, 690, 1220, 695, "FFFFFF", 0, 0.95)
                    if check_result:
                        # print('check 3')
                        int_x2, int_y2 = map(int, check_result.split("|"))
                        if int_x2 > 0 and int_y2 > 0:
                            # "下一关" 按钮可点击
                            check_if_next_level_available = 1
                        else:
                            # "下一关" 按钮不可点击，执行点击以防止卡住
                            for _ in range(5):
                                delay()  # 延迟时间，可以根据需要调整
                                idle_clicking()
                            delay(500)
                            check_if_next_level_available = 1

    return check_if_next_level_available


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

    break_flag = 0

    while config.NOW_GAME_LEVEL != level and break_flag == 0:

        if config.SCRIPT_STOP == 1:
            return
        # 延迟 100 毫秒，控制识别频率
        delay()

        # 检查当前关卡是否结束
        level_end_flag = see_if_next_level_available()

        if level_end_flag == 1:  # "下一关"按钮可用，关卡结束

            config.GAME_SPEED = -abs(config.GAME_SPEED)  # 游戏速度由之前的速度转变为暂停，用负数代表
            config.NOW_GAME_LEVEL += 1  # 正常游戏，关卡计数器 +1
            config.RETRY_TIMES = 0  # 成功进入下一关，重置重试次数

            if config.STOP_HERE == 0:
                change_game_speed(3)  # 三倍速进入下一关
            else:
                config.STOP_HERE = 0  # 将在本局开头停止的标识重置

            # 记录日志
            if config.LOG_FILE_GRANULARITY >= 2:
                write_game_log(f"关卡 {config.NOW_GAME_LEVEL}", config.CUSTOM_SAVE_PATH)

        # 检查当前关卡是否失败
        check_fail_result = find_color_ex(400, 500, 405, 505, "3C6091", 0, 0.95)
        if check_fail_result:  # 找到了失败框的蓝色
            # 二次判断，识别猴子名称框中的棕色
            check_fail_result2 = find_color_ex(1240, 110, 1245, 115, "946336", 0, 0.9)
            if not check_fail_result2:  # 猴子名称框中的棕色找不到，证明此时的确在中断状态，关卡失败

                config.FAIL_COUNT += 1  # 增加全局失败统计
                config.GAME_SPEED = -1  # 此时游戏是暂停的，且会变为一倍速
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
                    change_game_speed(3)  # 三倍速进入下一关

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


'''
# 定义保存目录
save_directory = "D:/desktop"  # 确保路径存在，否则需要创建
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# 初始化 EasyOCR 识别器
reader = easyocr.Reader(['en'], gpu=True)  # 禁用 GPU，可根据需要启用 GPU：gpu=True

# 定义屏幕区域（左上角 (100, 100) 到 (180, 150)）
if config.MAX_GAME_LEVEL >= 100:
    monitor = {"top": 51, "left": 920, "width": 1039 - 920, "height": 77 - 45}  # 矩形
elif config.MAX_GAME_LEVEL < 100:
    monitor = {"top": 51, "left": 930, "width": 46, "height": 40}  # 矩形


def capture_screen_and_recognize_digits():
    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)

        # 图像预处理
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

        # 二值化图像取反
        inverted_binary = cv2.bitwise_not(binary)

        # 保存取反后的图像到指定路径
        save_path = os.path.join(save_directory, '1.png')
        cv2.imwrite(save_path, inverted_binary)
        # print(f"取反后的图像已保存到: {save_path}")

        # OCR 识别
        results = reader.readtext(inverted_binary, allowlist='0123456789')  # 限制为数字
        # results = reader.recognize(inverted_binary)  # 直接对裁剪区域进行识别
        # print('results:', results)  # 打印完整 OCR 结果

        # 输出所有识别的文本（仅数字）
        recognized_numbers = [text for (bbox, text, prob) in results]
        print("识别到的数字:", recognized_numbers)

        return recognized_numbers


# 主循环
print("开始循环检测屏幕中的阿拉伯数字...")
while True:

    time.sleep(0.2)
    # 开始计时
    start_time = time.time()

    # 捕获屏幕并识别数字
    digits = capture_screen_and_recognize_digits()

    # 结束计时
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 打印结果和耗时
    if digits:
        print(f"检测到数字: {digits}，耗时: {elapsed_time:.2f} 秒")
    else:
        print(f"未检测到数字，耗时: {elapsed_time:.2f} 秒")

    # 为了不占用过多资源，可以稍作延迟
    # time.sleep(0.5)  # 每次循环间隔 0.5 秒
'''
