import cv2
import virtual_board_all 
from ultralytics import YOLO
import time
from cvzone_hand import HandDetector
import process_frame
import matrix_to_pieces
import tasks
import warnings
import store_as_video
from belief import GroupSkillBelief, plot_beliefs

class FullMasteries():
    def __init__(self, uids, tids) -> None:
        self.uids = uids

        self.masteries = {}
        self.tasks = {}
        self.tids = tids
        self.task_list_id = 0

        for uid in uids:
            self.masteries[uid] = {}
            for sid in tasks.sid_skill_map:
                self.masteries[uid][sid] = 0.5

        for tid in tids:
            self.tasks[tid] = tasks.get_task(tid, uids)

    def move_to_next_task(self, beliefs):

        for sid in beliefs:
            belief = beliefs[sid]
            for uid in belief.users:
                self.masteries[uid][sid] = belief.users[uid].H[-1]

        self.task_list_id += 1

    
    def get_current_task(self):
        if self.task_list_id < len(self.tids):
            return True, self.tasks[self.tids[self.task_list_id]], self.tids[self.task_list_id]
        else:
            return False, None, None

def create_beliefs(task, uids, full_masteries):
    beliefs = {}
    
    for sid in task.sids:
        p_L_0s = {}
        for uid in uids:
            p_L_0s[uid] = full_masteries.masteries[uid][sid]

        skill = tasks.sid_skill_map[sid]
        skill_probs = skill.skill_probs

        skill_belief = GroupSkillBelief(sname=skill.skill_name,
                                        sid=sid, 
                                        uids=task.uids, 
                                        p_L_0s=p_L_0s, 
                                        p_S=skill_probs.prob_slipping, 
                                        p_G=skill_probs.prob_guessing, 
                                        p_T=skill_probs.prob_learning,
                                        n=10, 
                                        discussion_time=task.discussion_time,
                                        solve_time=task.solve_time)
        beliefs[sid] = skill_belief
    return beliefs

def initialise_cv():
    source = 1
    warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")

    cap = cv2.VideoCapture(source)

    # pre-trained YOLO model and hand model
    model = YOLO('best (8).pt')
    detector = HandDetector(detectionCon=0.5, maxHands=4)

    ret, frame = cap.read()
    if not ret:
        print("Camera Connection Failed")
        return False, None

    # Focus on board
    frame_for_board, _ = process_frame.crop_frame_general(frame, crop_size=250, crop_hand_size=400)

    # We draw pegs on the board using the first frame. This is done because we assume that the board will remain stationary
    # throughout the video. Drawing the pegs in the initial frame helps us avoid any shift or misalignment of the
    # pegs when a piece moves near or past the edge of the board.
    matrix_to_recolor, peg_size, frame_tilt, frame_circle, angle, board_size = virtual_board_all.draws_pegs_on_rotated_board(frame_for_board)

    return True, (source, cap, model, detector, matrix_to_recolor, peg_size, frame_tilt, frame_circle, angle, board_size)

def initialise_cv_recorded(source):
    warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")

    cap = cv2.VideoCapture(source)

    # pre-trained YOLO model and hand model
    model = YOLO('best (8).pt')
    detector = HandDetector(detectionCon=0.5, maxHands=4)

    ret, frame = cap.read()
    if not ret:
        print("Camera Connection Failed")
        return False, None

    # Focus on board
    frame_for_board, _ = process_frame.crop_frame_general(frame, crop_size=200, crop_hand_size=400)

    # We draw pegs on the board using the first frame. This is done because we assume that the board will remain stationary
    # throughout the video. Drawing the pegs in the initial frame helps us avoid any shift or misalignment of the
    # pegs when a piece moves near or past the edge of the board.
    matrix_to_recolor, peg_size, frame_tilt, frame_circle, angle, board_size = virtual_board_all.draws_pegs_on_rotated_board(frame_for_board)

    return True, (source, cap, model, detector, matrix_to_recolor, peg_size, frame_tilt, frame_circle, angle, board_size)

def finish_cv(cap):
    cap.release()
    cv2.destroyAllWindows()

