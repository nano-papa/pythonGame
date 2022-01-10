class Settings:
    """存储游戏《外星人入侵》中的所有设置类"""

    def __init__(self):
        """初始化游戏的设置"""
        # 屏幕设置
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)
        # 飞船的设置
        self.ship_speed = 10
        # 飞船有几条命
        self.ship_limit = 3
        # 子弹的设置
        self.bullet_color = (60, 60, 60)
        self.bullet_width = 8
        self.bullet_height = 18
        self.bullet_speed = 10
        self.bullet_allowed = 10
        # 外星人的设置
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        # fleet_direction 为1表示向右移动，为-1 表示向左移动
        self.fleet_direction = 1

        # 加快游戏节奏

        self.speed_scale = 1.1

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """初始化随游戏的进行而变化的设置"""
        self.ship_speed = 10
        self.bullet_speed = 10
        self.alien_speed = 1.0

        """fleet_direction为1是表示右，为-1表示左"""
        self.fleet_direction = 1
        # 记分
        self.alien_points = 50

    def increase_speed(self):
        """提高速度设置"""
        self.ship_speed *= self.speed_scale
        self.bullet_speed *= self.speed_scale
        self.alien_speed *= self.speed_scale

        self.alien_points = int(self.alien_points * self.speed_scale)
