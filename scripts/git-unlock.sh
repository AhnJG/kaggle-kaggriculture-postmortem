#!/bin/sh
# Cowork VM 은 마운트된 폴더에서 파일을 '삭제'할 수 없다(Operation not permitted).
# git 은 매 작업마다 .lock 을 만들고 지우는데, 지우기가 거부되어 잠금이 남는다.
# 삭제는 막혀 있지만 '이동'은 허용되므로, 잠금을 .git/_trash 로 밀어낸다.
GD="$(git rev-parse --git-dir 2>/dev/null)" || exit 0
mkdir -p "$GD/_trash"
n=0
for f in "$GD"/*.lock "$GD"/refs/heads/*.lock "$GD"/objects/*/tmp_obj_*; do
  [ -e "$f" ] || continue
  mv -f "$f" "$GD/_trash/$(basename "$f").$$" 2>/dev/null && n=$((n+1))
done
[ "$n" -gt 0 ] && echo "git-unlock: $n개 정리"
exit 0
