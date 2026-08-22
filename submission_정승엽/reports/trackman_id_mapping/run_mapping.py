"""Phase 2 실행 스크립트.

v1: 투수 단위 시즌 지문 매칭(2-A) → 그 안에서 투구 단위 매칭(2-B).
v2 (주 결과): situational_key + tier + 양쪽 손을 모두 합친 조합키로
직접 행 단위 매칭(Step A, 사전 투수 식별 없음) → 그 결과에서 투수
정체성을 역산(Step B) → 식별된 투수 안에서 행 매칭 재실행(Step C,
v1의 match_rows 재사용)으로 커버리지 회복.

data/processed/trackman_clean.csv, data/processed/train_match_keys.csv
(Phase 1 산출물)과 원본 data/train.csv, data/trackman_history.csv를 읽어서
매핑을 재구성하고 검증 수치를 출력한다. 원본/Phase1 산출물 모두 읽기만
하고 수정하지 않는다.

실행:
    python reports/trackman_id_mapping/run_mapping.py

표준출력을 reports/trackman_id_mapping/mapping_run_log.txt 로
리다이렉트해서 보관 — README.md의 모든 수치는 이 로그에서만 가져온다.
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import numpy as np
import pandas as pd

from trackman_id_mapping import (
    build_train_pitcher_fingerprints,
    build_trackman_pitcher_fingerprints,
    match_pitchers_by_season,
    consolidate_pitcher_mapping,
    order_consistency_check,
    match_rows,
    match_rows_direct_unique,
    induce_pitcher_mapping,
    induce_pitcher_mapping_iterative,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
TABLES_DIR = os.path.join(os.path.dirname(__file__), "tables")
os.makedirs(TABLES_DIR, exist_ok=True)


def report_row_match_quality(name, row_matches, train_match_keys, trackman_clean, train_n):
    print(f"--- [{name}] 행 단위 매칭: {len(row_matches)} / train 전체 {train_n} 행 ({len(row_matches) / train_n:.4%}) ---")
    if "row_confidence" in row_matches.columns:
        print("row_confidence 분포:")
        print(row_matches["row_confidence"].value_counts())

    gt = train_match_keys.set_index("row_id")["game_type"]
    tier = trackman_clean.set_index("trackman_id")["pitcher_team_tier"]
    rm = row_matches.copy()
    rm["game_type"] = rm["row_id"].map(gt)
    rm["trackman_pitcher_team_tier"] = rm["trackman_id"].map(tier)
    expected = rm["game_type"].map({"R": "major", "F": "minor"})
    tier_agree_rate = (expected == rm["trackman_pitcher_team_tier"]).mean()
    print(f"독립 신호 검증(game_type vs trackman team_tier) 일치율: {tier_agree_rate:.4%}")
    return rm


def main():
    print("=" * 70)
    print("0. 로드 + 기초 사실 확인")
    print("=" * 70)
    train_raw = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig")
    train_match_keys = pd.read_csv(os.path.join(PROCESSED_DIR, "train_match_keys.csv"), encoding="utf-8-sig")
    trackman_clean = pd.read_csv(os.path.join(PROCESSED_DIR, "trackman_clean.csv"), encoding="utf-8-sig")
    print(f"train_raw: {train_raw.shape}, train_match_keys: {train_match_keys.shape}, trackman_clean: {trackman_clean.shape}")
    print(f"train 고유 pitcher_id 수: {train_raw['pitcher_id'].nunique()}")
    print(f"trackman 고유 pitcher_trackman_id 수: {trackman_clean['pitcher_trackman_id'].nunique()}")

    print()
    print("--- train pitcher_team_id(13개) 별 투구 수 / 고유 pitcher_id 수 ---")
    print(train_raw.groupby("pitcher_team_id").agg(n_rows=("row_id", "size"), n_pitchers=("pitcher_id", "nunique")))
    print()
    print("--- trackman pitcher_team_franchise 별 투구 수 / 고유 pitcher_trackman_id 수 (major+minor 합산) ---")
    print(trackman_clean.groupby("pitcher_team_franchise").agg(n_rows=("trackman_id", "size"), n_pitchers=("pitcher_trackman_id", "nunique")).sort_values("n_rows", ascending=False))

    print()
    print("--- pitcher_hand / batter_hand: train 정수 코드 vs trackman 문자열 비율 대응 근거 ---")
    print("train pitcher_hand:", train_raw["pitcher_hand"].value_counts(normalize=True).to_dict())
    print("trackman pitcher_hand:", trackman_clean["pitcher_hand"].value_counts(normalize=True).to_dict())
    print("train batter_hand:", train_raw["batter_hand"].value_counts(normalize=True).to_dict())
    print("trackman batter_hand:", trackman_clean["batter_hand"].value_counts(normalize=True).to_dict())

    # =========================================================================
    print()
    print("=" * 70)
    print("v1. 투수 단위 시즌 지문 매칭(2-A) -> 투구 단위(2-B)  [참고/비교용]")
    print("=" * 70)
    train_fp = build_train_pitcher_fingerprints(train_raw, train_match_keys)
    trackman_fp = build_trackman_pitcher_fingerprints(trackman_clean)
    season_matches = match_pitchers_by_season(train_fp, trackman_fp)
    pitcher_mapping_v1 = consolidate_pitcher_mapping(season_matches)
    print("v1 confidence tier 분포:")
    print(pitcher_mapping_v1["confidence"].value_counts())
    row_matches_v1 = match_rows(train_match_keys, trackman_clean, pitcher_mapping_v1, confidences=("high", "medium"))
    report_row_match_quality("v1", row_matches_v1, train_match_keys, trackman_clean, len(train_raw))

    # =========================================================================
    print()
    print("=" * 70)
    print("v2 Step A. 조합키(situational_key + tier + pitcher_hand + batter_hand) 직접 매칭")
    print("=" * 70)
    direct = match_rows_direct_unique(train_match_keys, trackman_clean)
    print(f"조합키 1:1 유일 매칭 (사전 투수 식별 없음): {len(direct)}행")
    print(f"관련 고유 train pitcher_id 수: {direct['pitcher_id'].nunique()} / 792")
    print(f"관련 고유 trackman pitcher_trackman_id 수: {direct['matched_pitcher_trackman_id'].nunique()} / 906")

    print()
    print("=" * 70)
    print("v2 Step B. Step A 결과에서 투수 정체성 역산")
    print("=" * 70)
    pitcher_mapping_v2 = induce_pitcher_mapping(direct)
    print(f"역산된 pitcher_id 매핑: {len(pitcher_mapping_v2)} / train 전체 {train_raw['pitcher_id'].nunique()} 명")
    print("confidence tier 분포:")
    print(pitcher_mapping_v2["confidence"].value_counts())
    print("confidence tier별 평균 purity / n_votes_total / season_consistency:")
    print(pitcher_mapping_v2.groupby("confidence")[["purity", "n_votes_total", "season_consistency"]].mean())

    print()
    print("--- v1 vs v2 교차검증: 둘 다 confident(high/medium)한 투수들의 매칭 결과 일치율 ---")
    v1_conf = pitcher_mapping_v1[pitcher_mapping_v1["confidence"].isin(["high", "medium"])][
        ["pitcher_id", "matched_pitcher_trackman_id"]
    ].rename(columns={"matched_pitcher_trackman_id": "v1_match"})
    v2_conf = pitcher_mapping_v2[pitcher_mapping_v2["confidence"].isin(["high", "medium"])][
        ["pitcher_id", "matched_pitcher_trackman_id"]
    ].rename(columns={"matched_pitcher_trackman_id": "v2_match"})
    both = v1_conf.merge(v2_conf, on="pitcher_id", how="inner")
    print(f"양쪽 다 confident한 투수 수: {len(both)}")
    if len(both):
        agree = (both["v1_match"] == both["v2_match"]).mean()
        print(f"v1/v2 매칭 결과 일치율: {agree:.4%}")

    print()
    print("--- 독립 신호 검증: pitcher_hand 일치율 (v2, 사후 확인) ---")
    tm_hand_lookup = trackman_clean.drop_duplicates("pitcher_trackman_id").set_index("pitcher_trackman_id")["pitcher_hand"]
    train_hand_lookup = train_raw.drop_duplicates("pitcher_id").set_index("pitcher_id")["pitcher_hand"].map({2: "Right", 1: "Left"})
    check = pitcher_mapping_v2.copy()
    check["train_hand"] = check["pitcher_id"].map(train_hand_lookup)
    check["tm_hand"] = check["matched_pitcher_trackman_id"].map(tm_hand_lookup)
    print(f"전체 hand 일치율: {(check['train_hand'] == check['tm_hand']).mean():.4%}")

    print()
    print("=" * 70)
    print("v2 Step C (1회). 역산된 투수 정체성으로 행 단위 매칭 재실행 (커버리지 회복)")
    print("=" * 70)
    for min_conf in [["high"], ["high", "medium"]]:
        oc = order_consistency_check(train_match_keys, trackman_clean, pitcher_mapping_v2, min_confidence=min_conf)
        print(f"순서 정합 sanity check (confidence in {min_conf}): {oc}")

    row_matches_v2 = match_rows(train_match_keys, trackman_clean, pitcher_mapping_v2, confidences=("high", "medium"))
    rm2 = report_row_match_quality("v2 (1회)", row_matches_v2, train_match_keys, trackman_clean, len(train_raw))
    print("pitcher_confidence x row_confidence 교차표:")
    print(pd.crosstab(row_matches_v2["pitcher_confidence"], row_matches_v2["row_confidence"]))

    conf_pids_v2 = pitcher_mapping_v2[pitcher_mapping_v2["confidence"].isin(["high", "medium"])]["pitcher_id"]
    own_rows = train_raw[train_raw["pitcher_id"].isin(conf_pids_v2)]
    print(f"v2 confident 투수({len(conf_pids_v2)}명)의 자기 행 수: {len(own_rows)}, 그 중 매칭된 비율: {len(row_matches_v2) / len(own_rows):.4%}")

    # =========================================================================
    print()
    print("=" * 70)
    print("v3. 반복 정제(iterative refinement) — 확정된 투수/트랙맨ID를 제외하고 Step A/B 재실행")
    print("=" * 70)
    pitcher_mapping_v3, round_logs = induce_pitcher_mapping_iterative(
        train_match_keys, trackman_clean, n_rounds=5, min_support=3
    )
    print("라운드별 진행 로그:")
    print(round_logs.to_string(index=False))
    print()
    print(f"최종 역산된 pitcher_id 매핑: {len(pitcher_mapping_v3)} / train 전체 {train_raw['pitcher_id'].nunique()} 명 ({len(pitcher_mapping_v3) / train_raw['pitcher_id'].nunique():.4%})")
    print("confidence tier 분포:")
    print(pitcher_mapping_v3["confidence"].value_counts())

    never_resolved = set(train_raw["pitcher_id"].unique()) - set(pitcher_mapping_v3["pitcher_id"])
    own_never = train_raw[train_raw["pitcher_id"].isin(never_resolved)]
    print(f"끝까지 미해결 투수: {len(never_resolved)}명, 그들의 자기 행 수: {len(own_never)} ({len(own_never) / len(train_raw):.4%} of train)")

    print()
    print("--- 독립 신호 검증: pitcher_hand 일치율 (v3) ---")
    check3 = pitcher_mapping_v3.copy()
    check3["train_hand"] = check3["pitcher_id"].map(train_hand_lookup)
    check3["tm_hand"] = check3["matched_pitcher_trackman_id"].map(tm_hand_lookup)
    print(f"전체 hand 일치율: {(check3['train_hand'] == check3['tm_hand']).mean():.4%}")

    for min_conf in [["high"], ["high", "medium"]]:
        oc = order_consistency_check(train_match_keys, trackman_clean, pitcher_mapping_v3, min_confidence=min_conf)
        print(f"순서 정합 sanity check (confidence in {min_conf}): {oc}")

    row_matches_v3 = match_rows(train_match_keys, trackman_clean, pitcher_mapping_v3, confidences=("high", "medium"))
    rm3 = report_row_match_quality("v3 (반복정제)", row_matches_v3, train_match_keys, trackman_clean, len(train_raw))
    print("pitcher_confidence x row_confidence 교차표:")
    print(pd.crosstab(row_matches_v3["pitcher_confidence"], row_matches_v3["row_confidence"]))

    conf_pids_v3 = pitcher_mapping_v3[pitcher_mapping_v3["confidence"].isin(["high", "medium"])]["pitcher_id"]
    own_rows3 = train_raw[train_raw["pitcher_id"].isin(conf_pids_v3)]
    print(f"v3 confident 투수({len(conf_pids_v3)}명)의 자기 행 수: {len(own_rows3)}, 그 중 매칭된 비율: {len(row_matches_v3) / len(own_rows3):.4%}")

    print()
    print("--- is_illegal_count(trackman) 매칭된 행 중 대응 여부 (v3) ---")
    illegal_matched = row_matches_v3[row_matches_v3["trackman_is_illegal_count"]]
    print(f"매칭된 행 중 trackman 카운트-위반 플래그가 있는 행: {len(illegal_matched)} (전체 위반 97건 중)")

    print()
    print("--- Step C에서 매칭 안 된 confident 투수 행들 중, 후보 자체가 없는(진짜 커버리지 갭) 비율 ---")
    matched_ids = set(row_matches_v3["row_id"])
    unmatched = own_rows3[~own_rows3["row_id"].isin(matched_ids)]
    unmatched2 = unmatched.merge(train_match_keys[["row_id", "situational_key"]], on="row_id")
    pid2tmid3 = dict(zip(conf_pids_v3, pitcher_mapping_v3.set_index("pitcher_id").loc[conf_pids_v3, "matched_pitcher_trackman_id"]))
    unmatched2["tmid"] = unmatched2["pitcher_id"].map(pid2tmid3)
    tm_keys_by_pitcher = trackman_clean.groupby("pitcher_trackman_id")["situational_key"].apply(set).to_dict()
    unmatched2["has_candidate"] = unmatched2.apply(lambda row: row["situational_key"] in tm_keys_by_pitcher.get(row["tmid"], set()), axis=1)
    print(f"매칭 안 된 {len(unmatched2)}행 중, 해당 투수의 trackman 데이터에 같은 situational_key가 아예 없는(진짜 데이터 공백) 행: {(~unmatched2['has_candidate']).sum()} ({(~unmatched2['has_candidate']).mean():.4%})")

    print()
    print("=" * 70)
    print("저장")
    print("=" * 70)
    pitcher_mapping_v1.to_csv(os.path.join(TABLES_DIR, "pitcher_mapping_v1.csv"), index=False, encoding="utf-8-sig")
    row_matches_v1.to_csv(os.path.join(TABLES_DIR, "row_mapping_v1.csv"), index=False, encoding="utf-8-sig")
    direct.to_csv(os.path.join(TABLES_DIR, "row_mapping_v2_step_a_direct.csv"), index=False, encoding="utf-8-sig")
    pitcher_mapping_v2.to_csv(os.path.join(TABLES_DIR, "pitcher_mapping_v2_single_round.csv"), index=False, encoding="utf-8-sig")
    row_matches_v2.to_csv(os.path.join(TABLES_DIR, "row_mapping_v2_single_round.csv"), index=False, encoding="utf-8-sig")
    pitcher_mapping_v3.to_csv(os.path.join(TABLES_DIR, "pitcher_mapping.csv"), index=False, encoding="utf-8-sig")
    row_matches_v3.to_csv(os.path.join(TABLES_DIR, "row_mapping.csv"), index=False, encoding="utf-8-sig")
    print("저장 완료: pitcher_mapping_v1/row_mapping_v1 (폐기, 참고용),")
    print("          pitcher_mapping_v2_single_round/row_mapping_v2_single_round (1회 Step A/B, 참고용),")
    print("          pitcher_mapping.csv / row_mapping.csv (v3 반복정제, 주 결과)")


if __name__ == "__main__":
    main()
