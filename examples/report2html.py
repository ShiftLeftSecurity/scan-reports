#!/usr/bin/env python3
import sys

sys.path.append("..")
import reporter.sarif as sarif
import reporter.grafeas as grafeas
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="SARIF file path", required=True)
parser.add_argument("-o", "--output", help="HTML report name", required=True)
args = parser.parse_args()
if args.input:
    # Quick condition for depscan testing
    if "depscan" in args.input:
        report_data = grafeas.parse(args.input)
    else:
        report_data = sarif.parse(args.input)
if args.output:
    with open(args.output, mode="w", encoding="utf-8") as f:
        if "depscan" in args.input:
            grafeas.render_html(report_data, f.name)
        else:
            sarif.render_html(report_data, f.name)
