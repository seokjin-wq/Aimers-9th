"""Row-local feature engineering.

Every feature here is computed independently per row from columns that
are already part of the official train/test schema. No cross-row
aggregation, no external data — see CLAUDE.md "Competition Safety
Rules". Safe to apply identically to train and test.

exp_002 adds two things on top of exp_001's 15 features (see
experiments/exp_002_asof_refinement.md for the full per-feature
rationale table):

1. 8 new row-local derived columns (`DERIVED_COLS`) — situational
   interactions, a cleaner recency-trend decomposition, batter-side
   mirroring, and a handedness-matchup flag.
2. A cold-start empirical-Bayes shrinkage mechanism (`SHRINKAGE_SPECS`
   / `fit_shrinkage_priors` / `apply_shrinkage`) for the asof_* rate
   columns. This is a *fit/transform* pair, unlike everything else in
   this module: `fit_shrinkage_priors` MUST be called only on the
   training split (never on validation or test rows), because the
   prior it computes is a global mean that would leak validation/test
   statistics if fit on them. `apply_shrinkage` itself is row-local and
   safe to call on any split once the priors are fit.

exp_003 adds features found in the group1-5 + cross-group EDA
(reports/eda_group1-5, reports/eda_final) that weren't yet in
exp_002's feature set (see experiments/exp_003_*.md for the full
rationale table):

3. 3 new row-local derived columns — hand-matchup x pitch-mix
   interactions (reports/eda_final §B) and a three-ball x
   scoring-position interaction (reports/eda_final §D).
4. `SHRINKAGE_SPECS`'s batter-side k raised from 50 to 150
   (reports/eda_group5 §8 — batter cold-start bias is ~4x larger than
   pitcher's at matched sample size).
5. A post-shrinkage multiplicative pitcher x batter interaction
   (`POST_SHRINKAGE_COLS`, computed from the *shrunk* rates so it's
   NaN-free) — reports/eda_final §H found the two effects are mostly
   additive but with a mild multiplicative residual.

exp_004 tried simplifying the feature set (dropping 8 raw columns that
were either exact duplicates of another raw column, or had zero
CatBoost split importance in exp_003) and adding 5 more EDA-validated
derived columns. Every combination tested (removal only, addition only,
addition minus the two flags that scored exactly 0 importance, and the
full bundle) scored *below* exp_003's 723.17 — see
experiments/exp_004_feature_simplification.md for the full ablation
table. **None of it was adopted; this file is unchanged from exp_003.**
The mathematically-redundant raw columns turned out to still carry real
marginal value for CatBoost's tree splits despite the duplication, and
low/zero importance did not reliably predict whether removing or adding
a column would help — importance ranking alone is not a safe proxy for
an ablation test in this feature set.

exp_005 tried `trackman_history.csv`-informed features (EDA:
reports/eda_trackman/README.md; leak-safe as-of join mechanism:
src/trackman_features.py, kept as reusable infrastructure even though
unused by the current pipeline). All 3 tested variants scored *below*
exp_003's 723.17 — full bundle of 4 trackman features + row-local
`is_postseason` scored 703.21 (-19.96), and isolating either the two
season-trend-correlated trackman features (703.21 -> still -10.39 by
themselves) or the two situational (three-ball) ones (-17.30 by
themselves) confirmed neither half was salvageable; see
experiments/exp_005_trackman.md for the full ablation table. **None of
it was adopted; this file is unchanged from exp_003** (the `is_postseason`
column that was briefly added here for exp_005 has been reverted since
it was dead weight on its own, importance 0.00 in every run).
"""

import numpy as np

CAT_COLS = ["top_bottom", "game_type", "base_state"]

