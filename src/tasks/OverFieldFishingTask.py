import re
import time

from qfluentwidgets import FluentIcon
from ok import TaskDisabledException

from src.tasks.OverFieldBaseTask import OverFieldBaseTask

class OverFieldFishingTask(OverFieldBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动钓鱼"
        self.description = "自动持续钓鱼（请保证拥有足够的鱼饵）"
        self.group_name = "日常"        
        self.icon = FluentIcon.LIBRARY
        self.default_config.update({
            '鱼饵等级': "1",
            '钓鱼循环次数(设置为0为不限制循环次数)': "0",
            '开始下一次钓鱼前的等待时间 (秒)': "3"
        })
        self.config_type["鱼饵等级"] = {'type': "drop_down",
                                      'options': ['1', '2', '3', '4', '5']}
        self.config_type["开始下一次钓鱼前的等待时间 (秒)"] = {'type': "drop_down",
                'options': ['1', '2', '3', '5', '10']}

    def take_fishing_rod(self):
        """
        装备鱼竿
        在互动菜单中查找并点击鱼竿
        """
        # 打开互动菜单
        self.open_interactive_menu()
        # 延迟等加载
        self.send_key_down('alt')
        self.sleep(0.8)
        # 装备鱼竿
        self.log_info('正在装备鱼竿...')
        fishing_rod = self.find_one('fishing_rod', threshold=0.85)
        if fishing_rod:
            # 尝试双击装备鱼竿
            self.log_info('找到鱼竿，尝试装备')
            self.click(fishing_rod, after_sleep=0.5)
            self.log_info('鱼竿装备完成')
        else:
            # 如果找不到鱼竿图像，使用相对坐标双击
            self.log_info('未找到鱼竿图像，使用默认位置点击')
            self.click_relative(0.7, 0.9, after_sleep=0.5)
            self.log_info('鱼竿装备完成')
        self.send_key_up('alt')

    def select_bait(self, bait_level: str):
        """
        选择鱼饵
        """
        self.log_info(f'正在选择{bait_level}级鱼饵...')

        # 初始化默认坐标
        valid_levels = ('1', '2', '3', '4', '5')
        fallback_positions = {
            '5': (0.8, 0.3),
            '4': (0.8, 0.4),
            '3': (0.8, 0.5),
            '2': (0.8, 0.6),
            '1': (0.8, 0.7),
        }

        bait_level = str(bait_level).strip()
        if bait_level not in valid_levels:
            self.log_info(f'未知的鱼饵等级: {bait_level}, 使用默认 1 级鱼饵')
            bait_level = '1'

        bait_indicator_templates = {
            '5': 'fishing_bait_indicator_lv5',
            '4': 'fishing_bait_indicator_lv4',
            '3': 'fishing_bait_indicator_lv3',
            '2': 'fishing_bait_indicator_lv2',
            '1': 'fishing_bait_indicator_lv1',
            'none': 'fishing_bait_indicator_none',
        }
        bait_option_templates = {
            '5': 'fishing_bait_option_lv5',
            '4': 'fishing_bait_option_lv4',
            '3': 'fishing_bait_option_lv3',
            '2': 'fishing_bait_option_lv2',
            '1': 'fishing_bait_option_lv1',
        }

        # 先匹配目标等级，再匹配其他等级，最后兜底检查“未选择”状态
        indicator_search_order = [bait_level]
        indicator_search_order.extend([lvl for lvl in valid_levels if lvl != bait_level])
        indicator_search_order.append('none')

        current_level = None
        indicator_box = None

        def detect_indicator():
            """
            通过模板匹配检测当前鱼饵，返回 (level, box)。
            """
            for level in indicator_search_order:
                template_name = bait_indicator_templates.get(level)
                if not template_name:
                    continue
                match = self.find_one(template_name, threshold=0.85)
                if match:
                    return level, match
            return None, None

        def wait_option():
            template = bait_option_templates.get(bait_level)
            if not template:
                return None
            for attempt in range(6):
                box = self.find_one(template, threshold=0.82)
                if box:
                    return box
                self.sleep(0.2)
            return None

        def detect_backpack():
            """
            检测是否出现"背包"字样，表示鱼饵列表已打开
            """
            backpack = self.find_one('backpack_text', threshold=0.85)
            return backpack is not None

        self.send_key_down('alt')
        self.sleep(0.2)
        try:
            # UI 弹出有动画，循环尝试几次，期间短暂等待
            for attempt in range(5):
                current_level, indicator_box = detect_indicator()
                if current_level:
                    break
                self.sleep(0.2)

            if current_level == bait_level:
                self.log_info(f'检测到当前已是{bait_level}级鱼饵，无需重新选择')
            else:
                option_box = None
                for open_attempt in range(3):
                    if indicator_box:
                        if open_attempt == 0:
                            self.log_info(f"检测到当前为{current_level or '未知'}级鱼饵，点击图标唤出列表")
                        else:
                            self.log_info('鱼饵列表未显示，再次点击指示器尝试展开')
                        self.click(indicator_box, after_sleep=0.3)
                    else:
                        if open_attempt == 0:
                            self.log_info('未识别到鱼饵状态图标，使用默认坐标尝试打开列表')
                        else:
                            self.log_info('仍未识别到鱼饵状态图标，继续使用默认坐标打开列表')
                        self.click_relative(0.4, 0.65, after_sleep=0.3)

                    option_box = wait_option()
                    if option_box:
                        break
                    self.log_info('鱼饵列表尚未出现，稍后重试...')
                    current_level, indicator_box = detect_indicator()
                    self.sleep(0.2)

                if option_box:
                    self.click(option_box, after_sleep=0.8)
                else:
                    fallback_x, fallback_y = fallback_positions[bait_level]
                    self.log_info('未匹配到目标鱼饵图像，回退到固定坐标点击')
                    self.click_relative(fallback_x, fallback_y, after_sleep=0.8)
        finally:
            self.send_key_up('alt')

        self.log_info(f'{bait_level}级鱼饵已选择')

    def start_fishing(self):
        """
        开始钓鱼
        查找并点击"开始钓鱼"按钮
        """
        self.log_info('正在开始钓鱼...')
        self.send_key_down('alt')
        self.sleep(0.2)
        try:
            # 尝试查找"开始钓鱼"按钮
            start_button = self.find_one('menu_start_fishing', threshold=0.85)
            if start_button:
                self.click(start_button, after_sleep=2.0)
                self.log_info('钓鱼已开始')
                return True
            else:
                # 如果找不到按钮，使用默认位置
                self.log_info('未找到开始钓鱼按钮，使用默认位置点击')
                self.click_relative(0.6, 0.83, after_sleep=2.0)
                return True
        finally:
            self.send_key_up('alt')

        

    def is_fishing_active(self) -> bool:
        """
        检查是否正在钓鱼
        可以通过查找钓鱼相关UI元素来判断
        """
        fishing_ui = self.find_one('fishing_ui', threshold=0.85)
        return fishing_ui is not None

    def wait_for_fishing_complete(self):
        """
        等待钓鱼完成
        """
        self.log_info('等待钓鱼完成...')
        while True:
            if not self.is_fishing_active():
                self.log_info('检测到可能的上钩全屏 UI，尝试等待4秒确认...')

                recovered = False
                for _ in range(8):  # 每次 0.5s，最多 8 次
                    self.sleep(0.5)
                    if self.is_fishing_active():
                        recovered = True
                        break

                if recovered:
                    self.log_info('确认上钩 UI 已关闭，继续等待钓鱼结束')
                    continue

                self.log_info('未检测到钓鱼界面，判定钓鱼已完成')
                return True

            self.sleep(1)

    def fishing_cycle(self, bait_level: str):
        """
        执行一次完整的钓鱼循环
        """
        try:
            self.sleep(0.5)
            # 打开钓鱼菜单
            self.click(0.5,0.5)
            
            # 选择鱼饵
            self.select_bait(bait_level)
            
            # 开始钓鱼
            if self.start_fishing():
                # 等待钓鱼完成
                self.wait_for_fishing_complete()
                return True
            else:
                self.log_info('启动钓鱼失败')
                return False
                
        except TaskDisabledException:
            raise  # 关键修复：重新抛出停止异常，让外层 run() 捕获
        except Exception as e:
            self.log_info(f'钓鱼循环出现错误: {str(e)}')
            return False

    def do_run(self):
        """
        执行钓鱼任务的主要逻辑
        """
        # 获取配置参数
        bait_level = self.config.get('鱼饵等级', '1')

        def parse_int(value, default):
            try:
                return int(str(value).strip())
            except (ValueError, TypeError, AttributeError):
                return default

        cycle_count = parse_int(self.config.get('钓鱼循环次数(设置为0为不限制循环次数)', '0'), 10)
        wait_time = parse_int(self.config.get('开始下一次钓鱼前的等待时间 (秒)', '3'), 3)

        # 允许输入 0 代表无限循环，负数也按无限处理
        if cycle_count < 0:
            cycle_count = 0

        cycle_label = '无限' if cycle_count == 0 else cycle_count
        self.log_info(f'配置参数 - 鱼饵等级: {bait_level}, 循环次数: {cycle_label}, 等待时间: {wait_time}秒')
        
        # 初始化，回到主页面
        self.go_main_screen()
        self.sleep(1)

        # 解除装备钓竿
        if self.already_equip_something():
            self.un_equip()
        
        # 装备钓竿
        self.take_fishing_rod()
        self.sleep(1)

        # 执行钓鱼循环
        if cycle_count == 0:
            cycle_num = 0
            while True:
                cycle_num += 1
                self.log_info(f'开始第 {cycle_num} 次钓鱼循环')
                if not self.fishing_cycle(bait_level):
                    self.log_info('钓鱼循环失败，尝试重新开始')
                # 循环间隔等待（这里 sleep 会触发停止检查）
                self.sleep(wait_time)
        else:
            total_cycles = cycle_count
            for i in range(total_cycles):
                self.log_info(f'开始第 {i+1}/{total_cycles} 次钓鱼循环')
                if not self.fishing_cycle(bait_level):
                    self.log_info('钓鱼循环失败，尝试重新开始')
                if i < total_cycles - 1:
                    self.sleep(wait_time)
        
        self.log_info('自动钓鱼任务完成!', notify=True)

    def run(self):
        """
        任务入口点，处理异常和任务停止
        """
        self.log_info('开始自动钓鱼任务', notify=True)

        try:
            return self.do_run()
        except TaskDisabledException as e:
            self.log_info('任务已被停止', notify=True)
            pass
        except Exception as e:
            self.log_info(f'钓鱼任务执行出错: {str(e)}', notify=True)
            raise e
