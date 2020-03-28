#!/usr/bin/env python3
import sys

sys.path.append("..")
import reporter.sarif as sarif
import reporter.grafeas as grafeas
import reporter.licence as licence
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="SARIF file path", required=True)
parser.add_argument("-o", "--output", help="HTML report name", required=True)
args = parser.parse_args()
if args.input:
    # Quick condition for depscan testing
    if "depscan" in args.input:
        report_data = grafeas.parse(args.input)
    elif "sarif" in args.input:
        report_data = sarif.parse(args.input)
    elif "license" in args.input:
        report_data = licence.parse(args.input)
if args.output:
    with open(args.output, mode="w", encoding="utf-8") as f:
        if "depscan" in args.input:
            grafeas.render_html(report_data, f.name)
        elif "sarif" in args.input:
            sarif.render_html(report_data, f.name)
        elif "license" in args.input:
            licence.render_html(report_data, f.name)
