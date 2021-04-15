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


def parse(lic_file):
    """
    Parse the grafeas file

    :param lic_file: Licence scan report in custom JSON format
    :return: Licence List
    """
    licence_data = []
    with open(lic_file, mode="r") as report_file:
        try:
            for line in report_file:
                licence_data.append(json.loads(line))
        except json.decoder.JSONDecodeError:
            logging.warning("Unable to parse licence file {}".format(lic_file))
            return None
        return licence_data


def render_html(licence_data, out_file):
    """
    Renders the licence compiliance data into html
    :param licence_data: Licence compilance data
    :param out_file: Output filename
    :return: HTML contents
    """
    template = env.get_template("licence-report.html")
    try:
        isWarn = False
        metrics = {
            "include-copyright": 0,
            "include-copyright--source": 0,
            "document-changes": 0,
            "disclose-source": 0,
            "network-use-disclose": 0,
            "same-license": 0,
            "same-license--file": 0,
            "same-license--library": 0,
            "total": 0,
        }
        for data in licence_data:
            for condition in data.get("License conditions").replace(" ", "").split(","):
                metrics[condition] += 1
            # This is total packages
            metrics["total"] += 1
        if any(v > 0 for v in metrics.values()):
            isWarn = True
        report_html = template.render(
            datas=licence_data,
            isWarn=isWarn,
            metrics=metrics,
            total=metrics["total"],
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
