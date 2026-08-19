"""model/ 안의 학습된 아티팩트 + submission/script.py + requirements.txt를
Dacon 제출 규격(model/, script.py, requirements.txt가 zip 최상위에 바로
있어야 함)에 맞춰 submission/submit.zip으로 패키징한다.

사용법:
    python src/package_submission.py exp001_lgbm

- submission/submit.zip: 항상 최신 빌드 (Dacon에 이 파일을 업로드)
- submission/archive/<label>/: 그 실험에서 실제로 쓰인 model/, script.py,
  requirements.txt 원본 그대로 + 그때 만든 submit.zip까지 통째로 보존
  (압축을 안 풀어도 파일을 바로 열어볼 수 있고, 나중에 모델 종류가
  바뀌어도 이전 버전 정보가 사라지지 않음)
"""

import argparse
import os
import shutil
import zipfile

MODEL_DIR = "./model"
SUBMISSION_DIR = "./submission"


def _fresh_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def build(label):
    # 1) submission/model/: 압축 대상 스테이징. 매번 비우고 ./model/의
    #    현재 내용으로 다시 채운다 - 안 비우면 예전 실험에서 쓰던 파일이
    #    (예: 모델 종류를 바꿔서 파일명이 달라진 경우) 계속 남아 쌓인다.
    sub_model_dir = os.path.join(SUBMISSION_DIR, "model")
    _fresh_dir(sub_model_dir)
    for fname in os.listdir(MODEL_DIR):
        if fname == ".gitkeep":
            continue
        shutil.copy2(os.path.join(MODEL_DIR, fname), os.path.join(sub_model_dir, fname))

    # exp_002부터: submission/script.py가 src/features.py를 그대로 import해서
    # 쓰므로(더 이상 피처 로직을 손으로 복붙하지 않음), 그 소스를 zip에 같이
    # 넣어야 한다. Dacon 공식 구조는 zip 최상위가 정확히 model/, script.py,
    # requirements.txt여야 한다고 명시되어 있어 최상위에 4번째 파일을 얹지
    # 않고, model/ 폴더 "안"에 넣는다 (model/ 내부 파일 구성 자체는 제약이
    # 없음 — lgbm_booster.txt/lgbm_meta.pkl도 이미 자유롭게 여기 들어있음).
    shutil.copy2("./src/features.py", os.path.join(sub_model_dir, "features.py"))

    script_path = os.path.join(SUBMISSION_DIR, "script.py")
    req_path = os.path.join(SUBMISSION_DIR, "requirements.txt")

    # 2) submission/submit.zip: 항상 최신 빌드, 이 이름 고정.
    zip_path = os.path.join(SUBMISSION_DIR, "submit.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)

    entries = {"script.py": script_path, "requirements.txt": req_path}
    for fname in os.listdir(sub_model_dir):
        entries[f"model/{fname}"] = os.path.join(sub_model_dir, fname)

    # zipfile은 arcname을 준 그대로 저장한다 (OS와 무관하게 '/' 를 직접
    # 넣어주면 Linux 평가 서버에서도 정상적으로 model/ 하위 폴더로 풀림).
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, path in entries.items():
            zf.write(path, arcname)

    # 3) submission/archive/<label>/: 이번 빌드에 쓰인 원본 파일 전체를
    #    라벨별 폴더로 통째 보존 (같은 라벨로 다시 실행하면 그 라벨만
    #    깨끗하게 덮어씀 - 다른 라벨의 기록은 건드리지 않음).
    archive_dir = os.path.join(SUBMISSION_DIR, "archive", label)
    _fresh_dir(archive_dir)
    shutil.copytree(sub_model_dir, os.path.join(archive_dir, "model"))
    shutil.copy2(script_path, os.path.join(archive_dir, "script.py"))
    shutil.copy2(req_path, os.path.join(archive_dir, "requirements.txt"))
    shutil.copy2(zip_path, os.path.join(archive_dir, "submit.zip"))

    print(f"Built:    {zip_path}  (Dacon에 이 파일을 업로드)")
    print(f"Archived: {archive_dir}/  (model/, script.py, requirements.txt 원본 + submit.zip 보존)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("label", help="예: exp001_lgbm")
    args = parser.parse_args()
    build(args.label)
