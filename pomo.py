# pomo.py

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Digits
from textual.reactive import reactive


CSS = """


TimerDisplay {
    color: magenta;
    text-align: center;
    padding: 5;
    height: 33%;
}


TimerDisplay.-alert {
    background: red;
    color: white;
}


ModeDisplay {
    text-align: center;
    padding: 1;
    height: 3;
}
"""

class TimerState:
    WAITING = "Waiting for user input"
    POMODORO = "Pomodoro"
    SHORT_BREAK = "Short Break"
    LONG_BREAK = "Long Break"


DURATIONS = {
    TimerState.POMODORO: 25 * 60,
    TimerState.SHORT_BREAK: 5 * 60,
    TimerState.LONG_BREAK: 15 * 60,
}


class TimerDisplay(Digits):
    time_left = reactive("25:00")

    def watch_time_left(self, new_time: str) -> None:
        self.update(new_time)


class ModeDisplay(Static):
    mode = reactive(TimerState.POMODORO)

    def render(self):
        return f"[bold green]Current:[/bold green] {self.mode}"


class Pomo(App):
    CSS = CSS
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        ("1", "start_pomodoro", "25m"),
        ("2", "start_short_break", "5m"),
        ("3", "start_long_break", "15m"),
        ("space", "start_next", "Next"),
        ("q", "quit", "Quit"),
    ]

    seconds_left = reactive(0)
    current_mode = reactive(TimerState.WAITING)
    next_mode = reactive(TimerState.POMODORO)
    completed_pomodoros = reactive(0)
    timer_task = None

    def compose(self) -> ComposeResult:
        # yield Header()
        with Container():
            self.timer_display = TimerDisplay()
            self.mode_display = ModeDisplay()
            yield self.timer_display
            yield self.mode_display
        yield Footer()



    def on_mount(self):
        self.update_display()
        # self.query_one("HeaderIcon").visible = False


    def update_display(self):
        minutes = self.seconds_left // 60
        seconds = self.seconds_left % 60
        self.timer_display.time_left = f"{minutes:02}:{seconds:02}"
        self.mode_display.mode = self.current_mode

    def start_timer(self, mode: str):
        if self.timer_task:
            self.timer_task.stop()
        self.current_mode = mode
        self.seconds_left = DURATIONS[mode]
        self.timer_task = self.set_interval(1.0, self.tick)
        self.update_display()
        self.timer_display.remove_class("-alert")

        # Update next_mode based on what we just started
        if mode == TimerState.POMODORO:
            self.completed_pomodoros += 1
            if self.completed_pomodoros % 4 == 0:
                self.next_mode = TimerState.LONG_BREAK
            else:
                self.next_mode = TimerState.SHORT_BREAK
        else:
            self.next_mode = TimerState.POMODORO

    def tick(self):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.update_display()
        else:
            self.timer_task.stop()
            self.timer_display.add_class("-alert")
            self.mode_display.mode = "[bold red]Time's up![/bold red]"

    def action_start_pomodoro(self):
        self.start_timer(TimerState.POMODORO)

    def action_start_short_break(self):
        self.start_timer(TimerState.SHORT_BREAK)

    def action_start_test(self):
        self.start_timer(TimerState.SHORT_BREAK)

    def action_start_long_break(self):
        self.start_timer(TimerState.LONG_BREAK)

    def action_start_next(self):
        self.start_timer(self.next_mode)


if __name__ == "__main__":
    Pomo().run()
