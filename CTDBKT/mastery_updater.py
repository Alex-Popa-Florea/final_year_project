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
                self.masteries[sid] = 0.5

        for tid in tids:
            self.tasks[tid] = tasks.get_task(tid, uids)

    def move_to_next_task(self, beliefs):

        for sid in beliefs:
            for uid in beliefs[sid]:
                self.masteries[uid][sid] = beliefs[sid][uid]

        self.task_list_id += 1

    
    def get_current_task(self):
        if self.tid < len(self.tids):
            return True, self.tasks[self.tid[self.task_list_id]]
        else:
            return False, None

def create_beliefs(task, uids, full_masteries):
    beliefs = {}

    p_L_0s = {}
    for sid in task.sids:
        for uid in uids:
            p_L_0s

    
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


def run_task(user_masteries, uids, unique_uids):
    more_tasks, task = user_masteries.get_current_task()

    if not more_tasks:
        return False, None

    beliefs = create_beliefs(task, uids, user_masteries)

    source = 1
    store = True
    show = True
    
    first_viable_frame = 0

    warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")

    cap = cv2.VideoCapture(source)

    # pre-trained YOLO model and hand model
    model = YOLO('best (8).pt')
    detector = HandDetector(detectionCon=0.5, maxHands=4)

    # initialize
    time_step_index = 0
    board = matrix_to_pieces.initialise_board(90)
    task = tasks.get_task("task1", uids)

    # store video
    if store: writer = store_as_video.store_video_titled(cv2.VideoCapture(source), unique_uids, user_masteries.tid)

    hands_over_board = {}
    for uid in uids:
        hands_over_board[uid] = []
    changed = False

    beliefs = create_beliefs(task, {0: 0.5, 1: 0.5})

    while True:
        # Capture a frame
        ret, frame = cap.read()
        if not ret:
            print("Camera Connection Failed")
            break

        if show: cv2.imshow("Uncropped Image", frame)
        # Store video
        if store: writer.write(frame)

        if time_step_index >= first_viable_frame:
            
            # Focus on board
            frame_for_board, frame_for_hand = process_frame.crop_frame(frame)
            #frame_for_board, frame_for_hand = process_frame.crop_frame_home(frame)
            # frame_for_board, frame_for_hand = process_frame.crop_frame_general(frame, crop_size=320)
            if show: cv2.imshow("Board Frame Image", frame_for_board)
            if show: cv2.imshow("Hand Frame Image", frame_for_hand)
            
            # We draw pegs on the board using the first frame. This is done because we assume that the board will remain stationary
            # throughout the video. Drawing the pegs in the initial frame helps us avoid any shift or misalignment of the
            # pegs when a piece moves near or past the edge of the board.
            if time_step_index == first_viable_frame:
                matrix_to_recolor, peg_size, frame_tilt, frame_circle, angle = virtual_board_all.draws_pegs_on_rotated_board(frame_for_board)
            else:
                frame_tilt = virtual_board_all.tilt(frame_for_board, angle) 

            if show: cv2.imshow("Board with Pegs", frame_circle)

            # Detecting hand
            hands, img = detector.findHands(frame_for_hand)
            if show: cv2.imshow("Hand Detected Large Image", img)

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

                board, changed = matrix_to_pieces.data_to_board(board, data, output, frame_tilt, angle, {0: user_0_contribution, 1: user_1_contribution})
                
                
                task.check_skills(board)
            
            else:
                # hand on board
                print("\033[91mHand On Board!\033[0m")
                hands, img = detector.findHands(frame_for_hand) #NOTEEEEE
                if show: cv2.imshow("Hand Detected Image", img)
                # for all hands, store the history of its center
                for hand in hands:
                    if hand['type'] == "ID: 0":
                        hands_over_board[0].append(time_step_index)
                    else:
                        hands_over_board[1].append(time_step_index)

            if changed:
                hands_over_board = {}
                for uid in uids:
                    hands_over_board[uid] = []
                changed = False

            for sid in beliefs:
                c_ts = {}
                for uid in uids:
                    c_ts[uid] = task.cs[sid][uid]
                beliefs[sid].step(task.os[sid], c_ts)

            

        time.sleep(0.1) 
        # Check for the 'q' key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if time_step_index > task.discussion_time + task.solve_time:
            break
        time_step_index += 1
        
    print("OUTPUTS: ")
    print(board.history)
    plot_beliefs(beliefs=beliefs)

    # Release the webcam and close the windows
    cap.release()
    if store: writer.release() 
    cv2.destroyAllWindows()

    return True, beliefs