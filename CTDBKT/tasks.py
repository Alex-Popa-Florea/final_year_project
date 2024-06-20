from enum import Enum
from pieces import StudType

# Default skill probability values
class SkillProbs():
    def __init__(self, prob_slipping=0.1, prob_guessing=0.2, prob_learning=0.7) -> None:
        self.prob_slipping = prob_slipping
        self.prob_guessing = prob_guessing
        self.prob_learning = prob_learning
    
class Skill():
    def __init__(self, skill_name, skill_type, skill_probs) -> None:
        self.skill_name = skill_name
        self.skill_type = skill_type
        self.skill_probs = skill_probs

# A skill refering to identifying pieces
class PieceSkill(Skill):
    def __init__(self, skill_name, piece_type, skill_probs) -> None:
        self.piece_type = piece_type
        super().__init__(skill_name=skill_name, skill_type="piece", skill_probs = skill_probs)

# A skill refering to knowing the correct direction of a piece
class StudDirectionSkill(Skill):
    def __init__(self, skill_name, piece_type, stud_type, skill_probs) -> None:
        self.piece_type = piece_type
        self.stud_type = stud_type
        super().__init__(skill_name=skill_name, skill_type="stud_direction", skill_probs = skill_probs)

# List of skills
sid_skill_map = {
    0: PieceSkill("identify_fm", "fm", SkillProbs(prob_guessing=0.1, prob_learning=0.5)),
    1: PieceSkill("identify_buzzer", "buzzer", SkillProbs(prob_guessing=0.1)),
    2: PieceSkill("identify_touch_plate", "touch_plate", SkillProbs(prob_guessing=0.1)),
    3: PieceSkill("identify_reed_switch", "reed_switch", SkillProbs(prob_guessing=0.1)),
    4: PieceSkill("identify_button_switch", "button_switch", SkillProbs()),
    5: PieceSkill("identify_normal_switch", "switch", SkillProbs()),
    6: PieceSkill("identify_cds", "cds", SkillProbs(prob_guessing=0.1)),
    7: PieceSkill("identify_led", "led", SkillProbs()),
    8: PieceSkill("identify_lamp", "lamp", SkillProbs()),
    9: PieceSkill("identify_battery", "battery", SkillProbs()),
    10: PieceSkill("identify_speaker", "speaker", SkillProbs()),
    11: PieceSkill("identify_mc", "mc", SkillProbs(prob_guessing=0.1)),
    12: PieceSkill("identify_motor", "motor", SkillProbs()),
    13: Skill("connect_pieces", "connection", SkillProbs(prob_guessing=0.1, prob_learning=0.5)),
    14: Skill("close_circuit", "closed", SkillProbs(prob_guessing=0.1, prob_slipping=0.3, prob_learning=0.4)),
    15: Skill("series_circuit", "series", SkillProbs(prob_guessing=0.1, prob_slipping=0.3, prob_learning=0.5)),
    16: Skill("parallel_circuit", "parallel", SkillProbs(prob_guessing=0.1, prob_slipping=0.3, prob_learning=0.5)),
    17: StudDirectionSkill("led_pos_stud", "led", StudType.POSITIVE, SkillProbs(prob_guessing=0.3, prob_slipping=0.2, prob_learning=0.6)),
    18: StudDirectionSkill("led_neg_stud", "led", StudType.NEGATIVE, SkillProbs(prob_guessing=0.3, prob_slipping=0.2, prob_learning=0.6)),
    19: StudDirectionSkill("fm_in_stud", "fm", StudType.IN, SkillProbs(prob_guessing=0.1, prob_slipping=0.4, prob_learning=0.5)),
    20: StudDirectionSkill("fm_out_stud", "fm", StudType.OUT, SkillProbs(prob_guessing=0.1, prob_slipping=0.4, prob_learning=0.5)),
    21: StudDirectionSkill("fm_signal_stud", "fm", StudType.SIGNAL, SkillProbs(prob_guessing=0.1, prob_slipping=0.5, prob_learning=0.5)),
    22: StudDirectionSkill("mc_in_stud", "mc", StudType.IN, SkillProbs(prob_guessing=0.1, prob_slipping=0.4, prob_learning=0.5)),
    23: StudDirectionSkill("mc_out_stud", "mc", StudType.OUT, SkillProbs(prob_guessing=0.1, prob_slipping=0.4, prob_learning=0.5)),
    24: StudDirectionSkill("mc_trigger_stud", "mc", StudType.TRIGGER, SkillProbs(prob_guessing=0.1, prob_slipping=0.5, prob_learning=0.5)),
    25: StudDirectionSkill("mc_repeat_stud", "mc", StudType.REPEAT, SkillProbs(prob_guessing=0.1, prob_slipping=0.5, prob_learning=0.5)),
    26: StudDirectionSkill("mc_restart_stud", "mc", StudType.RESTART, SkillProbs(prob_guessing=0.1, prob_slipping=0.5, prob_learning=0.5)),
}

