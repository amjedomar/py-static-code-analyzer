import re
import sys
import os
import ast
import typing


class Utils:
    @staticmethod
    def find_comment(text):
        pattern = r"(((?<!\\)([\"']{3}|[\"']).*?#.*?(?<!\\)\3)|(#))"
        matches = re.finditer(pattern, text)

        for match in matches:
            if match.group() == '#':
                return match.start()

        return None

    @staticmethod
    def form_msg(cond, msg):
        return msg if cond else None


class StaticCheckers:
    def __init__(self):
        self.preceding_empty_lines = 0

    @staticmethod
    def check_issue_s001(line):
        return Utils.form_msg(len(line.rstrip()) > 79, 'Too long')

    @staticmethod
    def check_issue_s002(line):
        if re.match(r"\s*$", line):
            return None

        ind = len(line) - len(line.lstrip())
        return Utils.form_msg(ind % 4 != 0, 'Indentation is not a multiple of four')

    @staticmethod
    def check_issue_s003(line):
        comment_idx = Utils.find_comment(line)
        code_line = line[:comment_idx]
        pattern = r"(((?<!\\)([\"']{3}|[\"']).*?;.*?(?<!\\)\3)|(;))"

        matches = re.finditer(pattern, code_line)

        for match in matches:
            if match.group() == ';':
                return 'Unnecessary semicolon'

        return None

    @staticmethod
    def check_issue_s004(line):
        comment_idx = Utils.find_comment(line.rstrip())
        if comment_idx is None or comment_idx == 0:
            return None
        before_comment = line[comment_idx - 2: comment_idx]
        is_issue = before_comment != '  '
        return Utils.form_msg(is_issue, 'At least two spaces required before inline comments')

    @staticmethod
    def check_issue_s005(line):
        comment_idx = Utils.find_comment(line)
        if comment_idx is None:
            return None

        comment_line = line[comment_idx + 1:]
        pattern = 'todo'
        is_issue = re.search(pattern, comment_line, flags=re.I) is not None
        return Utils.form_msg(is_issue, 'TODO found')

    def check_issue_s006(self, line):
        if line.rstrip() != '':
            if self.preceding_empty_lines > 2:
                self.preceding_empty_lines = 0
                return 'More than two blank lines used before this line'
            self.preceding_empty_lines = 0
        else:
            self.preceding_empty_lines += 1

        return None

    @staticmethod
    def check_issue_s007(line):
        pattern = r"\s*(def|class)\b(\s+)"
        match = re.match(pattern, line)
        if match:
            keyword, spaces = match.group(1), match.group(2)
            if len(spaces) > 1:
                return f"Too many spaces after '{keyword}'"
        return None

    @staticmethod
    def check_issue_s008(line):
        line_pattern = r"\s*class\b\s+([\S\w]+?)\b"
        match = re.match(line_pattern, line)
        if match:
            name_pattern = r"[A-Z]+[A-Za-z\d]*$"
            class_name = match.group(1)
            is_issue = re.match(name_pattern, class_name) is None
            return Utils.form_msg(is_issue, f"Class name 'user' should use CamelCase")

    @staticmethod
    def check_issue_s009(line):
        line_pattern = r"\s*def\b\s+([\S\w]+?)\b"
        match = re.match(line_pattern, line)
        if match:
            name_pattern = r"[_a-z]+[_a-z\d]*$"
            fn_name = match.group(1)
            is_issue = re.match(name_pattern, fn_name) is None
            return Utils.form_msg(is_issue, f"Function name {fn_name} should use snake_case")


class CheckAst:
    def __init__(self, code):
        self.issues = {}
        self.tree = ast.parse(code)

    def append_issue(self, lineno: int, err: (str, str)):
        if lineno not in self.issues:
            self.issues[lineno] = []
        self.issues[lineno].append(err)

    def check(self):
        name_pattern = r"[_a-z]+[_a-z\d]*$"

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                fn_node = typing.cast(ast.FunctionDef, node)

                for arg in fn_node.args.args:
                    if re.match(name_pattern, arg.arg) is None:
                        issue = 's010', f"Argument name '{arg.arg}' should be snake_case"
                        self.append_issue(fn_node.lineno, issue)
                        break

                for arg_default in fn_node.args.defaults:
                    if isinstance(arg_default, (ast.List, ast.Dict)):
                        issue = 's012', 'Default argument value is mutable'
                        self.append_issue(fn_node.lineno, issue)
                        break

                for local_node in ast.walk(fn_node):
                    if isinstance(local_node, ast.Name) and isinstance(local_node.ctx, ast.Store):
                        if re.match(name_pattern, local_node.id) is None:
                            issue = 's011', f"Variable '{local_node.id}' in function should be snake_case"
                            self.append_issue(local_node.lineno, issue)


def lint_file(file_path):
    with open(file_path) as f:
        code = f.read()

        static_checkers = StaticCheckers()
        check_ast = CheckAst(code)
        check_ast.check()

        for num, line in enumerate(code.splitlines(), start=1):
            for instance_attr in dir(static_checkers):
                pattern = r"check_issue_(s\d{3})$"
                match = re.match(pattern, instance_attr)
                if match:
                    check_issue_fn = getattr(static_checkers, match.group())
                    code = match.group(1)
                    issue_msg = check_issue_fn(line)
                    if issue_msg:
                        print(f'{file_path}: Line {num}: {code} {issue_msg}')

            line_ast_issues = check_ast.issues.get(num, [])
            for ast_issue_code, ast_issue_msg in line_ast_issues:
                print(f'{file_path}: Line {num}: {ast_issue_code} {ast_issue_msg}')


def lint_directory(directory_path):
    for root_path, dirs, files in os.walk(directory_path):
        for file_path in files:
            if re.search(r"\.py$", file_path):
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
