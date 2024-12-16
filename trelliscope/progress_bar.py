"""Progress bar used for printing progress when creating Trelliscope display."""


class ProgressBar:
    """Configurable progress bar created by printing progress of an iteration.

    Code based loosely on: https://stackoverflow.com/a/34325723
    """

    def __init__(
        self,
        total: int,
        prefix: str = "",
        suffix: str = "Complete",
        decimals: int = 1,
        length: int = 50,
        fill: str = "█",
        print_end: str = "\r",
    ) -> None:
        """Create Progress bar.

        Args:
            total: Total expected iterations.
            prefix: Prefix of progress messages.
            suffix: Suffix of progress messages.
            decimals: Number of decimals to show of progress percentage.
            length: Total number of characters in a completed progress bar.
            fill: Character that represents a single bar in the progress bar.
            print_end: String appended after the last printed value, passed to `print(..., end=print_end)`.
        """
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end

        self.current_iteration = 0

    def print_progress_bar_at_iteration(self, iteration: int) -> None:
        """Print progress bar at given iteration.

        Args:
            iteration: integer iteration.
        """
        percent = ("{0:." + str(self.decimals) + "f}").format(
            100 * (iteration / float(self.total))
        )
        filledLength = int(self.length * iteration // self.total)
        bar = self.fill * filledLength + "-" * (self.length - filledLength)
        print(f"\r{self.prefix} |{bar}| {percent}% {self.suffix}", end=self.print_end)

        # Print New Line on Complete
        if iteration == self.total:
            self.record_finish()

    def record_progress(self) -> None:
        """Prints current progress and then adds 1 to internal count of iterations."""
        self.print_progress_bar_at_iteration(self.current_iteration)
        self.current_iteration += 1

    def record_finish(self) -> None:
        """Print empty newline, should be used after tracked iteration is finished."""
        print()
