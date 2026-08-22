"""Root-cause / ceiling diagnostic (2026-08-21, user request after
exp_010-017): NOT a new model or feature -- a purely diagnostic script
that asks "how much of the remaining gap to score 1000 is even
theoretically extractable from pre-pitch information in this dataset,
vs. genuine pitch-to-pitch randomness (motor execution noise)?"

Method: on the SAME 2024 validation split used everywhere in this
project, compute a series of IN-SAMPLE "oracle" predictions at
increasing granularity (global mean -> pitcher mean -> pitcher x count
-> pitcher x situational bucket -> pitcher x batter). Each oracle uses
group averages computed FROM THE VAL SET ITSELF (leaky, NOT a valid
model -- a real model can never see its own target). This is
intentional: an in-sample group-mean oracle is the *best possible*
Brier score achievable by ANY predictor that only distinguishes rows by
that grouping key, so it is a valid upper bound on how much signal that
key could ever contribute, no matter how good the model or how much
data. Comparing the champion's actual (honest, out-of-sample) Brier
against these upper bounds tells us whether the ceiling is set by model
quality (headroom exists, oracle >> champion) or by irreducible
randomness (little headroom, oracle ~= baseline even at fine
granularity).
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import numpy as np
import pandas as pd

from features import build_features
from metrics import official_score

DATA_DIR = "./data"
TARGET = "control_success"
CHAMPION_LOCAL_SCORE = 749.58
CHAMPION_LOCAL_BRIER = 0.247934

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != "row_id"]


def oracle_score(df, group_cols, min_group_size=1):
    """In-sample group-mean prediction restricted to groups with
    >= min_group_size rows (tiny groups fall back to the global mean --
    without this, single-pitch groups would trivially predict their own
    outcome perfectly and this stops being a meaningful upper bound)."""
    r = df[TARGET].mean()
    grp = df.groupby(group_cols)[TARGET]
    counts = grp.transform("size")
    means = grp.transform("mean")
    pred = np.where(counts >= min_group_size, means, r)
    brier, score = official_score(pred, df[TARGET].to_numpy())
    n_groups = df.groupby(group_cols).ngroups
    return brier, score, n_groups


def main():
    print("=" * 80)
    print("0. 데이터 로드 (2024 검증셋 기준, 챔피언과 동일 분할)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)
    val = train.loc[train["season"] == 2024].copy()
    r = val[TARGET].mean()
    baseline_brier = r * (1 - r)
    print(f"val n={len(val)}, control_success rate r={r:.4f}, baseline_brier(r(1-r))={baseline_brier:.6f}")
    print(f"챔피언(exp_010, 실제 out-of-sample) 기준: Brier={CHAMPION_LOCAL_BRIER:.6f}, score={CHAMPION_LOCAL_SCORE:.2f}")

    print()
    print("=" * 80)
    print("1. In-sample 그룹평균 오라클 (leaky, 모델 아님 -- 이론적 상한선용)")
    print("=" * 80)
    print("주의: 아래는 val set 자기 자신의 평균을 예측값으로 쓰는 '치팅'이므로")
    print("실제 모델 성능이 아니라 '이 그룹핑 키 하나로 도달 가능한 최댓값'을 보는 용도.")
    print()

    specs = [
        ("전체 평균 (baseline)", []),
        ("pitcher_id", ["pitcher_id"]),
        ("pitcher_id x (balls,strikes)", ["pitcher_id", "balls_before", "strikes_before"]),
        ("pitcher_id x base_state", ["pitcher_id", "base_state"]),
        ("pitcher_id x batter_id", ["pitcher_id", "batter_id"]),
        ("pitcher_id x batter_id x (balls,strikes)", ["pitcher_id", "batter_id", "balls_before", "strikes_before"]),
    ]
    rows = []
    for name, cols in specs:
        if not cols:
            brier, score, n_groups = baseline_brier, 0.0, 1
        else:
            brier, score, n_groups = oracle_score(val, cols, min_group_size=5)
        avg_group_size = len(val) / n_groups
        rows.append((name, n_groups, avg_group_size, brier, score))
        print(f"[{name}] n_groups={n_groups:>6} | avg_size={avg_group_size:6.1f} | Brier={brier:.6f} | score={score:8.2f}")

    print()
    print("=" * 80)
    print("2. 챔피언 대비 갭 분해")
    print("=" * 80)
    pitcher_only = next(r_ for r_ in rows if r_[0] == "pitcher_id")
    print(f"전체 이론적 여지(baseline score 0 -> pitcher_id 단독 오라클 {pitcher_only[4]:.2f}): "
          f"pitcher_id 하나만으로도 최대 {pitcher_only[4]:.2f}점까지 가능(치팅 기준)")
    print(f"챔피언 실제 달성: {CHAMPION_LOCAL_SCORE:.2f} "
          f"({100*CHAMPION_LOCAL_SCORE/pitcher_only[4]:.1f}% of pitcher_id 오라클 상한)")
    finest = rows[-1]
    print(f"가장 세밀한 그룹({finest[0]}, 평균 그룹크기 {finest[2]:.1f}행) 오라클: {finest[4]:.2f}"
          f" -- 그룹이 작아질수록 치팅 상한이 과장되므로 참고용")

    print()
    print("=" * 80)
    print("3. asof_pitcher_n(누적 경험치)별 챔피언 난이도 -- 콜드스타트가 병목인가?")
    print("=" * 80)
    val["cold_start"] = val["asof_pitcher_n"] < 50
    for label, mask in [("cold_start(n<50)", val["cold_start"]), ("warm(n>=50)", ~val["cold_start"])]:
        sub = val.loc[mask]
        sub_r = sub[TARGET].mean()
        sub_baseline = sub_r * (1 - sub_r)
        print(f"[{label}] n={len(sub)} ({100*len(sub)/len(val):.1f}%), r={sub_r:.4f}, "
              f"baseline_brier(r(1-r))={sub_baseline:.6f} -- 이 구간 자체의 이론적 최대 baseline")

    print("\n완료.")


if __name__ == "__main__":
    main()
