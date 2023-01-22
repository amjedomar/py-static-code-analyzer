import re
file_path = input()

# utils


def find_comment(text):
    pattern = r"(((?<!\\)([\"']{3}|[\"']).*?#.*?(?<!\\)\3)|(#))"
    matches = re.finditer(pattern, text)

    for match in matches:
        if match.group() == '#':
            return match.start()

    return None


# checkers


def check_issue_s001(line):
    return len(line) > 79


def check_issue_s002(line):
    if re.match(r"\s*$", line):
        return False

    ind = len(line) - len(line.lstrip())
    return ind % 4 != 0


def check_issue_s003(line):
    comment_idx = find_comment(line)
    code_line = line[:comment_idx]
    pattern = r"(((?<!\\)([\"']{3}|[\"']).*?;.*?(?<!\\)\3)|(;))"

    matches = re.finditer(pattern, code_line)

    for match in matches:
        if match.group() == ';':
            return True

    return False


def check_issue_s004(line):
    comment_idx = find_comment(line.rstrip())
    if comment_idx is None or comment_idx == 0:
        return False
    before_comment = line[comment_idx - 2: comment_idx]
    return before_comment != '  '


def check_issue_s005(line):
    comment_idx = find_comment(line)
    if comment_idx is None:
        return False

    comment_line = line[comment_idx + 1:]
    pattern = 'todo'

    return re.search(pattern, comment_line, flags=re.I) is not None


preceding_empty_lines = 0


def check_issue_s006(line):
    global preceding_empty_lines

    if line.rstrip() != '':
        if preceding_empty_lines > 2:
            preceding_empty_lines = 0
            return True
        preceding_empty_lines = 0
    else:
        preceding_empty_lines += 1

    return False


codes = {
    's001': (check_issue_s001, 'Too long'),
    's002': (check_issue_s002, 'Indentation is not a multiple of four'),
    's003': (check_issue_s003, 'Unnecessary semicolon'),
    's004': (check_issue_s004, 'At least two spaces required before inline comments'),
    's005': (check_issue_s005, 'TODO found'),
    's006': (check_issue_s006, 'More than two blank lines used before this line')
}


def main():
    with open(file_path) as f:
        for num, line in enumerate(f.readlines(), start=1):
            for code, (check_issue_fn, check_msg) in codes.items():
                if check_issue_fn(line):
                    print(f'Line {num}: {code} {check_msg}')


if __name__ == '__main__':
    main()
