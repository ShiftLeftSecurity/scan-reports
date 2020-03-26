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
    text = text.replace("\n", "<br/>")
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
