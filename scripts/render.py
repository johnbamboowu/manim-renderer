#!/usr/bin/env python3
"""
render.py — 本地 Manim 渲染辅助脚本

功能：
1. 检查 scenes/ 目录下的 .py 文件
2. git add + commit + push 触发 GitHub Actions
3. 轮询等待 Actions 完成
4. 下载渲染好的 MP4 artifact

用法：
    python scripts/render.py                    # 渲染所有场景
    python scripts/render.py scenes/example.py  # 渲染指定文件
    python scripts/render.py --quick            # 快速模式（ql 画质）
"""

import os
import sys
import time
import json
import subprocess
import urllib.request
from pathlib import Path

# ============ 配置 ============
REPO = "johnbamboowu/manim-renderer"
BRANCH = "main"
POLL_INTERVAL = 15  # 秒
MAX_WAIT = 1800     # 30 分钟超时
OUTPUT_DIR = Path("output")


def get_token():
    """从 git-credentials 读取 GitHub token"""
    cred_path = Path.home() / ".git-credentials"
    if not cred_path.exists():
        print("❌ 找不到 ~/.git-credentials")
        sys.exit(1)
    
    import re
    content = cred_path.read_text()
    for line in content.strip().splitlines():
        if "johnbamboowu" in line and "github.com" in line:
            m = re.match(r"https://[^:]+:([^@]+)@github\.com", line)
            if m:
                return m.group(1)
    
    print("❌ 找不到 GitHub token")
    sys.exit(1)


def github_api(endpoint, token, method="GET", data=None):
    """调用 GitHub API"""
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    if data:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ GitHub API 错误 {e.code}: {body[:200]}")
        return None


def push_changes(files=None):
    """git add, commit, push"""
    print("📝 提交代码...")
    
    # git add
    if files:
        for f in files:
            subprocess.run(["git", "add", f], check=True)
    else:
        subprocess.run(["git", "add", "-A"], check=True)
    
    # 检查是否有变更
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode == 0:
        print("ℹ️  没有变更需要提交")
        return False
    
    # commit
    ts = time.strftime("%Y-%m-%d %H:%M")
    subprocess.run(["git", "commit", "-m", f"render: update scenes [{ts}]"], check=True)
    
    # push
    print("🚀 推送到 GitHub...")
    subprocess.run(["git", "push", "origin", BRANCH], check=True)
    print("✅ 推送成功！")
    return True


def wait_for_actions(token, sha=None):
    """等待最近的 workflow run 完成"""
    print("⏳ 等待 GitHub Actions 完成...")
    
    start = time.time()
    run_id = None
    
    while time.time() - start < MAX_WAIT:
        # 获取最近的 workflow runs
        runs = github_api(f"/repos/{REPO}/actions/runs?branch={BRANCH}&per_page=3", token)
        if not runs or not runs.get("workflow_runs"):
            print("  暂未发现 workflow run，等待中...")
            time.sleep(POLL_INTERVAL)
            continue
        
        latest = runs["workflow_runs"][0]
        status = latest["status"]
        conclusion = latest.get("conclusion")
        run_id = latest["id"]
        
        elapsed = int(time.time() - start)
        if status == "completed":
            if conclusion == "success":
                print(f"\n✅ Actions 渲染完成！（耗时 {elapsed}s）")
                return latest
            else:
                print(f"\n❌ Actions 失败: {conclusion}")
                print(f"   详情: {latest.get('html_url', '')}")
                return latest
        
        print(f"  [{elapsed}s] 状态: {status}...", end="\r")
        time.sleep(POLL_INTERVAL)
    
    print(f"\n⏰ 超时（{MAX_WAIT}s）")
    return None


def download_artifact(token, run_id):
    """下载最新的 artifact"""
    print("📥 下载渲染结果...")
    
    artifacts = github_api(f"/repos/{REPO}/actions/runs/{run_id}/artifacts", token)
    if not artifacts or not artifacts.get("artifacts"):
        print("⚠️  没有找到 artifact")
        return
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    for art in artifacts["artifacts"]:
        name = art["name"]
        size = art["size_in_bytes"]
        print(f"  📦 {name} ({size / 1024:.1f} KB)")
        
        # 下载 zip
        download_url = f"https://api.github.com/repos/{REPO}/actions/artifacts/{art['id']}/zip"
        req = urllib.request.Request(download_url, headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        })
        
        resp = urllib.request.urlopen(req)
        zip_path = OUTPUT_DIR / f"{name}.zip"
        with open(zip_path, "wb") as f:
            f.write(resp.read())
        
        # 解压
        subprocess.run(["unzip", "-o", str(zip_path), "-d", str(OUTPUT_DIR)], 
                      capture_output=True)
        zip_path.unlink()  # 删除 zip
        
        # 列出下载的文件
        for mp4 in OUTPUT_DIR.rglob("*.mp4"):
            print(f"  🎬 {mp4}")
        for gif in OUTPUT_DIR.rglob("*.gif"):
            print(f"  🎞️  {gif}")
    
    print("✅ 下载完成！")


def main():
    files = None
    quick_mode = False
    
    args = sys.argv[1:]
    if "--quick" in args:
        quick_mode = True
        args.remove("--quick")
    if args:
        files = args
    
    token = get_token()
    print(f"🔑 GitHub token 已加载")
    
    # 检查仓库
    repo_info = github_api(f"/repos/{REPO}", token)
    if not repo_info:
        print(f"❌ 仓库 {REPO} 不存在")
        sys.exit(1)
    print(f"📦 仓库: {repo_info['html_url']}")
    
    # Push
    pushed = push_changes(files)
    
    if not pushed:
        print("ℹ️  没有新变更，跳过 Actions")
        return
    
    # 等待 Actions
    result = wait_for_actions(token)
    if not result:
        print("⚠️  请手动检查: https://github.com/" + REPO + "/actions")
        return
    
    # 下载 artifact
    download_artifact(token, result["id"])
    
    # 输出链接
    print(f"\n🔗 查看 Actions: {result.get('html_url', '')}")
    print(f"📂 本地输出: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()
