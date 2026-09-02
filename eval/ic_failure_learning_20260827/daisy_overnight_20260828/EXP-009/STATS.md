# EXP-009 Statistics

**Primary verdict:** UNDERPOWERED
**Exploratory pattern:** DIRECTIONALLY_POSITIVE_SECONDARY

{
  "schema": "hydradg.daisy_overnight.stats.v1",
  "experiment_id": "EXP-009",
  "primary_endpoint": "E06_PREVENTS_C_MEDIA_NOT_IN_VAULT",
  "E06_power_state": "KNOWN_LIMITED",
  "by_model": {
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
      "discordant": 1,
      "b": 0,
      "c": 1,
      "p_exact": 1.0,
      "p_report": 1.0,
      "ci95_low": null,
      "ci95_high": null,
      "method": "bootstrap_insufficient_n",
      "n_paired": 1,
      "pairs": [
        [
          null,
          true
        ],
        [
          false,
          false
        ]
      ]
    }
  },
  "macro_descriptive": {
    "n_paired_total": 3,
    "weighted_rd": 0.0
  },
  "secondary_tests": [
    {
      "metric": "E05_top1",
      "model": "qwen3:1.7b",
      "n": 1,
      "rd": 0.0,
      "c0_rate": 0.0,
      "c1_rate": 0.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E05_top1",
      "model": "qwen2.5-coder:7b",
      "n": 1,
      "rd": 0.0,
      "c0_rate": 0.0,
      "c1_rate": 0.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E05_top3",
      "model": "qwen3:1.7b",
      "n": 1,
      "rd": 1.0,
      "c0_rate": 0.0,
      "c1_rate": 1.0,
      "discordant": 1,
      "b": 0,
      "c": 1,
      "p_exact": 1.0,
      "p_report": 1.0,
      "p_holm": 1.0
    },
    {
      "metric": "E05_top3",
      "model": "qwen2.5-coder:7b",
      "n": 1,
      "rd": 1.0,
      "c0_rate": 0.0,
      "c1_rate": 1.0,
      "discordant": 1,
      "b": 0,
      "c": 1,
      "p_exact": 1.0,
      "p_report": 1.0,
      "p_holm": 1.0
    },
    {
      "metric": "E01_cold_start",
      "model": "qwen3:1.7b",
      "n": 1,
      "rd": 0.0,
      "c0_rate": 0.0,
      "c1_rate": 0.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E01_cold_start",
      "model": "qwen2.5-coder:7b",
      "n": 1,
      "rd": 0.0,
      "c0_rate": 0.0,
      "c1_rate": 0.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E01_vault_media",
      "model": "qwen3:1.7b",
      "n": 1,
      "rd": 0.0,
      "c0_rate": 0.0,
      "c1_rate": 0.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E01_vault_media",
      "model": "qwen2.5-coder:7b",
      "n": 1,
      "rd": 0.0,
      "c0_rate": 1.0,
      "c1_rate": 1.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E01_origin_gap",
      "model": "qwen3:1.7b",
      "n": 1,
      "rd": 0.0,
      "c0_rate": 0.0,
      "c1_rate": 0.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E01_origin_gap",
      "model": "qwen2.5-coder:7b",
      "n": 1,
      "rd": 0.0,
      "c0_rate": 1.0,
      "c1_rate": 1.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E07_directional_gate",
      "model": "qwen3:1.7b",
      "n": 5,
      "rd": 0.0,
      "c0_rate": 0.0,
      "c1_rate": 0.0,
      "discordant": 0,
      "b": 0,
      "c": 0,
      "p_exact": null,
      "note": "no_discordant_pairs"
    },
    {
      "metric": "E07_directional_gate",
      "model": "qwen2.5-coder:7b",
      "n": 5,
      "rd": 0.39999999999999997,
      "c0_rate": 0.2,
      "c1_rate": 0.6,
      "discordant": 2,
      "b": 0,
      "c": 2,
      "p_exact": 0.5,
      "p_report": 0.5,
      "p_holm": 1.0
    }
  ],
  "alpha": 0.05
}
