# ==== 导入模块 ====
# 标准库
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import configparser

# 第三方库
import keyboard
import pyautogui
from PIL import ImageGrab

# 本地模块
from BTD6_ExecuteCommands import play_game, play_game_test_placement
from BTDWindow import find_and_focus_window
from BTD6_Level_Control import return_to_menu, get_insta_map_name, collect_insta
from BTD6_Key_and_Mouse_Controls import key_press, ControlMouseUponKeyPress
from BTD6_TraceLogs import write_game_log
from config import config, global_text, keybind_config, DEFAULT_KEY_MAPPING, KEY_OPTIONS

# ==== 全局变量初始化 ====
show_mouse_info = False  # 控制鼠标位置显示
loaded_config = configparser.ConfigParser()
config_file_path = "custom_keybind.ini"

# ==== 主窗口初始化 ====
root = tk.Tk()
root.title("气球塔防6脚本控制面板-龙雕心文")
root.geometry("500x600")
hook_id = None


def resovle_keybind(key_name, default_key):
    resolved_key = keybind_config.get_key(key_name)
    if resolved_key:
        return resolved_key
    else:
        return default_key


resoved_keybind_start_script = resovle_keybind("开始脚本", 'f10')
resoved_keybind_stop_script = resovle_keybind("停止脚本", 'f12')


