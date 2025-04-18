# 20250418 游戏版本V48 龙雕心文（以下内容尚未更新到新版，仅供参考）
---
## 1. 脚本初始配置
### 运行脚本 > 全局设置
- 输入想要的日志、截图保存路径，保存更改
- 如果不更改的话，日志可能会生成在C盘临时文件夹
### 键位配置
- 设置游戏内热键或脚本快捷键，使二者保持一致，并应用更改
- （目前不支持组合按键。脚本的默认设置与游戏默认设置相同，人鱼猴子按键为`o`）
---
## 2. 游戏窗口设置
- 游戏设置为窗口化、`1280*720`、语言简体中文
- 窗口位置随意，不要放置太偏，以防显示不全或是被弹窗、广告阻挡
---
## 3. 运行测试脚本
1. 选择杰拉尔多，进入新手图中的"循环"，选择沙盒模式
2. 点击"加载关卡文件"，加载脚本测试的`xlsx`文件
3. 按<kbd>F10</kbd>运行脚本
4. 脚本运行完成后，按<kbd>F12</kbd>停止
5. 检查当前地图上结果是否如图所示：
!
> **异常处理**  
> - 如果猴子有缺少：确认分辨率设置，并在全局设置内调整窗口偏移
> - 如果杰拉尔多道具未正常使用：检查快捷键设置是否统一
---
## 4. 正常运行脚本文件
1. 如测试正常，可将循环次数拖到`0`（无限）
2. 模式选择单一关卡
3. 加载对应关卡文件
4. 在主菜单界面按下开始按键即可自动运行：
![运行界面示意图](需替换为实际图片路径)
> **停止方法**  
> 直接按下停止按钮或热键即可
---
## 5. 自定义脚本文件
- 如果游戏界面调整导致地图进入位置变化，或平衡性调整导致关卡无法通过：
  1. 修改脚本文件中的具体操作
  2. 参照脚本文件夹中的《脚本指令介绍与用法、完整脚本示例》文件
  3. 所有脚本操作都可以自定义完成
> **高级操作**  
> 复杂操作可通过手动编写以下指令实现：  
> - 延时
> - 鼠标移动/点击
> - 键盘点击
---
## 6. 后续更新计划
| 更新内容 | 进度规划 |
|---------|----------|
| 补足所有专家图的点击模式 | 开发中 |
| 双金极难模式脚本 | 规划中 |
| 循环地图刷insta猴功能 | 待insta猴活动时测试 |
> 版本更新可能导致现有脚本失效，建议保持关注最新脚本版本
