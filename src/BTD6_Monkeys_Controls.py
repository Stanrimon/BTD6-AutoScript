from config import config
from BTD6_TraceLogs import write_game_log
from BTD6_Level_Control import find_color_ex, resovle_keybind
from BTD6_Key_and_Mouse_Controls import delay, move2, left_click, key_press


"""
函数名称：monkey_place
函数功能：放置目标猴子
入口参数：
    arr_monkey：列表，包含猴子坐标信息、放下猴子后的升级、快捷键。如 [200, 400, 0, 0, 0, "Q"]
    top, mid, btm：三个整数，表示期望的猴子三路升级等级。
出口参数：
    返回修改后的 arr_monkey 列表，更新了猴子的等级信息。
备    注：
    调用了 monkey_upgrade()，以在放置后即时升级放下的猴子。
"""

'''def monkey_place(arr_monkey, top, mid, btm):
    delay()
    move2(arr_monkey[0], arr_monkey[1])
    delay()
    key_press(arr_monkey[5])
    delay()
    left_click()
    delay()

    if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
        write_game_log(f"放置猴子，快捷键{arr_monkey[5]}；坐标{arr_monkey[0]}，{arr_monkey[1]}", config.CUSTOM_SAVE_PATH)

    if top or mid or btm:
        arr_monkey = monkey_upgrade(arr_monkey, top, mid, btm)
    return arr_monkey
'''


def monkey_place(monkey, top=0, mid=0, btm=0):
    # 使用 Monkey 对象的属性
    move2(monkey.x, monkey.y)  # 移动鼠标到猴子的位置
    key_press(monkey.key)  # 按下快捷键
    left_click()

    if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
        write_game_log(
            f"放置猴子，应用于{monkey.monkey_id}；坐标 {monkey.x}, {monkey.y}",
            config.CUSTOM_SAVE_PATH,
        )

    if top or mid or btm:
        # 如果有升级需求，调用升级函数
        monkey_upgrade(monkey, top, mid, btm)

    return monkey


"""
函数名称：monkey_place_desperate
函数功能：急切地放置目标猴子
入口参数：
    arr_monkey：列表，包含猴子坐标信息的数组。如 [200, 400, 0, 0, 0, "Q"]
    try_times：整数，将进行尝试放置的次数。
出口参数：
    返回 arr_monkey 列表。
备    注：
    由于是连续按升级键，当钱过多时可能升不止一级——但基本不会在此情况使用本函数。
"""


def monkey_place_desperate(monkey, try_times):
    move2(monkey.x, monkey.y)  # 移动鼠标到猴子的位置
    for _ in range(try_times):
        key_press(monkey.key)  # 按下快捷键
        left_click()
    move2(1200, 400)  # 清除输入

    if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
        write_game_log(
            f"急切地放置猴子，应用于 {monkey.monkey_id}；坐标 {monkey.x}, {monkey.y}，尝试次数：{try_times}",
            config.CUSTOM_SAVE_PATH,
        )
    return monkey


"""
函数名称：monkey_sell
函数功能：出售目标猴子
入口参数：
    arr_monkey：列表，包含猴子坐标信息的数组。如 [200, 400, 0, 0, 0, "Q"]
出口参数：
    无。
备    注：
    出售猴子是通过选择猴子并按下Backspace键来完成的。
"""


def monkey_sell(monkey):
    move2(monkey.x, monkey.y)
    left_click()
    key_press('出售')

    if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
        write_game_log(f"出售猴子，应用于{monkey.monkey_id}；坐标{monkey.x}, {monkey.y}", config.CUSTOM_SAVE_PATH)


"""
函数名称：monkey_upgrade
函数功能：升级目标猴子
入口参数：
    arr_monkey：列表，包含猴子坐标、当前等级、快捷键信息的数组。如 [200, 400, 0, 0, 0, "Q"]
    top, mid, btm：期望的猴子三路等级。
出口参数：
    返回更新后的 arr_monkey 列表，包含新的等级信息。
备    注：
    通过分别按下不同的键来升级猴子的三个路径。
"""


