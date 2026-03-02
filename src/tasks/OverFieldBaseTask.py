# src/tasks/OverFieldBaseTask.py

import re
from ok import BaseTask, Logger

logger = Logger.get_logger(__name__)

class OverFieldBaseTask(BaseTask):
    """
    OverField 基类
    所有具体 Task 都继承这个类，不要直接实例化
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_config = self.get_global_config('Game Hotkey Config')

    def operate(self, func):
        self.executor.interaction.operate(func, block=True)

    def do_mouse_down(self, key):
        self.executor.interaction.do_mouse_down(key=key)

    def do_mouse_up(self, key):
        self.executor.interaction.do_mouse_up(key=key)

    def do_send_key_down(self, key):
        self.executor.interaction.do_send_key_down(key)

    def do_send_key_up(self, key):
        self.executor.interaction.do_send_key_up(key)

    # ------------------------------------------------------------------ #
    #  界面检测                                                            #
    # ------------------------------------------------------------------ #

    def is_in_main_screen(self) -> bool:
        """
        判断当前是否在大世界
        做法: find R键回溯
        """
        return self.find_one(
            'r_key_rewind',
            threshold=0.85
        ) is not None

    def is_in_esc_screen(self) -> bool:
        """
        判断当前是否在主菜单
        做法: find 好友列表入口
        """
        return self.find_one(
            'esc_friends',
            threshold=0.85
        ) is not None

    def is_in_battle(self) -> bool:
        """
        判断当前是否在战斗中
        做法: find 自动战斗按钮
        """
        return self.find_one(
            'auto_fight',
            threshold=0.85
        ) is not None

    def is_in_world_selector(self) -> bool:
        """
        判断当前是否在世界选择页面
        做法: find 世界选择UI
        """
        return self.find_one(
            'world_selector_page_ui',
            threshold=0.85
        ) is not None

    def already_equip_something(self) -> bool:
        """
        判断当前是否已经装备工具
        做法: find 解除装备
        """
        return self.find_one(
            'unequip',
            threshold=0.85
        ) is not None

    # ------------------------------------------------------------------ #
    #  导航操作                                                            #
    # ------------------------------------------------------------------ #

    def go_main_screen(self, time_out: int = 60):
        """
        确保在游戏主界面
        做法: 反复按 ESC 直到 is_in_main_screen() 为 true
        """
        if not self.wait_until(
            self.is_in_main_screen,
            time_out=time_out,
            raise_if_not_found=False,
            post_action=lambda: self.send_key('esc', after_sleep=2)
        ):
            raise Exception(f'无法返回主界面，已超时 {time_out}s')
        self.log_info('已返回主界面')

    def go_esc_screen(self, time_out: int = 60):
        """
        确保在ESC菜单页面
        做法: 先回主界面，再反复按 ESC 直到 is_in_esc_screen() 为 true
        """
        self.go_main_screen()
        if not self.wait_until(
            self.is_in_esc_screen,
            time_out=time_out,
            raise_if_not_found=False,
            post_action=lambda: self.send_key('esc', after_sleep=2)
        ):
            raise Exception(f'无法打开主菜单，已超时 {time_out}s')

    def open_world_selector(self, time_out: int = 10):
        """
        打开世界切换菜单
        做法: 先确保处于主菜单，再匹配按钮并点击
        """
        self.go_esc_screen()
        switcher = self.find_one('esc_world_selector', threshold=0.85)
        if switcher is None:
            raise Exception('找不到世界切换器入口')
        self.click(switcher, after_sleep=2.0)  # 界面动画要时间，延迟一下避免检测bug

    def open_interactive_menu(self, time_out: int = 10):
        """
        打开互动菜单
        做法: 先按住Alt呼出鼠标, 点击互动按钮后再抬起Alt
        """
        # 按住Alt键呼出鼠标
        self.send_key_down('alt')
        self.sleep(0.5)  # 等待鼠标显示
        
        switcher = self.find_one('interactive', threshold=0.85)
        if switcher is None:
            self.send_key_up('alt')  # 如果找不到按钮，先抬起Alt
            raise Exception('找不到互动按钮')
        
        # 点击互动按钮
        self.click(switcher, after_sleep=1.0)
        
        # 抬起Alt键
        self.send_key_up('alt')
        self.sleep(1.0)  # 界面动画要时间，延迟一下避免检测bug

    def un_equip(self, time_out: int = 10):
        """
        解除装备
        做法: 先按住Alt呼出鼠标, 点击互动按钮后再抬起Alt
        """
        # 按住Alt键呼出鼠标
        self.send_key_down('alt')
        self.sleep(0.5)  # 等待鼠标显示
        
        switcher = self.find_one('unequip', threshold=0.85)
        if switcher is None:
            self.send_key_up('alt')  # 如果找不到按钮，先抬起Alt
            raise Exception('找不到解除装备按钮')
        
        # 点击互动按钮
        self.click(switcher, after_sleep=1.0)
        
        # 抬起Alt键
        self.send_key_up('alt')
        self.sleep(0.5)

    # ------------------------------------------------------------------ #
    #  角色操作                                                            #
    # ------------------------------------------------------------------ #

    def move_toward(self, direction: str, duration: float = 1.0):
        """
        朝某方向移动一段时间
        direction: 'w'前 's'后 'a'左 'd'右
        """
        self.send_key_down(direction)
        self.sleep(duration)
        self.send_key_up(direction)

    def interact(self):
        """
        触发交互
        做法: 按 F 键
        """
        self.send_key('f', after_sleep=0.3)

    def jump(self, after_sleep: float = 0.01):
        """
        跳跃
        做法: 按空格键
        """
        self.send_key(
            self.key_config.get('Jump Key', 'space'),
            after_sleep=after_sleep
        )

    def sprint(self, duration: float = 0.5):
        """
        冲刺
        做法: 按住 Shift 持续 duration 秒
        """
        self.send_key_down('shift')
        self.sleep(duration)
        self.send_key_up('shift')
