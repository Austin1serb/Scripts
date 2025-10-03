# start clean
git rebase --abort 2>/dev/null || true
git checkout main
git pull --ff-only
git checkout -b tidy-2025-04-21-final

FROM="2025-04-21 00:00"
TO="2025-04-22 00:00"

# last commit within the day
END=$(git rev-list -n1 --before="$TO" main) || { echo "No END commit"; exit 1; }

# commit immediately BEFORE the day; if none, fall back to root commit
BASE=$(git rev-list -n1 --before="$FROM" main)
if [ -z "$BASE" ]; then BASE=$(git rev-list --max-parents=0 main); fi

# validate—these must both be commits
git cat-file -e "${END}^{commit}"
git cat-file -e "${BASE}^{commit}"

echo "BASE=$BASE"; echo "END=$END"
git show --no-patch --oneline "$BASE"
git show --no-patch --oneline "$END"

# build the single commit for the day
git reset --hard "$END"      # worktree = end-of-day snapshot
git reset --soft "$BASE"     # stage exactly BASE..END
git commit -m "chore: squash commits for 2025-04-21"

# replay all commits AFTER the day, letting later commits win conflicts
git rebase --rebase-merges -X theirs --onto HEAD "$END" main

# verify you now have exactly one commit on 2025-04-21
git log --oneline --decorate --graph --since="$FROM" --until="$TO" main

# publish
git checkout main
git reset --hard tidy-2025-04-21-final
git push --force-with-lease
