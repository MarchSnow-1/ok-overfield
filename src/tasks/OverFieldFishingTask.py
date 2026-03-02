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
            '钓鱼循环次数': "10",
            '等待时间': "3"
        })
        self.config_type["鱼饵等级"] = {'type': "drop_down",
                                      'options': ['1', '2', '3', '4', '5']}
        self.config_type["钓鱼循环次数"] = {'type': "drop_down",
                'options': ['1', '5', '10', '20', '50', '无限']}
        self.config_type["等待时间"] = {'type': "drop_down",
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
        
        # 点击鱼饵选择区域
        self.send_key_down('alt')
        self.click_relative(0.4, 0.65, after_sleep=1.0)
        self.sleep(0.5)
        
        # 根据鱼饵等级选择对应位置
        bait_positions = {
            '5': (0.8, 0.3),
            '4': (0.8, 0.4),
            '3': (0.8, 0.5),
            '2': (0.8, 0.6),
            '1': (0.8, 0.7)
        }
        
        if bait_level in bait_positions:
            x, y = bait_positions[bait_level]
        else:
            self.log_info(f'未知的鱼饵等级: {bait_level}, 使用默认 1 级鱼饵')
            x, y = bait_positions['1']

        self.click_relative(x, y, after_sleep=1.0) 
        self.send_key_up('alt')  
        self.log_info(f'{bait_level}级鱼饵已选择')

    def start_fishing(self):
        """
        开始钓鱼
        查找并点击"开始钓鱼"按钮
        """
        self.log_info('正在开始钓鱼...')
        
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
        自动跳过上钩全屏UI（3秒），响应更快
        """
        self.log_info('等待钓鱼完成...')
        while True:
            if not self.is_fishing_active():
                # 上钩UI出现 → 等待足够时间让它消失
                self.log_info('检测到可能的上钩全屏 UI, 等待4秒确认...')
                self.sleep(4) 
                
                # 再次确认
                if not self.is_fishing_active():
                    self.log_info('钓鱼已完成')
                    return True
                else:
                    self.log_info('仍在钓鱼, 继续等待...')
                    # 如果第二次还是有，可能是误判，继续循环
            
            # 正常巡检间隔（保持快速响应）
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
        # 获取配置参数（保持不变）
        bait_level = self.config.get('鱼饵等级', '1')
        cycle_count = self.config.get('钓鱼循环次数', '10')
        wait_time = int(self.config.get('等待时间', '3'))
        
        self.log_info(f'配置参数 - 鱼饵等级: {bait_level}, 循环次数: {cycle_count}, 等待时间: {wait_time}秒')
        
        # 初始化，回到主页面
        self.go_main_screen()
        self.sleep(1)
        
        # 装备钓竿
        self.take_fishing_rod()
        self.sleep(1)

        # 执行钓鱼循环
        if cycle_count == '无限':
            cycle_num = 0
            while True:
                cycle_num += 1
                self.log_info(f'开始第 {cycle_num} 次钓鱼循环')
                if not self.fishing_cycle(bait_level):
                    self.log_info('钓鱼循环失败，尝试重新开始')
                # 循环间隔等待（这里 sleep 会触发停止检查）
                self.sleep(wait_time)
        else:
            total_cycles = int(cycle_count)
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
        
        if self.already_equip_something():
            self.un_equip()

        try:
            return self.do_run()
        except TaskDisabledException as e:
            self.log_info('任务已被停止', notify=True)
            pass
        except Exception as e:
            self.log_info(f'钓鱼任务执行出错: {str(e)}', notify=True)
            raise e
