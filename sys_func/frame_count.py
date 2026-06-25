global prev_flip_time

prev_flip_time = None

frame_log = []

prev_flip_time = None
frame_count = 0


def frame_timer(flip_time):

    global prev_flip_time
    global frame_log
    global frame_count

    frame_count += 1

    if prev_flip_time is None:

        prev_flip_time = flip_time
        return

    dt = flip_time - prev_flip_time

    frame_log.append({
        "frame": frame_count,
        "frame_duration": dt
    })

    prev_flip_time = flip_time