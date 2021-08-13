import os

from github import Github

from reporter.common import LOG


def get_user(gh):
    return gh.get_user()


def get_context():
    return {
        "repoWorkspace": os.getenv("GITHUB_WORKSPACE"),
        "runID": os.getenv("GITHUB_RUN_ID"),
        "repoFullname": os.getenv("GITHUB_REPOSITORY"),
        "triggerEvent": os.getenv("GITHUB_EVENT_NAME"),
        "headRef": os.getenv("GITHUB_HEAD_REF"),
        "baseRef": os.getenv("GITHUB_BASE_REF"),
        "githubToken": os.getenv("GITHUB_TOKEN"),
        "commitSHA": os.getenv("GITHUB_SHA"),
        "workflow": os.getenv("GITHUB_WORKFLOW"),
        "home": os.getenv("HOME"),
        "actionId": os.getenv("GITHUB_ACTION"),
        "trigger": os.getenv("GITHUB_ACTOR"),
        "triggerBranchTag": os.getenv("GITHUB_REF"),
        "triggerPath": os.getenv("GITHUB_EVENT_PATH"),
    }


def get_workflow(g, github_context):
    if not github_context.get("repoFullname") or not github_context.get("runID"):
        return
    repo = g.get_repo(github_context.get("repoFullname"))
    runID = github_context.get("runID")
    if runID and runID.isdigit():
        runID = int(runID)
    try:
        return repo.get_workflow_run(runID)
    except Exception as e:
        LOG.error(e)
        return None


def client():
    gh = None
    if not os.getenv("GITHUB_TOKEN"):
        LOG.info(
            "Please ensure GITHUB_TOKEN environment variable is set with permissions to read/write to pull requests"
        )
        return None
    try:
        # Try GitHub enterprise first
        # Variables beginning with GITHUB_ cannot be overridden
        server_url = os.getenv("GH_SERVER_URL")
        if not server_url:
            server_url = os.getenv("GITHUB_SERVER_URL")
        if server_url and server_url != "https://github.com":
            if not server_url.startswith("http"):
                server_url = "https://" + server_url
            if not server_url.endswith("/"):
                server_url = server_url + "/"
            LOG.info("Authenticating to GitHub Enterprise server: " + server_url)
            gh = Github(
                base_url=f"{server_url}api/v3",
                login_or_token=os.getenv("GITHUB_TOKEN"),
            )
        else:
            # Fallback to public GitHub
            gh = Github(os.getenv("GITHUB_TOKEN"))
        user = get_user(gh)
        if not user:
            return None
    except Exception as e:
        LOG.error(e)
        return None
    return gh


def annotate(findings, scan_info):
    github_context = get_context()
    scan_version = scan_info.get("version")
    g = client()
    if not g:
        LOG.info("Unable to authenticate with GitHub. Skipping PR annotation")
        return
    workflow_run = get_workflow(g, github_context)
    if not workflow_run:
        LOG.info("Unable to find the workflow run for this invocation")
        return
    pull_requests = workflow_run.pull_requests
    if not pull_requests:
        LOG.info("No Pull Requests are associated with this workflow run")
        return
    for pr in pull_requests:
        commits = pr.get_commits()
        last_commit = None
        changed_files = None
        if commits:
            last_commit = commits.reversed[0]
        elif github_context.get("commitSHA"):
            last_commit = g.get_commit(github_context.get("commitSHA"))
        if not last_commit:
            continue
        changed_files = [f.filename for f in last_commit.files]
        if findings:
            for f in findings:
                details = f.get("details")
                file_locations = details.get("file_locations")
                owasp_category = f.get("owasp_category")
                severity = f.get("severity")
                version_first_seen = f.get("version_first_seen")
                # Ignore legacy findings
                if version_first_seen != scan_version:
                    continue
                # Ignore sensitive data exposure
                if "a3-" in owasp_category or severity in ("INFO"):
                    continue
                if file_locations:
                    deep_link = f"https://www.shiftleft.io/findingDetail/{f.get('app')}/{f.get('id')}"
                    body = f'{f.get("title")}\n**Severity:** {severity}\n**OWASP Category:** {owasp_category}\n\n**Finding Link:** {deep_link}'
                    source_loc = file_locations[0].split(":")
                    source_path = source_loc[0]
                    source_line = int(source_loc[-1]) if source_loc[-1].isdigit() else 0
                    sink_loc = file_locations[-1].split(":")
                    sink_path = sink_loc[0]
                    sink_line = int(sink_loc[-1]) if sink_loc[-1].isdigit() else 0
                    # Automatically prefix src/main/java or src/main/scala
                    if source_path.endswith(".java") and not source_path.startswith(
                        "src"
                    ):
                        source_path = "src/main/java/" + source_path
                    if source_path.endswith(".scala") and not source_path.startswith(
                        "src"
                    ):
                        source_path = "src/main/scala/" + source_path
                    if sink_path.endswith(".java") and not sink_path.startswith("src"):
                        sink_path = "src/main/java/" + sink_path
                    if sink_path.endswith(".scala") and not sink_path.startswith("src"):
                        sink_path = "src/main/scala/" + sink_path
                    if source_path in changed_files:
                        last_commit.create_comment(body, source_line, source_path)
                        LOG.debug(f"Added comment to {source_path} {source_line}")
                    if sink_path != source_path and sink_line in changed_files:
                        last_commit.create_comment(body, sink_line, sink_path)
                        LOG.debug(f"Added comment to {sink_path} {sink_line}")
