VERBS_LIST = ["affects", "impacts", "impacted", "affected", "upgrade", "downgrade"]
LINK_SOURCES = {
    "nvd.nist.gov": "CVE",
    "cve.mitre.org": "CVE",
    "shiftleft": "ShiftLeft Advisory",
    "github.com/advisories": "GitHub Advisory",
    "github.com": "GitHub",
    "npmjs.com/advisories": "NPM Advisory",
    "npmjs.com": "NPM",
    "snyk.io": "Snyk Advisory",
    "hackerone.com": "Hackerone Report",
    "secunia.com": "Secunia Report",
    "apache.org": "Apache",
    "huawei.com": "Huawei Bulletins",
    "oracle.com": "Oracle Security",
    "securityfocus.com": "SecurityFocus",
    "packetstormsecurity.com": "packet storm",
    "securitytracker.com": "SecurityTracker",
    "wooyun.org": "Wooyun",
    "osvdb.org": "OSVDB",
}


def auto_text_highlight(text):
    """
    Automatically highlight interesting parts in the text
    :param text:
    :return:
    """
    text = text.replace(
        "In class", "<span class='bg-light chip d-inline-flex mb-1'>Class</span>"
    )
    text = text.replace(
        "In method", "<span class='bg-light chip d-inline-flex mb-1'>Method</span>"
    )
    text = text.replace(
        "At ", "<span class='bg-light chip d-inline-flex mb-1'>File</span>"
    )
    text = text.replace(
        "line ", "<span class='bg-light chip d-inline-flex mb-1'>line</span>"
    )
    text = text.replace(
        "Commit:", "<span class='bg-light chip d-inline-flex mb-1'>Commit</span>"
    )
    text = text.replace(
        "Line:", "<span class='bg-light chip d-inline-flex mb-1'>Line</span>"
    )
    text = text.replace(
        "Message:", "<span class='bg-light chip d-inline-flex mb-1'>Message</span>"
    )
    text = text.replace("\n", "<br/>")
    # Boldify verbs
    for v in VERBS_LIST:
        text = text.replace(v, "<b>{}</b>".format(v))
    return text


def auto_colourize(text):
    """
    Automatically convert text to suitable colour
    :param text:
    :return:
    """
    text = text.lower().strip()
    if text == "critical":
        return "error"
    if text == "high":
        return "warning"
    if text == "medium":
        return "dark"
    if text == "low":
        return "success"
    return text


def linkify(links_list):
    """
    Method to convert a list of links into user friendly html <a> tags
    :param links_list: List of links
    :return: HTML list of links
    """
    if not len(links_list):
        return ""
    flist = []
    html_link = """<span class="text-dark chip"><i class="icon icon-link"> </i>&nbsp; <a href="%(href)s" target="_blank">%(text)s</a></span>"""
    matched = False
    for link in links_list:
        for k, v in LINK_SOURCES.items():
            if k in link:
                matched = True
                flist.append(html_link % dict(href=link, text=v))
                break
        if not matched:
            flist.append(html_link % dict(href=link, text=link))
    return "<br/>".join(flist)


def linkify_rule(ruleId, rules):
    """
    Converts ruleId in to links
    :param ruleId: Rule Id
    :param rules: Rules list from SARIF file
    :return: ruleId converted into a link
    """
    html_link = """<span class="text-dark chip"><a href="%(href)s" target="_blank">%(text)s</a></span>"""
    for rule in rules:
        if rule.get("id") == ruleId:
            text = rule.get("name")
            if not text:
                text = ruleId
            return html_link % dict(href=rule.get("helpUri"), text=text.split(":")[0])
    return ruleId


def remove_end_period(text):
    """
    Remove the period from the end of a sentence
    :param text: Text to check
    :return: Text with end period removed
    """
    if text.endswith("."):
        return text[:-1]
    return text
