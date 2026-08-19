"""Trackman 기본 EDA — data/trackman_history.csv (2019~2024, 30개 컬럼).

담당 컬럼 (전체 30개, 6개 그룹으로 묶어서 분석):
    시간 정보 (4):   season, game_date, game_month, game_dayofweek
    식별자 (5):      trackman_id, trackman_game_id, pitch_no,
                     pitcher_trackman_id, batter_trackman_id
    손유형·팀 (4):    pitcher_hand, batter_hand, pitcher_team, batter_team
    경기 상황 (6):    inning, top_bottom, balls_before, strikes_before,
                     outs_before, pitch_of_pa
    구종 분류 (3):    tagged_pitch_type, auto_pitch_type, pitch_type_group
    수치형 특성 (8):  rel_speed, spin_rate, induced_vert_break, horz_break,
                     extension, rel_height, rel_side, zone_speed

이 스크립트는 trackman_history.csv를 읽고(§8만 예외적으로 train.csv에서
ID 비교용 컬럼 4개만 추가로 읽음), 행 단위 통계와 group-by 집계만 수행한다.
trackman_history.csv는 train.csv/test.csv와 1:1로 결합되는 테이블이
아니므로(docs/data_description.md §3), 여기서 나온 어떤 집계값도 그대로
test.csv 피처로 옮기지 않는다 — 실제 피처화 시에는 반드시 season/game_month
기준 as-of 컷오프를 적용해야 한다(CLAUDE.md 규칙 10).

실행:
    python reports/eda_trackman/run_eda.py

산출물:
    reports/eda_trackman/figures/*.png
    reports/eda_trackman/tables/*.csv
    (표준출력을 reports/eda_trackman/eda_run_log.txt 로 리다이렉트해서 보관 —
     README.md의 모든 수치는 이 로그에서만 가져온다)
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

DATA_DIR = "./data"
OUT_DIR = "./reports/eda_trackman"
FIG_DIR = os.path.join(OUT_DIR, "figures")
TAB_DIR = os.path.join(OUT_DIR, "tables")

TIME_COLS = ["season", "game_date", "game_month", "game_dayofweek"]
ID_COLS = ["trackman_id", "trackman_game_id", "pitch_no", "pitcher_trackman_id", "batter_trackman_id"]
HANDTEAM_COLS = ["pitcher_hand", "batter_hand", "pitcher_team", "batter_team"]
SITUATION_COLS = ["inning", "top_bottom", "balls_before", "strikes_before", "outs_before", "pitch_of_pa"]
PITCHTYPE_COLS = ["tagged_pitch_type", "auto_pitch_type", "pitch_type_group"]
NUMERIC_COLS = ["rel_speed", "spin_rate", "induced_vert_break", "horz_break", "extension", "rel_height", "rel_side", "zone_speed"]
ALL_COLS = TIME_COLS + ID_COLS + HANDTEAM_COLS + SITUATION_COLS + PITCHTYPE_COLS + NUMERIC_COLS


def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_data():
    df = pd.read_csv(
        os.path.join(DATA_DIR, "trackman_history.csv"), encoding="utf-8-sig", usecols=ALL_COLS
    )
    return df


def step1_quality(df):
    section("1. 데이터 품질/구조 확인")
    print(f"trackman_history.csv shape: {df.shape}")
    missing_cols = [c for c in ALL_COLS if c not in df.columns]
    print(f"누락된 컬럼: {missing_cols if missing_cols else '없음 (전부 존재, 30개)'}")

    rows = []
    for c in ALL_COLS:
        s = df[c]
        is_num = pd.api.types.is_numeric_dtype(s)
        rows.append(
            {
                "column": c,
                "dtype": str(s.dtype),
                "n_null": int(s.isna().sum()),
                "null_rate_pct": s.isna().mean() * 100,
                "n_unique": int(s.nunique()),
                "min": s.min() if is_num else "",
                "max": s.max() if is_num else "",
            }
        )
    quality = pd.DataFrame(rows)
    print(quality.to_string(index=False))
    quality.to_csv(os.path.join(TAB_DIR, "00_quality_summary.csv"), index=False)

    dup = int(df.duplicated().sum())
    dup_id = int(df["trackman_id"].duplicated().sum())
    print(f"\n완전 중복행: {dup}건")
    print(f"trackman_id 중복: {dup_id}건 (0이어야 행 고유 식별자로 타당)")
    return quality


def step2_time_coverage(df):
    section("2. 시간 범위 커버리지")
    df = df.copy()
    # game_date 형식이 시즌마다 다르다: 2019~2021은 'MM/DD/YYYY', 2022~2024는
    # 'YYYY-MM-DD' (ISO). 단일 format을 강제하면 절반 가까이 파싱 실패가 나서
    # (실제로 최초 시도에서 확인됨) 슬래시/하이픈 형식을 나눠서 각각 파싱한다.
    is_slash = df["game_date"].str.contains("/", na=False)
    parsed = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    parsed.loc[is_slash] = pd.to_datetime(df.loc[is_slash, "game_date"], format="%m/%d/%Y", errors="coerce")
    parsed.loc[~is_slash] = pd.to_datetime(df.loc[~is_slash, "game_date"], format="%Y-%m-%d", errors="coerce")
    df["game_date_parsed"] = parsed
    n_bad_date = int(df["game_date_parsed"].isna().sum())
    print(f"game_date 형식: '/' 포함(MM/DD/YYYY) {int(is_slash.sum()):,}행, "
          f"'-' 포함(YYYY-MM-DD) {int((~is_slash).sum()):,}행 — 시즌별로 형식이 다름")
    print(f"game_date 파싱 실패 행 수: {n_bad_date}")
    print(f"game_date 범위: {df['game_date_parsed'].min()} ~ {df['game_date_parsed'].max()}")

    month_from_date = df["game_date_parsed"].dt.month
    month_match_rate = (month_from_date == df["game_month"]).mean()
    print(f"game_date에서 추출한 월 vs game_month 컬럼 일치율: {month_match_rate*100:.4f}%")

    season_counts = df["season"].value_counts().sort_index()
    month_counts = df["game_month"].value_counts().sort_index()
    dow_counts = df["game_dayofweek"].value_counts().sort_index()
    print("\n[season별 행 수]")
    print(season_counts.to_string())
    print("\n[game_month별 행 수]")
    print(month_counts.to_string())
    print("\n[game_dayofweek별 행 수]")
    print(dow_counts.to_string())
    season_counts.to_csv(os.path.join(TAB_DIR, "02_season_counts.csv"), header=["n"])
    month_counts.to_csv(os.path.join(TAB_DIR, "02_month_counts.csv"), header=["n"])
    dow_counts.to_csv(os.path.join(TAB_DIR, "02_dayofweek_counts.csv"), header=["n"])

    sm = df.groupby(["season", "game_month"]).size().unstack(fill_value=0)
    print("\n[season x game_month 행 수]")
    print(sm.to_string())
    sm.to_csv(os.path.join(TAB_DIR, "02_season_month_grid.csv"))

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes[0, 0].bar(season_counts.index.astype(str), season_counts.values, color="#4C72B0")
    axes[0, 0].set_title("season 별 투구 수")
    axes[0, 1].bar(month_counts.index.astype(str), month_counts.values, color="#55A868")
    axes[0, 1].set_title("game_month 별 투구 수")
    axes[1, 0].bar(dow_counts.index.astype(str), dow_counts.values, color="#C44E52")
    axes[1, 0].set_title("game_dayofweek 별 투구 수 (0=월)")
    im = axes[1, 1].imshow(sm.values, cmap="viridis", aspect="auto")
    axes[1, 1].set_xticks(range(len(sm.columns)))
    axes[1, 1].set_xticklabels(sm.columns)
    axes[1, 1].set_yticks(range(len(sm.index)))
    axes[1, 1].set_yticklabels(sm.index)
    axes[1, 1].set_title("season x game_month 행 수")
    fig.colorbar(im, ax=axes[1, 1])
    fig.suptitle("Trackman — 시간 범위 커버리지 (4개 컬럼)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "01_grid_time_coverage.png"), dpi=120)
    plt.close(fig)
    return season_counts, month_counts, dow_counts, sm


def step3_id_team(df):
    section("3. 식별자 및 선수·팀 특성")
    rows = []
    for c in ID_COLS:
        s = df[c]
        rows.append({"column": c, "n_unique": int(s.nunique()), "min": s.min(), "max": s.max()})
    id_summary = pd.DataFrame(rows)
    print(id_summary.to_string(index=False))
    id_summary.to_csv(os.path.join(TAB_DIR, "03_id_summary.csv"), index=False)

    pitcher_counts = df.groupby("pitcher_trackman_id").size()
    batter_counts = df.groupby("batter_trackman_id").size()
    print(f"\n투수당 투구 수: n_unique={len(pitcher_counts)}, median={pitcher_counts.median():.1f}, "
          f"min={pitcher_counts.min()}, max={pitcher_counts.max()}")
    print(f"타자당 상대 투구 수: n_unique={len(batter_counts)}, median={batter_counts.median():.1f}, "
          f"min={batter_counts.min()}, max={batter_counts.max()}")
    pitcher_counts.describe().to_csv(os.path.join(TAB_DIR, "03_pitcher_pitch_count_describe.csv"))
    batter_counts.describe().to_csv(os.path.join(TAB_DIR, "03_batter_pitch_count_describe.csv"))

    team_p = df["pitcher_team"].value_counts().sort_index()
    team_b = df["batter_team"].value_counts().sort_index()
    print(f"\n고유 pitcher_team 수: {len(team_p)}")
    print(team_p.to_string())
    print(f"\n고유 batter_team 수: {len(team_b)}")
    print(team_b.to_string())
    team_p.to_csv(os.path.join(TAB_DIR, "03_pitcher_team_counts.csv"), header=["n"])
    team_b.to_csv(os.path.join(TAB_DIR, "03_batter_team_counts.csv"), header=["n"])

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes[0, 0].hist(pitcher_counts, bins=40, color="#4C72B0")
    axes[0, 0].set_title(f"투수당 투구 수 분포 (n_unique={len(pitcher_counts)})")
    axes[0, 1].hist(batter_counts, bins=40, color="#55A868")
    axes[0, 1].set_title(f"타자당 상대 투구 수 분포 (n_unique={len(batter_counts)})")
    axes[1, 0].bar(team_p.index.astype(str), team_p.values, color="#C44E52")
    axes[1, 0].set_title("pitcher_team 별 투구 수")
    axes[1, 0].tick_params(axis="x", rotation=90)
    axes[1, 1].bar(team_b.index.astype(str), team_b.values, color="#8172B2")
    axes[1, 1].set_title("batter_team 별 투구 수")
    axes[1, 1].tick_params(axis="x", rotation=90)
    fig.suptitle("Trackman — 식별자 및 선수·팀 특성")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "02_grid_id_team.png"), dpi=120)
    plt.close(fig)
    return id_summary, team_p, team_b


def step4_situation(df):
    section("4. 경기 상황 변수 (단변량 그리드)")
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, col in zip(axes.flat, SITUATION_COLS):
        vc = df[col].value_counts().sort_index()
        ax.bar(vc.index.astype(str), vc.values, color="#4C72B0")
        ax.set_title(f"{col} (n_levels={len(vc)})")
        ax.tick_params(axis="x", rotation=45 if len(vc) > 6 else 0)
        vc.to_csv(os.path.join(TAB_DIR, f"04_counts_{col}.csv"), header=["n"])
        print(f"\n[{col}]")
        print(vc.to_string())
    fig.suptitle("Trackman — 경기 상황 변수 6개")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "03_grid_situation.png"), dpi=120)
    plt.close(fig)


def step5_pitchtype(df):
    section("5. 구종 분류 체계")
    tagged_vc = df["tagged_pitch_type"].value_counts()
    auto_vc = df["auto_pitch_type"].value_counts()
    group_vc = df["pitch_type_group"].value_counts()
    print("[tagged_pitch_type]")
    print(tagged_vc.to_string())
    print("\n[auto_pitch_type]")
    print(auto_vc.to_string())
    print("\n[pitch_type_group]")
    print(group_vc.to_string())
    tagged_vc.to_csv(os.path.join(TAB_DIR, "05_tagged_pitch_type_counts.csv"), header=["n"])
    auto_vc.to_csv(os.path.join(TAB_DIR, "05_auto_pitch_type_counts.csv"), header=["n"])
    group_vc.to_csv(os.path.join(TAB_DIR, "05_pitch_type_group_counts.csv"), header=["n"])

    for c in PITCHTYPE_COLS:
        print(f"{c} 결측률: {df[c].isna().mean()*100:.4f}%")

    match_rate = (df["tagged_pitch_type"] == df["auto_pitch_type"]).mean()
    print(f"\ntagged_pitch_type == auto_pitch_type 일치율: {match_rate*100:.4f}%")

    season_group = df.groupby(["season", "pitch_type_group"]).size().unstack(fill_value=0)
    season_group_rate = season_group.div(season_group.sum(axis=1), axis=0)
    print("\n[시즌별 pitch_type_group 비율(%)]")
    print((season_group_rate * 100).round(4).to_string())
    season_group_rate.to_csv(os.path.join(TAB_DIR, "05_season_pitch_type_group_rate.csv"))

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    axes[0].bar(group_vc.index.astype(str), group_vc.values, color="#4C72B0")
    axes[0].set_title("pitch_type_group 분포")
    top10 = tagged_vc.head(10)
    axes[1].barh(top10.index[::-1].astype(str), top10.values[::-1], color="#55A868")
    axes[1].set_title("tagged_pitch_type 상위 10")
    for col in season_group_rate.columns:
        axes[2].plot(season_group_rate.index, season_group_rate[col] * 100, marker="o", label=str(col))
    axes[2].set_title("시즌별 pitch_type_group 비율(%)")
    axes[2].legend(fontsize=8)
    fig.suptitle("Trackman — 구종 분류 체계")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "04_grid_pitchtype.png"), dpi=120)
    plt.close(fig)
    return tagged_vc, auto_vc, group_vc, match_rate, season_group_rate


def step6_numeric(df):
    section("6. 수치형 트래킹 특성 분포")
    desc = df[NUMERIC_COLS].describe().T
    desc["n_missing"] = df[NUMERIC_COLS].isna().sum()
    desc["missing_rate_pct"] = df[NUMERIC_COLS].isna().mean() * 100
    print(desc.to_string())
    desc.to_csv(os.path.join(TAB_DIR, "06_numeric_describe.csv"))

    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    for ax, col in zip(axes.flat, NUMERIC_COLS):
        s = df[col].dropna()
        ax.hist(s, bins=50, color="#4C72B0")
        ax.set_title(col)
    for ax in axes.flat[len(NUMERIC_COLS):]:
        ax.axis("off")
    fig.suptitle("Trackman — 수치형 특성 히스토그램 (8개)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "05_grid_numeric_hist.png"), dpi=120)
    plt.close(fig)

    groups = sorted(df["pitch_type_group"].dropna().unique())
    data_speed = [df.loc[df["pitch_type_group"] == g, "rel_speed"].dropna() for g in groups]
    data_spin = [df.loc[df["pitch_type_group"] == g, "spin_rate"].dropna() for g in groups]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    axes[0].boxplot(data_speed)
    axes[0].set_xticks(range(1, len(groups) + 1))
    axes[0].set_xticklabels(groups)
    axes[0].set_title("구종군별 rel_speed 분포")
    axes[1].boxplot(data_spin)
    axes[1].set_xticks(range(1, len(groups) + 1))
    axes[1].set_xticklabels(groups)
    axes[1].set_title("구종군별 spin_rate 분포")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "06_box_speed_spin_by_pitchtype.png"), dpi=120)
    plt.close(fig)

    g = df.groupby("pitch_type_group")[["rel_speed", "spin_rate"]].agg(["count", "mean", "std"])
    print("\n[구종군별 rel_speed / spin_rate 요약]")
    print(g.to_string())
    g.to_csv(os.path.join(TAB_DIR, "06_pitchtype_speed_spin_summary.csv"))
    return desc, g


def step7_missing_outlier(df):
    section("7. 결측치·이상치 점검")
    miss = df[NUMERIC_COLS].isna().mean().sort_values(ascending=False) * 100
    print("[수치형 컬럼 결측률(%)]")
    print(miss.to_string())
    miss.to_csv(os.path.join(TAB_DIR, "07_missing_rate.csv"), header=["missing_rate_pct"])

    # 공식 문서에 물리적 유효범위가 명시돼 있지 않으므로, 고정 임계값을 가정하지
    # 않고 분위수 기반 극단값 비율로만 점검한다 (CLAUDE.md: 근거 없는 가정 금지).
    rows = []
    for col in NUMERIC_COLS:
        s = df[col].dropna()
        lo, hi = s.quantile(0.001), s.quantile(0.999)
        n_out = int(((s < lo) | (s > hi)).sum())
        rows.append(
            {
                "column": col,
                "p0.1%": lo,
                "p99.9%": hi,
                "n_extreme": n_out,
                "pct_extreme": n_out / len(s) * 100 if len(s) else np.nan,
            }
        )
    ext = pd.DataFrame(rows)
    print("\n[분위수 기반 극단값 점검 (0.1% / 99.9% 밖)]")
    print(ext.to_string(index=False))
    ext.to_csv(os.path.join(TAB_DIR, "07_extreme_value_check.csv"), index=False)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(miss.index, miss.values, color="#C44E52")
    ax.set_ylabel("결측률(%)")
    ax.set_title("수치형 트래킹 특성 결측률")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "07_bar_missing_rate.png"), dpi=120)
    plt.close(fig)
    return miss, ext


def step8_train_link(df):
    section("8. train.csv 연결 가능성 재확인")
    train_cols = ["pitcher_id", "batter_id", "pitcher_team_id", "batter_team_id"]
    train_df = pd.read_csv(
        os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=train_cols
    )

    rows = []
    for col in ["pitcher_id", "batter_id"]:
        s = train_df[col]
        rows.append({"dataset": "train", "column": col, "n_unique": int(s.nunique()), "min": s.min(), "max": s.max()})
    for col in ["pitcher_trackman_id", "batter_trackman_id"]:
        s = df[col]
        rows.append({"dataset": "trackman", "column": col, "n_unique": int(s.nunique()), "min": s.min(), "max": s.max()})
    id_compare = pd.DataFrame(rows)
    print(id_compare.to_string(index=False))
    id_compare.to_csv(os.path.join(TAB_DIR, "08_id_space_compare.csv"), index=False)

    train_team_p = train_df["pitcher_team_id"].value_counts().sort_index()
    trackman_team_p = df["pitcher_team"].value_counts().sort_index()
    print(f"\ntrain pitcher_team_id 고유값 수: {len(train_team_p)}")
    print(train_team_p.to_string())
    print(f"\ntrackman pitcher_team 고유값 수: {len(trackman_team_p)}")
    print(trackman_team_p.to_string())
    train_team_p.to_csv(os.path.join(TAB_DIR, "08_train_pitcher_team_id_counts.csv"), header=["n"])
    trackman_team_p.to_csv(os.path.join(TAB_DIR, "08_trackman_pitcher_team_counts.csv"), header=["n"])

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].bar(train_team_p.index.astype(str), train_team_p.values, color="#4C72B0")
    axes[0].set_title(f"train.csv pitcher_team_id (n_unique={len(train_team_p)})")
    axes[0].tick_params(axis="x", rotation=90)
    axes[1].bar(trackman_team_p.index.astype(str), trackman_team_p.values, color="#55A868")
    axes[1].set_title(f"trackman pitcher_team (n_unique={len(trackman_team_p)})")
    axes[1].tick_params(axis="x", rotation=90)
    fig.suptitle("팀 코드 개수/형태 비교 — train.csv vs trackman_history.csv")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "08_bar_team_compare.png"), dpi=120)
    plt.close(fig)
    return id_compare, train_team_p, trackman_team_p


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(TAB_DIR, exist_ok=True)

    df = load_data()
    print(f"전체 행 수: {len(df):,}  |  컬럼 수: {df.shape[1]}")

    step1_quality(df)
    step2_time_coverage(df)
    step3_id_team(df)
    step4_situation(df)
    step5_pitchtype(df)
    step6_numeric(df)
    step7_missing_outlier(df)
    step8_train_link(df)

    section("완료")
    print(f"그래프: {FIG_DIR}")
    print(f"표: {TAB_DIR}")


if __name__ == "__main__":
    main()
