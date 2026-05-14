import json
import random
import os
from collections import deque
from set_opts.visual_opts import UI_CONFIG
from config import WAITING,HEIGHT,WIDTH, HANDLE,FRAME_EXAMPLE_bs,FRAME_EXAMPLE_bf,waiting_frames
from draw_func.draw_marker import draw_white_marker
from utils.labjack_trigger import send_trigger, reset_trigger, TRIG_B_START, TRIG_B_RESPOND
from phase_func.show_info import show_random_food_pair, show_random_gene_single
from phase_func.waiting import random_isi_phase
from psychopy import visual, core, event
from psychopy.visual import TextBox2
from pyjosa.josa import Josa
from stimuli.category import DISEASE_POOL



# =========================S
# 1. JSON 로드
# =========================
def load_both_web(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    animals = data["animals"]
    food_edges = [tuple(e) for e in data["food_edges"]]
    gene_edges = [tuple(e) for e in data["gene_edges"]]

    return animals, food_edges, gene_edges


# =========================
# 2. 그래프 생성
# =========================
def build_graph(edges, bidirectional=False):
    graph = {}

    for a, b in edges:
        graph.setdefault(a, []).append(b)
        if bidirectional:
            graph.setdefault(b, []).append(a)

    return graph


# =========================
# 3. 거리 계산
# =========================
def compute_all_distances(start, graph):
    queue = deque([(start, 0)])
    visited = {}

    while queue:
        node, dist = queue.popleft()

        if node in visited:
            continue

        visited[node] = dist

        for neighbor in graph.get(node, []):
            queue.append((neighbor, dist + 1))

    return visited


def split_by_distance(dist_dict, animals):
    groups = {}

    for a in animals:
        d = dist_dict.get(a, float("inf"))
        groups.setdefault(d, []).append(a)

    return groups

def compute_distance(start, target, graph):
    """
    graph: dict 형태 {node: [neighbors]}
    start → target까지 최단 거리 (hop 수)
    """

    queue = deque([(start, 0)])
    visited = set()

    while queue:
        node, dist = queue.popleft()

        if node == target:
            return dist

        if node in visited:
            continue
        visited.add(node)

        for neighbor in graph.get(node, []):
            queue.append((neighbor, dist + 1))

    return float("inf")  # 연결 안됨

def build_candidate_table(premise, animals, graph, task_type):

    table = []

    for a in animals:
        if a == premise:
            continue

        d_forward = compute_distance(premise, a, graph)

        if task_type == "food":
            d_backward = compute_distance(a, premise, graph)

            if d_forward < float("inf"):
                direction = "forward"
                dist = d_forward
            elif d_backward < float("inf"):
                direction = "backward"
                dist = d_backward
            else:
                direction = "none"
                dist = float("inf")
        else:
            # gene은 방향 없음
            direction = "undirected"
            dist = d_forward

        table.append({
            "animal": a,
            "dist": dist,
            "direction": direction
        })

    return table

def pick_option(candidates, dist=None, direction=None):

    filtered = candidates

    if dist is not None:
        filtered = [c for c in filtered if c["dist"] == dist]

    if direction is not None:
        filtered = [c for c in filtered if c["direction"] == direction]

    if not filtered:
        return None

    return random.choice(filtered)


# =========================
# 4. Trial 생성
# =========================
def generate_trials(
    animals,
    food_edges,
    gene_edges,
    n_trials=60
):

    trials = []

    # =========================
    # graph 생성
    # =========================
    food_graph = build_graph(
        food_edges,
        bidirectional=False
    )

    gene_graph = build_graph(
        gene_edges,
        bidirectional=True
    )

    # =========================
    # 거리 pool
    # =========================
    food_distances = [1, 2, 3, float("inf")]

    gene_distances = [2, 4, 5]

    # =========================
    # 10 trial block 단위 생성
    # =========================
    block_size = 10

    n_blocks = n_trials // block_size

    task_sequence = []

    for _ in range(n_blocks):

        block = (
            ["food"] * 5 +
            ["gene"] * 5
        )

        random.shuffle(block)

        task_sequence.extend(block)

    # 남는 trial 처리
    remain = n_trials % block_size

    if remain > 0:

        remain_block = (
            ["food"] * int(remain * 0.5) +
            ["gene"] * (remain - int(remain * 0.5))
        )

        random.shuffle(remain_block)

        task_sequence.extend(remain_block)

    # =========================
    # trial 생성
    # =========================
    for task_type in task_sequence:

        while True:

            premise = random.choice(animals)

            # =========================
            # graph 선택
            # =========================
            if task_type == "food":

                graph = food_graph
                possible_distances = food_distances

            else:

                graph = gene_graph
                possible_distances = gene_distances

            # =========================
            # candidate table
            # =========================
            table = build_candidate_table(
                premise,
                animals,
                graph,
                task_type
            )

            # =========================
            # 옵션1 선택
            # =========================
            dist1 = random.choice(
                possible_distances
            )

            if task_type == "food":

                dir1 = random.choice([
                    "forward",
                    "backward",
                    "none"
                ])

            else:

                dir1 = None

            opt1 = pick_option(
                table,
                dist=dist1,
                direction=dir1
            )

            if opt1 is None:
                continue

            # =========================
            # 옵션2 선택
            # =========================
            dist2 = random.choice(
                possible_distances
            )

            if task_type == "food":

                dir2 = random.choice([
                    "forward",
                    "backward",
                    "none"
                ])

            else:

                dir2 = None

            opt2 = pick_option(
                table,
                dist=dist2,
                direction=dir2
            )

            if opt2 is None:
                continue

            if opt1["animal"] == opt2["animal"]:
                continue

            # =========================
            # 같은 거리 제거
            # =========================
            if opt1["dist"] == opt2["dist"]:
                continue

            # =========================
            # 정답 계산
            # =========================
            if opt1["dist"] < opt2["dist"]:

                correct = "left"

            else:

                correct = "right"

            # =========================
            # 저장
            # =========================
            trials.append({

                "task_type": task_type,

                "premise": premise,

                "option1": opt1["animal"],
                "option2": opt2["animal"],

                "dist1": opt1["dist"],
                "dist2": opt2["dist"],

                "dir1": opt1["direction"],
                "dir2": opt2["direction"],

                "correct": correct
            })

            break

    return trials


# =========================
# 5. Trial 실행 (UI)
# =========================
def run_trial(win, trial, handle):

    cfg = UI_CONFIG
    left_option = trial["option1"]
    right_option = trial["option2"]

    left_image_path = os.path.join("stimuli", f"{left_option}.png")
    right_image_path = os.path.join("stimuli", f"{right_option}.png")

    # =========================
    # premise image 경로 추가
    # =========================
    premise_image_path = os.path.join(
        "stimuli",
        f"{trial['premise']}.png"
    )

    # =========================
    # 질문 (추후 종류 세분화하기)
    # =========================
    if trial["task_type"] == "food":
        target = random.choice(DISEASE_POOL["food"])
    else:
        target = random.choice(DISEASE_POOL["gene"])

    #===== target + 조사 분리 =====
    full_target = Josa.get_full_string(target, '을')

    # 조사만 추출
    josa_part = full_target[len(target):]

    # category별 색
    target_color = (
        [0.5, -1, -1]
        if trial["task_type"] == "food"
        else [-1, -1, 0.5]
    )

    # ===== 질문 문장 =====
    question_text = (
        f"{Josa.get_full_string(trial['premise'], '가')} "
        f"<c={target_color}>{target}</c>{josa_part}"
        f" 가진다.\n"
        f"어느 쪽이 더 그 "
        f"<c={target_color}>{target}</c>{josa_part}"
        f" 가질 가능성이 큰가?"
    )

    # ===== TextBox2 =====
    question = TextBox2(
        win,

        text=question_text,

        pos=cfg["question"]["pos"],

        size=(
            cfg["question"]["wrapWidth"],
            None
        ),

        letterHeight=cfg["question"]["height"],

        color=cfg["question"]["color"],

        font=cfg["question"]["font"],

        alignment="center",

        anchor="center"
    )

    # =========================
    # premise 이미지 추가
    # =========================
    premise_image = visual.ImageStim(
        win,
        image=premise_image_path,

        # 원하는 위치
        pos=(-650, 300),

        # 원하는 크기
        size=(120, 120)
    )

    # =========================
    # 옵션
    # =========================
    left_option = visual.TextStim(
        win,
        text=trial["option1"],
        pos=cfg["option"]["left_pos"],
        height=cfg["option"]["height"],
        color=cfg["option"]["color"],
        font=cfg["option"]["font"]
    )

    right_option = visual.TextStim(
        win,
        text=trial["option2"],
        pos=cfg["option"]["right_pos"],
        height=cfg["option"]["height"],
        color=cfg["option"]["color"],
        font=cfg["option"]["font"]
    )

    # ===== 이미지 =====
    left_image = visual.ImageStim(
        win,
        image=left_image_path,
        pos=cfg["image"]["left_pos"],
        size=cfg["image"]["size"]
    )

    right_image = visual.ImageStim(
        win,
        image=right_image_path,
        pos=cfg["image"]["right_pos"],
        size=cfg["image"]["size"]
    )

    # =========================
    # 화살표
    # =========================
    left_arrow = visual.TextStim(
        win,
        text="◀",
        pos=cfg["arrow"]["left_pos"],
        height=cfg["arrow"]["height"],
        color=cfg["arrow"]["color"]
    )

    right_arrow = visual.TextStim(
        win,
        text="▶",
        pos=cfg["arrow"]["right_pos"],
        height=cfg["arrow"]["height"],
        color=cfg["arrow"]["color"]
    )

    clock = core.Clock()
    event.clearEvents()

    response = None
    rt = None

    # =========================
    # response phase
    # =========================
    frame_count = 0
    timeout_frames = cfg["timing"]["timeout_frames"]

    while frame_count < timeout_frames:

        # ===== marker =====
        if frame_count < FRAME_EXAMPLE_bs:
            draw_white_marker(
                win,
                pos=(-WIDTH//2 + 120, -HEIGHT//2 + 120),
                size=(50, 50)
            )

        # ===== draw =====
        question.draw()

        # premise 이미지 draw
        premise_image.draw()

        if frame_count >= waiting_frames:
            left_option.draw()
            right_option.draw()
            left_image.draw()
            right_image.draw()
            left_arrow.draw()
            right_arrow.draw()

        # trigger ON
        if frame_count == 0:

            win.callOnFlip(
                send_trigger,
                handle,
                TRIG_B_START
            )

        # trigger OFF
        elif frame_count == 1:

            win.callOnFlip(
                reset_trigger,
                handle
            )

        # ===== flip =====
        win.flip()

        # ===== key check =====
        if frame_count >= waiting_frames:

            keys = event.getKeys(
                keyList=["left", "right", "escape"],
                timeStamped=clock
            )

            if keys:

                key, rt = keys[0]

                if key == "escape":
                    core.quit()

                if key == "left":

                    left_arrow.color = (
                        cfg["arrow"]["active_color"]
                    )

                    response = "left"

                else:

                    right_arrow.color = (
                        cfg["arrow"]["active_color"]
                    )

                    response = "right"

                break

        frame_count += 1

    # =========================
    # response trigger phase
    # =========================
    frame_count = 0

    while frame_count < 2:

        question.draw()

        # premise 이미지 draw
        premise_image.draw()

        left_option.draw()
        right_option.draw()

        left_image.draw()
        right_image.draw()

        left_arrow.draw()
        right_arrow.draw()

        # ON
        if frame_count == 0:

            win.callOnFlip(
                send_trigger,
                handle,
                TRIG_B_RESPOND
            )

        # OFF
        elif frame_count == 1:

            win.callOnFlip(
                reset_trigger,
                handle
            )

        win.flip()

        frame_count += 1

    # =========================
    # feedback phase
    # =========================
    frame_count = 0
    feedback_frames = cfg["timing"]["feedback_frames"]

    while frame_count < feedback_frames:

        # ===== marker =====
        if frame_count < FRAME_EXAMPLE_bf:

            draw_white_marker(
                win,
                pos=(-WIDTH//2 + 120, -HEIGHT//2 + 120),
                size=(50, 50)
            )

        # ===== draw =====
        question.draw()

        # premise 이미지 draw
        premise_image.draw()

        left_option.draw()
        right_option.draw()

        left_image.draw()
        right_image.draw()

        left_arrow.draw()
        right_arrow.draw()

        win.flip()

        frame_count += 1

    # =========================
    # 색 복구
    # =========================
    left_arrow.color = cfg["arrow"]["color"]
    right_arrow.color = cfg["arrow"]["color"]

    return response, rt

# =========================
# 6. 전체 실행
# =========================
def run_both_task(win, json_path,handle):

    animals, food_edges, gene_edges = load_both_web(json_path)

    trials = generate_trials(animals, food_edges, gene_edges, n_trials=60)

    results = []

    i=0

    for t in trials:

        random_isi_phase(win)

        if i == 5:

            show_random_food_pair(win,handle)

            show_random_gene_single(win,handle)

        elif i > 5 and (i - 5) % 15 == 0:

            show_random_food_pair(win, handle)

            show_random_gene_single(win, handle)


        response, rt = run_trial(win, t,handle)

        
        is_correct = (response == t["correct"]) if response else False

        results.append({
            **t,
            "response": response,
            "rt": rt,
            "is_correct": is_correct
        })



        i+=1

        

    return results