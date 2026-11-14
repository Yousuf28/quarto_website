---
title: "fd command"
author: "Yousuf Ali"
date: "2026-11-13"
categories: [fd, terminal, bash, rust,linux]
format: html
---
# fd: The File Finder You'll Actually Enjoy Using

*Install it on macOS and Windows, then bend it to your will with fzf, awk, cut, and sort.*

---

## Table of contents

1. [Why fd instead of find](#why-fd-instead-of-find)
2. [Installing fd](#installing-fd)
   - [macOS](#macos)
   - [Windows](#windows)
   - [Verify the install](#verify-the-install)
3. [The mental model](#the-mental-model)
4. [Finding files](#finding-files)
5. [Finding directories](#finding-directories)
6. [Acting on results: exec and xargs](#acting-on-results-exec-and-xargs)
7. [fd + fzf: the pairing that ruins other file pickers for you](#fd--fzf-the-pairing-that-ruins-other-file-pickers-for-you)
8. [fd + awk](#fd--awk)
9. [fd + cut](#fd--cut)
10. [fd + sort and uniq](#fd--sort-and-uniq)
11. [fd with everything else](#fd-with-everything-else)
12. [Generating Markdown files](#generating-markdown-files)
13. [Windows and PowerShell notes](#windows-and-powershell-notes)
14. [Cheat sheet](#cheat-sheet)

---

## Why fd instead of find

`find` is powerful, portable, and almost universally installed. It is also exhausting to type:

```bash
# find: files modified in the last 7 days, excluding node_modules
find . -type f -mtime -7 -not -path '*/node_modules/*'

# fd: same thing
fd -t f --changed-within 7d -E node_modules
```

`fd` is a fast, Rust-based alternative to `find` with opinionated defaults that match what people actually want 90% of the time:

| Behavior | `find` | `fd` |
| --- | --- | --- |
| Syntax | `find . -iname '*pattern*'` | `fd pattern` |
| Case sensitivity | Case-sensitive by default | Smart case (lowercase = insensitive) |
| Hidden files | Included | Skipped |
| `.gitignore` | Ignored | Respected automatically |
| Regex | `-regex` with full-path matching | Pattern is a regex by default, matched on filename |
| Parallel execution | `-exec ... {} +` | `-x` and `-X` run in parallel |
| Output color | None | Colorized, like `ls` |
| Empty pattern | Error | Lists everything |

The big win is not raw speed (though it is fast) — it's that the defaults are right. You type less, and you don't accidentally grep through `node_modules`.

Two defaults are worth remembering, because they explain most "where did my file go?" moments:

- **Hidden entries are skipped.** Add `-H` (or `-u` to also ignore `.gitignore`).
- **`.gitignore` is respected.** Add `-I`, or `-u` for both.

---

## Installing fd

The binary is called `fd` on macOS and Windows. (On Debian/Ubuntu it is packaged as `fd-find` and installed as `fdfind` — see the note at the end of this section.)

### macOS

**Homebrew** (recommended):

```bash
brew install fd
```

**MacPorts:**

```bash
sudo port install fd
```

**Cargo**, if you already have a Rust toolchain:

```bash
cargo install fd-find
```

**Prebuilt binary:** download the macOS archive from the [releases page](https://github.com/sharkdp/fd/releases), unpack it, and move `fd` somewhere on your `PATH`:

```bash
mkdir -p ~/.local/bin
mv ~/Downloads/fd ~/.local/bin/
# make sure ~/.local/bin is on PATH (add to ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

On Apple Silicon, `brew install fd` is the least friction. It also gives you shell completions and man pages for free.

### Windows

`fd` is a single static `.exe`, so any of these work.

**winget** (built into Windows 10/11):

```powershell
winget install sharkdp.fd
```

**Scoop:**

```powershell
scoop install fd
```

**Chocolatey** (admin PowerShell):

```powershell
choco install fd
```

**Cargo:**

```powershell
cargo install fd-find
```

**WSL / Git Bash:** if you live in a Unix-like shell on Windows, use the Linux instructions. In WSL:

```bash
sudo apt install fd-find
```

**Manual:** grab `fd-v*-x86_64-pc-windows-msvc.zip` from the releases page, extract `fd.exe`, and put it in a folder that is on your `PATH` (for example `C:\Tools\fd`).

> **The `fdfind` gotcha:** Debian and Ubuntu package the binary as `fdfind` to avoid a name clash with another package. If you're on those distros, either call `fdfind` directly or add an alias:
>
> ```bash
> alias fd='fdfind'
> ```
>
> Every example in this post uses `fd`.

### Verify the install

```bash
fd --version
# fd 10.5.0
```

If the command is not found on Windows, close and reopen your terminal so the updated `PATH` is picked up.

Optional but nice: generate shell completions.

```bash
# zsh
fd --gen-completions zsh > "${fpath[1]}/_fd"

# bash
fd --gen-completions bash | sudo tee /etc/bash_completion.d/fd > /dev/null

# fish
fd --gen-completions fish > ~/.config/fish/completions/fd.fish

# PowerShell
fd --gen-completions powershell | Out-File -Append $PROFILE
```

---

## The mental model

Almost every `fd` invocation is:

```bash
fd [options] <pattern> [path...]
```

- **`pattern`** is a regular expression matched against the **filename** (not the full path, unless you pass `-p`).
- **`path`** is where to search. Omit it and `fd` searches the current directory recursively.
- If you omit the pattern too, it matches everything.

```bash
fd                      # every file and directory below .
fd config               # names containing "config"
fd '^test_' tests/      # names starting with "test_" inside tests/
fd . src                # everything under src
```

A few notes that save time later:

- Smart case: `fd readme` is case-insensitive, `fd Readme` is case-sensitive. Force either with `-i` / `-s`.
- `-F` treats the pattern as a literal string. `-g` treats it as a glob. `-p` matches the full path instead of just the name.
- Directories are printed with a trailing `/`, which is handy visually but matters when you pipe through `cut`.

---

## Finding files

### The basics

```bash
# all Markdown files
fd -e md

# several extensions at once
fd -e jpg -e jpeg -e png

# names containing "config"
fd config

# exact-ish: names starting with "test_" and ending in .py
fd '^test_.*\.py$'

# literal string (no regex escaping)
fd -F 'foo[1].txt'

# glob syntax
fd -g '*.tsx'
fd -g 'src/**/*.css'

# match against the full path, not just the filename
fd -p 'components/.*\.tsx$'

# force case-insensitive / case-sensitive
fd -i readme
fd -s Readme

# PID files anywhere under /var
fd -p '\.pid$' /var
```

### Hidden files and ignored files

This is the number one source of confusion, so learn these three flags:

```bash
fd -H                 # include hidden files and directories
fd -I                 # ignore .gitignore / .ignore / .fdignore rules
fd -u                 # both (-H -I); "unrestricted"
```

Examples:

```bash
fd -H .env                    # find .env files
fd -u -t d cache              # cache dirs, even if gitignored
fd -H -e json                 # hidden JSON files, still respecting gitignore
fd -I -e log                  # logs that may be gitignored
```

One nuance: by default, `fd` only honors `.gitignore` when it detects a git repository. If you want gitignore rules applied outside a repo:

```bash
fd --no-require-git -e js
```

### Excluding things

`-E` accepts a glob and beats every other ignore rule:

```bash
fd -E node_modules -E dist -E target
fd -e js -E '*.min.js'
fd -t f -E '.git' -E 'vendor'
```

`--prune` is different: it stops descending into directories that match your search pattern.

```bash
# do not walk into any directory called "build"
fd -t d --prune build
```

### Filtering by type

```bash
fd -t f        # regular files
fd -t d        # directories
fd -t l        # symlinks
fd -t x        # executables
fd -t e        # empty files and directories
fd -t s        # sockets
fd -t p        # named pipes

# combine types
fd -t f -t l               # files and symlinks
fd -t e -t d               # empty directories
fd -t e -t f               # empty files
```

### Filtering by size, time, and owner

```bash
# files larger than 100 MB
fd -t f --size +100M

# files smaller than 10 KB
fd -t f --size -10k

# exactly 1 MiB (binary units: ki, mi, gi, ti)
fd -t f --size 1mi

# modified within the last 3 days
fd -t f --changed-within 3d

# modified before a date
fd -t f --changed-before 2025-01-01

# older than two weeks
fd -t f --changed-before 2weeks

# files owned by a user or group
fd -t f --owner deploy
fd -t f --owner '!root'
```

### Depth control

```bash
fd -d 1                # only the current directory
fd -d 2                # two levels down
fd --min-depth 2       # skip the top level
fd --exact-depth 3     # only level 3
```

### Stopping early, checking existence, listing details

```bash
fd -1 package.json             # stop after the first match
fd --max-results 20 -e log     # cap the output
fd -q '\.env$' && echo "found" # no output, exit code only
fd -l -e zip                   # ls -l style details
fd -L -t l                     # follow symlinks while walking
```

`-l` is handy because it shows sizes, timestamps, and symlink targets:

```bash
fd -l --size +50M -t f
```

---

## Finding directories

Directories are where `fd` shines, because `find . -type d -name ...` is a lot of typing.

```bash
# every directory
fd -t d

# only top-level project folders
fd -t d -d 1

# just the names, no trailing slash noise
fd -t d -d 1 --format '{/}'

# directories named "src", excluding noise
fd -t d src -E node_modules -E .git

# nested src folders, e.g. packages/*/src
fd -t d -p 'packages/[^/]+/src$'

# empty directories (safe to delete after review)
fd -t e -t d

# recently changed directories
fd -t d --changed-within 1d

# hidden directories, e.g. .config folders
fd -t d -H -d 2

# find the directory containing a file
fd -p 'src/main\.rs$' --format '{//}'
```

That last one is a great example of why `--format` exists: `{//}` gives you the parent directory only.

A practical one — list the top-level folders in a monorepo with their file counts:

```bash
for d in $(fd -t d -d 1); do
  printf '%-30s %s\n' "$d" "$(fd -t f . "$d" | wc -l)"
done
```

Or without a loop, using `awk` (see [fd + awk](#fd--awk)):

```bash
fd -t f | awk -F/ 'NF>1 {print $1}' | sort | uniq -c | sort -rn
```

---

## Acting on results: exec and xargs

`fd` does not need `xargs` for most jobs. It has two execution modes:

| Flag | Behavior | Runs |
| --- | --- | --- |
| `-x`, `--exec` | One command **per result**, in parallel | Many times |
| `-X`, `--exec-batch` | One command with **all results** as arguments | Once (possibly batched) |

### Placeholders

| Placeholder | Expands to | Example path | Result |
| --- | --- | --- | --- |
| `{}` | Full path | `src/app.tsx` | `src/app.tsx` |
| `{/}` | Basename | `src/app.tsx` | `app.tsx` |
| `{//}` | Parent directory | `src/app.tsx` | `src` |
| `{.}` | Path without extension | `src/app.tsx` | `src/app` |
| `{/.}` | Basename without extension | `src/app.tsx` | `app` |

If you don't include a placeholder, `{}` is appended automatically.

### Examples

```bash
# line counts for every Markdown file (parallel)
fd -e md -x wc -l

# one wc call for all files, plus a total line
fd -e md -X wc -l

# unzip each archive into a folder named after the archive
fd -e zip -x unzip {} -d {/.}

# convert JPG to WebP next to the original
fd -e jpg -x magick {} {.}.webp

# format only changed TypeScript files
fd -e ts --changed-within 2d -x prettier --write {}

# gofmt all Go files in one shot
fd -e go -X gofmt -w

# make every shell script executable
fd -t f -e sh -x chmod +x

# find old logs, print the delete command first (dry run)
fd -e log --changed-before 30d -x echo rm {}

# then actually delete
fd -e log --changed-before 30d -x rm {}

# copy every PNG into one folder (careful with duplicate names)
fd -e png -x cp {} ~/Pictures/all/

# one shell per file, with proper quoting
fd -e png -x sh -c 'cp "$1" "$HOME/backup/$(basename "$1")"' _ {}
```

Two important behaviors:

1. **Parallelism means unordered output.** Use `-j 1` (or `--threads 1`) if order matters.
2. **`-x` and `-X` prefix paths with `./`.** That prevents a filename starting with `-` from being read as a flag. Strip it with `--strip-cwd-prefix`:

```bash
fd -e md -x wc -l | sort -k1 -n
#        0 ./README.md
#       12 ./docs/intro.md

fd -e md --strip-cwd-prefix -x wc -l | sort -k1 -n
#        0 README.md
#       12 docs/intro.md
```

### Piping to `xargs`

Use `-0` whenever filenames might contain spaces or newlines:

```bash
fd -0 -e md | xargs -0 wc -l
fd -0 -t f -e png | xargs -0 -n 20 pngquant --force --ext .png
fd -0 -e log | xargs -0 -I{} sh -c 'gzip "{}"'
```

`xargs` is still worth knowing for tools that read from stdin or for splitting work into batches (`-n`, `-P`). But if `-x`/`-X` can do the job, prefer them: they handle quoting correctly and skip the extra process.

---

## fd + fzf: the pairing that ruins other file pickers for you

[fzf](https://github.com/junegunn/fzf) is a fuzzy filter for any list. `fd` produces a great list. Together they replace most GUI file pickers.

Install fzf:

```bash
# macOS
brew install fzf

# Windows
winget install junegunn.fzf
# or: scoop install fzf
```

### The one-liner you'll use daily

```bash
fd | fzf
```

That's it. Start typing part of a path; fzf narrows the list.

### Preview files before opening

```bash
# plain preview
fd -t f | fzf --preview 'head -60 {}'

# with bat, if installed
fd -t f | fzf --preview 'bat --style=numbers --color=always --line-range=:80 {}'

# works with or without bat
fd -t f | fzf --preview 'bat --color=always {} 2>/dev/null || head -60 {}'
```

### Preview directories

```bash
fd -t d | fzf --preview 'ls -la {}'
fd -t d -d 2 | fzf --height 50% --preview 'eza --tree --level=2 {} 2>/dev/null || ls -la {}'
```

### Open the selection in your editor

```bash
# single file
vim "$(fd -t f -e md | fzf)"

# VS Code
code "$(fd -t f -e tsx | fzf)"

# multi-select, robust against spaces in names
fd -t f -e tsx | fzf -m --print0 | xargs -0 code

# multi-select into vim
fd -t f -e md | fzf -m --print0 | xargs -0 vim
```

### Jump to a directory

Add this to `~/.zshrc` or `~/.bashrc`:

```bash
fcd() {
  local dir
  dir=$(fd -t d -H --exclude .git | fzf --height 40% --reverse) || return
  cd "$dir" || return
}
```

Then:

```bash
fcd
```

For old-school Ctrl+T / Alt+C behavior, fzf's shell integration already provides file and directory picking. Modern fzf uses its built-in walker, but you can hand it `fd` explicitly when you want filtering:

```bash
# ~/.zshrc
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
```

### Narrow the list before fzf even opens

The real power move is using `fd`'s filters to make the fuzzy list tiny:

```bash
# only files changed this week
fd -t f --changed-within 7d | fzf --preview 'bat --color=always {}'

# only files larger than 10 MB
fd -t f --size +10M | fzf

# only images, multi-select, copy picks into a folder
fd -t f -e jpg -e png -e webp |
  fzf -m --print0 |
  xargs -0 -I{} cp "{}" ~/Pictures/picks/

# only Markdown in docs/, open the chosen one in $PAGER
fd -e md . docs | fzf --preview 'bat --color=always {}' | xargs -r less

# pick a branch's changed files (requires git)
git diff --name-only | fzf --preview 'git diff -- {}'
```

### A reusable "pick a file" function

```bash
# usage: fe [pattern]
fe() {
  local file
  file=$(fd -t f -H "${1:-}" | fzf --height 40% --reverse \
    --preview 'bat --color=always --line-range=:80 {} 2>/dev/null || head -40 {}') || return
  ${EDITOR:-vim} "$file"
}

# usage: fcp — pick one file, copy its path to the clipboard (macOS)
fcp() {
  fd -t f | fzf | pbcopy
}

# usage: fcdp — pick a file, jump to its directory
fcdp() {
  local f
  f=$(fd -t f | fzf) && cd "$(dirname "$f")"
}
```

### fzf on Windows

Same idea in PowerShell:

```powershell
fd | fzf
fd -e md | fzf --preview 'Get-Content {} -TotalCount 40'
```

If you use Git Bash or WSL, all of the Unix examples work unchanged.

---

## fd + awk

`awk` turns a list of paths into answers: counts, sizes, depths, reports.

### Count files by extension

```bash
fd -t f | awk -F. 'NF>1 {print $NF}' | sort | uniq -c | sort -rn
```

Output:

```text
   34 tsx
   21 ts
    8 json
    3 md
```

### Total size of all matching files

`stat` differs by OS. On macOS:

```bash
fd -t f -e mp4 -x stat -f%z | awk '{sum += $1} END {printf "%.1f MB\n", sum/1048576}'
```

On Linux:

```bash
fd -t f -e mp4 -x stat -c%s | awk '{sum += $1} END {printf "%.1f MB\n", sum/1048576}'
```

### Files per directory

```bash
fd -t f |
  awk -F/ 'NF>1 {d=$0; sub("/[^/]+$", "", d); c[d]++}
           END {for (d in c) print c[d], d}' |
  sort -rn |
  head -10
```

Output:

```text
214 src/components
 88 src/utils
 41 tests
```

### Directory depth distribution

```bash
fd -t f | awk -F/ '{print NF-1}' | sort -n | uniq -c
```

```text
  120 0    # top-level files
  340 1
  210 2
   45 3
```

### Find the deepest paths

```bash
fd -t f | awk -F/ '{print NF-1, $0}' | sort -rn | head -5
```

### Report duplicate basenames

```bash
fd -t f -e png | awk -F/ '{print $NF}' | sort | uniq -d
```

### Turn paths into a CSV

```bash
fd -t f -e mp4 -x stat -f '%N,%z' | awk -F, '{printf "%s,%d\n", $1, $2}' > videos.csv
```

### Rewrite paths (preview a rename)

```bash
fd -e jpeg | awk '{print $0 " -> " $0 ".bak"}'
```

Then pipe the pairs into `while read` if you want to actually rename:

```bash
fd -e jpeg | awk '{print $0 " " $0 ".bak"}' | while read -r from to; do
  mv -- "$from" "$to"
done
```

### Check that a field exists

```bash
# files whose path has at least 3 segments (i.e. under a subdirectory)
fd -t f | awk -F/ 'NF>=3'
```

> **Watch out:** paths with spaces break naive `awk '{print $2}'` field access. If spaces are possible, use a delimiter that can't appear in paths (like `-0` + `xargs`, or `stat` with a tab separator), or parse from the left with `-F/` as above.

---

## fd + cut

`cut` is the blunt instrument for fixed-position fields: split on a delimiter, take a field. That makes it excellent for path segments and a poor fit for extensions (a name like `Button.test.tsx` has more than one dot). Use `awk` for the extension case; reach for `cut` when you're already slicing paths.

### Tally by top-level directory

```bash
fd -t f | cut -d/ -f1 | sort | uniq -c | sort -rn
```

Note that top-level *files* also show up, each as its own single-item group. Filter to paths with a slash first:

```bash
fd -t f | grep / | cut -d/ -f1 | sort | uniq -c | sort -rn
```

### Unique second-level segments

```bash
fd -t f -e tsx | cut -d/ -f2 | sort -u
```

### List project folders without the trailing slash

`fd -t d` prints `src/`, so `cut -d/ -f1` already strips the slash:

```bash
fd -t d -d 1 | cut -d/ -f1
```

### Extract extensions from a known-safe set of names

```bash
fd -t f -d 1 | cut -d. -f2 | sort -u
```

### Strip a prefix from every path

```bash
fd -t f . src | cut -c5-
```

### Basenames only

```bash
fd -t f | rev | cut -d/ -f1 | rev
fd -t f | sed 's|.*/||'            # simpler, same result
fd -t f --format '{/}'             # best: no external tools
```

That last line is the lesson: if `fd` can already do it with `--format`, you don't need `cut`. Use `cut` when you're already in a pipeline with other tools.

---

## fd + sort and uniq

### Sort paths alphabetically

```bash
fd -t f | sort
fd -t f | sort -r
```

### Largest files first

```bash
# macOS / Linux (du -k is portable enough)
fd -t f | xargs du -k | sort -rn | head -10
```

Using `-x`:

```bash
fd -t f -x du -k | sort -rn | head -10
```

### Most recently modified files

```bash
# macOS
fd -t f -x stat -f '%m %N' | sort -rn | head -10

# Linux
fd -t f -x stat -c '%Y %n' | sort -rn | head -10
```

Human-readable dates, macOS:

```bash
fd -t f -x stat -f '%Sm %N' | sort -r | head -10
```

### Largest files with human-readable sizes

```bash
fd -t f -x du -h | sort -rh | head -20
```

Note: `sort -h` is GNU and also available in modern macOS `sort`. If yours complains, sort by kilobytes instead.

### Files with the most lines

```bash
fd -e ts -e tsx -x wc -l | sort -k1 -nr | head -10
```

### Duplicate extensions, sorted by frequency

```bash
fd -t f | awk -F. 'NF>1 {print $NF}' | sort | uniq -c | sort -rn
```

### Files that exist in two trees

```bash
comm -12 \
  <(fd -t f . v1 | sed 's|^v1/||' | sort) \
  <(fd -t f . v2 | sed 's|^v2/||' | sort)
```

### Count total files quickly

```bash
fd -t f | wc -l
fd -t f -e java | wc -l
```

---

## fd with everything else

### grep / ripgrep

```bash
# grep inside every Python file
fd -e py -x grep -n 'TODO' {}

# ripgrep already respects gitignore, but fd lets you pre-filter
fd -e ts -e tsx -0 | xargs -0 rg -n 'deprecated'
```

### sed

```bash
# macOS requires an empty backup suffix for -i
fd -e md -X sed -i '' 's/old-domain.com/new-domain.com/g'

# GNU sed
fd -e md -X sed -i 's/old-domain.com/new-domain.com/g'
```

### tar

```bash
# archive every log file, reading the list from stdin
fd -e log | tar -czf logs.tar.gz -T -

# safer with null separators
fd -0 -e log | tar -czf logs.tar.gz --null -T -
```

### rsync

```bash
fd -t f -e jpg --changed-within 7d |
  rsync -av --files-from=- . /Volumes/Backup/photos/
```

### GNU parallel

```bash
fd -e png | parallel 'convert {} {.}.webp'
fd -e mp4 | parallel -j 4 'ffmpeg -i {} -vf scale=1280:-2 {.}-720p.mp4'
```

### git

```bash
# stage every changed TypeScript file
fd -e ts --changed-within 1d | xargs git add

# find files that are tracked but deleted
comm -13 <(git ls-files | sort) <(fd -t f | sort)
```

### open / xdg-open / start

```bash
# macOS
fd -e pdf -1 | xargs open

# Linux
fd -e pdf -1 | xargs xdg-open

# Windows PowerShell
fd -e pdf -1 | ForEach-Object { Start-Process $_ }
```

### wc for a project total

```bash
fd -e py -X wc -l | tail -1
```

### chmod / cleanup

```bash
# dry run, then execute
fd -t f -e sh -x echo chmod +x {}
fd -t f -e sh -x chmod +x {}

fd -t e -t f -x echo rm {}
```

### Build a `.gitignore`-style exclude list from results

```bash
fd -t d -d 1 | sed 's|/$||' | sed 's|^|/|' > .fdignore
```

---

## Generating Markdown files

This is where `fd` stops being a search tool and becomes a small static-site generator.

### 1. A repository index

```bash
{
  echo "# Repository index"
  echo
  echo "Generated on $(date +%Y-%m-%d)"
  echo
  fd -t f -E node_modules -E .git | sort | sed 's|^|- [ ] |'
} > INDEX.md
```

Result:

```markdown
# Repository index

Generated on 2026-11-14

- [ ] README.md
- [ ] package.json
- [ ] src/app.tsx
- [ ] src/components/Button.tsx
```

Swap `- [ ]` for `- [x]` to make a checklist, or use plain `-` for a list.

### 2. A table of files with line counts

```bash
{
  echo "| File | Lines |"
  echo "| --- | ---: |"
  fd -t f -e tsx -x wc -l |
    awk '{gsub(/^\.\//, "", $2); printf "| `%s` | %d |\n", $2, $1}'
} > TSX-TABLE.md
```

Result:

```markdown
| File | Lines |
| --- | ---: |
| `src/app.tsx` | 0 |
| `src/components/Button.tsx` | 0 |
```

If filenames may contain spaces, use `fd --format` to produce the path and `stat` for the metric instead, or quote the field with a separator that cannot appear in a path.

### 3. A Markdown image gallery

```bash
{
  echo "# Photo gallery"
  echo
  fd -t f -e jpg -e jpeg -e png -e webp | sort | sed 's|.*|![](<&>)|'
} > GALLERY.md
```

The `<...>` around the path is valid Markdown and survives spaces in filenames.

### 4. A table of contents for a docs folder

```bash
{
  echo "# Docs"
  echo
  fd -t f -e md . docs | sort | sed -E 's|^docs/(.*)\.md$|- [\1](\1.md)|'
} > docs/README.md
```

### 5. A file inventory with sizes

```bash
{
  echo "| Path | Size | Modified |"
  echo "| --- | ---: | --- |"
  fd -t f -x stat -f '%N|%z|%Sm' |
    sed 's|^\./||' |
    awk -F'|' '{printf "| `%s` | %s B | %s |\n", $1, $2, $3}'
} > INVENTORY.md
```

(Linux: replace `stat -f '%N|%z|%Sm'` with `stat -c '%n|%s|%y'`.)

### 6. A per-directory README stub

```bash
fd -t d -d 1 |
  while read -r dir; do
    name=$(basename "$dir")
    [ -f "$dir/README.md" ] && continue
    printf '# %s\n\nFiles:\n\n' "$name" > "$dir/README.md"
    fd -t f . "$dir" | sed 's|^|- |' >> "$dir/README.md"
  done
```

### 7. A "missing tests" report

Pair `fd` with `comm` and emit a Markdown table:

```bash
{
  echo "| Source | Test |"
  echo "| --- | --- |"
  fd -t f -e ts . src | while read -r src; do
    test_file="tests/$(basename "${src%.ts}").test.ts"
    [ -f "$test_file" ] || printf '| `%s` | missing |\n' "$src"
  done
} > MISSING-TESTS.md
```

### 8. A quick Markdown link dump for a PR description

```bash
fd -t f -e md --changed-within 1d |
  sort |
  sed -E 's|^(.*)/([^/]+)\.md$|- [\2](\1/\2.md)|'
```

---

## Windows and PowerShell notes

`fd` itself is cross-platform. The surrounding toolchain is not.

### Paths

Windows prints `\` separators by default. Normalize when you plan to pipe into Unix tools:

```powershell
fd -e tsx --path-separator / src
```

`--path-separator /` is also useful when generating Markdown links on Windows.

### Native PowerShell replacements

| Unix pipeline | PowerShell |
| --- | --- |
| `fd \| head -10` | `fd \| Select-Object -First 10` |
| `fd \| sort` | `fd \| Sort-Object` |
| `fd \| wc -l` | `fd \| Measure-Object -Line` |
| `fd \| xargs rm` | `fd \| ForEach-Object { Remove-Item $_ }` |
| `fd \| grep foo` | `fd \| Select-String foo` |
| `fd -x wc -l` | `fd -x wc -l` (if Git's Unix tools are on `PATH`) |

Examples:

```powershell
# ten most recently modified files
fd -t f | Get-Item | Sort-Object LastWriteTime -Descending | Select-Object -First 10

# count files per extension
fd -t f | Get-Item | Group-Object Extension | Sort-Object Count -Descending |
  Select-Object Count, Name

# open a fuzzy-picked file
fd -t f -e md | fzf | ForEach-Object { code $_ }

# total size in MB
fd -t f | ForEach-Object { (Get-Item $_).Length } |
  Measure-Object -Sum |
  ForEach-Object { "{0:N1} MB" -f ($_.Sum / 1MB) }
```

### When you want awk, cut, grep, and sort

Two good options:

1. **Git Bash** — ships with Git for Windows and includes `awk`, `cut`, `sort`, `sed`, `grep`, and `xargs`. Most examples in this post work as written.
2. **WSL** — a real Linux userland. Install `fd` with `sudo apt install fd-find` and alias it.

In Git Bash:

```bash
fd -t f | awk -F. 'NF>1 {print $NF}' | sort | uniq -c | sort -rn
```

Works exactly like macOS/Linux.

### `-x` quoting on Windows

`fd` passes each result as a single argument, so spaces are safe. When you need shell features (redirection, pipes, `%VAR%`), wrap in `cmd` or PowerShell:

```powershell
fd -e log -x powershell -NoProfile -Command "Compress-Archive -Path '{}' -DestinationPath '{}.zip'"
```

Prefer `-X` when the command is a plain executable; it avoids spawning a shell per file.

---

## Cheat sheet

### Install

| Platform | Command |
| --- | --- |
| macOS (Homebrew) | `brew install fd` |
| macOS (MacPorts) | `sudo port install fd` |
| Windows (winget) | `winget install sharkdp.fd` |
| Windows (Scoop) | `scoop install fd` |
| Windows (Chocolatey) | `choco install fd` |
| Any (Cargo) | `cargo install fd-find` |
| Debian/Ubuntu | `sudo apt install fd-find` → binary is `fdfind` |
| WSL | `sudo apt install fd-find` |
| Verify | `fd --version` |

### Search basics

| Command | What it does |
| --- | --- |
| `fd` | List everything (respecting ignores) |
| `fd pattern` | Names matching regex `pattern` |
| `fd pattern path/` | Search inside `path/` |
| `fd -F 'a.b'` | Literal string |
| `fd -g '*.tsx'` | Glob pattern |
| `fd -p 'src/.*\.ts$'` | Match against full path |
| `fd -i foo` / `fd -s foo` | Force case-insensitive / case-sensitive |
| `fd --and bar` | Additional required pattern (AND) |

### Visibility

| Flag | Meaning |
| --- | --- |
| `-H` | Include hidden files/dirs |
| `-I` | Don't respect `.gitignore`, `.ignore`, or `.fdignore` |
| `-u` | Both (`-H -I`) |
| `-E node_modules` | Exclude a glob |
| `--prune` | Don't descend into matching dirs |
| `--no-require-git` | Respect gitignore outside git repos |

### Filters

| Flag | Meaning |
| --- | --- |
| `-t f` / `-t d` / `-t l` | File / directory / symlink |
| `-t x` / `-t e` | Executable / empty |
| `-e md` | Extension (repeatable) |
| `-S +100M` / `-S -10k` | Size greater/less than |
| `--changed-within 7d` | Modified recently |
| `--changed-before 2025-01-01` | Modified before a date |
| `--owner user:group` | Filter by owner (`!` to negate) |
| `-d 2` / `--min-depth 2` / `--exact-depth 2` | Depth control |
| `-L` | Follow symlinks |

### Output

| Flag | Meaning |
| --- | --- |
| `-a` | Absolute paths |
| `-0` | NUL-separated output (for `xargs -0`) |
| `-1` | Stop after first match |
| `--max-results N` | Cap result count |
| `-q` | No output, exit code only |
| `-l` | `ls -l` style details |
| `--format '{/}'` | Custom output: `{}`, `{/}`, `{//}`, `{.}`, `{/.}` |
| `--strip-cwd-prefix` | Remove `./` added by `-x`/`-X`/`-0` |
| `--path-separator /` | Force `/` separators (Windows) |
| `-c never` | Disable color |
| `-j 1` | Single-threaded (ordered execution) |

### Execute

| Command | Meaning |
| --- | --- |
| `fd -e md -x wc -l` | Run per file, in parallel |
| `fd -e md -X wc -l` | Run once with all files |
| `fd -x cmd {} {.}` | Path and path-without-extension |
| `fd -x cmd {/} {//}` | Basename and parent dir |
| `fd -0 ... \| xargs -0 ...` | Safe piping for odd filenames |
| `fd -x echo rm {}` | Dry run before deleting |

### Handy one-liners

| Goal | Command |
| --- | --- |
| Files by extension count | `fd -t f \| awk -F. 'NF>1{print $NF}' \| sort \| uniq -c \| sort -rn` |
| Files per top-level dir | `fd -t f \| awk -F/ 'NF>1{print $1}' \| sort \| uniq -c \| sort -rn` |
| Total size | `fd -t f -x stat -f%z \| awk '{s+=$1} END{print s}'` (macOS) |
| Largest files | `fd -t f -x du -h \| sort -rh \| head -20` |
| Longest files | `fd -e ts -x wc -l \| sort -k1 -nr \| head` |
| Newest files | `fd -t f -x stat -f '%m %N' \| sort -rn \| head` |
| Empty dirs | `fd -t e -t d` |
| Find duplicates by name | `fd -t f \| awk -F/ '{print $NF}' \| sort \| uniq -d` |
| Fuzzy pick and edit | `vim "$(fd -t f \| fzf)"` |
| Fuzzy pick and cd | `cd "$(fd -t d \| fzf)"` |
| Preview then pick | `fd -t f \| fzf --preview 'bat --color=always {}'` |
| Multi-select and open | `fd -t f \| fzf -m --print0 \| xargs -0 code` |
| Markdown checklist | `fd -t f \| sort \| sed 's\|^\|- [ ] \|' > INDEX.md` |
| Append a file list to a note | `fd -t f >> NOTES.md` |

### Aliases worth adding

```bash
# ~/.zshrc or ~/.bashrc
alias fda='fd -H -I'                 # show everything
alias fdf='fd -t f'                  # files only
alias fdd='fd -t d'                  # dirs only
alias fdx='fd -t x'                  # executables

export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
```

---

## Closing thoughts

`fd` is one of those tools that looks like a small quality-of-life upgrade and quietly changes how you work. The pattern is always the same: **narrow with `fd`, then hand the list to something else.**

- Narrow with `-t`, `-e`, `-d`, `-S`, `--changed-within`.
- Explore interactively with `fzf --preview`.
- Summarize with `awk`, `cut`, `sort`, `uniq`.
- Act with `-x`, `-X`, or `xargs -0`.
- Ship the result as Markdown with a tiny `{ ... } > FILE.md` block.

Learn five flags this week — `-t`, `-e`, `-d`, `-H`, `-x` — and you'll rarely reach for `find` again.