DERIVED_COLS = [
    "count_diff",
    "count_total",
    "two_strike",
    "three_ball",
    "full_count",
    "late_inning",
    "score_margin_abs",
    "is_close_game",
    "runners_scoring_position",
    "pitcher_minus_batter_success",
    "pitcher_middle_minus_success",
    "pitcher_recent_form_delta",
    "pitcher_experience_log",
    "batter_experience_log",
    "pitchmix_diversity",
    # --- exp_002 additions below ---
    "pitcher_success_under_pressure",
    "pitcher_reverse_under_pressure",
    "pitcher_success_x_risp",
    "pitcher_form_trend_isolated",
    "pitcher_middle_trend_isolated",
    "pitcher_form_volatility",
    "batter_middle_minus_success",
    "same_hand_matchup",
    # --- exp_003 additions below ---
    "same_hand_x_breaking_rate",
    "same_hand_x_offspeed_rate",
    "three_ball_x_risp",
]

# (raw rate col, sample-size col, shrinkage strength k, output col name).
# shrunk = (n*rate + k*prior) / (n+k) — prior must come from
# fit_shrinkage_priors(train_only_df). k=50 is chosen so that only the
# genuine cold-start tail is pulled toward the prior: the 1st-5th
# percentiles of asof_pitcher_n / asof_batter_n in train.csv are
# ~18-107, so k=50 meaningfully shrinks that tail while leaving the
# bulk of rows close to their raw rate (at n=0 the formula reduces
# exactly to the prior).
#
# exp_003: the two asof_batter_* specs use k=150 instead of 50.
# reports/eda_group5/README.md §8 shows the batter reliability table
# has a much larger n=1-vs-n=1001+ gap than the pitcher one
# (7.0%p vs 1.8%p at matched sample-size bins), so the same k=50
# under-shrinks the batter cold-start tail relative to the pitcher one.
SHRINKAGE_SPECS = [
    ("asof_pitcher_success_rate", "asof_pitcher_n", 50, "shrunk_pitcher_success_rate"),
    ("asof_pitcher_reverse_rate", "asof_pitcher_n", 50, "shrunk_pitcher_reverse_rate"),
    ("asof_pitcher_middle_rate", "asof_pitcher_n", 50, "shrunk_pitcher_middle_rate"),
    ("asof_pitcher_ball_rate", "asof_pitcher_n", 50, "shrunk_pitcher_ball_rate"),
    ("asof_pitcher_strike_rate", "asof_pitcher_n", 50, "shrunk_pitcher_strike_rate"),
    ("asof_batter_success_rate", "asof_batter_n", 150, "shrunk_batter_success_rate"),
    ("asof_batter_middle_rate", "asof_batter_n", 150, "shrunk_batter_middle_rate"),
    ("asof_pitcher_fastball_rate", "asof_pitcher_pitchmix_n", 50, "shrunk_pitcher_fastball_rate"),
    ("asof_pitcher_breaking_rate", "asof_pitcher_pitchmix_n", 50, "shrunk_pitcher_breaking_rate"),
    ("asof_pitcher_offspeed_rate", "asof_pitcher_pitchmix_n", 50, "shrunk_pitcher_offspeed_rate"),
]
SHRUNK_COLS = [spec[3] for spec in SHRINKAGE_SPECS]

# exp_003: computed *after* shrinkage (inside apply_shrinkage below) since
# it needs the NaN-free shrunk rates, not the raw asof_* columns.
POST_SHRINKAGE_COLS = ["shrunk_pitcher_x_batter_success"]

ALL_DERIVED_COLS = DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS


