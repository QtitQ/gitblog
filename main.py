# -*- coding: utf-8 -*-
import argparse
import functools
import io
import os
import subprocess
from operator import contains

import requests
from github import Github
from github.Issue import Issue

MD_HEAD = """## Gitblog
My personal blog using issues and GitHub Action
"""

ANCHOR_NUMBER = 5
TOP_ISSUES_LABELS = ["Top"]
TODO_ISSUES_LABELS = ["TODO"]


def get_me(user):
    return user.get_user().login


def isMe(issue, me):
    return issue.user.login == me


def format_time(time):
    return str(time)[:10]


def login(token):
    return Github(token)


def get_repo(user: Github, repo: str):
    return user.get_repo(repo)


def parseTODO(issue):
    body = issue.body.splitlines()
    todo_undone = [l for l in body if l.startswith("- [ ] ")]
    todo_done = [l for l in body if l.startswith("- [x] ")]
    # just add info all done
    if not todo_undone:
        return f"[{issue.title}]({issue.html_url}) all done", []
    return (
        f"[{issue.title}]({issue.html_url})--{len(todo_undone)} jobs to do--{len(todo_done)} jobs done",
        todo_done + todo_undone,
    )


def get_top_issues(repo):
    return repo.get_issues(labels=TOP_ISSUES_LABELS)


def get_todo_issues(repo):
    return repo.get_issues(labels=TODO_ISSUES_LABELS)


def get_repo_labels(repo):
    return [l for l in repo.get_labels()]


def get_issues_from_label(repo, label):
    return repo.get_issues(labels=(label,))


def add_issue_info(issue, md):
    time = format_time(issue.created_at)
    md.write(f"- [{issue.title}]({issue.html_url})--{time}\n")


def add_md_todo(repo, md, me):
    todo_issues = list(get_todo_issues(repo))
    if not TODO_ISSUES_LABELS or not todo_issues:
        return
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## TODO\n")
        for issue in todo_issues:
            if isMe(issue, me):
                todo_title, todo_list = parseTODO(issue)
                md.write("TODO list from " + todo_title + "\n")
                for t in todo_list:
                    md.write(t + "\n")
                # new line
                md.write("\n")


def add_md_top(repo, md, me):
    top_issues = list(get_top_issues(repo))
    if not TOP_ISSUES_LABELS or not top_issues:
        return
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## 置顶文章\n")
        for issue in top_issues:
            if isMe(issue, me):
                add_issue_info(issue, md)


def add_md_recent(repo, md, me):
    new_five_issues = repo.get_issues()[:5]
    with open(md, "a+", encoding="utf-8") as md:
        # one the issue that only one issue and delete (pyGitHub raise an exception)
        try:
            md.write("## 最近更新\n")
            for issue in new_five_issues:
                if isMe(issue, me):
                    add_issue_info(issue, md)
        except:
            return


def add_toc(repo, me):
    the_newest_issue = repo.get_issues()[:1]
    for issue in the_newest_issue:
        if isMe(issue, me):
            try:
                split_line = "\*" * 60
                issue_body = issue.body
                if split_line in issue_body:
                    issue_body = issue_body[issue_body.find(split_line) + split_line.count("*") * 2 + 1 :]
                handle = open("tmp.tmp", "w")
                handle.write(issue_body)
                handle.close()
                body = "\n".join(
                    subprocess.check_output(f"./gh-md-toc ./tmp.tmp", shell=True).decode("utf-8").split("\n")[:-2]
                )
                issue.edit(body=body + "\n" + split_line + "\n" + issue_body)
            except Exception as e:
                pass


def add_md_header(md):
    with open(md, "w", encoding="utf-8") as md:
        md.write(MD_HEAD)


def add_md_label(repo, md, me):
    labels = get_repo_labels(repo)

    def cmp(a, b):
        b_len = len(list(repo.get_issues(labels=[b])))
        a_len = len(list(repo.get_issues(labels=[a])))
        if a_len > b_len:
            return -1
        elif a_len == b_len:
            return a_len > b_len
        else:
            return 1

    labels = sorted(labels, key=functools.cmp_to_key(cmp))
    with open(md, "a+", encoding="utf-8") as md:
        for label in labels:

            if label.name.contains("不显示_"):
                continue

            # we don't need add top label again
            if label.name in TOP_ISSUES_LABELS:
                continue

            # we don't need add todo label again
            if label.name in TODO_ISSUES_LABELS:
                continue

            issues = get_issues_from_label(repo, label)
            if issues.totalCount:
                md.write("## " + label.name + "\n")
                issues = sorted(issues, key=lambda x: x.created_at, reverse=True)
            i = 0
            for issue in issues:
                if not issue:
                    continue
                if isMe(issue, me):
                    if i == ANCHOR_NUMBER:
                        md.write("<details><summary>显示更多</summary>\n")
                        md.write("\n")
                    add_issue_info(issue, md)
                    i += 1
            if i > ANCHOR_NUMBER:
                md.write("</details>\n")
                md.write("\n")


def main(token, repo_name):
    user = login(token)
    me = get_me(user)
    repo = get_repo(user, "chaleaoch/gitblog")
    add_md_header("README.md")
    add_toc(repo, me)
    # add to readme one by one, change order here
    for func in [add_md_top, add_md_recent, add_md_label, add_md_todo]:
        func(repo, "README.md", me)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    options = parser.parse_args()
    main(options.github_token, options.repo_name)
