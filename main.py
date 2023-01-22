file_path = input()


def check_issue_s001(line):
    return len(line) > 79


codes = {
    's001': (check_issue_s001, 'Too long')
}


def main():
    with open(file_path) as f:
        for num, line in enumerate(f.readlines(), start=1):
            for code, (check_issue_fn, check_msg) in codes.items():
                if check_issue_fn(line):
                    print(f'Line {num}: {code} {check_msg}')


if __name__ == '__main__':
    main()
