#!/bin/bash
set -x
cd /Users/byron/projects/active/hydradg
bash eval/sglang_bcg_kaggle_20260826/scripts/watch_and_collect.sh
rc=$?
echo WATCH_RC=$rc
bash eval/sglang_bcg_kaggle_20260826/scripts/finalize_after_collect.sh
echo FINALIZE_DONE
