class ProgressBar:
    # Code based loosely on: https://stackoverflow.com/a/34325723

    def __init__(
        self,
        total,
        prefix="",
        suffix="Complete",
        decimals=1,
        length=50,
        fill="█",
        print_end="\r",
    ) -> None:
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end

        self.current_iteration = 0

    def print_progress_bar_at_iteration(self, iteration):
        percent = ("{0:." + str(self.decimals) + "f}").format(
            100 * (iteration / float(self.total))
        )
        filledLength = int(self.length * iteration // self.total)
        bar = self.fill * filledLength + "-" * (self.length - filledLength)
        print(f"\r{self.prefix} |{bar}| {percent}% {self.suffix}", end=self.print_end)

        # Print New Line on Complete
        if iteration == self.total:
            print()

    def record_progress(self):
        self.print_progress_bar_at_iteration(self.current_iteration)
        self.current_iteration += 1

    def record_finish(self):
        print()