def run_task_prerecorded(user_masteries, uids, unique_uids, source, cap, model, detector, matrix_to_recolor, peg_size, frame_tilt, frame_circle, angle, board_size, store=False, show=True):
    more_tasks, task, tid = user_masteries.get_current_task()

    if not more_tasks:
        return False, None
    
    if show: cv2.imshow("Board with Pegs", frame_circle)

    beliefs = create_beliefs(task=task, uids=uids, full_masteries=user_masteries)

    # initialize
    time_step_index = 0
    if board_size[0] > board_size[1]:
        board = matrix_to_pieces.initialise_board(90)
    else:
        board = matrix_to_pieces.initialise_board(0)

    # store video
    if store: writer = store_as_video.store_video_titled(cv2.VideoCapture(source), unique_uids, tid)

    hands_over_board = {}
    for uid in uids:
        hands_over_board[uid] = []
    someone_contributed = False

    while True:

        # Capture a frame
        ret, frame = cap.read()
        if not ret:
            print("Camera Connection Failed")
            break

        if show: cv2.imshow("Uncropped Image", frame)
        # Store video
        if store: writer.write(frame)

        frame_for_board, frame_for_hand = process_frame.crop_frame_general(frame, crop_size=200, crop_hand_size=400, y_offset=-10)
        if show: cv2.imshow("Board Frame Image", frame_for_board)
        if show: cv2.imshow("Hand Frame Image", frame_for_hand)
        
        frame_tilt = virtual_board_all.tilt(frame_for_board, angle) 

        # Detecting hand
        other_hands, other_img = detector.findHands(frame_for_board)
        if show: cv2.imshow("Tight Hand Detected Image", other_img)
        hands, img = detector.findHands(frame_for_hand)
        if show: cv2.imshow("Wide Hand Detected Image", img)

        if not hands:
            matrix, data, output = process_frame.process_frame_with_yolo(frame_tilt, model, matrix_to_recolor, peg_size)

            user_0_time = len(hands_over_board[0])
            user_1_time = len(hands_over_board[1])
            total_time = user_0_time + user_1_time
            if total_time != 0:
                user_0_contribution = user_0_time / total_time
                user_1_contribution = user_1_time / total_time
            else:
                user_0_contribution = 0
                user_1_contribution = 0

            board, changed = matrix_to_pieces.data_to_board(board, data, output, frame_tilt, angle, time_step_index, {0: user_0_contribution, 1: user_1_contribution}, someone_contributed=someone_contributed)
            
            if changed:
                someone_contributed = False
                print(time_step_index)
                print(board)
            
            task.check_skills(board)
        
        else:
            if not someone_contributed:
                hands_over_board = {}
                for uid in uids:
                    hands_over_board[uid] = []
                someone_contributed = True
            # hand on board
            print("\033[91mHand On Board!\033[0m")
            u_0_contributed = False
            u_1_contributed = False

            for hand in hands:
                if hand['type'] == "ID: 0" and not u_0_contributed:
                    u_0_contributed = True
                    hands_over_board[0].append(time_step_index)
                if hand['type'] == "ID: 1" and not u_1_contributed:
                    u_1_contributed = True
                    hands_over_board[1].append(time_step_index)

        for sid in beliefs:
            c_ts = {}
            for uid in uids:
                c_ts[uid] = task.cs[sid][uid]
            beliefs[sid].step(task.os[sid], c_ts)

        time.sleep(0.1)
        
        time_step_index += 1
        
    print("OUTPUTS: ")
    print(board.history)
    print(board)
    plot_beliefs(beliefs=beliefs)

    if store: writer.release()

    return True, beliefs

def run_task(user_masteries, uids, unique_uids, source, cap, model, detector, matrix_to_recolor, peg_size, frame_tilt, frame_circle, angle, board_size, store=True, show=True):

    more_tasks, task, tid = user_masteries.get_current_task()

    if not more_tasks:
        return False, None
    
    if show: cv2.imshow("Board with Pegs", frame_circle)

    beliefs = create_beliefs(task=task, uids=uids, full_masteries=user_masteries)

    # initialize
    time_step_index = 0
    if board_size[0] > board_size[1]:
        board = matrix_to_pieces.initialise_board(90)
    else:
        board = matrix_to_pieces.initialise_board(0)

    # store video
    if store: writer = store_as_video.store_video_titled(cv2.VideoCapture(source), unique_uids, tid)

    hands_over_board = {}
    for uid in uids:
        hands_over_board[uid] = []
    someone_contributed = False

    while True:
        start_time = time.time()

        # Capture a frame
        ret, frame = cap.read()
        if not ret:
            print("Camera Connection Failed")
            break

        if show: cv2.imshow("Uncropped Image", frame)
        # Store video
        if store: writer.write(frame)

        frame_for_board, frame_for_hand = process_frame.crop_frame_general(frame, crop_size=250, crop_hand_size=400)
        if show: cv2.imshow("Board Frame Image", frame_for_board)
        if show: cv2.imshow("Hand Frame Image", frame_for_hand)
        
        frame_tilt = virtual_board_all.tilt(frame_for_board, angle) 

        # Detecting hand
        # other_hands, other_img = detector.findHands(frame_for_board)
        # if show: cv2.imshow("Tight Hand Detected Image", other_img)
        hands, img = detector.findHands(frame_for_hand)
        if show: cv2.imshow("Wide Hand Detected Image", img)

        if not hands:
            matrix, data, output = process_frame.process_frame_with_yolo(frame_tilt, model, matrix_to_recolor, peg_size)

            user_0_time = len(hands_over_board[0])
            user_1_time = len(hands_over_board[1])
            total_time = user_0_time + user_1_time
            if total_time != 0:
                user_0_contribution = user_0_time / total_time
                user_1_contribution = user_1_time / total_time
            else:
                user_0_contribution = 0
                user_1_contribution = 0

            board, changed = matrix_to_pieces.data_to_board(board, data, output, frame_tilt, angle, time_step_index, {0: user_0_contribution, 1: user_1_contribution}, someone_contributed=someone_contributed)
            
            if changed:
                someone_contributed = False
                print(time_step_index)
                print(board)
            
            task.check_skills(board)
        
        else:
            if not someone_contributed:
                hands_over_board = {}
                for uid in uids:
                    hands_over_board[uid] = []
                someone_contributed = True
            # hand on board
            print("\033[91mHand On Board!\033[0m")
            u_0_contributed = False
            u_1_contributed = False

            for hand in hands:
                if hand['type'] == "ID: 0" and not u_0_contributed:
                    u_0_contributed = True
                    hands_over_board[0].append(time_step_index)
                if hand['type'] == "ID: 1" and not u_1_contributed:
                    u_1_contributed = True
                    hands_over_board[1].append(time_step_index)

        for sid in beliefs:
            c_ts = {}
            for uid in uids:
                c_ts[uid] = task.cs[sid][uid]
            beliefs[sid].step(task.os[sid], c_ts)

        end_time = time.time()
        if end_time < start_time + 1:
            print(start_time + 1 - end_time)
            time.sleep(start_time + 1 - end_time)

        if time_step_index >= task.discussion_time + task.solve_time:
            break
        time_step_index += 1
        
    print("OUTPUTS: ")
    print(board.history)
    print(board)
    plot_beliefs(beliefs=beliefs)

    if store: writer.release()

    return True, beliefs