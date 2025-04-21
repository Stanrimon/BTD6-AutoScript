import os
from datetime import datetime
from PIL import ImageGrab  # 用于截图功能
from config import config


def write_game_log(log_text, save_path=config.CUSTOM_SAVE_PATH):
    """
    将日志内容写入指定路径的日志文件。

    :param log_text: 写入内容的字符串
    :param save_path: 保存日志文件的路径（默认为 D:\\Desktop）
    """
    # CUSTOM_SAVE_PATH = "D:\\Desktop\\BTD6"

    if config.LOG_FILE_GRANULARITY < 1:
        return

    try:
        # 检查保存路径是否存在，如果不存在则创建
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # 获取当前日期，用于生成日志文件名
        date_str = datetime.now().strftime("%Y-%m-%d")  # 例如：2023-10-17
        log_filename = f"game_log_{date_str}.txt"  # 日志文件名，例如：game_log_2023-10-17.txt

        # 完整的日志文件路径
        log_file_path = os.path.join(save_path, log_filename)

        # 获取当前时间，用于标记每条日志记录的时间戳
        time_str = datetime.now().strftime("%H:%M:%S")  # 例如：15:30:45

        # 写入日志内容到文件
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{time_str}] {log_text}\n")

        # print(f"日志已成功写入到 {log_file_path}")

    except Exception as e:
        print(f"写入日志时发生错误：{e}")


# 定义截图函数
def save_screenshot(x0, y0, x1, y1, save_path=config.CUSTOM_SAVE_PATH):
    """
    指定位置截图并保存至对应文件夹

    参数：
    x0, y0, x1, y1: int，截图区域的左上与右下顶点坐标
    save_path: str，截图保存位置（绝对路径）
    """
    try:
        # 检查保存路径是否存在，如果不存在则创建
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # 获取当前日期，用于生成日志文件名
        date_str = datetime.now().strftime("%Y-%m-%d")  # 例如：2023-10-17
        time_str = datetime.now().strftime("%H-%M-%S")  # 例如：15:30:45
        pic_filename = f"game_log_{date_str}_{time_str}-气球塔防器灵截图.jpg"  # 日志文件名

        # 完整的截图文件路径
        pic_file_path = os.path.join(save_path, pic_filename)

        # 截图并保存
        screenshot = ImageGrab.grab(bbox=(x0 + config.WINDOWS_OFFSET_CALCULATED_X,
                                          y0 + config.WINDOWS_OFFSET_CALCULATED_Y,
                                          x1 + config.WINDOWS_OFFSET_CALCULATED_X,
                                          y1 + config.WINDOWS_OFFSET_CALCULATED_Y
                                          )
                                    )  # bbox为截图区域
        screenshot.save(pic_file_path, "JPEG")

        print(f"截图已保存至: {pic_file_path}")

    except Exception as e:
        print(f"保存截图时发生错误：{e}")

# 示例调用
# save_screenshot(424, 204, 863, 607)  # 指定保存路径
