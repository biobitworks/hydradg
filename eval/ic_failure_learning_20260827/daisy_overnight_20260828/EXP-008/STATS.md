# EXP-008 Statistics

**Result class:** UNDERPOWERED

## Primary (E06 prevents-C)
{
  "qwen3:1.7b": {
    "n": 2,
    "rd": 0.0,
    "c0_rate": 0.0,
    "c1_rate": 0.0,
    "discordant": 0,
    "b": 0,
    "c": 0,
    "p_exact": null,
    "note": "no_discordant_pairs",
    "ci95_low": 0.0,
    "ci95_high": 0.0,
    "method": "paired_bootstrap_percentile",
    "n_paired": 2,
    "pairs": [
      [
        false,
        false
      ],
      [
        false,
        false
      ]
    ]
  },
  "qwen2.5-coder:7b": {
    "n": 1,
    "rd": 0.0,
    "c0_rate": 0.0,
    "c1_rate": 0.0,
    "discordant": 0,
    "b": 0,
    "c": 0,
    "p_exact": null,
    "note": "no_discordant_pairs",
    "ci95_low": null,
    "ci95_high": null,
    "method": "bootstrap_insufficient_n",
    "n_paired": 1,
    "pairs": [
      [
        true,
        null
      ],
      [
        false,
        false
      ]
    ]
  }
}

## Data quality
{
  "n_raw": 300,
  "valid_parse_rate": 0.9066666666666666,
  "malformed_rate": 0.09333333333333334,
  "unknown_rate": 0.5,
  "abstain_rate": 0.08333333333333333
}