# The observatiosn and contributions throughout a task
class TaskObservations():
    def __init__(self, description, involved_skill_ids, uids, discussion_time=30, solve_time=30) -> None:
        self.description = description
        self.sids = involved_skill_ids
        self.uids = uids
        self.discussion_time = discussion_time
        self.solve_time = solve_time
        
        self.os = {}
        self.last_cs = {}
        self.best_cs = {}
        for sid in self.sids:
            self.last_cs[sid] = {}
            self.best_cs[sid] = {}
            self.os[sid] = 0
            for uid in self.uids:
                self.last_cs[sid][uid] = 0
                self.best_cs[sid][uid] = 0
    
    def __str__(self):
        string = ""
        for sid in self.os:
            string += f"{self.os[sid]} "
            for uid in self.best_cs[sid]:
                string += f"{self.best_cs[sid][uid]} "
            string += "\n"
        return string
    
    def check_identify_skill(self, sid, piece_type, board):
        o = 0
        if board.find_piece(piece_type):
            o = 1
        last_c = {}
        best_c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                best_uid_c = 0
                last_uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "piece":
                        if history_elem.piece_type == piece_type and history_elem.move == "added":
                            last_uid_c = history_elem.contr_percentage
                            best_uid_c = max(best_uid_c, history_elem.contr_percentage)
                best_c[uid] = best_uid_c
                last_c[uid] = last_uid_c
            else:
                last_c[uid] = 0
                best_c[uid] = 0
        self.os[sid] = o
        self.last_cs[sid] = last_c
        self.best_cs[sid] = best_c


    def check_connection_skill(self, sid, board):
        o = 0
        for piece_id in board.pieces:
            _, con_count = board.get_connections(piece_id)
            if con_count > 0:
                o = 1
                break
        last_c = {}
        best_c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                last_uid_c = 0
                best_uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "connection" and history_elem.move == "added":
                        last_uid_c = history_elem.contr_percentage
                        best_uid_c = max(best_uid_c, history_elem.contr_percentage)
                last_c[uid] = last_uid_c
                best_c[uid] = best_uid_c
            else:
                last_c[uid] = 0
                best_c[uid] = 0
        self.os[sid] = o
        self.last_cs[sid] = last_c
        self.best_cs[sid] = best_c
    
    def check_series_skill(self, sid, board, num_flows):
        o = 0
        if num_flows == 1:
            o = 1
        last_c = {}
        best_c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                last_uid_c = 0
                best_uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "series" and history_elem.move == "added":
                        last_uid_c = history_elem.contr_percentage
                        best_uid_c = max(best_uid_c, history_elem.contr_percentage)
                last_c[uid] = last_uid_c
                best_c[uid] = best_uid_c
            else:
                last_c[uid] = 0
                best_c[uid] = 0
        self.os[sid] = o
        self.last_cs[sid] = last_c
        self.best_cs[sid] = best_c

    def check_parallel_skill(self, sid, board, num_flows):
        o = 0
        if num_flows > 1:
            o = 1
        last_c = {}
        best_c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                last_uid_c = 0
                best_uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "parallel" and history_elem.move == "added":
                        last_uid_c = history_elem.contr_percentage
                        best_uid_c = max(best_uid_c, history_elem.contr_percentage)
                last_c[uid] = last_uid_c
                best_c[uid] = best_uid_c
            else:
                last_c[uid] = 0
                best_c[uid] = 0
        self.os[sid] = o
        self.last_cs[sid] = last_c
        self.best_cs[sid] = best_c

    def check_closed_skill(self, sid, board, found_flow):
        o = 0
        if found_flow:
            o = 1
        last_c = {}
        best_c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                last_uid_c = 0
                best_uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "closed" and history_elem.move == "added":
                        last_uid_c = history_elem.contr_percentage
                        best_uid_c = max(best_uid_c, history_elem.contr_percentage)
                last_c[uid] = last_uid_c
                best_c[uid] = best_uid_c
            else:
                last_c[uid] = 0
                best_c[uid] = 0
        self.os[sid] = o
        self.last_cs[sid] = last_c
        self.best_cs[sid] = best_c
    
    def check_stud_direction_skill(self, sid, piece_type, stud_type, board, found_flow, correct_studs):
        o = 0
        if found_flow:
            for correct_stud in correct_studs:
                if correct_stud[1] == piece_type and correct_stud[2].value == stud_type.value:
                    o = 1
        last_c = {}
        best_c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                last_uid_c = 0
                best_uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "stud_direction":
                        if history_elem.piece_type == piece_type and history_elem.stud_type.value == stud_type.value and history_elem.move == "added":
                            last_uid_c = history_elem.contr_percentage
                            best_uid_c = max(best_uid_c, history_elem.contr_percentage)
                last_c[uid] = last_uid_c
                best_c[uid] = best_uid_c
            else:
                last_c[uid] = 0
                best_c[uid] = 0
        self.os[sid] = o
        self.last_cs[sid] = last_c
        self.best_cs[sid] = best_c
        return correct_studs

    def check_skills(self, board):
        found_flow, num_flows, correct_studs = board.find_flow()

        for sid in self.sids:
            skill = sid_skill_map[sid]
            if skill.skill_type == "piece":
                self.check_identify_skill(sid, skill.piece_type, board)
            if skill.skill_type == "connection":
                self.check_connection_skill(sid, board)
            if skill.skill_type == "closed":
                self.check_closed_skill(sid, board, found_flow)
            if skill.skill_type == "series":
                self.check_series_skill(sid, board, num_flows)
            if skill.skill_type == "parallel":
                self.check_parallel_skill(sid, board, num_flows)
            if skill.skill_type == "stud_direction":
                self.check_stud_direction_skill(sid, skill.piece_type, skill.stud_type, board, found_flow, correct_studs)

# Task name to task mapping
def get_task(tid, uids):
    if tid == "task1":
        return TaskObservations('Build a circuit with a lamp that can be turned on and off using a switch.', [5, 8, 9, 13, 14], uids, discussion_time=60, solve_time=60)
    if tid == "task2":
        return TaskObservations('Build a circuit with a led and motor in series that can be turned on and off using a button.', [4, 7, 9, 12, 13, 14, 15, 17, 18], uids, discussion_time=60, solve_time=75)
    if tid == "task3":
        return TaskObservations('Build a circuit with an led that is turned on and off by a switch and the lamp is turned on and off by a button.', [4, 5, 7, 8, 9, 13, 14, 16, 17, 18], uids, discussion_time=120, solve_time=125)
    if tid == "task4":
        return TaskObservations('Build a circuit with a music box plays music through a speaker when a switch is turned on once then stops.', [5, 9, 10, 11, 13, 14, 22, 23, 24], uids, discussion_time=240, solve_time=165)


