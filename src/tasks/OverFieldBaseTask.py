# src/tasks/OverFieldBaseTask.py

import re
from ok import Logger, BaseTask

logger = Logger.get_logger(__name__)

class OverFieldBaseTask(BaseTask):
    """
    OverField 基类
    所有具体 Task 都继承这个类，不要直接实例化
    """

    # ------------------------------------------------------------------ #
    #  界面检测                                                            #
    # ------------------------------------------------------------------ #

    def is_in_main_screen(self) -> bool:
        """
        判断当前是否在大世界
        做法: find 抽卡入口
        """
        return self.find_element(
            "assets/ui/gacha.png",
            threshold=0.85
        ) is not None

    def is_in_esc_screen(self) -> bool:
        """
        判断当前是否在主菜单
        做法: find 邮箱 & 设置
        """
        return self.find_element(
            "assets/ui/esc_mail_and_settings.png",
            threshold=0.85
        ) is not None

    def is_in_battle(self) -> bool:
        """
        判断当前是否在战斗中
        做法: find 自动战斗
        """
        return self.find_element(
            "assets/ui/auto_fight.png",
            threshold=0.85
        ) is not None

    def is_in_world_selector(self) -> bool:
        """
        判断当前是否在世界选择页面
        做法: find 世界选择UI
        """
        return self.find_element(
            "assets/ui/world_selector_page_ui.png",
            threshold=0.85
        ) is not None

    # ------------------------------------------------------------------ #
    #  导航操作                                                            #
    # ------------------------------------------------------------------ #

    def ensure_main_screen(self, time_out: int = 60):
        """
        确保在游戏主界面
        做法: 反复按 ESC 直到 is_in_main_screen() 为 true
        """
        self.log_info('正在返回主界面...')
        end_time = self.time() + time_out
        while self.time() < end_time:
            if self.is_in_main_screen():
                self.log_info('已在主界面')
                return
            # 关闭弹窗/地图/菜单
            self.send_key('esc', after_sleep=1.0)
        raise Exception(f'无法返回主界面，已超时, 执行时长 {time_out}s')

    def ensure_esc_screen(self, time_out: int = 60):
        """
        确保在ESC菜单页面
        做法: 反复按 ESC 直到 is_in_esc_screen() 为 true
        """
        # 初始化
        self.ensure_main_screen()
        # 打开菜单
        self.log_info('正在打开菜单...')
        end_time = self.time() + time_out
        while self.time() < end_time:
            if self.is_in_esc_screen():
                self.log_info('已在主界面')
                return
            # 打开菜单
            self.send_key('esc', after_sleep=1.0)
        raise Exception(f'无法打开菜单，已超时, 执行时长 {time_out}s')

    def open_world_selecter(self, time_out: int = 10):
        """
        打开世界切换菜单
        做法: 先确保处于主页面，再确保处于主菜单，最后匹配按钮按下
        """
        # 确保处于主页面
        self.ensure_esc_screen()

        # 查找位置
        switcher = self.find_element(
            "assets/ui/esc_world_selector.png",
            threshold=0.85
        )
        if switcher is None:
            raise Exception('找不到世界切换器入口')
        # 点击对应位置
        self.click_box(switcher, after_sleep=1.0)

    # ------------------------------------------------------------------ #
    #  工具方法                                                            #
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
        """触发交互 (通常是 F 键)"""
        self.send_key('f', after_sleep=0.3)

    def jump(self):
        """跳跃 (空格)"""
        self.send_key('space', after_sleep=0.1)

    def sprint(self, duration: float = 0.5):
        """冲刺 (Shift)"""
        self.send_key_down('shift')
        self.sleep(duration)
        self.send_key_up('shift')