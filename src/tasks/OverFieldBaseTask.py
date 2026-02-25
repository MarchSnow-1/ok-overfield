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
        做法: 先回主页面，再匹配互动按钮并点击
        """
        self.go_main_screen()
        switcher = self.find_one('interactive', threshold=0.85)
        if switcher is None:
            raise Exception('找不到互动菜单入口')
        self.click(switcher, after_sleep=2.0)  # 界面动画要时间，延迟一下避免检测bug



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