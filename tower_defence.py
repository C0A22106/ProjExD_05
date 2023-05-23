import math
import random
import sys
import time

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ

def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（敵，主人公）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：敵SurfaceのRect
    引数2 dst：主人公SurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Hero(pg.sprite.Sprite):
    """
    ゲームキャラクターに関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        主人公画像Surfaceを生成する
        引数1 num：主人公画像ファイル名の番号
        引数2 xy：主人公画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトの主人公
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10


    def change_img(self, num: int, screen: pg.Surface):
        """
        主人公画像を切り替え，画面に転送する
        引数1 num：主人公画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じて主人公を移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)
        
    def get_direction(self) -> tuple[int, int]:
        return self.dire
    
class Tower(pg.sprite.Sprite):
    """
    タワーに関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.image.load("ex05/fig/1.png")
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)
        self.life = 3
        self.gameover = False
        self.super = 0

    def update(self, screen):
        """
        引数 screen：画面surface
        """
        screen.blit(self.image, self.rect)
        self.super -= 1
    

class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"ex05/fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self, tower: Tower):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        while True:
            x, y = random.randint(-50, WIDTH+50), random.randint(-50, HEIGHT+50)
            if (x < 0 or x > WIDTH) and (y < 0 or y > HEIGHT):
                self.rect.center = x, y
                break
        self.vx, self.vy = calc_orientation(self.rect, tower.rect) 


    def update(self):
        """
        画面中央の位置に向かって速度ベクトルを設定
        敵機を速度ベクトルself_vx,self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.vx*10, self.vy*10)


class Boss(pg.sprite.Sprite):
    """
    ボスに関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load("ex05/fig/alien1.png"), 0, 5.0)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH/2, 0
        self.bound = 200  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.skill_wait = 100
        self.vy = 6
        self.vx = 0
        self.count_charge = 0

    def update(self, screen):
        """
        ボスを速度ベクトルself.vyに基づき移動（降下）させる
        停止位置_boundまで降下したら，_stateを停止状態に変更する
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
    
        if self.rect.centerx <= 0:
            self.skill_wait = random.randint(50, 300)
            self.count_charge += 1
            if self.count_charge > 5:
                self.state = "down"
                self.rect.center = WIDTH/2, 200
                self.vx = 0
                self.vy = -10
        if self.rect.centery <= -5000:
            self.vy = 6
            self.count_charge = 0

        self.rect.centery += self.vy
        self.rect.centerx += self.vx
        screen.blit(self.image, self.rect)

    def charge(self, hero: Hero):
        """
        ボスがhero.rectから主人公のy座標を薙ぎ払うように突進する
        """
        if self.skill_wait > 0:
            self.vx, self.vy = 0, 0
            self.rect.center = WIDTH, hero.rect.centery
            self.skill_wait -= 1
        else:
            self.vx = -25


def main():
    pg.display.set_caption("守れ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex04/fig/pg_bg.jpg")

    hero = Hero(3, (900, 400))
    tower = Tower()
    emys = pg.sprite.Group()
    boss = Boss()

    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        screen.blit(bg_img, [0, 0])
        
        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy(tower))

        if boss.state == "stop":
                # ボスが停止状態に入ったら，intervalに応じて突進
                boss.charge(hero)

        if pg.sprite.spritecollide(hero, emys, True):
            continue

        if pg.sprite.spritecollide(tower, emys, True) or pg.sprite.collide_rect(boss, tower):
            hero.change_img(8, screen) # こうかとん悲しみエフェクト
            if tower.super <= 0:
                print(tower.life)
                tower.life -= 1
                tower.super = 100
            if tower.life == 0:
                pg.display.update()
                time.sleep(2)
                return

        hero.update(key_lst, screen)
        emys.update()
        emys.draw(screen)
        boss.update(screen)
        tower.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()