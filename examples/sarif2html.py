#!/usr/bin/env python3

from reporter.sarif import parse, render_html
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='SARIF file path', required=True)
parser.add_argument('-o', '--output', help='HTML report name', required=True)
args = parser.parse_args()
if args.input:
    report_data = parse(args.input)
if args.output:
    with open(args.output, mode="w", encoding="utf-8") as f:
        render_html(report_data, f.name)