def build_features(df):
    """Return a copy of df with derived columns added (no columns dropped)."""
    df = df.copy()

    df["count_diff"] = df["strikes_before"] - df["balls_before"]
    df["count_total"] = df["strikes_before"] + df["balls_before"]
    df["two_strike"] = (df["strikes_before"] == 2).astype(int)
    df["three_ball"] = (df["balls_before"] == 3).astype(int)
    df["full_count"] = df["two_strike"] & df["three_ball"]

    df["late_inning"] = (df["inning"] >= 7).astype(int)

    df["score_margin_abs"] = df["score_diff_pitcher_team"].abs()
    df["is_close_game"] = (df["score_margin_abs"] <= 1).astype(int)
    df["runners_scoring_position"] = (
        (df["runner_on_2b"] == 1) | (df["runner_on_3b"] == 1)
    ).astype(int)

    df["pitcher_minus_batter_success"] = (
        df["asof_pitcher_success_rate"] - df["asof_batter_success_rate"]
    )
    df["pitcher_middle_minus_success"] = (
        df["asof_pitcher_middle_rate"] - df["asof_pitcher_success_rate"]
    )
    df["pitcher_recent_form_delta"] = (
        df["asof_pitcher_prev1_game_success_rate"]
        - df["asof_pitcher_prev5_game_success_rate"]
    )

    df["pitcher_experience_log"] = np.log1p(df["asof_pitcher_n"])
    df["batter_experience_log"] = np.log1p(df["asof_batter_n"])

    mix_cols = [
        "asof_pitcher_fastball_rate",
        "asof_pitcher_breaking_rate",
        "asof_pitcher_offspeed_rate",
    ]
    mix_sq_sum = sum(df[c].fillna(0) ** 2 for c in mix_cols)
    df["pitchmix_diversity"] = 1 - mix_sq_sum

    # --- exp_002 additions ---

    # A. 압박 상황별 투수 경향: li(leverage index)·득점권 주자로 투수의
    # 성공률/반대성 비율을 조건화. 트리 모델은 두 피처를 각각 분할할 순
    # 있어도 곱셈적 상호작용은 명시적으로 줘야 num_leaves=63 안에서
    # 찾기 쉬움.
    df["pitcher_success_under_pressure"] = df["asof_pitcher_success_rate"] * df["li"]
    df["pitcher_reverse_under_pressure"] = df["asof_pitcher_reverse_rate"] * df["li"]
    df["pitcher_success_x_risp"] = (
        df["asof_pitcher_success_rate"] * df["runners_scoring_position"]
    )

    # B. 최근 폼 추세/변동성: prev1/3/5는 중첩 누적 평균이라 단순
    # prev1-prev5는 prev5에 최근 경기가 섞여 추세가 흐려짐. 대수적으로
    # "4~5경기째만의 평균" = (5*prev5 - 3*prev3) / 2 로 분리해서, 가장
    # 최근 경기 대 진짜 예전 경기를 비교하는 추세 피처를 만든다.
    def _isolated_trend(prev1, prev3, prev5):
        early_only = (5 * prev5 - 3 * prev3) / 2
        return prev1 - early_only

    df["pitcher_form_trend_isolated"] = _isolated_trend(
        df["asof_pitcher_prev1_game_success_rate"],
        df["asof_pitcher_prev3_game_success_rate"],
        df["asof_pitcher_prev5_game_success_rate"],
    )
    df["pitcher_middle_trend_isolated"] = _isolated_trend(
        df["asof_pitcher_prev1_game_middle_rate"],
        df["asof_pitcher_prev3_game_middle_rate"],
        df["asof_pitcher_prev5_game_middle_rate"],
    )
    form_cols = df[
        [
            "asof_pitcher_prev1_game_success_rate",
            "asof_pitcher_prev3_game_success_rate",
            "asof_pitcher_prev5_game_success_rate",
        ]
    ]
    df["pitcher_form_volatility"] = form_cols.max(axis=1) - form_cols.min(axis=1)

    # C. 타자 지표 보완: 기존엔 pitcher_middle_minus_success만 있고
    # 타자 쪽 동일 지표가 없었음 — 대칭적으로 추가.
    df["batter_middle_minus_success"] = (
        df["asof_batter_middle_rate"] - df["asof_batter_success_rate"]
    )

    # D. 손잡이 매치업: 전형적인 platoon 신호. pitcher_hand/batter_hand는
    # 이미 원본 컬럼으로 모델에 들어가지만 둘을 직접 비교한 피처는 없었음.
    df["same_hand_matchup"] = (df["pitcher_hand"] == df["batter_hand"]).astype(int)

    # --- exp_003 additions ---

    # E. 손 유형 매치업 x 과거 구종 성향: reports/eda_final §B — 손 유형
    # 조합 안에서도 투수의 평소 구종 성향(breaking/offspeed 비율)에 따라
    # 성공률이 10%p 가까이 벌어짐(46.82~56.41%). same_hand_matchup과
    # 구종 비율을 각각 넣는 것만으로는 트리가 이 조합을 찾기까지
    # num_leaves=63 예산 안에서 비효율적일 수 있어 곱을 명시적으로 준다.
    df["same_hand_x_breaking_rate"] = df["same_hand_matchup"] * df["asof_pitcher_breaking_rate"]
    df["same_hand_x_offspeed_rate"] = df["same_hand_matchup"] * df["asof_pitcher_offspeed_rate"]

    # F. 3볼 x 득점권 주자: reports/eda_final §D — 3볼 상황에서는 득점권
    # 주자 유무가 outs=0/1에서는 있을 때 성공률이 더 높고 outs=2에서는
    # 반대로 뒤집히는 비단조 패턴이 나타났다("가설" 수준, outs_before는
    # 이미 원본 컬럼으로 모델에 들어가므로 outs와의 3-way 조합은 트리가
    # three_ball x runners_scoring_position 신호만 명시적으로 받으면
    # outs_before와 알아서 추가 분할할 수 있다).
    df["three_ball_x_risp"] = df["three_ball"] * df["runners_scoring_position"]

    return df


