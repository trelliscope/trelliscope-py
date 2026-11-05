from trelliscope.progress_bar import ProgressBar


def test_record_progress_reaches_complete(capsys):
    bar = ProgressBar(3, "Saving Images:")

    for _ in range(3):
        bar.record_progress()

    output = capsys.readouterr().out
    assert "100.0% Complete" in output
    assert output.endswith("\n")