def monkey_upgrade(monkey, top, mid, btm):
    """
    升级指定的猴子到目标等级。
    :param monkey: Monkey 对象
    :param top: 目标 Path 1 的等级
    :param mid: 目标 Path 2 的等级
    :param btm: 目标 Path 3 的等级
    """
    move2(monkey.x, monkey.y)  # 使用 Monkey 对象的坐标属性
    left_click()

    # 通过快捷键升级路径 1
    for _ in range(top):  # 计算需要升级的次数
        key_press('升级路线1')

    # 通过快捷键升级路径 2
    for _ in range(mid):
        key_press('升级路线2')

    # 通过快捷键升级路径 3
    for _ in range(btm):
        key_press('升级路线3')

    # 更新 Monkey 对象的路径等级
    monkey.path1_level = top
    monkey.path2_level = mid
    monkey.path3_level = btm

    left_click()

    # 记录日志
    if config.LOG_FILE_GRANULARITY >= 2:
        write_game_log(
            (
                f"升级猴子，应用于{monkey.monkey_id}；快捷键 {monkey.key}；"
                f"坐标 {monkey.x}, {monkey.y}，"
                f"等级 {monkey.path1_level}, {monkey.path2_level}, {monkey.path3_level}"
            ),
            config.CUSTOM_SAVE_PATH
        )

    return monkey


"""
函数名称：monkey_upgrade_desperate
函数功能：急切地升级目标猴子
入口参数：
    arr_monkey：列表，包含猴子坐标、当前等级、快捷键信息的数组。如 [200, 400, 0, 0, 0, "Q"]
    top, mid, btm：期望的猴子三路等级；try_times：将进行尝试升级的次数。
出口参数：
    返回更新后的 arr_monkey 列表，包含新的等级信息。
备    注：
    由于是连续按升级键，当钱过多时可能升不止一级。
"""


def monkey_upgrade_desperate(monkey, top, mid, btm, try_times):
    move2(monkey.x, monkey.y)  # 使用 Monkey 对象的坐标属性
    left_click()
    for _ in range(try_times):
        # 通过快捷键升级路径 1
        for _ in range(top):  # 计算需要升级的次数
            key_press('升级路线1')

        # 通过快捷键升级路径 2
        for _ in range(mid):
            key_press('升级路线2')

        # 通过快捷键升级路径 3
        for _ in range(btm):
            key_press('升级路线3')

    # 更新 Monkey 对象的路径等级
    monkey.path1_level = top
    monkey.path2_level = mid
    monkey.path3_level = btm

    left_click()

    # 记录日志
    if config.LOG_FILE_GRANULARITY >= 2:
        write_game_log(
            (
                f"急切地升级猴子，应用于{monkey.monkey_id}；"
                f"坐标 {monkey.x}, {monkey.y}，"
                f"等级 {monkey.path1_level}, {monkey.path2_level}, {monkey.path3_level}，"
                f"尝试次数：{try_times}"
            ),
            config.CUSTOM_SAVE_PATH
        )

    return monkey


"""
函数名称：monkey_retarget
函数功能：改变猴子瞄准优先级
入口参数：
    arr_monkey：列表，包含猴子坐标信息，如 [200, 400, 0, 0, 0, "Q"]
    mode：整数，等同于对猴子按Tab键的次数，以改变猴子瞄准方式。
出口参数：
    无。
备    注：
    不同猴子瞄准方式不同，需自行测试。
"""


def monkey_retarget(monkey, mode):
    move2(monkey.x, monkey.y)
    left_click()

    for _ in range(mode):
        key_press('更改目标')

    move2(monkey.x, monkey.y)
    left_click()

    if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
        write_game_log(
            f"改变猴子攻击优先级，应用于{monkey.monkey_id}；坐标{monkey.x}, {monkey.y}，按键切换次数：{mode}",
            config.CUSTOM_SAVE_PATH
        )


"""
函数名称：monkey_retarget_aim
函数功能：为有瞄准功能的猴子锁定目标坐标
入口参数：

出口参数：
    无。
备    注：
    不同猴子瞄准方式不同，需自行测试。假设快捷键为“~”。
"""