def fit_shrinkage_priors(train_df, specs=SHRINKAGE_SPECS):
    """Compute the global prior rate for each shrinkage spec.

    MUST be called on the training split only (e.g. seasons 2019-2023
    for the held-out validation run, or the full 2019-2024 train.csv
    for the final refit) — never on validation or test rows, since the
    prior is a dataset-wide mean and would otherwise leak those splits'
    statistics into a "training-derived" feature.
    """
    return {rate_col: train_df[rate_col].mean() for rate_col, _, _, _ in specs}


def apply_shrinkage(df, priors, specs=SHRINKAGE_SPECS):
    """Row-local empirical-Bayes shrinkage: shrunk = (n*r + k*prior)/(n+k).

    Safe to call on any split (train/val/test) once `priors` has been
    fit on the training split via `fit_shrinkage_priors`. Always
    NaN/inf-free: raw rate and sample-size are filled with 0 first, so
    n=0 (cold start) reduces exactly to the prior.
    """
    df = df.copy()
    for rate_col, n_col, k, shrunk_col in specs:
        r = df[rate_col].fillna(0)
        n = df[n_col].fillna(0)
        df[shrunk_col] = (n * r + k * priors[rate_col]) / (n + k)

    # exp_003 G: 투수 x 타자 품질 매치업. reports/eda_final §H — 5x5
    # 분위 heatmap에서 두 효과가 거의 가법적이지만(P5-P1 격차가
    # batter 분위 전체에서 9.85~11.57%p로 비교적 일정) 살짝 커지는
    # 경향이 있어 약한 곱셈적 상호작용의 여지가 있었다. 기존
    # pitcher_minus_batter_success(차)는 build_features에서 raw
    # asof_*로 계산되고(cold-start 시 NaN 가능), 이 피처는 반드시
    # 여기서 shrunk 값(NaN 없음)으로 계산해야 한다.
    if "shrunk_pitcher_success_rate" in df.columns and "shrunk_batter_success_rate" in df.columns:
        df["shrunk_pitcher_x_batter_success"] = (
            df["shrunk_pitcher_success_rate"] * df["shrunk_batter_success_rate"]
        )
    return df
