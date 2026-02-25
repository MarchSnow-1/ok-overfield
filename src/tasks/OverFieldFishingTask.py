import re
import time

from qfluentwidgets import FluentIcon

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

    def something_have_been_equipped(self) -> bool:
        """
        检查是否有装备已装备
        通过查找"解除装备"按钮来判断
        """
        return self.find_one('unequip', threshold=0.85) is not None

    def un_equip(self):
        """
        解除当前装备
        """
        self.log_info('检测到已装备物品，正在解除装备...')
        unequip_button = self.find_one('unequip', threshold=0.85)
        if unequip_button:
            self.click(unequip_button, after_sleep=2.0)
            self.log_info('装备已解除')
        else:
            self.log_info('未找到解除装备按钮')

    def equip_fishing_rod(self):
        """
        装备鱼竿
        在互动菜单中查找并点击鱼竿
        """
        self.log_info('正在装备鱼竿...')
        # 这里需要根据实际游戏界面添加鱼竿的图像识别
        # 暂时使用坐标点击，实际使用时需要添加对应的图像资源
        fishing_rod = self.find_one('鱼竿', threshold=0.85)
        if fishing_rod:
            self.click(fishing_rod, after_sleep=2.0)
            self.log_info('鱼竿已装备')
        else:
            # 如果找不到鱼竿图像，使用相对坐标点击
            self.log_info('未找到鱼竿图像，使用默认位置点击')
            self.click_relative(0.5, 0.3, after_sleep=2.0)

    def open_fishing_menu(self):
        """
        左键点击唤出钓鱼菜单
        """
        self.log_info('正在打开钓鱼菜单...')
        self.click_relative(0.5, 0.5, button='left', after_sleep=2.0)

    def select_bait(self, bait_level: str):
        """
        选择鱼饵
        """
        self.log_info(f'正在选择{bait_level}级鱼饵...')
        
        # 点击鱼饵选择区域 (x0.4, y0.6)
        self.click_relative(0.4, 0.6, after_sleep=1.0)
        
        # 根据鱼饵等级选择对应位置
        bait_positions = {
            '1': (0.3, 0.4),
            '2': (0.4, 0.4),
            '3': (0.5, 0.4),
            '4': (0.6, 0.4),
            '5': (0.7, 0.4)
        }
        
        if bait_level in bait_positions:
            x, y = bait_positions[bait_level]
            self.click_relative(x, y, after_sleep=1.0)
            self.log_info(f'{bait_level}级鱼饵已选择')
        else:
            self.log_info(f'未知的鱼饵等级: {bait_level}，使用默认1级鱼饵')
            self.click_relative(0.3, 0.4, after_sleep=1.0)

    def start_fishing(self):
        """
        开始钓鱼
        查找并点击"开始钓鱼"按钮
        """
        self.log_info('正在开始钓鱼...')
        
        # 尝试查找"开始钓鱼"按钮
        start_button = self.find_one('开始钓鱼', threshold=0.85)
        if start_button:
            self.click(start_button, after_sleep=2.0)
            self.log_info('钓鱼已开始')
            return True
        else:
            # 如果找不到按钮，使用默认位置
            self.log_info('未找到开始钓鱼按钮，使用默认位置点击')
            self.click_relative(0.5, 0.7, after_sleep=2.0)
            return True

    def is_fishing_active(self) -> bool:
        """
        检查是否正在钓鱼
        可以通过查找钓鱼相关UI元素来判断
        """
        # 这里需要根据实际游戏界面添加钓鱼状态的判断逻辑
        # 暂时返回False，实际使用时需要完善
        fishing_ui = self.find_one('钓鱼界面', threshold=0.85)
        return fishing_ui is not None

    def wait_for_fishing_complete(self, timeout: int = 300):
        """
        等待钓鱼完成
        timeout: 超时时间（秒）
        """
        self.log_info('等待钓鱼完成...')
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查是否还在钓鱼状态
            if not self.is_fishing_active():
                self.log_info('钓鱼已完成')
                return True
            
            # 检查是否回到了主界面（钓鱼结束的标志）
            if self.is_in_main_screen():
                self.log_info('已返回主界面，钓鱼循环结束')
                return True
            
            self.sleep(2)  # 每2秒检查一次
        
        self.log_info(f'钓鱼等待超时（{timeout}秒）')
        return False

    def fishing_cycle(self, bait_level: str):
        """
        执行一次完整的钓鱼循环
        """
        try:
            # 打开钓鱼菜单
            self.open_fishing_menu()
            
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
                
        except Exception as e:
            self.log_info(f'钓鱼循环出现错误: {str(e)}')
            return False

    def run(self):
        self.log_info('开始自动钓鱼任务', notify=True)
        
        try:
            # 获取配置参数
            bait_level = self.config.get('鱼饵等级', '1')
            cycle_count = self.config.get('钓鱼循环次数', '10')
            wait_time = int(self.config.get('等待时间', '3'))
            
            self.log_info(f'配置参数 - 鱼饵等级: {bait_level}, 循环次数: {cycle_count}, 等待时间: {wait_time}秒')
            
            # 初始化，回到主页面
            self.go_main_screen()
            
            # 如果已装备，解除装备
            if self.something_have_been_equipped():
                self.un_equip()
            
            # 打开互动菜单
            self.open_interactive_menu()
            
            # 装备鱼竿
            self.equip_fishing_rod()
            
            # 执行钓鱼循环
            if cycle_count == '无限':
                cycle_num = 0
                while True:
                    cycle_num += 1
                    self.log_info(f'开始第 {cycle_num} 次钓鱼循环')
                    if not self.fishing_cycle(bait_level):
                        self.log_info('钓鱼循环失败，尝试重新开始')
                        # 重新回到主界面准备下一次循环
                        self.go_main_screen()
                        self.open_interactive_menu()
                    # 循环间隔等待
                    self.sleep(wait_time)
            else:
                total_cycles = int(cycle_count)
                for i in range(total_cycles):
                    self.log_info(f'开始第 {i+1}/{total_cycles} 次钓鱼循环')
                    if not self.fishing_cycle(bait_level):
                        self.log_info('钓鱼循环失败，尝试重新开始')
                        # 重新回到主界面准备下一次循环
                        self.go_main_screen()
                        self.open_interactive_menu()
                    
                    # 如果不是最后一次循环，等待一段时间
                    if i < total_cycles - 1:
                        self.sleep(wait_time)
            
            self.log_info('自动钓鱼任务完成!', notify=True)
            
        except Exception as e:
            self.log_info(f'钓鱼任务执行出错: {str(e)}', notify=True)
            raise e
