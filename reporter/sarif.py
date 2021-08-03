import json
import logging
from os.path import basename

import markdown
from jinja2 import Environment, Markup, PackageLoader, exceptions, select_autoescape

from reporter.utils import (
    auto_colourize,
    auto_text_highlight,
    linkify_rule,
    remove_end_period,
)

md = markdown.Markdown(extensions=["meta"])

env = Environment(
    loader=PackageLoader("reporter", "templates"),
    autoescape=select_autoescape(["html"]),
)
env.filters["markdown"] = lambda text: Markup(md.convert(text))
env.filters["basename"] = basename
env.filters["auto_text_highlight"] = auto_text_highlight
env.filters["auto_colourize"] = auto_colourize
env.filters["linkify_rule"] = linkify_rule
env.filters["remove_end_period"] = remove_end_period


def parse(sarif_file):
    """
    Parse sarif file
    :param sarif_file: Sarif file from SAST scan
    :return: Json data
    """
    report_data = {}
    with open(sarif_file, mode="r") as report_file:
        try:
            report_data = json.loads(report_file.read())
        except json.decoder.JSONDecodeError:
            logging.warning("Unable to parse sarif file {}".format(sarif_file))
            return None
        return report_data


def compute_metrics(report_data, results):
    """
    Compute summary metrics from results found in the sarif file
    :param report_data: Report data
    :param results: Results section from the sarif
    :return: metrics - dict containing severity as key and count as the value
    """
    metrics = {"total": len(results), "critical": 0, "high": 0, "medium": 0, "low": 0}
    for res in results:
        severity = res.get("properties").get("issue_severity")
        severity = severity.lower()
        if severity == "moderate":
            severity = "medium"
        if not severity:
            severity = "low"
        metrics[severity] += 1
    return metrics


def render_html(report_data, out_file):
    """
    Renders the SAST report data as html
    :param report_data: Report data from sarif files
    :param out_file: Output filename
    :return: HTML contents
    """
    template = env.get_template("sast-report.html")
    try:
        run = report_data.get("runs")[-1]
        results = run.get("results")
        key_issues = [r for r in results if r.get("level") == "error"]
        metrics = run.get("properties", {}).get("metrics")
        if not metrics:
            metrics = compute_metrics(report_data, results)
        if len(key_issues) > 4:
            key_issues = key_issues[:4]
        report_html = template.render(
            report_data, key_issues=key_issues, metrics=metrics
        )
    except exceptions.TemplateSyntaxError as te:
        logging.warning(te)
        return None
    if out_file:
        with open(out_file, mode="w") as fp:
            fp.write(report_html)
            logging.debug("Report written to {}".format(report_html))
    return report_html
