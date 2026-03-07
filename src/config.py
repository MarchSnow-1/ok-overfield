import os

import numpy as np
from ok import ConfigOption

version = "dev"
#不需要修改version, Github Action打包会自动修改

key_config_option = ConfigOption('Game Hotkey Config', { #全局配置示例
    'Echo Key': 'q',
    'Liberation Key': 'r',
    'Resonance Key': 'e',
    'Tool Key': 't',
}, description='In Game Hotkey for Skills')


def make_uid_area_black(frame,
                          x_left=0.135, y_top=0.965,
                          x_right=0.185, y_bottom=0.992):
    """
    将 UID 区域涂黑
    
    参数:
        frame: OpenCV 图像 (numpy array, BGR 格式)
        x_left, x_right: 水平相对坐标 0.0 ~ 1.0 (左→右)
        y_top, y_bottom: 垂直相对坐标 0.0 ~ 1.0 (上→下, 0=顶部, 1=底部)
    
    返回:
        修改后的图像
    """
    if frame is None or len(frame.shape) < 2:
        return frame
    
    try:
        height, width = frame.shape[:2]
        
        # 转换为像素坐标
        # y=0 是顶部，y=height-1 是底部
        start_x = int(x_left * width)
        end_x   = int(x_right * width)
        start_y = int(y_top * height)
        end_y   = int(y_bottom * height)
        
        # 防止越界
        start_x = max(0, min(start_x, width-1))
        end_x   = max(start_x+1, min(end_x, width))
        start_y = max(0, min(start_y, height-1))
        end_y   = max(start_y+1, min(end_y, height))
        
        # 涂黑该区域
        frame[start_y:end_y, start_x:end_x] = 0
        
        return frame
        
    except Exception as e:
        print(f"遮挡 UID 时出错: {e}")
        return frame

config = {
    'debug': False,  # Optional, default: False
    'use_gui': True, # 目前只支持True
    'config_folder': 'configs', #最好不要修改
    'global_configs': [key_config_option],
    'screenshot_processor': make_uid_area_black, # 在截图的时候对UID进行涂黑操作
    'gui_icon': 'icons/icon.png', #窗口图标, 最好不需要修改文件名
    'wait_until_before_delay': 0,
    'wait_until_check_delay': 0,
    'wait_until_settle_time': 0, #调用 wait_until时候, 在第一次满足条件的时候, 会等待再次检测, 以避免某些滑动动画没到预定位置就在动画路径中被检测到
    'ocr': { #可选, 使用的OCR库
        'lib': 'onnxocr',
        'params': {
            'use_openvino': True,
        }
    },
    'windows': {  # Windows游戏请填写此设置
        'exe': ['launcher.exe', 'OverField.exe', 'OverField-Win64-Shipping.exe'],
        'hwnd_class': 'UnityWndClass', #增加重名检查准确度
        'interaction': 'Genshin', # Genshin:某些操作可以后台, 部分游戏支持 PostMessage:可后台点击, 极少游戏支持 ForegroundPostMessage:前台使用PostMessage Pynput/PyDirect:仅支持前台使用
        'capture_method': ['WGC', 'BitBlt_RenderFull', 'DXGI', 'BitBlt'],  # Windows版本支持的话, 优先使用WGC, 否则使用BitBlt_Full. 支持的capture有 BitBlt, WGC, BitBlt_RenderFull, DXGI
        'check_hdr': True, #当用户开启AutoHDR时候提示用户, 但不禁止使用
        'force_no_hdr': False, #True=当用户开启AutoHDR时候禁止使用
        'require_bg': True # 要求使用后台截图
    },
    #'adb': {  # Windows游戏请填写此设置, mumu模拟器使用原生截图和input,速度极快. 其他模拟器和真机使用adb,截图速度较慢
    #    'packages': ['com.abc.efg1', 'com.abc.efg1']
    #},
    'start_timeout': 120,  # default 60
    'window_size': { #ok-script窗口大小
        'width': 1200,
        'height': 800,
        'min_width': 600,
        'min_height': 450,
    },
    'supported_resolution': {
        'ratio': '16:9', #支持的游戏分辨率
        'min_size': (1280, 720), #支持的最低游戏分辨率
        'resize_to': [(2560, 1440), (1920, 1080), (1600, 900), (1280, 720)], #可选, 如果非16:9自动缩放为 resize_to
    },
    'links': { # 关于里显示的链接, 可选
            'default': {
                'github': 'https://github.com/MarchSnow-1/ok-overfield',
                'share': 'Download from https://github.com/MarchSnow-1/ok-overfield',
                'faq': 'https://github.com/MarchSnow-1/ok-overfield'
            }
        },
    'screenshots_folder': "screenshots", #截图存放目录, 每次重新启动会清空目录
    'gui_title': 'ok-overfield',  #窗口名
    'template_matching': { # 可选, 如使用OpenCV的模板匹配
        'coco_feature_json': os.path.join('assets', 'result.json'), #coco格式标记, 需要png图片, 在debug模式运行后, 会对进行切图仅保留被标记部分以减少图片大小
        'default_horizontal_variance': 0.002, #默认x偏移, 查找不传box的时候, 会根据coco坐标, match偏移box内的
        'default_vertical_variance': 0.002, #默认y偏移
        'default_threshold': 0.8, #默认threshold
    },
    'version': version, #版本
    'my_app': ['src.globals', 'Globals'], #可选. 全局单例对象, 可以存放加载的模型, 使用og.my_app调用
    'onetime_tasks': [  # 用户点击触发的任务
        #["src.tasks.OverFieldTestTask", "OverFieldTestTask"],
        ["src.tasks.OverFieldFishingTask", "OverFieldFishingTask"],
        #["ok", "DiagnosisTask"],
    ],
    'trigger_tasks':[ # 不断执行的触发式任务
        #["src.tasks.MyTriggerTask", "MyTriggerTask"],
    ],
    #'custom_tabs': [
    #    ['src.ui.MyTab', 'MyTab'], #可选, 自定义UI, 显示在侧边栏
    #],
}
