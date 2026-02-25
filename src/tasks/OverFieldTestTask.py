# src/tasks/OverFieldTestTask.py

from ok import Logger
from src.tasks.OverFieldBaseTask import OverFieldBaseTask

logger = Logger.get_logger(__name__)


class OverFieldTestTask(OverFieldBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "测试任务"
        self.description = "测试基础功能是否正常"

    def run(self):
        self.log_info('=== 开始测试 ===')

        self.log_info(f'[1] 当前是否在主界面: {self.is_in_main_screen()}')
        self.log_info(f'[2] 当前是否在ESC菜单: {self.is_in_esc_screen()}')
        self.log_info(f'[3] 当前是否在战斗中: {self.is_in_battle()}')
        self.log_info(f'[4] 当前是否在世界选择: {self.is_in_world_selector()}')

        self.log_info('[5] 测试 go_main_screen...')
        self.go_main_screen()
        self.log_info(f'    go_main_screen 完成, 验证: {self.is_in_main_screen()}')

        self.log_info('[6] 测试 go_esc_screen...')
        self.go_esc_screen()
        self.log_info(f'    go_esc_screen 完成, 验证: {self.is_in_esc_screen()}')

        self.log_info('[7] 测试 open_world_selector...')
        self.open_world_selector()
        self.log_info(f'    open_world_selector 完成, 验证: {self.is_in_world_selector()}')

        self.log_info('=== 测试完成 ===', notify=True)