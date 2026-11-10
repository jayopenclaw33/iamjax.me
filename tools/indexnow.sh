#!/bin/bash
# Tell IndexNow engines (Bing, Yandex, Seznam, Naver) that pages changed.
# Usage: tools/indexnow.sh https://HOST/page1 https://HOST/page2 ...   (run after a deploy is live)
# The key below is public by design: it must match /f9e9d92e383ef073be93085c54e726a0.txt on the live site.
set -euo pipefail
HOST=iamjax.me
KEY="f9e9d92e383ef073be93085c54e726a0"
[ $# -gt 0 ] || { echo "usage: $0 URL..." >&2; exit 1; }
urls=$(printf '"%s",' "$@"); urls="[${urls%,}]"
curl -sS -o /dev/null -w "IndexNow HTTP %{http_code}\n" -X POST https://api.indexnow.org/indexnow \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d "{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY.txt\",\"urlList\":$urls}"