def monkey_retarget_aim(monkey, mode, target_x, target_y):
    move2(monkey.x, monkey.y)
    left_click()

    for _ in range(mode):
        key_press('更改目标')

    if 1:  # 本来想判断有x，y值才进行，但发现潜艇可以没有，因此这里实际上不判断，保留逻辑

        b = resovle_keybind("直升机飞行员", 'b')
        l = resovle_keybind("工程师猴", 'l')
        m = resovle_keybind("机枪猴", 'm')
        n = resovle_keybind("迫击炮猴", 'n')
        j = resovle_keybind("刺钉工厂", 'n')
        a = resovle_keybind("法师猴", 'a')
        x = resovle_keybind("猴子潜艇", 'x')
        v = resovle_keybind("皇家飞行员", 'v')

        if monkey.key in [b, l, m, n, j, "直升机飞行员", "工程师猴", "机枪猴", "迫击炮猴", "刺钉工厂"]:  # 直升机/工程师/机枪猴/迫击炮的瞄准：直接点瞄准键、鼠标对应位置点击
            key_press('特制猴子')
            move2(target_x, target_y)
            left_click()

        elif monkey.key in [a, "法师猴"]:  # 法师的瞄准：死灵法用pageup瞄准，火法用pagedown瞄准
            if monkey.path3_level >= 3:  # 下路法师
                key_press('特制猴子2')
            else:  # 火法
                key_press('特制猴子')

            move2(target_x, target_y)
            left_click()

        elif monkey.key in [x, "猴子潜艇"]:  # 潜艇的瞄准，仅按键即可沉浮
            key_press('特制猴子')

        elif monkey.key in [v, "皇家飞行员"]:  # 皇家飞行员“中央路线”无法使用快捷键，只能鼠标移动点击
            from pyautogui import mouseDown, mouseUp  # 此处特殊，left_click会由于过快被识别为双击，故引入原始函数进行延时

            if_monkey_placed_left = monkey.x < config.MIDDLE_POS_X

            move2(150 + if_monkey_placed_left * 800, 280)
            mouseDown()
            delay(0.5 * config.DELAY_TIME)
            mouseUp()
            delay(0.5 * config.DELAY_TIME)
            move2(target_x, target_y)
            left_click()
        else:  # 其它猴子的瞄准或者特殊修改（例如飞镖猴切换迷彩锁定、格温丢瓶子瞄准）：直接点瞄准键，如果有目标位置，则鼠标对应位置点击
            key_press('特制猴子')
            if target_x and target_y:
                move2(target_x, target_y)
                left_click()

    move2(monkey.x, monkey.y)
    left_click()

    if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
        write_game_log(
            f"改变猴子瞄准锁定，应用于{monkey.monkey_id}；坐标{monkey.x}, {monkey.y}",
            config.CUSTOM_SAVE_PATH
        )


