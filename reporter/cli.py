#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys

from joern2sarif.lib import convert as convertLib

from reporter import config as config
from reporter import gh as githubLib
from reporter import sarif as sarif
from reporter.common import LOG, extract_org_id, get_all_findings


def build_args():
    """
    Constructs command line arguments for the vulndb tool
    """
    parser = argparse.ArgumentParser(
        description="Utility script to convert ShiftLeft CORE json output to sarif and html format."
    )
    parser.add_argument(
        "-a",
        "--app",
        dest="app_name",
        required=True,
        help="App name",
        default=config.SHIFTLEFT_APP,
    )
    parser.add_argument("--version", dest="app_version", help="App Version")
    parser.add_argument("--branch", dest="app_branch", help="App Branch")
    parser.add_argument(
        "-o",
        "--reports_dir",
        dest="reports_dir",
        default="reports",
        help="Report directory",
    )
    parser.add_argument(
        "--annotate-pr",
        dest="annotate_pr",
        help="Annotate pull request (GitHub only)",
        action="store_true",
        default=False,
    )
    return parser.parse_args()


def main():
    args = build_args()
    reports_dir = args.reports_dir
    src_file = os.path.join(reports_dir, "ngsast.json")
    report_file = src_file.replace(".json", ".sarif")
    html_file = src_file.replace(".json", ".html")
    work_dir = os.getcwd()
    for e in ["GITHUB_WORKSPACE", "WORKSPACE"]:
        if os.getenv(e):
            work_dir = os.getenv(e)
            break
    # Download the findings using the v4 api
    if not config.SHIFTLEFT_ACCESS_TOKEN:
        LOG.info(
            "Set the environment variable SHIFTLEFT_ACCESS_TOKEN before running this script"
        )
        sys.exit(1)

    org_id = extract_org_id(config.SHIFTLEFT_ACCESS_TOKEN)
    if not org_id:
        LOG.info(
            "Ensure the environment varibale SHIFTLEFT_ACCESS_TOKEN is copied exactly as-is from the website"
        )
        sys.exit(1)
    # Create reports directory
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    LOG.debug(f"About to retrieve findings for {args.app_name}")
    findings_dict = {}
    findings_list, scan_info = get_all_findings(
        org_id, args.app_name, args.app_version, args.app_branch
    )
    if args.annotate_pr:
        githubLib.annotate(findings_list, scan_info)
    findings_dict[args.app_name] = findings_list
    with open(src_file, mode="w") as rp:
        json.dump(findings_dict, rp, ensure_ascii=True, indent=config.json_indent)
        LOG.debug(f"JSON report successfully exported to {src_file}")
    LOG.debug(f"About to convert {src_file}")
    sarif_data = convertLib.convert_file(
        "core",
        os.getenv("TOOL_ARGS", ""),
        work_dir,
        src_file,
        report_file,
        None,
    )
    if sarif_data:
        LOG.info(f"SARIF and html file created: {report_file} {html_file}")
        sarif.render_html(sarif.parse(report_file), html_file)


if __name__ == "__main__":
    main()
