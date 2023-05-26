import argparse
import datetime
import os
import time

import lief
import re


def tex_escape(text):
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key))
                       for key in sorted(conv.keys(), key=lambda item: -len(item))))
    return regex.sub(lambda match: conv[match.group()], text)


def export_to_latex(root: str, result: dict, file_name=None):
    report = '''\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage[htt]{hyphenat}
'''
    report += '\\title{BLDD Report for \\texttt{' + \
        tex_escape(root) + '}}\n'
    report += '\n'
    report += '\\begin{document}\n'
    report += '\\maketitle\n'

    for arch in result:
        report += '\\section{\\texttt{' + \
            tex_escape(arch.upper()) + '}}\n'
        usages = [(x, len(result[arch][x])) for x in result[arch].keys()]
        usages.sort(key=lambda x: -x[1])

        for lib in usages:
            report += '\\subsection{\\texttt{' + \
                tex_escape(lib[0]) + '}' + f' ({lib[1]} usages)' + '}\n'
            report += '\\begin{itemize}\n'

            for exc_path in result[arch][lib[0]]:
                report += ' ' * 4 + \
                    '\\item \\texttt{' + tex_escape(exc_path) + '}\n'

            report += '\\end{itemize}\n'
        report += '\n'

    report += '\\end{document}'

    if file_name is None:
        print(report)
        return

    with open(file_name, 'w') as f:
        f.write(report)


def export_to_txt(root: str, result: dict, file_name=None):
    report = f'BLDD report for {root}\n'
    for arch in result:
        report += f'{arch}\n'.upper()
        usages = [(x, len(result[arch][x])) for x in result[arch]]
        usages.sort(key=lambda x: -x[1])

        for lib in usages:
            report += f'{lib[0]} ({lib[1]} executables)\n'

            for exc_path in result[arch][lib[0]]:
                report += ' ' * 8 + f'-> {exc_path}\n'

    if file_name is None:
        print(report)
        return

    with open(file_name, 'w+') as f:
        f.write(report)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''
Print usages of libraries for all architectures
python bldd.py directory_name
Example: python bldd.py bin

Write report to txt file
python bldd.py --output=filename directory_name
Example: python bldd.py --output=report.txt bin

Write report to latex file
python bldd.py --report=latex --output=filename directory_name
Example: python bldd.py --report=latex --output=report.tex bin

Print usages of libraries for specified arch
python bldd.py --arch=name directory_name
Example: python bldd.py --arch=MIPS bin
''')
    parser.add_argument('path', help='Please specify path to folder')
    parser.add_argument('--report', help='Type of report',
                        choices=['text', 'latex'], default='text')
    parser.add_argument('--output', help='File to write report')
    parser.add_argument(
        '--arch', help='Specify architecture to search', default='')
    return parser.parse_args()


args = parse_args()
root = args.path
target_arch = args.arch
result = {}

for path, directories, files in os.walk(root):
    for file in files:
        abs_path = os.path.abspath(os.path.join(path, file))
        elf = lief.ELF.parse(abs_path)
        if elf is None or not elf.has_section('.interp') or '.so' in file:
            continue

        current_arch = elf.header.machine_type.name
        if target_arch != '' and current_arch != target_arch:
            continue

        if current_arch not in result:
            result[current_arch] = {}

        for lib in elf.libraries:
            if lib not in result[current_arch]:
                result[current_arch][lib] = []
            result[current_arch][lib].append(abs_path)

report_type = args.report.lower()
report_filename = args.output

match report_type:
    case 'text':
        export_to_txt(root, result, report_filename)
    case 'latex':
        export_to_latex(root, result, report_filename)
    case _:
        print('Error: Unknown report mode')
