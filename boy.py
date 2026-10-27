import os

from pico2d import get_time, load_image
from transitions import Machine

class Boy:
    CANVAS_WIDTH = 800
    SPRITE_HALF_WIDTH = 50
    AUTO_RUN_MULTIPLIER = 2

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.frame_duration = 0.1
        self.run_speed = 200
        self.pressed_directions = set()
        self.last_frame_time = get_time()
        self.last_update_time = self.last_frame_time
        self.idle_started_at = get_time()
        self.auto_run_started_at = self.last_update_time
        image_path = os.path.join(os.path.dirname(__file__), 'animation_sheet.png')
        self.image = load_image(image_path)
        self.machine = Machine(
            model=self,
            states=['idle', 'run', 'sleep', 'auto_run'],
            initial='idle',
            transitions=[
                {'trigger': 'start_running', 'source': 'idle', 'dest': 'run', 'after': 'enter_run'},
                {'trigger': 'start_running', 'source': 'sleep', 'dest': 'run', 'after': 'enter_run'},
                {'trigger': 'start_auto_run', 'source': 'idle', 'dest': 'auto_run', 'after': 'enter_auto_run'},
                {'trigger': 'cancel_auto_run', 'source': 'auto_run', 'dest': 'run', 'after': 'enter_run'},
                {'trigger': 'end_auto_run', 'source': 'auto_run', 'dest': 'idle', 'after': 'start_idle_timer'},
                {'trigger': 'stop_running', 'source': 'run', 'dest': 'idle', 'after': 'start_idle_timer'},
                {'trigger': 'fall_asleep', 'source': 'idle', 'dest': 'sleep', 'after': 'enter_sleep'},
                {'trigger': 'wake_up', 'source': 'sleep', 'dest': 'idle', 'after': 'start_idle_timer'},
            ],
        )

    def update(self):
        now = get_time()
        if self.state == 'idle':
            if now - self.idle_started_at >= 5.0:
                self.fall_asleep()
                return
            self.update_animation(now)
        elif self.state == 'auto_run' and now - self.auto_run_started_at >= 5.0:
            self.end_auto_run()
            return
        elif self.state in ('run', 'auto_run'):
            elapsed = now - self.last_update_time
            speed_multiplier = self.AUTO_RUN_MULTIPLIER if self.state == 'auto_run' else 1
            self.x += self.face_dir * self.run_speed * speed_multiplier * elapsed
            if self.state == 'auto_run':
                sprite_half_width = self.SPRITE_HALF_WIDTH * self.AUTO_RUN_MULTIPLIER
                if self.x >= self.CANVAS_WIDTH - sprite_half_width:
                    self.x = self.CANVAS_WIDTH - sprite_half_width
                    self.face_dir = -1
                elif self.x <= sprite_half_width:
                    self.x = sprite_half_width
                    self.face_dir = 1
            else:
                self.x = max(
                    self.SPRITE_HALF_WIDTH,
                    min(self.x, self.CANVAS_WIDTH - self.SPRITE_HALF_WIDTH),
                )
            self.update_animation(now)
        self.last_update_time = now

    def update_animation(self, now):
        elapsed_frames = int((now - self.last_frame_time) / self.frame_duration)
        if elapsed_frames:
            self.frame = (self.frame + elapsed_frames) % 8
            self.last_frame_time += elapsed_frames * self.frame_duration

    def press_direction(self, direction):
        self.pressed_directions.add(direction)
        self.face_dir = direction
        if self.state == 'auto_run':
            self.cancel_auto_run()
        elif self.state in ('idle', 'sleep'):
            self.start_running()

    def release_direction(self, direction):
        self.pressed_directions.discard(direction)
        if self.state != 'run':
            return
        if self.pressed_directions:
            self.face_dir = -1 if -1 in self.pressed_directions else 1
        else:
            self.stop_running()

    def enter_run(self):
        self.frame = 0
        self.last_frame_time = get_time()
        self.last_update_time = self.last_frame_time

    def enter_auto_run(self):
        self.enter_run()
        self.auto_run_started_at = self.last_update_time

    def enter_sleep(self):
        self.frame = 0

    def start_idle_timer(self):
        self.idle_started_at = get_time()
        self.last_frame_time = self.idle_started_at
        self.last_update_time = self.idle_started_at
        self.frame = 0

    def draw(self):
        if self.state == 'sleep':
            row_y = 300 if self.face_dir == 1 else 200
            angle = 80 if self.face_dir == 1 else -80
            self.image.clip_composite_draw(
                0, row_y, 100, 100, angle, '', self.x, self.y - 25, 100, 100
            )
            return

        if self.state in ('run', 'auto_run'):
            row_y = 100 if self.face_dir == 1 else 0
            size_multiplier = self.AUTO_RUN_MULTIPLIER if self.state == 'auto_run' else 1
            draw_size = 100 * size_multiplier
            draw_y = self.y + (draw_size - 100) / 2
            self.image.clip_draw(
                self.frame * 100, row_y, 100, 100, self.x, draw_y, draw_size, draw_size
            )
            return

        if self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