# ==== 创建主窗口 ====
def create_main_page(root):
    # ==== 主窗口内容 ====

    # 创建 Tab 页
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # ==== 主页面 ====
    main_page = tk.Frame(notebook)
    notebook.add(main_page, text="主页面")

    # ==== 后台线程运行脚本 ====
    def start_script_in_thread():
        config.START_BUTTON_ONOFF = 1
        thread = threading.Thread(target=start_script, daemon=True)
        thread.start()

    # ==== 停止脚本 ====
    def stop_script():
        print(f"{resoved_keybind_stop_script}被按下，脚本终止！")
        config.SCRIPT_STOP = 1
        config.START_BUTTON_ONOFF = 0
        start_button.config(text=f"开始脚本（{resoved_keybind_start_script}）", bg="green", fg="white")

    def listen_for_stop():
        keyboard.add_hotkey(resoved_keybind_stop_script, stop_script)

    # ==== 监听启动键 ====
    def listen_for_start():
        keyboard.add_hotkey(resoved_keybind_start_script, start_script_in_thread)

    listener_thread = threading.Thread(target=listen_for_stop, daemon=True)
    listener_thread.start()

    listener_thread2 = threading.Thread(target=listen_for_start, daemon=True)
    listener_thread2.start()

    # ==== 应用设置 ====
    def apply_changes():
        selected_mode = run_mode_var.get()
        try:

            # 添加自然排序处理函数
            def natural_sort_key(s):
                import re
                return [int(text) if text.isdigit() else text.lower()
                        for text in re.split(r'(\d+)', os.path.basename(s))]

            if repeat_scale.get() > 0:
                repeat_times = int(repeat_scale.get())
            elif repeat_scale.get() == 0:
                repeat_times = 99999  # 循环次数为0时代表无限

            config.REPEAT_TIMES = repeat_times
            print(f"循环次数设置为: {repeat_times}")

            # 先清空选择的关卡列表
            selected_files_listbox.delete(0, tk.END)

            if selected_mode == "选择单一关卡的 xlsx 文件":
                file_path = filedialog.askopenfilename(title="选择单一关卡的 xlsx 文件", filetypes=[("xlsx files", "*.xlsx")])
                if file_path:
                    print(f"选择的文件路径: {file_path}")
                    config.SELECTED_FILE = file_path
                    # 显示文件名
                    selected_files_listbox.insert(tk.END, os.path.basename(file_path))

                else:
                    messagebox.showwarning("未选择文件", "您没有选择任何 xlsx 文件。")
                    return

            elif selected_mode == "选择多个文件循环":
                file_paths = filedialog.askopenfilenames(title="请选择包含多个关卡的文件", filetypes=[("xlsx files", "*.xlsx")])
                if file_paths:
                    # 按自然顺序排序文件路径
                    sorted_files = sorted(file_paths, key=natural_sort_key)
                    config.SELECTED_FILES = sorted_files  # 存储排序后的列表
                    print(f"选择的文件路径列表: {file_paths}")
                    # 显示所有文件名
                    for path in sorted_files:
                        selected_files_listbox.insert(tk.END, os.path.basename(path))

                else:
                    messagebox.showwarning("未选择文件", "您没有选择任何文件。")


            elif selected_mode == "循环刷insta猴":
                file_paths = filedialog.askopenfilenames(title="请选择包含12个专家图的xlsx文件", filetypes=[("xlsx files", "*.xlsx")])
                if file_paths:
                    # 检查文件名是否包含所有必要的地图关键词
                    required_maps = ["冰河之径", "黑暗地下城", "避难所", "峡谷", "水淹山谷", "炼狱", "血腥水坑", "工坊", "方院", "黑暗城堡", "泥泞的水坑", "#哎哟"]
                    missing_maps = []
                    for map_name in required_maps:
                        found = False
                        for file_path in file_paths:
                            if map_name in os.path.basename(file_path):
                                found = True
                                break
                        if not found:
                            missing_maps.append(map_name)
                    if missing_maps:
                        messagebox.showerror("关卡文件缺失", f"关卡文件缺失：{', '.join(missing_maps)}\n刷insta活动需要识别所有专家图阵型，文件名需要包含地图名称。\n请确保选择了所有专家图的阵型，或修改所选文件的文件名")
                        return
                    # 按自然顺序排序文件路径
                    sorted_files = sorted(file_paths, key=natural_sort_key)
                    config.SELECTED_FILES = sorted_files  # 存储排序后的列表
                    print(f"选择的文件路径列表: {file_paths}")
                    # 显示所有文件名
                    for path in sorted_files:
                        selected_files_listbox.insert(tk.END, os.path.basename(path))
                else:
                    messagebox.showwarning("未选择文件", "您没有选择任何文件。")


            elif selected_mode == "模拟关卡放置":
                file_path = filedialog.askopenfilename(title="选择单一关卡的 xlsx 文件", filetypes=[("xlsx files", "*.xlsx")])
                if file_path:
                    print(f"选择的文件路径: {file_path}")
                    config.SELECTED_FILE = file_path
                    # 新增测试等级输入对话框
                    test_level = simpledialog.askinteger(
                        "测试等级设置",
                        "请输入测试等级数字:",
                        minvalue=1,  # 可选：限制最小输入值
                        maxvalue=500  # 可选：限制最大输入值
                    )
                    if test_level is not None:  # 如果用户没有取消输入
                        config.TEST_LEVEL = test_level
                    else:
                        print("警告：未输入测试等级，保持原设置或使用默认值")
                    # 显示文件名
                    selected_files_listbox.insert(tk.END, os.path.basename(file_path))

                else:
                    messagebox.showwarning("未选择文件", "您没有选择任何 xlsx 文件。")
                    return

            messagebox.showinfo("设置完成", f"运行模式: {selected_mode}\n循环次数: {repeat_times}")
        except ValueError:
            messagebox.showwarning("无效输入", "循环次数必须是有效的整数。")

    # ==== 启动脚本 ====
    def start_script():
        start_button.config(text=f"停止脚本（{resoved_keybind_stop_script}）", bg="red", fg="white")
        config.SCRIPT_STOP = 0

        selected_mode = run_mode_var.get()
        repeat_times = config.REPEAT_TIMES
        find_and_focus_window()

        # 游戏开始时清空指令显示
        global_text.command_history.clear()
        history_listbox.delete(0, tk.END)

        if selected_mode == "选择单一关卡的 xlsx 文件":
            # 更新当前文件显示
            current_file = os.path.basename(config.SELECTED_FILE)
            root.after(0, lambda: current_file_var.set(f"当前文件: {current_file}"))

            print(f"check1，文件: {config.SELECTED_FILE}")
            if not config.SELECTED_FILE:
                messagebox.showerror("错误", "未选择任何 xlsx 文件，请先应用设置。")
                return
            for i in range(repeat_times):
                if config.SCRIPT_STOP == 1:
                    return
                # 更新已完成数量
                root.after(50, lambda c=current_file, n=i: current_file_var.set(
                    f"进度({n}/{repeat_times})，当前文件: {c}"))
                config.new_game_reset()
                find_and_focus_window()
                print(f"运行模式1，文件: {config.SELECTED_FILE}")
                if config.LOG_FILE_GRANULARITY >= 1:
                    write_game_log(f"当前模式：单个文件循环，运行文件 {config.SELECTED_FILE} ",
                                    config.CUSTOM_SAVE_PATH
                                    )
                    
                play_game(config.SELECTED_FILE)
                return_to_menu()
                collect_insta()

                # 更新已完成数量
                root.after(0, lambda c=current_file, n=i: current_file_var.set(
                    f"进度({n + 1}/{repeat_times})，当前文件: {c}"))

        elif selected_mode == "选择多个文件循环":

            if not hasattr(config, "SELECTED_FILES") or not config.SELECTED_FILES:
                messagebox.showerror("错误", "未选择任何文件，请先应用设置。")
                return

            # 确保 SELECTED_FILES 是列表
            # config.SELECTED_FILES = list(config.SELECTED_FILES)

            total_loops = 0
            file_index = 0  # 用于追踪当前运行到哪个文件
            num_files = len(config.SELECTED_FILES)  # 文件总数
            while total_loops < repeat_times:
                if config.SCRIPT_STOP == 1:
                    return
                config.new_game_reset()
                find_and_focus_window()
                if total_loops >= repeat_times:
                    break
                # 取当前索引对应的文件

                file_path = config.SELECTED_FILES[file_index]

                # 更新当前文件显示、已完成数量
                current_file = os.path.basename(file_path)
                root.after(0, lambda f=current_file, n=total_loops: current_file_var.set(
                    f"进度({n}/{repeat_times})，当前文件: {f}"))

                print(f"运行模式2，文件: {file_path}")
                if config.LOG_FILE_GRANULARITY >= 1:
                    write_game_log(f"当前模式：多个文件循环，运行文件 {file_path} ",
                                    config.CUSTOM_SAVE_PATH
                                    )
                    
                play_game(file_path)
                return_to_menu()
                collect_insta()

                # 更新已完成数量
                root.after(0, lambda c=current_file, n=total_loops: current_file_var.set(
                    f"进度({n + 1}/{repeat_times})，当前文件: {c}"))

                # 更新文件索引并循环
                file_index = (file_index + 1) % num_files
                total_loops += 1


        elif selected_mode == "循环刷insta猴":
            if not hasattr(config, "SELECTED_FILES") or not config.SELECTED_FILES:
                messagebox.showerror("错误", "未选择任何文件，请先应用设置。")
                return
            total_loops = 0
            while total_loops < repeat_times:
                if config.SCRIPT_STOP == 1:
                    return
                config.new_game_reset()
                find_and_focus_window()
                if total_loops >= repeat_times:
                    break
                # 获取当前地图名称
                map_name = get_insta_map_name()
                print(f"当前地图: {map_name}")
                # 根据 map_name 找到对应的文件路径
                file_path = None
                for path in config.SELECTED_FILES:
                    if map_name in os.path.basename(path):
                        file_path = path
                        break
                if not file_path:
                    messagebox.showerror("错误", f"未找到与地图 {map_name} 对应的文件。")
                    return
                # 更新当前文件显示、已完成数量
                current_file = os.path.basename(file_path)
                root.after(0, lambda f=current_file, n=total_loops: current_file_var.set(
                    f"进度({n}/{repeat_times})，当前文件: {f}"))
                print(f"运行模式3，文件: {file_path}")
                if config.LOG_FILE_GRANULARITY >= 1:
                    write_game_log(f"当前模式：循环刷insta猴，运行文件 {file_path} ",
                                    config.CUSTOM_SAVE_PATH
                                    )
                    
                play_game(file_path)
                return_to_menu()
                collect_insta()

                # 更新已完成数量
                root.after(0, lambda c=current_file, n=total_loops: current_file_var.set(
                    f"进度({n + 1}/{repeat_times})，当前文件: {c}"))
                total_loops += 1

                
        elif selected_mode == "模拟关卡放置":
            # 更新当前文件显示
            current_file = os.path.basename(config.SELECTED_FILE)
            root.after(0, lambda: current_file_var.set(f"当前文件: {current_file}"))

            if not config.SELECTED_FILE:
                messagebox.showerror("错误", "未选择任何 xlsx 文件，请先应用设置。")
                return
            for i in range(repeat_times):
                if config.SCRIPT_STOP == 1:
                    return
                # 更新已完成数量
                root.after(50, lambda c=current_file, n=i: current_file_var.set(
                    f"进度({n}/{repeat_times})，当前文件: {c}"))
                config.new_game_reset()
                find_and_focus_window()
                print(f"运行模式4，文件: {config.SELECTED_FILE}")
                if config.LOG_FILE_GRANULARITY >= 1:
                    write_game_log(f"当前模式：模拟关卡放置，运行文件 {config.SELECTED_FILE} ",
                                    config.CUSTOM_SAVE_PATH
                                    )
                play_game_test_placement(config.SELECTED_FILE)

                # 更新已完成数量
                root.after(0, lambda c=current_file, n=i: current_file_var.set(
                    f"进度({n + 1}/{repeat_times})，当前文件: {c}"))

        print("脚本运行完成！")
        key_press(keybind_config.get_key("停止脚本"), 1)

    # ==== 主页面内容 ====
    # ==== 标题 ====
    title_label = tk.Label(main_page, text="气球塔防6脚本控制面板-20250419更新V48", font=("Microsoft Yahei", 16, "bold"))
    title_label.pack(pady=10)

    # ==== 循环次数滑动条 ====
    repeat_frame = tk.Frame(main_page)
    repeat_frame.pack(pady=10, fill="x")

    repeat_label = tk.Label(repeat_frame, text="循环次数: (0为无限)", font=("Microsoft Yahei", 12))
    repeat_label.pack(side="left", padx=5)

    # 创建水平滑动条
    repeat_scale = tk.Scale(
        repeat_frame,
        from_=0,  # 最小值
        to=30,  # 最大值
        orient="horizontal",  # 水平方向
        showvalue=True,  # 显示当前值
        resolution=1,  # 步长为1
        sliderlength=20,  # 滑块长度
        length=200  # 控件长度
    )
    repeat_scale.set(1)  # 设置默认值
    repeat_scale.pack(side="left", padx=5, fill="x", expand=True)

    # ==== 运行模式选择 ====
    mode_frame = tk.Frame(main_page)
    mode_frame.pack(pady=10, fill="x")

    mode_label = tk.Label(mode_frame, text="选择运行模式: ", font=("Microsoft Yahei", 12))
    mode_label.pack(side="left", padx=5)

    run_mode_var = tk.StringVar(value="选择单一关卡的 xlsx 文件")
    mode_dropdown = ttk.Combobox(mode_frame, textvariable=run_mode_var,
                                 values=["选择单一关卡的 xlsx 文件", "选择多个文件循环", "循环刷insta猴", "模拟关卡放置"])  # "循环刷insta猴"制作中
    mode_dropdown.pack(side="left", padx=5, expand=True)

    # ==== 加载关卡文件 ====
    load_level_file = tk.Frame(main_page)
    load_level_file.pack(pady=10, fill="x")

    apply_button = tk.Button(load_level_file, text="加载关卡文件", font=("Microsoft Yahei", 10), command=apply_changes)
    apply_button.pack(pady=10)

    # ==== 已选文件显示区域 ====
    selected_files_frame = tk.Frame(main_page)
    selected_files_frame.pack(pady=5, fill="both", expand=True)

    # 当前文件显示变量
    current_file_var = tk.StringVar(value="当前文件: 无")

    selected_files_label = tk.Label(
        selected_files_frame,
        textvariable=current_file_var,  # 改为使用变量
        font=("Microsoft Yahei", 12),
        anchor="w"
    )
    selected_files_label.pack(anchor="w", fill="x")

    listbox_frame = tk.Frame(selected_files_frame)
    listbox_frame.pack(fill="both", expand=True)

    # 显示已选关卡的滚动条和列表框
    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side="right", fill="y")

    selected_files_listbox = tk.Listbox(
        listbox_frame,
        yscrollcommand=scrollbar.set,
        height=4,
        selectmode=tk.SINGLE
    )
    selected_files_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=selected_files_listbox.yview)

    # ==== 开始按钮 ====
    start_button = tk.Button(
        main_page,
        text=f"开始脚本（{resoved_keybind_start_script}）",
        font=("Microsoft Yahei", 14, "bold"),
        command=lambda: start_script_in_thread() if config.START_BUTTON_ONOFF == 0 else stop_script(),
        bg="green",
        fg="white"
    )
    start_button.pack(pady=20)

    # ==== 指令显示区域 ====
    command_frame = tk.Frame(main_page)
    command_frame.pack(pady=10, fill="both", expand=True)  # 修改为填充布局

    # 创建带滚动条的Listbox
    history_listbox = tk.Listbox(
        command_frame,
        height=5,
        font=("Microsoft Yahei", 10),
        bg="#F0F0F0",  # 背景色
        selectbackground="#C0C0FF"  # 选中项背景色
    )
    scrollbar = tk.Scrollbar(command_frame)

    # 配置滚动条
    history_listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.config(command=history_listbox.yview)

    # 布局
    history_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 更新显示函数
    def update_command_display():
        # 获取当前命令长度
        current_length = len(global_text.command_history)

        # 判断是否有新指令添加（通过长度比较）
        if not hasattr(update_command_display, 'prev_length'):
            update_command_display.prev_length = 0  # 初始化历史长度记录

        if current_length > update_command_display.prev_length:
            # 有新指令时，更新显示并滚动到底部
            history_listbox.delete(0, tk.END)
            for cmd in global_text.command_history:  # 按原顺序显示
                history_listbox.insert(0, cmd)  # 始终插入到顶部
            history_listbox.yview_moveto(1.0)  # 滚动到页面下方
        else:
            # 无新指令时，不更新显示，保持原位置
            pass

        update_command_display.prev_length = current_length  # 更新历史长度记录
        root.after(200, update_command_display)  # 降低刷新频率到200ms

    # 初始化调用
    update_command_display()

    return notebook


