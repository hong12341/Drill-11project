from pico2d import get_time


class AutoRunState:
    DURATION = 5.0
    SPEED_MULTIPLIER = 2
    DRAW_SIZE = 200

    def __init__(self, boy):
        self.boy = boy
        self.started_at = 0

    def enter(self):
        now = get_time()
        self.started_at = now
        self.boy.frame = 0
        self.boy.last_frame_time = now
        self.boy.last_update_time = now

    def cancel(self):
        self.boy.cancel_auto_run()

    def update(self, now):
        if now - self.started_at >= self.DURATION:
            self.boy.end_auto_run()
            return

        elapsed = now - self.boy.last_update_time
        self.boy.x += (
            self.boy.face_dir
            * self.boy.run_speed
            * self.SPEED_MULTIPLIER
            * elapsed
        )
        sprite_half_width = self.boy.SPRITE_HALF_WIDTH * self.SPEED_MULTIPLIER
        if self.boy.x >= self.boy.CANVAS_WIDTH - sprite_half_width:
            self.boy.x = self.boy.CANVAS_WIDTH - sprite_half_width
            self.boy.face_dir = -1
        elif self.boy.x <= sprite_half_width:
            self.boy.x = sprite_half_width
            self.boy.face_dir = 1

        self.boy.update_animation(now)
        self.boy.last_update_time = now

    def draw(self):
        row_y = 100 if self.boy.face_dir == 1 else 0
        draw_y = self.boy.y + (self.DRAW_SIZE - 100) * 0.4
        self.boy.image.clip_draw(
            self.boy.frame * 100,
            row_y,
            100,
            100,
            self.boy.x,
            draw_y,
            self.DRAW_SIZE,
            self.DRAW_SIZE,
        )