"""Command-line entry point for the CatBoost feature-ablation submission.

Examples:
    python run.py build --data-dir /path/to/data
    python run.py validate --data-dir /path/to/data
    python run.py experiment --data-dir /path/to/data --experiments main55_fixed
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.pipeline import (
    FINAL_ITERATIONS,
    ModelConfig,
    build_submission,
    run_experiments,
    validate_submission_zip,
)


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = HERE / "output"


def add_model_arguments(parser: argparse.ArgumentParser, default_iterations: int) -> None:
    parser.add_argument("--iterations", type=int, default=default_iterations)
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--l2-leaf-reg", type=float, default=3.0)
    parser.add_argument("--subsample", type=float, default=0.7)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--thread-count", type=int, default=8)


def model_config(args: argparse.Namespace) -> ModelConfig:
    return ModelConfig(
        iterations=args.iterations,
        depth=args.depth,
        learning_rate=args.learning_rate,
        l2_leaf_reg=args.l2_leaf_reg,
        subsample=args.subsample,
        seed=args.seed,
        thread_count=args.thread_count,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CatBoost 피처 실험 및 제출 패키지 생성")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="최종 모델과 submit.zip 생성")
    build_parser.add_argument("--data-dir", type=Path, required=True)
    build_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    add_model_arguments(build_parser, FINAL_ITERATIONS)

    validation_parser = subparsers.add_parser(
        "validate", help="생성된 submit.zip을 5개 행으로 실행 검증"
    )
    validation_parser.add_argument("--data-dir", type=Path, required=True)
    validation_parser.add_argument(
        "--zip-path", type=Path, default=DEFAULT_OUTPUT_DIR / "submit.zip"
    )
    validation_parser.add_argument("--sample-rows", type=int, default=5)

    experiment_parser = subparsers.add_parser(
        "experiment", help="시즌 순서 검증으로 피처 구성을 비교"
    )
    experiment_parser.add_argument("--data-dir", type=Path, required=True)
    experiment_parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR / "experiments"
    )
    experiment_parser.add_argument(
        "--experiments", nargs="+", default=["raw47_catboost", "main55_fixed"]
    )
    experiment_parser.add_argument(
        "--validation-seasons", type=int, nargs="+", default=[2024]
    )
    add_model_arguments(experiment_parser, 300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "build":
        result = build_submission(
            args.data_dir, args.output_dir, config=model_config(args)
        )
    elif args.command == "validate":
        result = validate_submission_zip(
            args.data_dir, args.zip_path, sample_rows=args.sample_rows
        )
    else:
        frame = run_experiments(
            args.data_dir,
            args.output_dir,
            experiments=args.experiments,
            validation_seasons=args.validation_seasons,
            config=model_config(args),
        )
        result = frame.to_dict(orient="records")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
