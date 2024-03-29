import logging

import jwt
import requests
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress
from rich.theme import Theme

from reporter import config as config

custom_theme = Theme({"info": "cyan", "warning": "purple4", "danger": "bold red"})
console = Console(
    log_time=False,
    log_path=False,
    theme=custom_theme,
    color_system="256",
    force_terminal=True,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            console=console, markup=True, show_path=False, enable_link_path=False
        )
    ],
)
LOG = logging.getLogger(__name__)

# Authentication headers for all API
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config.SHIFTLEFT_ACCESS_TOKEN}",
}


def get_findings_url(org_id, app_name, version, branch):
    version_suffix = f"&version={version}" if version else ""
    branch_suffix = f"&tags=branch={branch}" if branch else ""
    return f"https://app.shiftleft.io/api/v4/orgs/{org_id}/apps/{app_name}/findings?per_page=249&type=secret&type=vuln&type=extscan&include_dataflows=true{version_suffix}{branch_suffix}"


def get_all_apps(org_id):
    """Return all the apps for the given organization"""
    list_apps_url = f"https://app.shiftleft.io/api/v4/orgs/{org_id}/apps"
    r = requests.get(list_apps_url, headers=headers)
    if r.ok:
        raw_response = r.json()
        if raw_response and raw_response.get("response"):
            apps_list = raw_response.get("response")
            return apps_list
    else:
        print(f"Unable to retrieve apps list for the organization {org_id}")
        print(r.status_code, r.json())
    return None


def get_all_findings(org_id, app_name, version, branch):
    """Method to retrieve all findings"""
    with Progress(
        transient=True,
        redirect_stderr=False,
        redirect_stdout=False,
        refresh_per_second=1,
    ) as progress:
        task = progress.add_task(
            f"[green] Collecting findings for {app_name}", start=False
        )
        findings_list = []
        findings_url = get_findings_url(org_id, app_name, version, branch)
        page_available = True
        scan = {}
        while page_available:
            # print (findings_url)
            r = requests.get(findings_url, headers=headers)
            if r.ok:
                raw_response = r.json()
                if raw_response and raw_response.get("response"):
                    response = raw_response.get("response")
                    total_count = response.get("total_count")
                    scan = response.get("scan")
                    if not scan:
                        page_available = False
                        continue
                    findings = response.get("findings")
                    if not findings:
                        page_available = False
                        continue
                    findings_list += findings
                    progress.start_task(task)
                    progress.update(
                        task, total=total_count, completed=len(findings_list)
                    )
                    if raw_response.get("next_page"):
                        findings_url = raw_response.get("next_page")
                        page_available = True
                    else:
                        page_available = False
            else:
                print(f"Unable to retrieve findings for {app_name}")
                print(r.status_code, r.json())
                page_available = False
        progress.stop()
    return findings_list, scan


def get_dataflow(org_id, app_name, finding_id):
    finding_url = f"https://app.shiftleft.io/api/v4/orgs/{org_id}/apps/{app_name}/findings/{finding_id}?include_dataflows=true"
    r = requests.get(finding_url, headers=headers)
    if r.ok:
        raw_response = r.json()
        if raw_response and raw_response.get("response"):
            response = raw_response.get("response")
            details = response.get("details")
            dataflow = details.get("dataflow", {}).get("list")
            return dataflow
    else:
        print(f"Unable to retrieve dataflows for {finding_id}")
        print(r.status_code, r.json())
        return None


def extract_org_id(token):
    """
    Parses SHIFTLEFT_ACCESS_TOKEN to retrieve organization ID
    """
    try:
        decoded = jwt.decode(
            token, options={"verify_signature": False, "verify_aud": False}
        )
        orgID = decoded.get("orgID")
        if orgID:
            return orgID
    except Exception:
        print("Unable to parse the environment variable SHIFTLEFT_ACCESS_TOKEN")
    return None
