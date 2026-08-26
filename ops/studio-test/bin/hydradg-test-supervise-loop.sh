#!/bin/bash
export HOME=/Users/byron
export PATH=/opt/homebrew/bin:/usr/bin:/bin
RUNTIME=/Volumes/magicBLACKbox/hydradg/services/hydradg-test
export npm_config_cache=$RUNTIME/cache/npm
export TMPDIR=$RUNTIME/tmp
mkdir -p $RUNTIME/logs $RUNTIME/state $RUNTIME/tmp
echo $$ > $RUNTIME/state/supervise.pid
while true; do
  WEB=$RUNTIME/current/apps/hydradg-web
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) supervise start" >> $RUNTIME/logs/supervise_web.log
  if [[ -d $WEB/.next ]]; then
    cd $WEB
    /opt/homebrew/bin/node ./node_modules/next/dist/bin/next start -H 127.0.0.1 -p 3000 \
      >>$RUNTIME/logs/web.out.log 2>>$RUNTIME/logs/web.err.log
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) exit=$?" >> $RUNTIME/logs/supervise_web.log
  else
    echo "missing build" >> $RUNTIME/logs/supervise_web.log
  fi
  sleep 2
done
