"""Farol da Nevoa: collect five crystals and relight the lighthouse."""

import pgzrun
from pygame import Rect


WIDTH = 960
HEIGHT = 640
TITLE = "Farol da Nevoa"
PLATFORMS = [
    Rect(0, 560, 270, 80), Rect(350, 560, 250, 80),
    Rect(680, 560, 280, 80), Rect(150, 455, 160, 18),
    Rect(365, 365, 180, 18), Rect(620, 280, 180, 18),
    Rect(795, 390, 145, 18),
]
CRYSTAL_POSITIONS = [(90, 522), (225, 417), (455, 327),
                     (710, 242), (895, 352)]
BUTTONS = [Rect(320, y, 320, 52) for y in (310, 378, 446)]
SOUND_NAMES = ("jump", "crystal", "hurt", "win", "click")
state = "menu"
audio_enabled = True
music_started = False
pointer = (0, 0)


class AnimatedCharacter:
    """Cycle real image frames; keep artwork separate from the hitbox."""

    def __init__(self, name, x, bottom, width, height):
        self.name = name
        self.x, self.y = x, bottom
        self.body = Rect(0, 0, width, height)
        self.body.midbottom = (round(x), round(bottom))
        self.actor = Actor(f"{name}_idle_right_0", anchor=("center", "bottom"))
        self.actor.pos = self.body.midbottom
        self.facing = "right"
        self.animation_time = 0.0

    def animate(self, dt, moving):
        self.animation_time += dt
        action = "walk" if moving else "idle"
        frame = int(self.animation_time * (10 if moving else 5)) % 4
        self.actor.image = f"{self.name}_{action}_{self.facing}_{frame}"
        self.actor.pos = self.body.midbottom

    def draw(self):
        self.actor.draw()


class Player(AnimatedCharacter):
    """Resolve each movement axis against solid platforms."""

    def __init__(self):
        super().__init__("keeper", 70, 560, 24, 38)
        self.velocity_y = 0.0
        self.grounded = True
        self.invulnerable = 0.0

    def jump(self):
        if self.grounded:
            self.velocity_y = -650
            self.grounded = False
            play_sound("jump")

    def move(self, dt):
        direction = int(keyboard.right or keyboard.d)
        direction -= int(keyboard.left or keyboard.a)
        if direction:
            self.facing = "right" if direction > 0 else "left"
        self.x = max(12, min(WIDTH - 12, self.x + direction * 240 * dt))
        self.body.centerx = round(self.x)
        for platform in PLATFORMS:
            if direction and self.body.colliderect(platform):
                if direction > 0:
                    self.body.right = platform.left
                else:
                    self.body.left = platform.right
                self.x = self.body.centerx
        self.velocity_y += 1600 * dt
        self.y += self.velocity_y * dt
        self.body.bottom = round(self.y)
        self.grounded = False
        for platform in PLATFORMS:
            if self.body.colliderect(platform):
                if self.velocity_y > 0:
                    self.body.bottom = platform.top
                    self.grounded = True
                else:
                    self.body.top = platform.bottom
                self.y = self.body.bottom
                self.velocity_y = 0
        if self.velocity_y >= 0 and any(
                self.body.bottom == platform.top
                and self.body.right > platform.left
                and self.body.left < platform.right for platform in PLATFORMS):
            self.grounded = True
            self.y = self.body.bottom
            self.velocity_y = 0
        self.invulnerable = max(0, self.invulnerable - dt)
        self.animate(dt, direction != 0)

    def draw(self):
        if not self.invulnerable or int(self.invulnerable * 12) % 2:
            super().draw()


class Sentinel(AnimatedCharacter):
    """Patrol one platform, stopping to look around at both ends."""

    def __init__(self, left, right, bottom, speed):
        super().__init__("sentinel", left, bottom, 30, 28)
        self.left_limit, self.right_limit = left, right
        self.speed = speed
        self.direction = 1
        self.pause = 0.6

    def move(self, dt):
        moving = self.pause <= 0
        if moving:
            self.x += self.direction * self.speed * dt
            if self.x >= self.right_limit or self.x <= self.left_limit:
                self.x = max(self.left_limit, min(self.right_limit, self.x))
                self.direction *= -1
                self.pause = 0.75
        else:
            self.pause -= dt
        self.facing = "right" if self.direction > 0 else "left"
        self.body.midbottom = (round(self.x), round(self.y))
        self.animate(dt, moving)


def play_sound(name):
    if audio_enabled:
        getattr(sounds, name).play()


def toggle_audio():
    global audio_enabled
    audio_enabled = not audio_enabled
    if audio_enabled:
        music.unpause()
        play_sound("click")
    else:
        music.pause()
        for name in SOUND_NAMES:
            getattr(sounds, name).stop()


