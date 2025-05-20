from pathlib import Path

from calc_repo_lines import calc_lines, count_lines_in_file


def test_count_lines_in_file(tmp_path: Path) -> None:
    file = tmp_path / "file.txt"
    file.write_text("a\n\n b \n")
    total, code = count_lines_in_file(file)
    assert total == 3
    assert code == 2


def test_calc_lines(tmp_path: Path) -> None:
    (tmp_path / 'sub').mkdir()
    (tmp_path / 'file1.txt').write_text('line1\n\nline3\n')
    (tmp_path / 'sub' / 'file2.py').write_text('# comment\ncode\n')
    # create .git file to ensure it is skipped
    (tmp_path / '.git').mkdir()
    (tmp_path / '.git' / 'ignore.txt').write_text('should be ignored\n')

    total, code = calc_lines(tmp_path)
    assert total == 5
    assert code == 4
