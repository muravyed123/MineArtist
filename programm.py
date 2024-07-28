import pygame as pg
from PIL import Image
import PIL

import worker
from pygame.locals import *
pg.init()
WIDTH = 1200
HEIGHT = 800

speed = 300
now_image = 'image.jpg'
clock = pg.time.Clock()
Screen = pg.display.set_mode((WIDTH, HEIGHT))
screen = pg.Surface((WIDTH, HEIGHT))
screen.fill((0, 0, 0))
pg.display.set_caption('Mine_artist')
icon = pg.image.load('icon.png')
pg.display.set_icon(icon)

base_color = (100, 100, 100)
font = pg.font.SysFont('couriernew', 40)

FPS = 30
image = pg.image.load(now_image)

image_screen = pg.Surface((4096, 4096))
x = 0
y = (HEIGHT - 600) // 2
scale = 1

class Button():
    def __init__(self, x, y, width, height, onclickFunction=None, onePress=False, index='', text=''):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = True
        self.index = index
        self.font = pg.font.SysFont('Arial', 40)
        self.buttonSurface = pg.Surface((self.width, self.height))
        self.buttonRect = pg.Rect(self.x, self.y, self.width, self.height)
        pg.draw.rect(screen, (255, 0, 0), self.buttonRect, 1)
        self.text = text
        self.buttonSurf = self.font.render(text, True, base_color)
        if self.text != '':
            self.buttonSurface.blit(self.buttonSurf, [
                self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
                self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
            ])
            screen.blit(self.buttonSurface, self.buttonRect)

    def process(self):
        mouse_pos = pg.mouse.get_pos()
        if self.buttonRect.collidepoint(mouse_pos):
            if pg.mouse.get_pressed(num_buttons=3)[0] and self.alreadyPressed != True:
                if self.onePress:
                    self.onclickFunction(self.index)
                elif not self.alreadyPressed:
                    self.onclickFunction(self.index)
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

def change_image():
    image_screen.fill((255, 255, 255))
    im = pg.transform.scale(image, (image.get_width()*scale, image.get_height()*scale))
    image_screen.blit(im, ((WIDTH - image.get_width() * scale)//2, (HEIGHT - image.get_height()*scale)//2))
    screen.blit(image_screen, (x, y))
def block_founding(pos_x, pos_y):
    local_x = (pos_x - (WIDTH - image.get_width() * scale)//2 - x)/scale
    local_y = (pos_y - (HEIGHT - image.get_height() * scale) // 2 - y)/scale
    if local_x < image.get_width() and local_x >= 0 and local_y < image.get_height() and local_y >= 0:
        i = local_x//16
        j = local_y//16
        block = worker.get_block(int(i), int(j))
        return block
    return ''
def start_transform(name):
    global image
    new_image = worker.transform_image(name)
    image = pg.image.fromstring(new_image.tobytes(), new_image.size, new_image.mode)

def draw(text_block = ''):
    buttons = []
    screen.fill((255, 255, 255))

    change_image()

    r = pg.Rect(0, 0, WIDTH, 100)
    pg.draw.rect(screen, (200, 100, 90), r, 0)

    text1 = font.render('Картинка:' + now_image, True, base_color)
    text_size = font.render('Размер сейчас :' + str(image.get_size()), True, base_color)
    text_bl = font.render(text_block, True, base_color)
    button1 = Button(10, 10, 130, 50, start_transform, False, now_image, 'change')

    buttons.append(button1)

    #screen.blit(text1, [400, 20])
    screen.blit(text_size, [300, 720])
    screen.blit(text_bl, [200, 20])

    return buttons


doing = True
buttons = draw()

vel = [0, 0]
while doing:
    pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            doing = False
        if event.type == pg.MOUSEWHEEL:
            scale += event.y/10
            if scale < 0.1:
                scale = 0.1
    key_pressed_is = pg.key.get_pressed()
    if key_pressed_is[K_LEFT]:
        x -= speed/FPS
        if x < -WIDTH//2: x = -WIDTH//2
    if key_pressed_is[K_RIGHT]:
        x += speed/FPS
        if x > WIDTH//2: x = WIDTH//2
    if key_pressed_is[K_UP]:
        y -= speed/FPS
    if key_pressed_is[K_DOWN]:
        y += speed/FPS
    for bu in buttons:
        bu.process()
    pos_x, pos_y = pg.mouse.get_pos()
    block = block_founding(pos_x, pos_y)
    draw(block)
    Screen.blit(screen, (0, 0))

    clock.tick(FPS)