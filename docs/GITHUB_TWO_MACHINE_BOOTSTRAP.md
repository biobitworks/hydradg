# GitHub bootstrap for magicSTUDIObox + magicPRObox

## Goal

Both machines use GitHub as the persistent source/evidence synchronization layer. No routine ZIP/download handoff is required.

Canonical paths on both machines:

- `/Users/byron/projects/active/hydradg`
- `/Users/byron/projects/active/lesswrong`

Repositories:

- `biobitworks/hydradg` — private canonical HydraDG history
- `biobitworks/lesswrong` — private canonical LessWrong/article history

Private custody branches:

- `main` — canonical private history
- `test` — experimental work/failures
- `stage` — release-candidate state

A public release remains a separate sanitized repository/export; it is not a public branch of the private history.

## Order matters

Run the bootstrap on **magicSTUDIObox first** because `/Users/byron/projects/active/lesswrong` on magicSTUDIObox is the canonical source directory for the initial LessWrong GitHub repository.

Then run it on **magicPRObox**, which will clone/synchronize that repository.

## One-time prerequisites on each machine

Check:

```bash
git --version
gh --version
gh auth status
```

If GitHub CLI is not authenticated:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
```

If Git identity is missing, configure your own GitHub-associated identity:

```bash
git config --global user.name 'YOUR NAME'
git config --global user.email 'YOUR GITHUB EMAIL OR NOREPLY EMAIL'
```

For the initial LessWrong push on magicSTUDIObox, Gitleaks is required:

```bash
brew install gitleaks
```

## 1. magicSTUDIObox

```bash
cd /Users/byron/projects/active/hydradg

git fetch origin setup/remote-work-20260818
git switch setup/remote-work-20260818
git pull --ff-only origin setup/remote-work-20260818

bash scripts/setup_github_both_machines.sh studio
```

Expected ending:

```text
GITHUB_MACHINE_READY=YES
ROLE=studio
HYDRADG=biobitworks/hydradg
LESSWRONG=biobitworks/lesswrong
```

The script will create the private `biobitworks/lesswrong` repository through `gh` only if it does not already exist, after size and Gitleaks gates pass. It creates/pushes `main`, `test`, and `stage`.

## 2. magicPRObox

After the studio run succeeds:

```bash
cd /Users/byron/projects/active/hydradg

git fetch origin setup/remote-work-20260818
git switch setup/remote-work-20260818
git pull --ff-only origin setup/remote-work-20260818

bash scripts/setup_github_both_machines.sh pro
```

Expected ending:

```text
GITHUB_MACHINE_READY=YES
ROLE=pro
HYDRADG=biobitworks/hydradg
LESSWRONG=biobitworks/lesswrong
```

If magicPRObox already has a non-Git `/Users/byron/projects/active/lesswrong` directory containing files, the script **fails closed** rather than overwriting it. Review/move that directory aside and rerun.

## 3. Final two-machine smoke

Once both bootstrap runs pass, execute from magicPRObox:

```bash
cd /Users/byron/projects/active/hydradg
bash scripts/final_two_machine_test.sh
```

This checks Tailscale/SSH, repository synchronization, the canonical LessWrong workspace on magicSTUDIObox, Ollarma, and a bounded Vithia training smoke. It does not launch the frozen VITHIA-OVERNIGHT-01 queue.

## Normal operating loop after bootstrap

At the start of work on either machine:

```bash
git fetch origin --prune
git switch test
git pull --ff-only origin test
```

Do active work on `test`. Promote deliberately:

`test → stage → main → separate public export`

Before pushing meaningful evidence:

`clean/sync → execute → receipt/hash → Gitleaks → commit → push → fetch → local==remote`

## Secret/key boundary

Never commit:

- private signing keys;
- active tokens/credentials;
- plaintext `.env` secrets.

Commit public keys, signatures, fingerprints, hashes, FCO/FCG receipts, manifests, and verification evidence.

## Database persistence boundary

GitHub is the source/code/evidence-control layer. Live HydraDB/SeedGraph databases remain runtime services/data stores and should be accessed over the private Tailscale/SSH path or through governed exports/receipts rather than by committing live database files blindly.
