# Part E — Git worktree lab

Source for every Git command: https://git-scm.com/docs/git-worktree (accessed 18 Nov 2026).
Supported `git worktree` subcommands: `add`, `list`, `lock`, `move`, `prune`, `remove`, `repair`, `unlock`.

## What has and has not been run

| Item | Status |
|---|---|
| Command sequence below | The assistant **dry-ran the same sequence in a throwaway repository** (`/tmp`, Linux, Git 2.43.0) to catch typos. It worked end to end, including the conflict. |
| Output shown in this file | **None.** I do not paste dry-run output as if it were yours. |
| Your report evidence (list output, conflict, graph) | **Student to run on the Mac and capture.** Until you do, do not claim a conflict was resolved. |

You need Git ≥ 2.28 for `git init -b main` (macOS: `git --version`; install Xcode Command Line Tools if missing).
Time: about 10 minutes.

## 0. One-time identity (skip if already set)
```bash
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
```

## 1. Initial Git setup (in the project)
```bash
cd ~/Nimbus-Campus-Helpdesk
git init -b main
printf 'Project status: baseline\n' > docs/status.md      # a shared line we will fight over later
git add .
git commit -m "Initial commit"
git status                                                # should say: nothing to commit, working tree clean
```
`.gitignore` already excludes `.venv/`, so your virtual environment is not committed.

## 2. Create three linked worktrees (one per branch)
Worktrees are created **next to** the project folder (`..`), not inside it.
```bash
git worktree add -b feature/skill-tests ../nimbus-wt-skill-tests
git worktree add -b feature/mcp-server  ../nimbus-wt-mcp-server
git worktree add -b bugfix/hook-path    ../nimbus-wt-hook-path
```
`-b <new-branch>` creates the branch and checks it out in the new directory.

## 3. List worktrees (screenshot this)
```bash
git worktree list
```
You should see four lines: the main directory on `main` plus three linked directories, each with its own branch.
(`git worktree list --porcelain` gives a script-friendly format.)

## 4. Make a separate change in each worktree
Two branches deliberately edit **line 1 of the same file** so they will conflict later.
```bash
# workstream 1 — skill tests
cd ../nimbus-wt-skill-tests
printf 'Project status: skill tests written\n' > docs/status.md
echo "# extra skill test notes" > tests/extra-notes.md
git add . && git commit -m "skill-tests: add notes and update status"

# workstream 2 — mcp server (touches a different file, so it merges cleanly)
cd ../nimbus-wt-mcp-server
echo "# MCP server notes" > docs/mcp-notes.md
git add . && git commit -m "mcp-server: add notes"

# workstream 3 — hook path fix (edits the SAME line as workstream 1)
cd ../nimbus-wt-hook-path
printf 'Project status: hook path fixed\n' > docs/status.md
git add . && git commit -m "hook-path: fix path and update status"
```

## 5. Merge, create the conflict, resolve it
Merging happens in the **main** worktree (the original project folder). `--no-ff` keeps a visible merge commit so the
graph shows the branches.
```bash
cd ~/Nimbus-Campus-Helpdesk
git merge --no-ff feature/mcp-server  -m "Merge feature/mcp-server"     # clean
git merge --no-ff feature/skill-tests -m "Merge feature/skill-tests"    # clean
git merge --no-ff bugfix/hook-path    -m "Merge bugfix/hook-path"       # CONFLICT in docs/status.md
```
The last command is **expected to stop** with a message that automatic merge failed.

Inspect the conflict (screenshot these):
```bash
git status                  # docs/status.md is listed as "both modified"
cat docs/status.md          # shows <<<<<<< HEAD, =======, >>>>>>> bugfix/hook-path markers
git diff                    # combined diff view
```
Resolve it **by deciding what the file should say**, not by letting a tool guess. Here we keep both facts:
```bash
printf 'Project status: skill tests written; hook path fixed\n' > docs/status.md
cat docs/status.md          # no markers left
git add docs/status.md
git commit --no-edit        # finishes the merge using the prepared merge message
```
Changed your mind mid-merge? `git merge --abort` returns to the state before the merge.

