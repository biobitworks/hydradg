# Logged-command protocol

From v0.3.3 onward, all operational commands should be run through
`scripts/run_logged.sh` or `scripts/run_sequence.sh`.

## Single command

```bash
bash scripts/run_logged.sh ECA_QUICK -- \
  modal run modal/modal_eca_extension.py --quick
```

On success:
- full output is retained under `logs/`;
- `logs/LAST_SUCCESS.txt` points to the latest success.

On failure:
- the full output remains under `logs/<timestamp>_<label>.log`;
- a compact evidence bundle is created as
  `logs/<timestamp>_<label>.ERROR.txt`;
- the newest compact bundle is copied to
  `logs/LAST_ERROR_FOR_CHAT.txt`.

To show only what needs to be pasted into ChatGPT:

```bash
bash scripts/show_last_error.sh
```

## Multi-command sequence

A command file contains one shell command per line.

```bash
bash scripts/run_sequence.sh ECA_RETRY commands/01_eca_modal_retry.txt
```

The sequence stops at the first failing command and generates the same compact error
bundle.

## Security boundary

The metadata writer reports whether common credential variables are set but never
prints their values.

The wrapper cannot guarantee redaction of a secret if the wrapped application itself
prints that secret to stdout/stderr. Do not intentionally run commands that print
tokens, private keys, passwords, or raw PHI.

## FCO/FCG use

A logged run is an evidence object only after its bytes are actually produced.
The wrapper records lineage but does not imply correctness, signing, Merkle/MMR
commitment, or independent verification.
