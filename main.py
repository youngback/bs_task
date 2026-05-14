from psychopy import visual, core, event
from openpyxl import Workbook
from phase_func.both_question import run_both_task
from phase_func.food_web_check import run_foodweb_task
from phase_func.gene_check import run_gene_task
from phase_func.fixation import attention_check
from phase_func.show_info import show_all_food_phase,  show_all_gene_phase
from save_func.save_results import save_results_to_excel, save_results_to_excel_A
from initiate import initiate
from utils.labjack_trigger import init_labjack
import random
import os
#.\new_ven\Scripts\activate  이후 python main.py 

def main():
    save_directory,handle = initiate()
    init_labjack()

    win = visual.Window(
        size=(1280, 800),
        fullscr=True,
        units="pix",
        color="light_gray"
    )


     # 질문 한국어로 수정
    # ui를 이전 태스크랑 유사하게
    # 지금 테스크를 LLM에 제로샷으로 풀게했을때 스트럭처가 나타날것인가?
    # LLM의 대답으로 스트럭처를 이용했는지 판단할수있나? (그게 학습된 방대한 데이터에 의한건지 prior구조에 의한건지 )
    # reasoning model / non-reasoning model
    # api key
    # 개개인이 가진 structure prior를 답변으로부터 유추할수있는지

    json_path = os.path.join("stimuli", "web.json")

    show_all_food_phase(win, handle)
    show_all_gene_phase(win, handle)

    results0 =run_foodweb_task(win, json_path,handle)

    save_results_to_excel_A(results0, save_directory, "results_cf.xlsx")

    results1 =run_gene_task(win, json_path,handle)

    save_results_to_excel_A(results1, save_directory, "results_cg.xlsx")

    attention_check(win)


    results = run_both_task(win, json_path, handle)
    
    save_results_to_excel(results,save_directory, "results_t.xlsx")

    print(results)

    win.close()
    core.quit()


if __name__ == "__main__":
    main()