def use_geraldo_tool(tool_list):
    """
    函数功能：使用杰拉尔多的道具，可单个使用道具，也可多个道具一起使用。
    """

    if_geraldo_placed_left = int(config.IF_GERALDO_PLACED_LEFT)
    print("if_geraldo_placed_left:", if_geraldo_placed_left)
    # 定义工具名称到序号的映射
    tool_mapping = {
        "turret": 0,
        "nails": 1,
        "idol": 2,
        "pickles": 3,
        "figure": 4,
        "camo": 5,
        "glue": 6,
        "stone": 7,
        "cape": 8,
        "blade": 9,
        "sauce": 10,
        "fertilizer": 11,
        "rabbit": 12,
        "rejuv": 13,
        "genie": 14,
        "paragon": 15,

        "射击炮塔": 0,
        "旧钉子堆": 1,
        "令人毛骨悚然的神像": 2,
        "泡菜罐": 3,
        "罕见的昆西可动人偶": 4,
        "识破隐形药水": 5,
        "一管神奇胶水": 6,
        "磨刀石": 7,
        "破旧的英雄斗篷": 8,
        "利刃陷阱": 9,
        "一瓶“格里之火”辣酱": 10,
        "肥料": 11,
        "宠物兔": 12,
        "回春药剂": 13,
        "精灵瓶": 14,
        "巅峰力量图腾": 15,
    }

    # 杰拉尔多商店的道具位置
    geraldo_tool_x = [60, 120, 180, 240] * 4
    geraldo_tool_y = [160] * 4 + [260] * 4 + [360] * 4 + [460] * 4

    # 如果输入的是一维数组，转换为二维数组
    if isinstance(tool_list[0], (int, float)):
        tool_list = [tool_list]

    key_press('英雄')  # 选中杰拉尔多

    # 如果商店未开启，进行开启操作
    if config.IF_SHOP_OPENED != 1:  # 第一次使用道具，判断商店是否开启
        print('正判断商店是否开启')
        delay(350)
        if not find_color_ex(88 + 938 * if_geraldo_placed_left, 425,
                             93 + 938 * if_geraldo_placed_left,
                             430, "6D432F", 0, 0.9):
            print('COLOR NOTFOUND AT ', 88 + 938 * if_geraldo_placed_left, ',425. opening shop')
            move2(300 + 500 * if_geraldo_placed_left, 160)
            left_click()
            delay(300)
        config.IF_SHOP_OPENED = 1  # 将商店设置为已开启
        # print("Shop opened.")
    else:
        print('商店已开启，无需判断')

    # 遍历工具列表，逐个放置道具
    for tool in tool_list:
        tool_name = tool[2].lower()  # 确保道具名称为小写
        tool_number = tool_mapping.get(tool_name, -1)  # 获取工具编号

        if tool_number != -1:  # 如果工具编号有效
            # 根据杰拉尔多商店位置计算点击位置
            if if_geraldo_placed_left:
                # 商店在右侧
                move2(geraldo_tool_x[tool_number] + 820, geraldo_tool_y[tool_number])
            else:
                # 商店在左侧
                move2(geraldo_tool_x[tool_number], geraldo_tool_y[tool_number])

            left_click()  # 点击道具
            # print("Clicking tool")

            # 检查目标位置是否在商店框范围内
            if config.IF_GERALDO_PLACED_LEFT:  # 商店在右边
                if tool[0] > 838 and 66 < tool[1] < 666:
                    move2(600, 300)  # 目标位置在商店框范围内，需先拿出商店框
            else:  # 商店在左边
                if tool[0] < 277 and 66 < tool[1] < 666:
                    move2(600, 300)  # 目标位置在商店框范围内，需先拿出商店框

            move2(tool[0], tool[1])  # 移动到道具的放置位置
            left_click()  # 放置道具
            # print("Placing tool")

            if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
                write_game_log(
                    f"放置杰哥道具：{tool[3]}；坐标{tool[0]},{tool[1]}",
                    config.CUSTOM_SAVE_PATH
                )
    key_press('esc')  # 关闭杰拉尔多商店窗口


"""
函数名称：monkey_overclock
函数功能：超频指定猴子
入口参数：
    arr_monkey：列表，包含猴子坐标信息，如 [200, 400, 0, 0, 0, "Q"]
    hotkey：字符串，本局游戏超频的快捷键。
出口参数：
    无。
备    注：
    超频的CD为45000ms。
"""


def monkey_overclock(monkey, hotkey):
    key_press(hotkey)
    move2(monkey.x, monkey.y)
    left_click()

    if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
        write_game_log(
            f"超频猴子；坐标{monkey.x}, {monkey.y}",
            config.CUSTOM_SAVE_PATH
        )


def activate_map_item(x1, y1, x2, y2):
    move2(x1, y1)
    left_click()
    if x2 and y2:
        delay(200)
        move2(x2, y2)
        left_click()

    if config.LOG_FILE_GRANULARITY >= 2:  # 记录日志
        write_game_log(
            f"互动地图元素；坐标{x1}, {y1}；{x2}, {y2}",
            config.CUSTOM_SAVE_PATH
        )
