import json
import logging
from datetime import datetime
from os.path import basename

from jinja2 import Environment, PackageLoader, exceptions, select_autoescape

from reporter.utils import auto_colourize, auto_text_highlight, linkify

env = Environment(
    loader=PackageLoader("reporter", "templates"),
    autoescape=select_autoescape(["html"]),
)
env.filters["basename"] = basename
env.filters["auto_text_highlight"] = auto_text_highlight
env.filters["auto_colourize"] = auto_colourize
env.filters["linkify"] = linkify


def parse(gr_file):
    """
    Parse the grafeas file

    :param gr_file: Dependency scan report in grafeas format
    :return: Vulnerability list
    """
    dep_vuln_data = []
    with open(gr_file, mode="r") as report_file:
        try:
            for line in report_file:
                dep_vuln_data.append(json.loads(line))
        except json.decoder.JSONDecodeError:
            logging.warning("Unable to parse sarif file {}".format(gr_file))
            return None
        return dep_vuln_data


def render_html(dep_vuln_data, out_file):
    """
    Renders the dependency vulnerabilities data into html
    :param dep_vuln_data: Dependency vulnerability data
    :param out_file: Output filename
    :return: HTML contents
    """
    template = env.get_template("dep-report.html")
    try:
        isError = False
        metrics = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "unspecified": 0,
            "total": 0,
        }
        for data in dep_vuln_data:
            metrics[data.get("severity").lower()] += 1
            metrics["total"] += 1
        # Simple logic to determine report status
        if metrics["critical"] > 0 or metrics["high"] > 2:
            isError = True
        report_html = template.render(
            datas=dep_vuln_data,
            isError=isError,
            metrics=metrics,
            scanTime=datetime.now().strftime("%Y-%m-%d at %H:%M"),
        )
    except exceptions.TemplateSyntaxError as te:
        logging.warning(te)
        return None
    if out_file:
        with open(out_file, mode="w") as fp:
            fp.write(report_html)
            logging.debug("Report written to {}".format(report_html))
    return report_html