## 6. Show the history graph (screenshot this)
```bash
git log --oneline --graph --decorate --all
```

## 7. Safe cleanup
```bash
# Remove clean linked worktrees properly (refuses if there are uncommitted changes — that is a safety feature)
git worktree remove ../nimbus-wt-skill-tests
git worktree remove ../nimbus-wt-mcp-server

# Delete branches that are fully merged (-d refuses to delete unmerged work)
git branch -d feature/skill-tests feature/mcp-server

# Demonstrate a STALE worktree: delete a worktree folder the wrong way, then repair the bookkeeping
rm -rf ../nimbus-wt-hook-path
git worktree list              # the entry is shown as prunable
git worktree prune --dry-run -v   # preview what would be removed
git worktree prune -v             # actually clean up the stale entry
git branch -d bugfix/hook-path
git worktree list                 # only the main worktree remains
```
Rules of thumb: prefer `git worktree remove` over deleting folders by hand; avoid `--force` unless you are sure
nothing uncommitted is lost; if you *moved* a worktree folder, use `git worktree repair` instead of prune; a worktree on
removable media can be protected from pruning with `git worktree lock`.

## 8. Conceptual answers (short paragraphs for your report)

**(a) Why does Git refuse to check out the same branch in two worktrees?**
A branch is a movable pointer to a commit. If two working directories had the same branch checked out, a commit made
in one would move the pointer under the other, whose files and index would suddenly no longer match its `HEAD`, and
later commits or merges could silently overwrite work. The manual says `git worktree add` refuses when the branch is
already checked out elsewhere, and `--force` overrides this safeguard — but forcing it removes exactly that
protection. If you only need to look at a branch, use a detached HEAD (`git worktree add -d <path> <commit-ish>`).

**(b) What is shared and what is not?**
*Shared* (one copy, stored in the main repository's `.git`, reached through `$GIT_COMMON_DIR`): the commit history and
objects, branches and tags, remotes and most configuration. *Separate per worktree* (a private directory under
`.git/worktrees/<name>` plus the worktree's own folder): the checked-out files (working directory), the index (staging
area), `HEAD`, and in-progress state such as a merge. **Not Git-managed at all**, so each worktree has its own
copy: untracked and ignored files such as `node_modules/`, `.venv/`, `.env` files and build output. A new worktree
therefore needs its own dependency install (e.g. a new virtual environment) and its own environment files.

**(c) How would you clean up stale worktrees safely?**
Use `git worktree list` to see every entry (stale ones are marked prunable), `git worktree prune --dry-run -v` to
preview, then `git worktree prune -v` to delete only the leftover administrative records. For worktrees you still
have, use `git worktree remove <path>` (which refuses if there are uncommitted changes), then delete merged branches
with `git branch -d`. Unreachable data is also cleaned automatically after a time set by `gc.worktreePruneExpire`.

**(d) The CTO: "Use the built-in `/worktree-merge` command in Claude Code, which resolves conflicts across worktrees automatically, so no manual review is needed."**
- *Does the command exist as a built-in?* **UNVERIFIED, and no evidence for it.** I did not find `/worktree-merge` in the
  official Claude Code documentation I read (plugins pages, 18 Nov 2026). The only similar names I found are
  **third-party**: a community plugin that adds a namespaced `/git:worktree-merge`, and other tools with their own merge
  commands. A plugin command is not a built-in. To settle it yourself: type `/` in a Claude Code session and read
  `/help`, and search the official docs index at https://code.claude.com/docs/llms.txt for the commands reference.
  If you cannot find it there, write "not found in the official built-in command list on <date>".
- *Is "automatic, no manual review" wise?* No, whether or not such a command exists. A merge conflict means two people
  (or agents) made incompatible decisions about the same text; choosing a side needs knowledge of intent. An automatic
  resolution can silently drop a change, keep both halves of a broken function, or "fix" a conflict so that the code
  compiles but behaves wrongly — and tests may not cover it. In this project a wrong merge of the hook script could
  quietly weaken the `data/` protection. Good practice: let an AI *propose* a resolution, but a human reads the diff,
  runs the tests, and makes the commit (and keeps `git merge --abort` / `git reflog` as an escape route).
