from enum import Enum

class StudType(Enum):
    NONE = 0
    POSITIVE = 1
    NEGATIVE = -1
    ANY = 2
    IN = 3
    OUT = 4
    TRIGGER = 5
    REPEAT = 6
    RESTART = 7
    SIGNAL = 8

class Skill():
    def __init__(self, skill_name, skill_type) -> None:
        self.skill_name = skill_name
        self.skill_type = skill_type

class PieceSkill(Skill):
    def __init__(self, skill_name, piece_type) -> None:
        self.piece_type = piece_type
        super().__init__(skill_name=skill_name, skill_type="piece")

class StudDirectionSkill(Skill):
    def __init__(self, skill_name, piece_type, stud_type) -> None:
        self.piece_type = piece_type
        self.stud_type = stud_type
        super().__init__(skill_name=skill_name, skill_type="stud_direction")

skills = {
    0: PieceSkill("identify_fm", "fm"),
    1: PieceSkill("identify_buzzer", "buzzer"),
    2: PieceSkill("identify_touch_plate", "touch_plate"),
    3: PieceSkill("identify_reed_switch", "reed_switch"),
    4: PieceSkill("identify_button_switch", "button_switch"),
    5: PieceSkill("identify_normal_switch", "switch"),
    6: PieceSkill("identify_cds", "cds"),
    7: PieceSkill("identify_led", "led"),
    8: PieceSkill("identify_lamp", "lamp"),
    9: PieceSkill("identify_battery", "battery"),
    10: PieceSkill("identify_speaker", "speaker"),
    11: PieceSkill("identify_mc", "mc"),
    12: PieceSkill("identify_motor", "motor"),
    13: Skill("connect_pieces", "connection"),
    14: Skill("close_circuit", "closed"),
    15: StudDirectionSkill("led_pos_stud", "led", StudType.POSITIVE),
    16: StudDirectionSkill("led_neg_stud", "led", StudType.NEGATIVE),
    17: StudDirectionSkill("fm_in_stud", "fm", StudType.IN),
    18: StudDirectionSkill("fm_out_stud", "fm", StudType.OUT),
    19: StudDirectionSkill("fm_signal_stud", "fm", StudType.SIGNAL),
    20: StudDirectionSkill("mc_in_stud", "mc", StudType.IN),
    21: StudDirectionSkill("mc_out_stud", "mc", StudType.OUT),
    22: StudDirectionSkill("mc_trigger_stud", "mc", StudType.TRIGGER),
    23: StudDirectionSkill("mc_repeat_stud", "mc", StudType.REPEAT),
    24: StudDirectionSkill("mc_restart_stud", "mc", StudType.RESTART),
}

class TaskObservations():
    def __init__(self, description, involved_skill_ids, uids) -> None:
        self.description = description
        self.sids = involved_skill_ids
        self.uids = uids
        
        self.os = {}
        self.cs = {}
        for sid in self.sids:
            self.cs[sid] = {}
            self.os[sid] = 0
            for uid in self.uids:
                self.cs[sid][uid] = 0
    
    def __str__(self):
        string = ""
        for sid in self.os:
            string += f"{self.os[sid]} "
            for uid in self.cs[sid]:
                string += f"{self.cs[sid][uid]} "
            string += "\n"
        return string
    
    def check_identify_skill(self, sid, piece_type, board):
        o = 0
        if board.find_piece(piece_type):
            o = 1
        c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "piece":
                        if history_elem.piece_type == piece_type and history_elem.move == "added":
                            uid_c = max(uid_c, history_elem.contr_percentage)
                c[uid] = uid_c
            else:
                c[uid] = 0
        self.os[sid] = o
        self.cs[sid] = c
    
    def check_connection_skill(self, sid, board):
        o = 0
        for piece_id in board.pieces:
            _, con_count = board.get_connections(piece_id)
            if con_count > 0:
                o = 1
                break
        c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "connection" and history_elem.move == "added":
                        uid_c = max(uid_c, history_elem.contr_percentage)
                c[uid] = uid_c
            else:
                c[uid] = 0
        self.os[sid] = o
        self.cs[sid] = c
    
    def check_closed_skill(self, sid, board, found_flow):
        o = 0
        if found_flow:
            o = 1
        c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "closed" and history_elem.move == "added":
                        uid_c = max(uid_c, history_elem.contr_percentage)
                c[uid] = uid_c
            else:
                c[uid] = 0
        self.os[sid] = o
        self.cs[sid] = c
    
    def check_stud_direction_skill(self, sid, piece_type, stud_type, board, found_flow, correct_studs):
        o = 0
        if found_flow:
            for correct_stud in correct_studs:
                if correct_stud[1] == piece_type and correct_stud[2].value == stud_type.value:
                    o = 1
        c = {}
        for uid in board.history.obs_history:
            if o:
                uid_hist = board.history.obs_history[uid]
                uid_c = 0
                for history_elem in uid_hist:
                    if history_elem.elem_type == "stud_direction":
                        if history_elem.piece_type == piece_type and history_elem.stud_type == stud_type and history_elem.move == "added":
                            uid_c = max(uid_c, history_elem.contr_percentage)
                c[uid] = uid_c
            else:
                c[uid] = 0
        self.os[sid] = o
        self.cs[sid] = c
        return correct_studs

    def check_skills(self, board):
        found_flow, correct_studs = board.find_flow()

        for sid in self.sids:
            skill = skills[sid]
            if skill.skill_type == "piece":
                self.check_identify_skill(sid, skill.piece_type, board)
            if skill.skill_type == "connection":
                self.check_connection_skill(sid, board)
            if skill.skill_type == "closed":
                self.check_closed_skill(sid, board, found_flow)
            if skill.skill_type == "stud_direction":
                self.check_stud_direction_skill(sid, skill.piece_type, skill.stud_type, board, found_flow, correct_studs)


def get_task(tid, uids):
    if tid == "task1":
        return TaskObservations("Build a circuit with a lamp that can be turned on and off using a regular switch", [5, 8, 9, 13, 14], uids)
    if tid == "task2":
        return TaskObservations("Build a circuit with a lamp that can be turned on and off using a button switch", [4, 8, 9, 13, 14], uids)
    if tid == "task3":
        return TaskObservations("Build a circuit with a lamp that can be turned on and off using a reed switch", [3, 8, 9, 13, 14], uids)
    if tid == "task4":
        return TaskObservations("Build a circuit with a lamp that can be turned on and off using a regular switch", [3, 8, 9, 13, 14], uids)
    if tid == "task4":
        return TaskObservations("Build a circuit with a light that can be turned on and off using a regular switch", [3, 8, 9, 13, 14], uids)
    if tid == "task5":
        return TaskObservations("Build a circuit with a light that can be turned on and off using a regular switch", [3, 8, 9, 13, 14], uids)
    if tid == "task6":
        return TaskObservations("Build a circuit with a light that can be turned on and off using a regular switch", [3, 8, 9, 13, 14], uids)