# ==== 全局变量配置页面 ====
def create_config_page(notebook_to_append, config_identity):
    """
    创建全局变量配置页面，并添加到指定的 Notebook 中。
    :param notebook_to_append: ttk.Notebook，页面的父容器
    :param config_identity: GlobalConfig，包含全局变量默认值的配置实例
    """
    # 全局变量及其中文翻译
    translations = {
        "DELAY_TIME": "操作间延迟时间（毫秒）",
        "COLLECT_INSTA_DELAY_TIME": "insta开箱前等待时间（毫秒）",
        "LOG_FILE_GRANULARITY": "日志文件粒度",
        "CUSTOM_SAVE_PATH": "日志、截图保存路径",
        "ALLOWED_RETRY_TIMES": "重试次数（仅点击难度）",
        "CUSTOM_OFFSET_X": "修正窗口偏移 X",
        "CUSTOM_OFFSET_Y": "修正窗口偏移 Y",
    }

    # 定义允许用户修改的全局变量的列表
    allowed_keys = [
        "DELAY_TIME",
        "COLLECT_INSTA_DELAY_TIME",
        "LOG_FILE_GRANULARITY",
        "CUSTOM_SAVE_PATH",
        "ALLOWED_RETRY_TIMES",
        "CUSTOM_OFFSET_X",
        "CUSTOM_OFFSET_Y",
    ]

    # 创建一个新的 Frame 并添加到 notebook
    config_page = tk.Frame(notebook_to_append)
    notebook_to_append.add(config_page, text="全局设置")

    # 用于存储输入框，以便稍后获取用户输入值
    entry_widgets = {}

    # 创建滚动区域
    canvas_ccp = tk.Canvas(config_page)
    scrollbar = tk.Scrollbar(config_page, orient="vertical", command=canvas_ccp.yview)
    scrollable_frame_ccp = tk.Frame(canvas_ccp)

    scrollable_frame_ccp.bind(
        "<Configure>",
        lambda e: canvas_ccp.configure(scrollregion=canvas_ccp.bbox("all"))
    )

    canvas_ccp.create_window((0, 0), window=scrollable_frame_ccp, anchor="nw")
    canvas_ccp.configure(yscrollcommand=scrollbar.set)

    canvas_ccp.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 加载并更新全局变量的值
    def load_global_vars():
        config_file = 'global_var.ini'
        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            for key in allowed_keys:
                if key in config['DEFAULT']:
                    value = config['DEFAULT'][key]
                    default_type = type(getattr(config_identity, key))  # 获取默认值的类型
                    try:
                        if default_type is int:
                            value = int(value)
                        elif default_type is float:
                            value = float(value)
                        setattr(config_identity, key, value)  # 更新全局变量
                    except ValueError:
                        print(f"无法加载 {key}，请检查配置文件中的值是否正确！")

    # 保存全局变量到文件
    def save_global_vars():
        config_file = 'global_var.ini'
        config = configparser.ConfigParser()
        config['DEFAULT'] = {}
        for key in allowed_keys:
            config['DEFAULT'][key] = str(getattr(config_identity, key))
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        print(f"全局变量已保存到 {config_file}")

    # 动态生成输入框，只显示允许的键
    row_index = 0
    for key in allowed_keys:
        if key in translations:  # 检查是否有对应翻译项
            # 标签（左对齐）
            tk.Label(scrollable_frame_ccp, text=f"{translations[key]}:", anchor="w", width=20).grid(
                row=row_index, column=0, sticky="w", padx=10, pady=5)

            # 输入框（右对齐）
            entry = tk.Entry(scrollable_frame_ccp, width=30)
            entry.insert(0, getattr(config_identity, key))  # 设置初始值
            entry.grid(row=row_index, column=1, sticky="e", padx=10, pady=5)
            entry_widgets[key] = entry

            row_index += 1

    # 加载现有配置文件内容并更新页面显示
    def load_and_update_ui():
        load_global_vars()
        for key, entry in entry_widgets.items():
            entry.delete(0, tk.END)
            entry.insert(0, getattr(config_identity, key))  # 更新输入框的值

    # 应用更改按钮的逻辑
    def apply_changes_ccp():
        for key, entry in entry_widgets.items():
            value = entry.get()
            default_type = type(getattr(config_identity, key))  # 获取默认值的类型
            try:
                # 根据默认值的类型转换用户输入
                if default_type is int:
                    value = int(value)
                elif default_type is float:
                    value = float(value)
                setattr(config_identity, key, value)  # 更新全局变量的值
                print(f"{key} 已更新为 {value}")
            except ValueError:
                print(f"无法更新 {key}，请检查输入值是否正确！")
        save_global_vars()  # 保存到文件
        messagebox.showinfo("全局设置已保存", f"保存成功！【请重启脚本确认加载】")

    apply_button_ccp = tk.Button(scrollable_frame_ccp, text="保存更改", command=apply_changes_ccp)
    apply_button_ccp.grid(row=row_index, column=0, columnspan=2, pady=10)

    # 初次加载时调用
    load_and_update_ui()


