class ProgressBar:
    max_value: float
    suffix: str
    prefix: str
    length: int
    step: float
    fill: str
    print_end: str
    decimals: int
    current_value: float

    @staticmethod
    def config(max_value: float = 100, prefix: str = '', suffix: str = '', length: int = 100, step: float = 1,
               decimals: int = 1, fill: str = '█'):
        ProgressBar.max_value = max_value
        ProgressBar.prefix = prefix
        ProgressBar.suffix = suffix
        ProgressBar.length = length
        ProgressBar.fill = fill
        ProgressBar.decimals = decimals
        ProgressBar.step = step
        ProgressBar.current_value = 0
        ProgressBar.draw_progress(0)

    @staticmethod
    def draw_progress(value: float):
        percent = ("{0:." + str(ProgressBar.decimals) + "f}").format(100 * (value / ProgressBar.max_value))
        filled_length = int(ProgressBar.length * value // ProgressBar.max_value)
        bar = ProgressBar.fill * filled_length + '-' * (ProgressBar.length - filled_length)
        print(f'\r{ProgressBar.prefix} |{bar}| {percent}% {ProgressBar.suffix}', end='', flush=True)
        ProgressBar.current_value = value
        if value == ProgressBar.max_value:
            print()

    @staticmethod
    def update_progress():
        ProgressBar.draw_progress(ProgressBar.current_value + ProgressBar.step)
