import sys

import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep

from games_stats import GameStats
from scoreboard import Scoreboard
from button import Button


class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        # pygame包的初始化
        pygame.init()
        # 将各个元素的配置导入
        self.settings = Settings()
        # 通过pygame设置一块屏幕
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        # 设置游戏名称
        pygame.display.set_caption("Alien Invasion")
        # 初始化游戏状态相关
        self.stats = GameStats(self)
        # 初始化计分板相关
        self.sb = Scoreboard(self)
        # 初始化飞船
        self.ship = Ship(self)
        # 子弹组
        self.bullets = pygame.sprite.Group()
        # 外星人组
        self.aliens = pygame.sprite.Group()
        # 创造外星人队
        self._create_fleet()

        # 创建play按钮
        self.play_button = Button(self, "play")

    def run_game(self):
        """开始游戏主循环"""
        while True:
            # 监视键盘和鼠标事件
            self._check_events()
            # 如果游戏处于活动状态
            if self.stats.game_active:
                # 飞船更新
                self.ship.update()
                # 更新子弹
                self._update_bullets()
                # 更新外星人
                self._update_alien()
                # 每次循环时都会重新绘制屏幕
            self._update_screen()
            # 让最近绘制的屏幕可见

    def _ship_hit(self):
        """响应飞机撞到外星人"""
        if self.stats.game_active:
            # 将ships_left减1并更新积分牌
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            #  清空剩余的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            # 创建一群新的外星人，并将飞船放到屏幕低端的中央
            self._create_fleet()
            self.ship.center_ship()
            # 暂停
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _update_bullets(self):
        """更更新子弹的位置，并且删除消失的子弹"""
        # 更新子弹的位置
        self.bullets.update()

        # 删除消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # 检查是否有子弹击中了外星人
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹的和外星人碰撞"""
        # 删除发生的碰撞的子弹和外星人
        # 如果击中了，就删除相应的子弹和外星人
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        # 击中之后记分牌加分
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()
        if not self.aliens:
            # 删除删除现在的所有子弹，并创建一群新的外星人
            self.bullets.empty()
            self._create_fleet()
            # 消灭所有外星人之后，加快游戏速度
            self.settings.increase_speed()
            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()

    def _update_alien(self):
        self._check_fleet_edges()
        self.aliens.update()
        # 检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # 检查是否有外星人到达屏幕底端
        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整个外星人下移，并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_events(self):
        """响应案件和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_play_button(self, mouse_pos):
        """在玩家点击play按钮之后开始游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        # 只有在游戏处于非轰动状态点击play按钮才生效
        if button_clicked and not self.stats.game_active:
            # 重置游戏设置
            self.settings.initialize_dynamic_settings()

            # 重置游戏统计的信息
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            # 清空剩下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            # 创建一群新的外星人并让飞船居中
            self._create_fleet()
            self.ship.center_ship()
            # 隐藏游戏鼠标
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """键盘按下"""
        if event.key == pygame.K_RIGHT:
            # 向右移动飞船
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_aliens_bottom(self):
        """检车是否有外星人到达屏幕底端"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 想飞船被撞击一样的处理
                self._ship_hit()
                break

    def _fire_bullet(self):
        """创建一颗子弹，并将其加入编组bullets中"""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)

            self.bullets.add(new_bullet)

    def _create_fleet(self):
        """创建外星人"""
        # 创建一个外星人
        alien = Alien(self)
        alien_height, alien_width = alien.rect.size
        # 能容纳外星人的可用空间
        ship_height = self.ship.rect.height
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        available_space_y = self.settings.screen_height - (3 * alien_height) - ship_height
        number_rows = available_space_y // (2 * alien_height)
        # 创建外星人群
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """创建一个外星人并将其放在当前行"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def _update_screen(self):
        """更行屏幕上的图像"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # 显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态的，就给绘制play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == "__main__":
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()