# ==== 键位配置页面 ====
def create_keybind_page(notebook_to_append):
    # 默认键位配置
    default_key_mapping = DEFAULT_KEY_MAPPING
    key_options = KEY_OPTIONS

    key_mapping_vars = []

    # ==== 加载配置文件 ====
    def load_keybinds():
        try:
            with open(config_file_path, "r", encoding="utf-8-sig") as config_file:
                loaded_config.read_file(config_file)

            # 遍历默认键位配置
            for operation_name1, _ in default_key_mapping:
                if "Keybinds" in loaded_config and operation_name1 in loaded_config["Keybinds"]:
                    key = loaded_config["Keybinds"][operation_name1]  # 从配置文件获取键位
                    # 更新 key_mapping_vars 中对应的变量
                    for var_name, var1 in key_mapping_vars:
                        if var_name == operation_name1:
                            var1.set(key)  # 设置下拉框的值为配置文件中的键
                            break
        except FileNotFoundError:
            print(f"未找到配置文件 {config_file_path}，将使用默认键位设置。")
        except UnicodeDecodeError:
            print(f"配置文件 {config_file_path} 编码错误，请确保配置文件使用 utf-8 编码。")

    # ==== 保存配置文件 ====
    def apply_global_changes():
        if "Keybinds" not in loaded_config:
            loaded_config["Keybinds"] = {}
        for name, var2 in key_mapping_vars:
            loaded_config["Keybinds"][name] = var2.get()
        with open(config_file_path, "w", encoding="utf-8-sig") as configfile:
            loaded_config.write(configfile)
        saved_message = "\n".join([f"{name}: {var3.get()}" for name, var3 in key_mapping_vars])
        messagebox.showinfo("键位设置已保存", f"保存成功！【请重启脚本确认加载】\n当前键位配置信息:\n\n{saved_message}")

    keybind_page = tk.Frame(notebook_to_append)
    notebook_to_append.add(keybind_page, text="键位配置")

    # 创建滚动区域
    canvas = tk.Canvas(keybind_page)
    scroll_y = tk.Scrollbar(keybind_page, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    left_column_items = [
        "开始脚本", "停止脚本", "飞镖猴", "回旋镖猴", "大炮", "图钉塔", "冰猴", "胶水炮手",
        "狙击手猴", "猴子潜艇", "海盗猴", "皇家飞行员", "直升机飞行员", "迫击炮猴", "机枪猴",
        "法师猴", "超猴侠", "忍者猴", "炼金术师", "德鲁伊", "人鱼猴子",
        "香蕉农场", "刺钉工厂", "猴子村", "工程师猴", "野兽之主",
        "英雄", "升级路线1", "升级路线2", "升级路线3", "更改目标", "特制猴子", "特制猴子2"
    ]

    right_column_items = [
        "出售", "播放/快进", "暂停", "激活技能1", "激活技能2", "激活技能3", "激活技能4", "激活技能5",
        "激活技能6", "激活技能7", "激活技能8", "激活技能9", "激活技能10"
    ]

    left_column = tk.Frame(scrollable_frame)
    left_column.grid(row=0, column=0, padx=10, pady=10, sticky="n")

    right_column = tk.Frame(scrollable_frame)
    right_column.grid(row=0, column=1, padx=10, pady=10, sticky="n")

    for operation_name, default_key in default_key_mapping:
        if operation_name in left_column_items:
            frame = tk.Frame(left_column)
            frame.pack(fill="x", pady=2)

            label = tk.Label(frame, text=f"{operation_name}:", font=("Microsoft Yahei", 10), anchor="w", width=12)
            label.pack(side="left", padx=2)

            var = tk.StringVar(value=default_key)
            key_mapping_vars.append((operation_name, var))

            dropdown = ttk.Combobox(frame, textvariable=var, values=key_options, width=10, justify="right")
            dropdown.pack(side="right", padx=2)

    for operation_name, default_key in default_key_mapping:
        if operation_name in right_column_items:
            frame = tk.Frame(right_column)
            frame.pack(fill="x", pady=2)

            label = tk.Label(frame, text=f"{operation_name}:", font=("Microsoft Yahei", 10), anchor="w", width=12)
            label.pack(side="left", padx=2)

            var = tk.StringVar(value=default_key)
            key_mapping_vars.append((operation_name, var))

            dropdown = ttk.Combobox(frame, textvariable=var, values=key_options, width=10, justify="right")
            dropdown.pack(side="right", padx=2)

    load_keybinds()  # 用ini文件中的值代替下拉框中的显示值

    apply_button_ckp = tk.Button(right_column, text="应用更改", font=("Microsoft Yahei", 12),
                                 command=lambda: apply_global_changes())
    apply_button_ckp.pack(pady=20)


# ==== 坐标颜色抓取页面 ====
def create_coordinate_page(notebook_to_append):
    coord_page = tk.Frame(notebook_to_append)
    notebook_to_append.add(coord_page, text="坐标颜色抓取")

    global show_mouse_info, hook_id
    show_mouse_info = False
    hook_id = None  # 新增hook_id用于存储键盘监听句柄
    records = []

    # 初始化鼠标控制器
    control_mouse_upon_key_press = ControlMouseUponKeyPress()
    control_mouse_upon_key_press.start_listen()  # 启动监听线程

    # ==== 控制按钮 ====
    toggle_frame = tk.Frame(coord_page)
    toggle_frame.pack(pady=10)

    toggle_button = tk.Button(toggle_frame, text="开启坐标颜色抓取", font=("Microsoft Yahei", 12, "bold"),
                              command=lambda: toggle_mouse_info(coord_page), bg="green", fg="white")
    toggle_button.pack(side="left", padx=5)

    # 方向键控制勾选框
    arrow_control_var = tk.BooleanVar()
    arrow_checkbox = tk.Checkbutton(
        toggle_frame,
        text="方向键移动鼠标",
        variable=arrow_control_var,
        font=("Microsoft Yahei", 12),
        command=lambda: control_mouse_upon_key_press.enable_control(arrow_control_var.get())
    )
    arrow_checkbox.pack(side="left", padx=5)

    # ==== 显示区域 ====
    info_frame = tk.Frame(coord_page)
    info_frame.pack(pady=5)

    mouse_position_var = tk.StringVar()
    mouse_position_label = tk.Label(info_frame, textvariable=mouse_position_var, font=("Microsoft Yahei", 12))
    mouse_position_label.pack()

    mouse_color_var = tk.StringVar()
    mouse_color_label = tk.Label(info_frame, textvariable=mouse_color_var, font=("Microsoft Yahei", 12))
    mouse_color_label.pack()

    # ==== 记录列表 ====
    list_frame = tk.Frame(coord_page)
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    record_listbox = tk.Listbox(
        list_frame,
        yscrollcommand=scrollbar.set,
        height=8,
        font=("Microsoft Yahei", 10)
    )
    record_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=record_listbox.yview)

    # ==== 清空按钮 ====
    def clear_records():
        records.clear()
        record_listbox.delete(0, tk.END)

    clear_button = tk.Button(coord_page, text="清空记录", font=("Microsoft Yahei", 10), command=clear_records)
    clear_button.pack(pady=5)

    # ==== 记录功能 ====
    def record_position(event=None):
        if show_mouse_info:
            x, y = pyautogui.position()
            screen = ImageGrab.grab()
            color = screen.getpixel((x, y))
            color_hex = "#{:02X}{:02X}{:02X}".format(*color)
            timestamp = time.strftime("%H:%M:%S")

            rel_x = x - config.WINDOWS_OFFSET_CALCULATED_X
            rel_y = y - config.WINDOWS_OFFSET_CALCULATED_Y
            record = f"点位{len(records) + 1}: 坐标({rel_x}, {rel_y}), 颜色{color_hex} ({timestamp})"

            records.append(record)
            record_listbox.insert(tk.END, record)  # 插入到列表末尾

    # ==== 鼠标坐标更新 ====
    def update_mouse_position_and_color():
        if show_mouse_info:
            x, y = pyautogui.position()
            rel_x = x - config.WINDOWS_OFFSET_CALCULATED_X
            rel_y = y - config.WINDOWS_OFFSET_CALCULATED_Y
            mouse_position_var.set(f"坐标: X={rel_x}, Y={rel_y}（相对游戏窗口位置）")

            screen = ImageGrab.grab()
            color = screen.getpixel((x, y))
            color_hex = "#{:02X}{:02X}{:02X}".format(*color)
            mouse_color_var.set(f"像素颜色: {color_hex}")

            coord_page.after(100, update_mouse_position_and_color)

    # ==== 切换显示状态 ====
    def toggle_mouse_info(page):
        global show_mouse_info, hook_id
        show_mouse_info = not show_mouse_info
        if show_mouse_info:
            toggle_button.config(text="关闭坐标颜色抓取", bg="red")
            if hook_id:
                keyboard.remove_hotkey(hook_id)
            hook_id = keyboard.add_hotkey("ctrl+s", record_position)
            update_mouse_position_and_color()
            record_listbox.insert(tk.END, "按Ctrl+S抓取点位，双击点位可编辑")
        else:
            toggle_button.config(text="开启坐标颜色抓取", bg="green")
            mouse_position_var.set("")
            mouse_color_var.set("")

    def edit_record(event):
        # 获取选中项
        selection = record_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        current_text = record_listbox.get(index)

        # 弹出编辑对话框
        new_text = simpledialog.askstring(
            "编辑备注",
            "修改记录内容:",
            initialvalue=current_text,
            parent=coord_page
        )

        if new_text and new_text != current_text:
            # 更新ListBox和记录数据
            record_listbox.delete(index)
            record_listbox.insert(index, new_text)
            records[index] = new_text

    # 绑定双击事件
    record_listbox.bind("<Double-Button-1>", edit_record)


notebook = create_main_page(root)
create_config_page(notebook, config)
create_keybind_page(notebook)
create_coordinate_page(notebook)
# ==== 主循环 ====


find_and_focus_window()
root.mainloop()
