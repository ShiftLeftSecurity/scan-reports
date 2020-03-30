VERBS_LIST = ["affects", "impacts", "impacted", "affected", "upgrade", "downgrade"]


def auto_text_highlight(text):
    """
    Automatically highlight interesting parts in the text
    :param text:
    :return:
    """
    text = text.replace("In class", "<span class='bg-light chip'>Class</span>")
    text = text.replace("In method", "<span class='bg-light chip'>Method</span>")
    text = text.replace("At ", "<span class='bg-light chip'>File</span>")
    text = text.replace("line ", "<span class='bg-light chip'>line</span>")
    text = text.replace("Commit:", "<span class='bg-light chip'>Commit</span>")
    text = text.replace("Line:", "<span class='bg-light chip'>Line</span>")
    text = text.replace("Message:", "<span class='bg-light chip'>Message</span>")
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
    text = text.lower()
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
    for link in links_list:
        if "nvd.nist.gov" in link:
            flist.append(html_link % dict(href=link, text="CVE"))
        elif "shiftleft" in link:
            flist.append(html_link % dict(href=link, text="ShiftLeft Advisory"))
        elif "github.com/advisories" in link:
            flist.append(html_link % dict(href=link, text="GitHub Advisory"))
        elif "github.com" in link:
            flist.append(html_link % dict(href=link, text="GitHub"))
        else:
            flist.append(html_link % dict(href=link, text=link))
    return "<br/>".join(flist)
