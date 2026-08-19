from __future__ import annotations

import argparse
import json
from pathlib import Path

from .builder import build_final_package, validate_package
from .config import (
    BASELINE_ROOT,
    DEFAULT_DATA_DIR,
    PROJECT_ROOT,
    resolve_final,
    resolve_study,
)
from .registry import (
    VALID_DECISIONS,
    create_experiment,
    decide_experiment,
    migrate_legacy_run_snapshots,
    plan_experiment,
    rebuild_index,
    run_experiment,
    show_experiment,
)
from .runner import check_feature_configs, run_study


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LG Aimers 실험 관리자")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser(
        "plan", help="학습 없이 control 대비 설정 차이 확인"
    )
    plan.add_argument("--study", type=Path, required=True)

    check = subparsers.add_parser(
        "check", help="실제 데이터 헤더로 설정과 피처 개수 검사"
    )
    check.add_argument("--study", type=Path, required=True)
    check.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)

    study = subparsers.add_parser("study", help="ablation study 실행")
    study.add_argument("--study", type=Path, required=True)
    study.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    study.add_argument("--runs-dir", type=Path, default=PROJECT_ROOT / "runs")
    study.add_argument("--only", nargs="+", help="control과 지정 variant만 실행")
    study.add_argument(
        "--no-predictions", action="store_true", help="fold별 예측 저장 생략"
    )

    build = subparsers.add_parser("build", help="선택된 최종 설정으로 제출 ZIP 생성")
    build.add_argument("--config", type=Path, default=BASELINE_ROOT / "final.toml")
    build.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    build.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "output/final")

    validate = subparsers.add_parser("validate-package", help="제출 ZIP 독립 실행 검사")
    validate.add_argument("--zip-path", type=Path, required=True)
    validate.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    validate.add_argument("--sample-rows", type=int, default=5)

    exp_new = subparsers.add_parser(
        "exp-new", help="다음 EXP_NNN 번호와 실험 템플릿 생성"
    )
    exp_new.add_argument("--title", required=True)
    exp_new.add_argument("--hypothesis", required=True)
    exp_new.add_argument("--scope", choices=["features", "model"], required=True)
    exp_new.add_argument(
        "--based-on", "--parent", dest="based_on", default="BASELINE_001_main55"
    )
    exp_new.add_argument("--reference-variant", default="main55_control")
    exp_new.add_argument("--ablation", required=True)
    exp_new.add_argument("--tags", nargs="*", default=[])

    exp_plan = subparsers.add_parser(
        "exp-plan", help="등록 실험의 변경점과 실행 준비 상태 확인"
    )
    exp_plan.add_argument("experiment_id")

    exp_run = subparsers.add_parser(
        "exp-run", help="EXP_NNN 실행 후 RUN_NNN 결과 자동 기록"
    )
    exp_run.add_argument("experiment_id")
    exp_run.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    exp_run.add_argument("--runs-dir", type=Path, default=PROJECT_ROOT / "runs")
    exp_run.add_argument("--only", nargs="+")
    exp_run.add_argument("--no-predictions", action="store_true")

    subparsers.add_parser("exp-list", help="전체 실험 인덱스 표시")

    exp_show = subparsers.add_parser(
        "exp-show", help="한 실험의 가설·실행·판단 이력 표시"
    )
    exp_show.add_argument("experiment_id")
    exp_show.add_argument("--history", action="store_true")

    exp_decide = subparsers.add_parser(
        "exp-decide", help="완료된 실험의 채택·기각 판단 기록"
    )
    exp_decide.add_argument("experiment_id")
    exp_decide.add_argument("--decision", choices=sorted(VALID_DECISIONS), required=True)
    exp_decide.add_argument("--reason", required=True)
    exp_decide.add_argument("--selected-variant")
    subparsers.add_parser(
        "exp-migrate-snapshots",
        help="기존 RUN_NNN.json을 완전 설정 snapshot 폴더로 이전",
    )
    return parser.parse_args()


def _plan_payload(resolved: dict) -> dict:
    return {
        "study": resolved["study"],
        "protocol": resolved["protocol"],
        "config_hash": resolved["config_hash"],
        "variants": [
            {
                "name": variant["name"],
                "change": variant["change"],
                "model": variant["model"]["name"],
                "features": variant["features"]["name"],
                "changed_fields_vs_control": variant[
                    "changed_fields_vs_control"
                ],
            }
            for variant in resolved["variants"]
        ],
    }


def main() -> None:
    args = parse_args()
    if args.command == "exp-new":
        result = create_experiment(
            title=args.title,
            hypothesis=args.hypothesis,
            change_scope=args.scope,
            ablation_summary=args.ablation,
            based_on=args.based_on,
            reference_variant=args.reference_variant,
            tags=args.tags,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "exp-migrate-snapshots":
        result = migrate_legacy_run_snapshots()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "exp-plan":
        result = plan_experiment(args.experiment_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "exp-run":
        result = run_experiment(
            args.experiment_id,
            data_dir=args.data_dir,
            raw_runs_root=args.runs_dir,
            only=args.only,
            store_predictions=False if args.no_predictions else None,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "exp-list":
        rows = rebuild_index()
        columns = [
            "id", "title", "based_on", "status", "run_count", "latest_run",
            "best_variant", "delta_brier", "decision", "selected_variant",
        ]
        if not rows:
            print("등록된 실험이 없습니다.")
            return
        widths = {
            column: max(
                len(column),
                *(
                    len(
                        str(
                            "-"
                            if row.get(column) is None or row.get(column) == ""
                            else row.get(column)
                        )
                    )
                    for row in rows
                ),
            )
            for column in columns
        }
        print("  ".join(column.ljust(widths[column]) for column in columns))
        print("  ".join("-" * widths[column] for column in columns))
        for row in rows:
            print(
                "  ".join(
                    str(
                        "-"
                        if row.get(column) is None or row.get(column) == ""
                        else row.get(column)
                    ).ljust(widths[column])
                    for column in columns
                )
            )
        return
    if args.command == "exp-show":
        result = show_experiment(args.experiment_id, include_history=args.history)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "exp-decide":
        result = decide_experiment(
            args.experiment_id,
            decision=args.decision,
            reason=args.reason,
            selected_variant=args.selected_variant,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.command in {"plan", "check", "study"}:
        resolved = resolve_study(args.study)
    if args.command == "plan":
        result = _plan_payload(resolved)
    elif args.command == "check":
        result = check_feature_configs(resolved, args.data_dir)
    elif args.command == "study":
        run_dir = run_study(
            resolved,
            data_dir=args.data_dir,
            runs_root=args.runs_dir,
            only=args.only,
            store_predictions=False if args.no_predictions else None,
        )
        result = {"status": "complete", "run_dir": str(run_dir)}
    elif args.command == "build":
        result = build_final_package(
            resolve_final(args.config),
            data_dir=args.data_dir,
            output_dir=args.output_dir,
        )
    else:
        result = validate_package(
            data_dir=args.data_dir,
            zip_path=args.zip_path,
            sample_rows=args.sample_rows,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
