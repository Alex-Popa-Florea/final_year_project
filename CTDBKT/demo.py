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
import group_belief
import numpy as np
import json
from matplotlib import pyplot as plt
from various_methods import all_methods


def create_beliefs_methods(task, uids, methods, methods_masteries, discussion_time, solve_time):
    beliefs_methods = {}
    for method in methods:
        beliefs = {}
        
        for sid in task.sids:
            skill = tasks.sid_skill_map[sid]
            skill_probs = skill.skill_probs
            p_L_0s = {}
            for uid in uids:
                p_L_0s[uid] = methods_masteries[method][uid][sid]

            skill_belief = group_belief.GroupSkillBelief(sname=skill.skill_name,
                                            sid=sid, 
                                            uids=uids, 
                                            p_L_0s=p_L_0s, 
                                            p_S=skill_probs.prob_slipping, 
                                            p_G=skill_probs.prob_guessing, 
                                            p_T=skill_probs.prob_learning,
                                            n=15,
                                            discussion_time=discussion_time,
                                            solve_time=solve_time,
                                            usb=methods[method]["usb"],
                                            use_history=methods[method]["use_history"])
            beliefs[sid] = skill_belief

        beliefs_methods[method] = beliefs
    return beliefs_methods 

all_sids = [4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 23, 24]
tids = ["task1", "task2", "task3", "task4"]
unique_uids_sets = [[5, 4]]
show = True
plt.ion()

for unique_uids in unique_uids_sets:
    uids = [0, 1]
    believed_mastery_methods = {}

    for method in all_methods:
        believed_mastery_methods[method] = {}
        for uid in uids:
            believed_mastery_methods[method][uid] = {}
            for sid in all_sids:
                believed_mastery_methods[method][uid][sid] = 0.5

    for task_name in tids:
        

        with open(f'user_study/values/[{unique_uids[0]}, {unique_uids[1]}]/user_study_ms_{task_name}.json', 'r') as f:
            m = json.load(f)
        

        video_source = f'user_study/user_study_[{unique_uids[0]}, {unique_uids[1]}]_{task_name}.mp4'
        

        warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")

        cap = cv2.VideoCapture(video_source)

        model = YOLO('best (8).pt')
        detector = HandDetector(detectionCon=0.5, maxHands=4)
        task = tasks.get_task(task_name, uids)

        beliefs_methods = create_beliefs_methods(task=task, uids=uids, methods=all_methods, methods_masteries=believed_mastery_methods, discussion_time=task.discussion_time, solve_time=task.solve_time)

        time_step_index = 0

        hands_over_board = {}
        for uid in uids:
            hands_over_board[uid] = []
        someone_contributed = False

        while True:

            ret, frame = cap.read()
            if not ret:
                print("Camera Connection Failed")
                break

            if show: cv2.imshow("Uncropped Image", frame)

            frame_for_board, frame_for_hand = process_frame.crop_frame_general(frame, crop_size=200, crop_hand_size=400, y_offset=-10)

            if time_step_index == 0:
                matrix_to_recolor, peg_size, frame_tilt, frame_circle, angle, board_size = virtual_board_all.draws_pegs_on_rotated_board(frame_for_board)
                if board_size[0] > board_size[1]:
                    board = matrix_to_pieces.initialise_board(90)
                else:
                    board = matrix_to_pieces.initialise_board(0)
            else:
                frame_tilt = virtual_board_all.tilt(frame_for_board, angle) 
            
            if show: cv2.imshow("Board with Pegs", frame_circle)
            if show: cv2.imshow("Board Frame Image", frame_for_board)
            if show: cv2.imshow("Hand Frame Image", frame_for_hand)


            hands, img = detector.findHands(frame_for_hand)
            if show: cv2.imshow("Hand Detected Image", img)

            if not hands:
                data, output = process_frame.yolo_process_frame(frame_tilt, model, matrix_to_recolor, peg_size)

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
                board_image = board.show_board()
                final_image_bgr = cv2.cvtColor(np.array(board_image), cv2.COLOR_RGB2BGR)
                cv2.imshow("Virtual Board Newer", final_image_bgr)
                if changed:
                    someone_contributed = False
                
                task.check_skills(board)
            
            else:
                if not someone_contributed:
                    hands_over_board = {}
                    for uid in uids:
                        hands_over_board[uid] = []
                    someone_contributed = True
                u_0_contributed = False
                u_1_contributed = False

                for hand in hands:
                    if hand['type'] == "ID: 0" and not u_0_contributed:
                        u_0_contributed = True
                        hands_over_board[0].append(time_step_index)
                    if hand['type'] == "ID: 1" and not u_1_contributed:
                        u_1_contributed = True
                        hands_over_board[1].append(time_step_index)

            for method in all_methods:
                beliefs = beliefs_methods[method]
                for sid in beliefs:
                    use_history = beliefs[sid].use_history
                    c_ts = {}
                    for uid in uids:
                        if use_history:
                            c_ts[uid] = task.best_cs[sid][uid]
                        else:
                            c_ts[uid] = task.last_cs[sid][uid]
                    beliefs[sid].step(task.os[sid], c_ts)

            time.sleep(0.1)
            
            
        
            for method in all_methods:
                beliefs = beliefs_methods[method]
                for sid in beliefs:
                    belief = beliefs[sid]
                    for uid in belief.users:
                        believed_mastery_methods[method][uid][sid] = belief.users[uid].H[-1]

            os, cs, _, bs, ts = group_belief.get_everything(beliefs_methods=beliefs_methods)

            ms = {}

            for sid in m:
                ms[sid] = {}
                for uid in m[sid]:
                    ms[sid][uid] = []
                        
                    for t in ts:
                        if str(t) in m[sid][uid]:
                            ms[sid][uid].append(m[sid][uid][str(t)])
                        else:
                            ms[sid][uid].append(ms[sid][uid][-1])

            
        
            if time_step_index != 0:
                bs_graph1.remove()
                bs_graph2.remove()
                bs_graph3.remove()

            plt.legend()
            plt.ylim(-0.1, 1.1)
            plt.xlabel('Time Step')
            plt.ylabel('Belief')
            plt.title('Belief Skill: SID: ' + str(5) + ' UID: ' + str(0))

            bs_graph1 = plt.plot(ts, bs[5][0]["CSCCTD_BKT"], linestyle='-', label=f'Belief {method}', color = 'g')[0]
            bs_graph2 = plt.plot(ts, bs[5][0]["CMCCTD_BKT"], linestyle='-', label=f'Belief {method}', color = 'b')[0]
            if ms != {}:
                bs_graph3 = plt.plot(ts, ms[sid][uid], linestyle=':', label='Truth', color = 'y')[0]

            

            plt.pause(0.25)

            time_step_index += 1
