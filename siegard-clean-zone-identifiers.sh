#!/usr/bin/env sh
# Remove every Zone.Identifier file this tree carries, from this script's own directory down.
#
# Windows writes an alternate data stream named `Zone.Identifier` beside a file it downloaded,
# recording which zone the file came from. Under WSL those streams surface as ordinary files named
# `<name>:Zone.Identifier`, and they arrive in bulk whenever material is copied into a repository
# from a browser or a share. Nothing here reads them: they carry a colon several tools cannot
# address, they are untracked so no diff shows them, and left alone they reach a commit, a survey,
# or a file set somebody names in an invocation — where they are noise that looks like content.
#
# It ships beside CLAUDE.md, at the root of the repository that installs this framework, because
# that root is the top of the tree it cleans and a housekeeping script kept anywhere else is one
# nobody runs. **Nothing in this framework invokes it** — no skill, no agent, no validator. It is a
# person's command, and it is the only thing shipped here that removes a file git is not already
# holding a copy of.
#
# What it matches is exact and narrow: a file whose name ends in `:Zone.Identifier`. A directory is
# never removed, a symbolic link is never followed out of the tree, `.git` is skipped whole, and a
# file named `Zone.Identifier` with no colon before it is not this artifact and is left where it is.
#
# Every removal is printed, and that is not decoration. This framework's rule is that a change git
# can show you is reviewed by `git diff`; these files are untracked, which is exactly why they were
# still there, so the receipt this prints is the only account of what stopped existing.
#
# Written to POSIX `sh` rather than to any one shell, and it presupposes no package: `find` and `rm`
# are the whole of what it needs.
#
# Usage:  ./siegard-clean-zone-identifiers.sh              remove them, printing each
#         ./siegard-clean-zone-identifiers.sh --dry-run    print what it would remove, remove nothing
#         ./siegard-clean-zone-identifiers.sh --help       print this text and stop
# Exit:   0 the tree held none, or every one found was removed
#         1 a file was found and could not be removed
#         2 cannot run

set -eu

# Printing this script's own header is what keeps `--help` from becoming a second copy of the
# usage: the text a reader sees on opening the file is the text the flag answers with. The awk
# reads from the shebang to the first line that is not a comment, and stops there.
help_text() {
    awk 'NR == 1 { next } /^#/ { sub(/^# ?/, ""); print; next } { exit }' "$0"
}

dry_run=0
for arg in "$@"; do
    case "$arg" in
        --help) help_text; exit 0 ;;
        --dry-run) dry_run=1 ;;
        *)
            printf 'cannot run: %s is not an argument this takes; --help prints the form\n' \
                   "$arg" >&2
            exit 2
            ;;
    esac
done

# The script's own directory, resolved, rather than wherever it was invoked from: what it cleans is
# the tree it sits at the top of, and that has to be the same tree whichever directory a person
# happened to be standing in.
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)

found=0
removed=0
failed=0

# Read from a here-document over the command substitution rather than from a pipe: a pipe would run
# the loop in a subshell and the three counters below would come back to nothing. One consequence
# to state rather than hide — a path containing a newline would be read as two, which the artifact
# this matches cannot have, since Windows composes the name from a file name it already wrote.
while IFS= read -r path; do
    [ -n "$path" ] || continue
    found=$((found + 1))
    if [ "$dry_run" -eq 1 ]; then
        printf 'would remove %s\n' "$path"
        continue
    fi
    if rm -f -- "$path"; then
        printf 'removed %s\n' "$path"
        removed=$((removed + 1))
    else
        printf 'could not remove %s\n' "$path" >&2
        failed=$((failed + 1))
    fi
done <<EOF
$(find "$here" -name .git -prune -o -type f -name '*:Zone.Identifier' -print)
EOF

if [ "$found" -eq 0 ]; then
    printf 'no Zone.Identifier file under %s\n' "$here"
elif [ "$dry_run" -eq 1 ]; then
    printf '\n%d file(s) would be removed under %s\n' "$found" "$here"
else
    printf '\n%d of %d file(s) removed under %s\n' "$removed" "$found" "$here"
fi

[ "$failed" -eq 0 ] || exit 1
exit 0
