import pytest
from pathlib import Path
from reporter.grafeas import parse, render_html
import tempfile


@pytest.fixture
def test_gr_file():
    return Path(__file__).parent / "data" / "depscan-report-java.json"


@pytest.fixture
def test_node_gr_file():
    return Path(__file__).parent / "data" / "depscan-report-nodejs.json"


def test_parse(test_gr_file):
    report_data = parse(test_gr_file)
    assert report_data


def test_render(test_gr_file):
    report_data = parse(test_gr_file)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=True) as hfile:
        html_content = render_html(report_data, hfile.name)
        assert "{{" not in html_content
        assert "UNSPECIFIED" in html_content


def test_nodejs_render(test_node_gr_file):
    report_data = parse(test_node_gr_file)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=True) as hfile:
        html_content = render_html(report_data, hfile.name)
        assert "Fix Version" in html_content