def reset_game():
    global player, enemies, crystals, lives, state
    player = Player()
    enemies = [Sentinel(177, 283, 455, 55),
               Sentinel(390, 563, 560, 75),
               Sentinel(645, 777, 280, 65),
               Sentinel(730, 920, 560, 85)]
    crystals = [Actor("crystal", pos) for pos in CRYSTAL_POSITIONS]
    lives = 3
    state = "playing"


def hurt_player():
    global player, lives, state
    lives -= 1
    play_sound("hurt")
    if lives == 0:
        state = "lost"
    else:
        player = Player()
        player.invulnerable = 2.0


def update(dt):
    global music_started, state
    if not music_started:
        music.set_volume(0.35)
        music.play("beacon")
        music_started = True
        if not audio_enabled:
            music.pause()
    if state != "playing":
        return
    remaining = min(dt, 0.1)
    while remaining > 0 and state == "playing":
        step = min(remaining, 1 / 120)
        remaining -= step
        player.move(step)
        for enemy in enemies:
            enemy.move(step)
        hit_enemy = any(player.body.colliderect(enemy.body)
                        for enemy in enemies)
        if player.body.top > HEIGHT or (hit_enemy and not player.invulnerable):
            hurt_player()
            continue
        for crystal in crystals[:]:
            if crystal.colliderect(player.body):
                crystals.remove(crystal)
                play_sound("crystal")
        if not crystals and player.body.colliderect(Rect(850, 482, 72, 78)):
            state = "won"
            play_sound("win")


def draw():
    screen.blit("landscape", (0, 0))
    if state != "menu":
        for crystal in crystals:
            screen.blit("crystal_glow", (crystal.x - 24, crystal.y - 24))
            crystal.draw()
        screen.blit("beacon_on" if not crystals else "beacon_off", (825, 435))
        for enemy in enemies:
            enemy.draw()
        player.draw()
        screen.blit("hud", (24, 22))
        screen.draw.text(f"CRISTAIS  {5 - len(crystals)} / 5",
                         (52, 38), fontsize=23, color="#dff8ef")
        screen.draw.text(f"VIDAS  {lives}", (273, 38), fontsize=23,
                         color="#ffc780")
        controls = "A D / SETAS: mover    ESPACO: pular    M: som    ESC: menu"
        screen.draw.text(controls,
                         center=(480, 615), fontsize=19, color="#c3dedb")
        if not crystals and state == "playing":
            screen.draw.text("Leve a luz ao farol!", center=(782, 101),
                             fontsize=24, color="#ffdc90")
    if state != "playing":
        screen.blit("menu_panel", (240, 91))
        title = {"menu": "FAROL DA NEVOA", "won": "O FAROL VIVE!",
                 "lost": "A LUZ AINDA ESPERA"}[state]
        subtitle = {"menu": "Cinco cristais. Uma luz para guiar o caminho.",
                    "won": "Voce trouxe a luz de volta a costa.",
                    "lost": "Respire fundo e tente um novo caminho."}[state]
        screen.draw.text("UMA PEQUENA AVENTURA DE PLATAFORMA",
                         center=(480, 141), fontsize=17, color="#75c4bd")
        screen.draw.text(title, center=(480, 194), fontsize=42,
                         color="#ffe0a3")
        screen.draw.text(subtitle, center=(480, 246), fontsize=20,
                         color="#d1e3df")
        labels = ["Comecar o jogo" if state == "menu" else "Jogar novamente",
                  "Musica e sons: " + ("LIGADOS" if audio_enabled else
                                       "DESLIGADOS"),
                  "Saida"]
        for rectangle, label in zip(BUTTONS, labels):
            hovered = rectangle.collidepoint(pointer)
            image = "button_hover" if hovered else "button"
            screen.blit(image, rectangle.topleft)
            screen.draw.text(label, center=rectangle.center, fontsize=25,
                             color="#142e3e" if hovered else "#e3f5ea")
        hint = "Recolha os cristais, evite as sentinelas e alcance o farol."
        screen.draw.text(hint,
                         center=(480, 535), fontsize=17, color="#a6c7c8")


def on_mouse_move(pos):
    global pointer
    pointer = pos


def on_mouse_down(pos, button):
    if state == "playing" or button != mouse.LEFT:
        return
    if BUTTONS[0].collidepoint(pos):
        play_sound("click")
        reset_game()
    elif BUTTONS[1].collidepoint(pos):
        toggle_audio()
    elif BUTTONS[2].collidepoint(pos):
        raise SystemExit


def on_key_down(key):
    global state
    if key == keys.M:
        toggle_audio()
    elif key == keys.ESCAPE:
        state = "menu"
    elif state == "playing" and key in (keys.SPACE, keys.UP, keys.W):
        player.jump()


pgzrun.go()
