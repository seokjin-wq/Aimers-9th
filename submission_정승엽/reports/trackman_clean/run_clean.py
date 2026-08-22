"""Phase 1 실행 스크립트 — trackman_history.csv 정제 + train 매칭 키 생성.

원본 data/trackman_history.csv, data/train.csv는 읽기만 하고 수정하지
않는다. 산출물은 모두 새 파일로 data/processed/에 쓴다:
    data/processed/trackman_clean.csv
    data/processed/train_match_keys.csv

실행:
    python reports/trackman_clean/run_clean.py

표준출력을 reports/trackman_clean/clean_run_log.txt 로 리다이렉트해서
보관 — README.md의 모든 수치는 이 로그에서만 가져온다 (기존
reports/eda_trackman 관례와 동일).
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pandas as pd

from trackman_clean import clean_trackman, build_train_match_keys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
OUT_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    print("=" * 70)
    print("1. 원본 로드")
    print("=" * 70)
    tm_raw = pd.read_csv(
        os.path.join(DATA_DIR, "trackman_history.csv"), encoding="utf-8-sig"
    )
    train_raw = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig")
    print(f"trackman_history.csv: {tm_raw.shape}")
    print(f"train.csv: {train_raw.shape}")

    print()
    print("=" * 70)
    print("2. trackman 정제 (clean_trackman)")
    print("=" * 70)
    tm_clean = clean_trackman(tm_raw)

    print("--- tagged_pitch_type: 정제 전/후 unique 값 개수 ---")
    print(f"전: {tm_raw['tagged_pitch_type'].nunique()}  후: {tm_clean['tagged_pitch_type_clean'].nunique()}")
    print("병합된 값 -> canonical:")
    changed = tm_raw["tagged_pitch_type"] != tm_clean["tagged_pitch_type_clean"]
    print(
        tm_raw.loc[changed, "tagged_pitch_type"]
        .value_counts()
        .to_frame("raw_count")
        .assign(
            canonical=lambda d: d.index.map(
                lambda v: tm_clean.loc[tm_raw["tagged_pitch_type"] == v, "tagged_pitch_type_clean"].iloc[0]
            )
        )
    )

    print()
    print("--- auto_pitch_type: 정제 전/후 unique 값 개수 ---")
    print(f"전: {tm_raw['auto_pitch_type'].nunique()}  후: {tm_clean['auto_pitch_type_clean'].nunique()}")
    changed = tm_raw["auto_pitch_type"] != tm_clean["auto_pitch_type_clean"]
    changed = changed & tm_raw["auto_pitch_type"].notna()
    print(
        tm_raw.loc[changed, "auto_pitch_type"]
        .value_counts()
        .to_frame("raw_count")
        .assign(
            canonical=lambda d: d.index.map(
                lambda v: tm_clean.loc[tm_raw["auto_pitch_type"] == v, "auto_pitch_type_clean"].iloc[0]
            )
        )
    )

    print()
    print("--- pitcher_team_tier 분포 (trackman) ---")
    print(tm_clean["pitcher_team_tier"].value_counts(dropna=False))
    print()
    print("--- pitcher_team -> pitcher_team_franchise 매핑 (26개 코드 -> 프랜차이즈) ---")
    print(
        tm_clean[["pitcher_team", "pitcher_team_tier", "pitcher_team_franchise"]]
        .drop_duplicates()
        .sort_values(["pitcher_team_franchise", "pitcher_team_tier"])
        .to_string(index=False)
    )

    print()
    print("--- is_illegal_count 플래그 (trackman) ---")
    n_illegal = tm_clean["is_illegal_count"].sum()
    print(f"플래그된 행: {n_illegal} / {len(tm_clean)} ({n_illegal / len(tm_clean):.4%})")
    print("season/game_month 분포:")
    print(tm_clean.loc[tm_clean["is_illegal_count"], ["season", "game_month"]].value_counts().sort_index())
    print(f"관련 pitcher_trackman_id 고유 수: {tm_clean.loc[tm_clean['is_illegal_count'], 'pitcher_trackman_id'].nunique()}")

    print()
    print("--- game_date_parsed: 파싱 실패(NaT) 건수 ---")
    n_nat = tm_clean["game_date_parsed"].isna().sum()
    print(f"NaT: {n_nat} / {len(tm_clean)}")
    match_rate = (tm_clean["game_date_parsed"].dt.month == tm_clean["game_month"]).mean()
    print(f"game_date_parsed 월 vs game_month 일치율: {match_rate:.4%}")

    print()
    print("--- situational_key 유일성(참고): 전체 행 중 situational_key 중복 비율 ---")
    dup_rate = tm_clean.duplicated(subset=["situational_key", "pitcher_trackman_id"]).mean()
    print(f"(situational_key, pitcher_trackman_id) 중복 행 비율: {dup_rate:.4%}")

    print()
    print("=" * 70)
    print("3. train 매칭 키 생성 (build_train_match_keys)")
    print("=" * 70)
    train_keys = build_train_match_keys(train_raw)
    print(f"train_match_keys shape: {train_keys.shape}")
    print()
    print("--- team_tier(=game_type 기반) 분포 (train) ---")
    print(train_keys["team_tier"].value_counts(dropna=False))
    print()
    print("--- pitcher_team_id x team_tier 교차표 (train) ---")
    print(pd.crosstab(train_keys["pitcher_team_id"], train_keys["team_tier"]))
    print()
    print("--- is_illegal_count 플래그 (train) ---")
    n_illegal_train = train_keys["is_illegal_count"].sum()
    print(f"플래그된 행: {n_illegal_train} / {len(train_keys)} ({n_illegal_train / len(train_keys):.4%})")

    print()
    print("=" * 70)
    print("4. 저장")
    print("=" * 70)
    tm_out_path = os.path.join(OUT_DIR, "trackman_clean.csv")
    train_out_path = os.path.join(OUT_DIR, "train_match_keys.csv")
    tm_clean.to_csv(tm_out_path, index=False, encoding="utf-8-sig")
    train_keys.to_csv(train_out_path, index=False, encoding="utf-8-sig")
    print(f"저장: {tm_out_path}  ({tm_clean.shape})")
    print(f"저장: {train_out_path}  ({train_keys.shape})")

    print()
    print("--- 원본 파일 미변경 확인 ---")
    tm_raw2 = pd.read_csv(os.path.join(DATA_DIR, "trackman_history.csv"), encoding="utf-8-sig")
    train_raw2 = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig")
    print("trackman_history.csv 재로드 shape 일치:", tm_raw2.shape == tm_raw.shape)
    print("train.csv 재로드 shape 일치:", train_raw2.shape == train_raw.shape)


if __name__ == "__main__":
    main()
