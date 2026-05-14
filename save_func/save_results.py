import os
from openpyxl import Workbook


from openpyxl import Workbook
import os

def save_results_to_excel(results, save_dir="data", filename="results.xlsx"):

    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    wb = Workbook()
    ws = wb.active
    ws.title = "results"

    # =========================
    # 헤더
    # =========================
    headers = [
        "premise",
        "option1",
        "option2",
        "task_type",

        "dist1",
        "dist2",
        "dir1",
        "dir2",

        "correct_answer",
        "response",
        "rt",
        "is_correct"
    ]
    ws.append(headers)

    # =========================
    # 데이터
    # =========================
    for r in results:
        ws.append([
            r.get("premise"),
            r.get("option1"),
            r.get("option2"),
            r.get("task_type"),

            r.get("dist1"),
            r.get("dist2"),
            r.get("dir1"),
            r.get("dir2"),

            r.get("correct"),   # 이름 맞춤
            r.get("response"),
            r.get("rt"),
            r.get("is_correct")
        ])

    wb.save(file_path)

    return file_path


def save_results_to_excel_A(results, save_dir="data", filename="results.xlsx"):

    # =========================
    # 1. 폴더 생성
    # =========================
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    # =========================
    # 2. 워크북 생성
    # =========================
    wb = Workbook()
    ws = wb.active
    ws.title = "results"

    # =========================
    # 3. 헤더
    # =========================
    headers = [
        "trial_index",
        "prey",
        "predator",
        "correct_answer",   # 1 (O) / 0 (X)
        "response",         # 1 / 0 / None
        "rt",
        "is_correct"
    ]
    ws.append(headers)

    # =========================
    # 4. 데이터 기록
    # =========================
    for i, r in enumerate(results, start=1):

        ws.append([
            i,
            r.get("prey"),
            r.get("predator"),
            r.get("correct_answer"),
            r.get("response"),
            r.get("rt"),
            r.get("is_correct")
        ])

    # =========================
    # 5. 저장
    # =========================
    wb.save(file_path)

    print(f"Saved to: {file_path}")
    return file_path