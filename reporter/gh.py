import os

from reporter.common import LOG

from github import Github


def get_user(gh):
    return gh.get_user()


def get_context():
    return {
        "repoWorkspace": os.getenv("GITHUB_WORKSPACE"),
        "runID": os.getenv("GITHUB_RUN_ID"),
        "repoFullname": os.getenv("GITHUB_REPOSITORY"),
        "triggerEvent": os.getenv("GITHUB_EVENT_NAME"),
        "apiUrl": os.getenv("GITHUB_API_URL"),
        "headRef": os.getenv("GITHUB_HEAD_REF"),
        "baseRef": os.getenv("GITHUB_BASE_REF"),
        "githubToken": os.getenv("GITHUB_TOKEN"),
        "commitSHA": os.getenv("GITHUB_SHA"),
        "workflow": os.getenv("GITHUB_WORKFLOW"),
        "home": os.getenv("HOME"),
        "actionId": os.getenv("GITHUB_ACTION"),
        "trigger": os.getenv("GITHUB_ACTOR"),
        "triggerBranchTag": os.getenv("GITHUB_REF"),
        "serverUrl": os.getenv("GITHUB_SERVER_URL"),
        "graphqlUrl": os.getenv("GITHUB_GRAPHQL_URL"),
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
    if not os.getenv("GITHUB_TOKEN"):
        LOG.info(
            "Please ensure GITHUB_TOKEN environment variable is set with permissions to read/write to pull requests"
        )
        return None
    try:
        gh = Github(os.getenv("GITHUB_TOKEN"))
        user = get_user(gh)
        if not user and os.getenv("GITHUB_SERVER_URL"):
            gh = Github(
                base_url=f"{os.getenv('GITHUB_SERVER_URL')}/api/v3",
                login_or_token=os.getenv("GITHUB_TOKEN"),
            )
            user = get_user(gh)
            if not user:
                LOG.info(
                    "Please ensure GITHUB_SERVER_URL environment variable is set to your enterprise server url. Eg: https://github.yourorg.com"
                )
        return gh
    except Exception as e:
        LOG.error(e)
        return None


def annotate(findings):
    github_context = get_context()
    g = client()
    repo = g.get_repo(github_context.get("repoFullname"))
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
                if file_locations:
                    deep_link = f"https://www.shiftleft.io/findingDetail/{f.get('app')}/{f.get('id')}"
                    body = f'{f.get("title")}\nOWASP Category: {f.get("owasp_category")}\nLink: {deep_link}'
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
