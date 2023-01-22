import re
import sys
import os


class Utils:
    @staticmethod
    def find_comment(text):
        pattern = r"(((?<!\\)([\"']{3}|[\"']).*?#.*?(?<!\\)\3)|(#))"
        matches = re.finditer(pattern, text)

        for match in matches:
            if match.group() == '#':
                return match.start()

        return None


class Checkers:
    preceding_empty_lines = 0

    @staticmethod
    def check_issue_s001(line):
        return len(line.rstrip()) > 79

    @staticmethod
    def check_issue_s002(line):
        if re.match(r"\s*$", line):
            return False

        ind = len(line) - len(line.lstrip())
        return ind % 4 != 0

    @staticmethod
    def check_issue_s003(line):
        comment_idx = Utils.find_comment(line)
        code_line = line[:comment_idx]
        pattern = r"(((?<!\\)([\"']{3}|[\"']).*?;.*?(?<!\\)\3)|(;))"

        matches = re.finditer(pattern, code_line)

        for match in matches:
            if match.group() == ';':
                return True

        return False

    @staticmethod
    def check_issue_s004(line):
        comment_idx = Utils.find_comment(line.rstrip())
        if comment_idx is None or comment_idx == 0:
            return False
        before_comment = line[comment_idx - 2: comment_idx]
        return before_comment != '  '

    @staticmethod
    def check_issue_s005(line):
        comment_idx = Utils.find_comment(line)
        if comment_idx is None:
            return False

        comment_line = line[comment_idx + 1:]
        pattern = 'todo'

        return re.search(pattern, comment_line, flags=re.I) is not None

    @staticmethod
    def check_issue_s006(line):
        if line.rstrip() != '':
            if Checkers.preceding_empty_lines > 2:
                Checkers.preceding_empty_lines = 0
                return True
            Checkers.preceding_empty_lines = 0
        else:
            Checkers.preceding_empty_lines += 1

        return False


codes = {
    's001': 'Too long',
    's002': 'Indentation is not a multiple of four',
    's003': 'Unnecessary semicolon',
    's004': 'At least two spaces required before inline comments',
    's005': 'TODO found',
    's006': 'More than two blank lines used before this line'
}


def lint_file(file_path):
    with open(file_path) as f:
        for num, line in enumerate(f.readlines(), start=1):
            for code, msg in codes.items():
                check_issue_fn = getattr(Checkers, f'check_issue_{code}')
                if check_issue_fn(line):
                    print(f'{file_path}: Line {num}: {code} {msg}')


def lint_directory(directory_path):
    for root_path, dirs, files in os.walk(directory_path):
        for file_path in files:
            if re.search(r"\d+\.py$", file_path):
                file_full_path = os.path.join(root_path, file_path)
                lint_file(file_full_path)


def main():
    dir_or_file_path = sys.argv[1]
    if os.path.isfile(dir_or_file_path):
        lint_file(dir_or_file_path)
    else:
        lint_directory(dir_or_file_path)


if __name__ == '__main__':
    main()
