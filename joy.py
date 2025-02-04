#!/usr/bin/env python3

import math
import pygame
import random

class Setup:
    size = (1600, 1200)
    log_size = (1600, 1200)
    fps = 30
    speed = 4
    scale = [log_size[0] / size[0], log_size[1] / size[1]]


class Color:
    black = (0, 0, 0)
    blue = (60, 100, 220)
    background = (180, 180, 180)


class State:
    maxspeed = 10
    accel = 5
    slowdown = 1.3
    joy_thresh = 0.3
    bloke_action_radius = 3600

    def __init__(self):
        self.x = Setup.log_size[0] / 2
        self.y = Setup.log_size[1] / 2
        self.vec = [0, 0]
        self.phase = 0
        self.bloke = (random.randint(100, Setup.log_size[0] - 100), random.randint(100, Setup.log_size[1] - 100))

    def tick(self, xaxis, yaxis):
        vx = self.vec[0]
        vy = self.vec[1]

        if xaxis < -self.joy_thresh:
            vx = max(-self.maxspeed, vx - self.accel)
        elif xaxis > self.joy_thresh:
            vx = min(self.maxspeed, vx + self.accel)
        else:
            vx /= self.slowdown

        if yaxis < -self.joy_thresh:
            vy = max(-self.maxspeed, vy - self.accel)
        elif yaxis > self.joy_thresh:
            vy = min(self.maxspeed, vy + self.accel)
        else:
            vy /= self.slowdown

        self.x = max(0, min(Setup.log_size[0], self.x + vx))
        self.y = max(0, min(Setup.log_size[1], self.y + vy))
        self.vec = [vx, vy]

        # walk phase; reset if not moving
        if abs(vx) < 2 and abs(vy) < 2:
            self.phase = 0
        else:
            self.phase += 1

        # the bloke
        if self.bloke_moves():
            dx = self.x - self.bloke[0]
            dy = self.y - self.bloke[1]
            alpha = math.atan(abs(dy)/abs(dx))
            speed = self.maxspeed / 2
            self.bloke = (
                self.bloke[0] + speed * math.copysign(math.cos(alpha), dx),
                self.bloke[1] + speed * math.copysign(math.sin(alpha), dy)
            )

    def get_pos(self):
        return (int(self.x), int(self.y))

    def get_phase(self):
        return self.phase

    def get_bloke(self):
        return (int(self.bloke[0]), int(self.bloke[1]))

    def bloke_moves(self):
        dx = self.x - self.bloke[0]
        dy = self.y - self.bloke[1]
        c = dx * dx + dy * dy
        return c >= self.bloke_action_radius


class App:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode(Setup.size)
        pygame.display.set_caption('Joystick')
        self.clock = pygame.time.Clock()
        self.state = State()
        self.walk = pygame.image.load('sprites/guy.png').convert_alpha()
        self.bloke = pygame.image.load('sprites/bloke.png').convert_alpha()
        self.bloke_walk_phase = 0
        self.bloke_sneeze_phase = 0

        pygame.joystick.init()
        num_joy = pygame.joystick.get_count()
        for j in range(num_joy):
            joy = pygame.joystick.Joystick(j)
            joy.init()
            print(f'joystick {j}: {joy.get_name()}')

    def stop(self):
        pygame.joystick.quit()
        pygame.quit()
        self.running = False

    def loop(self):
        self.clock.tick(Setup.fps)
        joystick = pygame.joystick.Joystick(0)
        xvalue = joystick.get_axis(0)
        yvalue = joystick.get_axis(1)
        self.state.tick(xvalue, yvalue)

    def get_guy_blit(self, phase):
        frames = 4
        wid = 142
        hei = 150
        ph = phase % (2 * frames - 2)
        if ph >= frames:
            ph = frames - (ph % frames + 1)
        return (self.walk, (ph * wid, 0, wid, hei))

    def get_bloke_blit(self, walk, sneeze):
        walk_frames = 4
        sneeze_frames = 5
        wid = 128
        hei = 180
        if walk is not None:
            ph = walk % (2 * walk_frames - 2)
            if ph >= walk_frames:
                ph = walk_frames - (ph % walk_frames + 1)
        elif sneeze is not None:
            ph = ((sneeze // 3) % sneeze_frames) + walk_frames
        else:
            ph = 0
        return (self.bloke, (ph * wid, 0, wid, hei))

    def render(self):
        buf = pygame.Surface(Setup.log_size, pygame.SRCALPHA, 32)
        buf.fill(Color.background)
        x, y = self.state.get_pos()
        phase = self.state.get_phase()
        x = int(x * Setup.scale[0])
        y = int(y * Setup.scale[1])

        guy_blit = self.get_guy_blit(phase)
        wid = guy_blit[1][2]
        hei = guy_blit[1][3]
        guy_blit = (guy_blit[0], (x-wid//2, y-wid//2), guy_blit[1])

        x, y = self.state.get_bloke()
        if self.state.bloke_moves():
            self.bloke_sneeze_phase = None
            if self.bloke_walk_phase is not None:
                self.bloke_walk_phase += 1
            else:
                self.bloke_walk_phase = 0
        else:
            self.bloke_walk_phase = None
            if self.bloke_sneeze_phase is not None:
                self.bloke_sneeze_phase += 1
            else:
                self.bloke_sneeze_phase = 0
        bloke_blit = self.get_bloke_blit(self.bloke_walk_phase, self.bloke_sneeze_phase)
        wid = bloke_blit[1][2]
        hei = bloke_blit[1][3]
        bloke_blit = (bloke_blit[0], (x-wid//2, y-wid//2), bloke_blit[1])

        buf.blits(blit_sequence=[guy_blit, bloke_blit])

        self.display.blit(buf, (0, 0), (0, 0, Setup.log_size[0], Setup.log_size[1]))

        pygame.display.update()

    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.stop()
                elif event.type == pygame.JOYAXISMOTION:
                    pass
                    # if event.joy == 0:
                    #    self.state = self.move(self.state, event.axis, event.value)
                    # print('joyaxismotion', event)
                elif event.type == pygame.JOYBUTTONDOWN:
                    pass
                    # print('joybuttondown', event)
                elif event.type == pygame.JOYBUTTONUP:
                    pass
                    # print('joybuttonup', event)
                elif event.type == pygame.JOYHATMOTION:
                    pass

            if not self.running:
                break

            self.loop()
            self.render()


if __name__ == '__main__':
    app = App()
    app.run()
