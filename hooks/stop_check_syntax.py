#!/usr/bin/env python3
"""Stop Hook: 检查本次修改的 C/C++ 文件语法。

返回值约定：
  exit 0  = 通过，Claude 正常结束
  exit 2  = 有意阻止，Claude 读取 stdout JSON 并自动修复
  其他非零 = 脚本自身出错，不阻止

注意：调试信息走 stderr，stdout 专供 Claude 读 JSON。
"""

import subprocess
import sys
import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_modified_files():
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True, text=True, timeout=10,
            cwd=PROJECT_ROOT
        )
        files = result.stdout.strip().split('\n')
        c_extensions = ('.c', '.cc', '.cpp', '.h', '.hpp')
        return [f for f in files if f and any(f.endswith(ext) for ext in c_extensions)]
    except Exception as e:
        print(f"Warning: git diff failed: {e}", file=sys.stderr)
        return []


def check_syntax(filepath):
    full_path = os.path.join(PROJECT_ROOT, filepath)
    if not os.path.exists(full_path):
        return True, ""

    if filepath.endswith('.c'):
        compiler = 'gcc'
        std_flag = '-std=c11'
    else:
        compiler = 'g++'
        std_flag = '-std=c++14'

    # srsRAN includes are repo-root-relative (e.g. #include "srsue/hdr/phy/sync.h"),
    # so the repo root itself must be on the include path — this mirrors the real
    # build (see build/compile_commands.json).
    include_paths = [
        '-I', PROJECT_ROOT,
        '-I', os.path.join(PROJECT_ROOT, 'lib', 'include'),
        '-I', os.path.join(PROJECT_ROOT, 'srsue', 'hdr'),
        '-I', os.path.join(PROJECT_ROOT, 'srsenb', 'hdr'),
    ]

    build_dir = os.path.join(PROJECT_ROOT, 'build')
    if os.path.exists(build_dir):
        include_paths += ['-I', build_dir]
        # Generated headers (e.g. version/config) live under build/lib/include
        build_lib_include = os.path.join(build_dir, 'lib', 'include')
        if os.path.exists(build_lib_include):
            include_paths += ['-I', build_lib_include]

    cmd = [compiler, '-fsyntax-only', std_flag] + include_paths + [full_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stderr.strip()
    except Exception as e:
        print(f"Warning: syntax check failed for {filepath}: {e}", file=sys.stderr)
        return True, ""


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    if hook_input.get('stop_hook_active', False):
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    files = get_modified_files()
    if not files:
        print("No C/C++ files modified, skipping syntax check.", file=sys.stderr)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    errors = []
    checked = 0
    for f in files:
        ok, err_msg = check_syntax(f)
        checked += 1
        if not ok:
            errors.append({"file": f, "error": err_msg[:200]})

    if errors:
        error_detail = "\n".join(
            f"  {e['file']}: {e['error']}" for e in errors
        )
        print(f"Syntax check found {len(errors)} error(s) in {checked} file(s):", file=sys.stderr)
        print(error_detail, file=sys.stderr)

        print(json.dumps({
            "decision": "block",
            "reason": f"Syntax errors in {len(errors)} file(s). Please fix them.",
            "continue": True,
            "errors": errors
        }))
        sys.exit(2)
    else:
        print(f"Syntax check passed for {checked} file(s).", file=sys.stderr)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)


if __name__ == '__main__':
    main()
