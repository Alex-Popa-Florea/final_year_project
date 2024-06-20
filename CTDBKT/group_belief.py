from matplotlib import pyplot as plt
import numpy as np

# Group skill 
class GroupSkillBelief():
    def __init__(self, sname, sid, uids, p_L_0s, p_S, p_G, p_T, n, discussion_time, solve_time, usb, use_history=True) -> None:
        self.sname = sname
        self.sid = sid
        self.users = {}
        self.p_L_0s = p_L_0s
        self.t = 1

        self.p_T = p_T
        self.o = [0]

        self.use_history = use_history

        for uid in uids:
            user = usb(uid=uid, sname=sname, sid=sid, p_L_0=p_L_0s[uid], p_S=p_S, p_G=p_G, p_T=p_T, E_k=discussion_time + solve_time, n=n)
            self.users[uid] = user

    def step(self, o_t, c_ts):
        self.o.append(o_t)
        sum_H = 0
        sum_c = 0
        sum_L = 0

        for uid in c_ts:
            sum_H += self.users[uid].H[self.t - 1]
            sum_c += c_ts[uid]
            sum_L += self.users[uid].p_L

        for uid in c_ts:
            if len(self.users) > 1:
                other_H = (sum_H - self.users[uid].H[self.t - 1]) / (len(self.users) - 1)
                other_c_t = sum_c - c_ts[uid]
                other_L = (sum_L - self.users[uid].p_L) / (len(self.users) - 1)
            else:
                other_H = 0.5
                other_c_t = 0
                other_L = 0.5
            self.users[uid].step(o_t, c_ts[uid], other_H, other_c_t, other_L)
        
        self.t += 1   

def plot_all(beliefs_methods, real_masteries={}):
    os = {}
    cs = {}
    ms = {}
    bs = {}
    skill_names = {}
    ts = []

    for method in beliefs_methods:
        beliefs = beliefs_methods[method]

        for sid in beliefs:
            belief = beliefs[sid]

            os[sid] = np.array(belief.o)
            
            if sid not in ms:
                ms[sid] = {}
                cs[sid] = {}
                bs[sid] = {}
                skill_names[sid] = belief.sname

            for uid in belief.users:
                if uid not in bs[sid]:
                    cs[sid][uid] = {}
                    bs[sid][uid] = {}
                    
                if real_masteries != {}:
                    mastery = real_masteries[uid][sid]
                    ms[sid][uid] = np.array(mastery)
                
                cs[sid][uid][method] = np.array(belief.users[uid].c)
                bs[sid][uid][method] = np.array(belief.users[uid].H)
                ts = np.arange(belief.users[uid].t)

    for sid in bs:
        plt.figure(figsize=(10, 5))
        plt.plot(ts, os[sid], linestyle='-')

        plt.xlabel('Time Step')
        plt.ylabel('Observation')
        plt.title('Observation SID: ' + str(sid))
        plt.ylim(-0.1, 1.1)
        plt.show()
        
        for uid in bs[sid]:
            plt.figure(figsize=(10, 5))

            for method in bs[sid][uid]:
                plt.plot(ts, cs[sid][uid][method], linestyle='-', label=f'Contr {method}')

            plt.xlabel('Time Step')
            plt.ylabel('Contribition')
            plt.title('Contribition SID: ' + str(sid) + ' UID: ' + str(uid))
            plt.legend()
            plt.ylim(-0.1, 1.1)
            plt.show()

            plt.figure(figsize=(10, 5))
            for method in bs[sid][uid]:
                plt.plot(ts, bs[sid][uid][method], linestyle='-', label=f'Belief {method}')

            if real_masteries != {}:
                plt.plot(ts, ms[sid][uid], linestyle=':', label='Truth')

            plt.xlabel('Time Step')
            plt.ylabel('Mastery')
            plt.title('Belief Skill: ' + str(skill_names[sid]) + ' SID: ' + str(sid) + ' UID: ' + str(uid))
            plt.legend()
            plt.ylim(-0.1, 1.1)
            plt.show()
    

def plot_everything(ts, bs, os={}, cs={}, ms={}, chosen_methods={}):

    for sid in bs:
        plt.figure(figsize=(10, 5))
        if os != {}:
            plt.plot(ts, os[sid], linestyle='-')

            plt.xlabel('Time Step')
            plt.ylabel('Observation')
            plt.title('Observation SID: ' + str(sid))
            plt.ylim(-0.1, 1.1)
            plt.show()
        
        for uid in bs[sid]:
            plt.figure(figsize=(10, 5))

            if cs != {}:
                for method in bs[sid][uid]:
                    if method in chosen_methods:
                        plt.plot(ts, cs[sid][uid][method], linestyle='-', label=f'Contr {method}')

                plt.xlabel('Time Step')
                plt.ylabel('Contribition')
                plt.title('Contribition SID: ' + str(sid) + ' UID: ' + str(uid))
                plt.legend()
                plt.ylim(-0.1, 1.1)
                plt.show()

            plt.figure(figsize=(10, 5))
            for method in bs[sid][uid]:
                if method in chosen_methods:
                    plt.plot(ts, bs[sid][uid][method], linestyle='-', label=f'Belief {method}')

            if ms != {}:
                plt.plot(ts, ms[sid][uid], linestyle=':', label='Truth')

            plt.xlabel('Time Step')
            plt.ylabel('Mastery')
            plt.title('Belief Skill: SID: ' + str(sid) + ' UID: ' + str(uid))
            plt.legend()
            plt.ylim(-0.1, 1.1)
            plt.show()

def get_everything(beliefs_methods, real_masteries={}):
    os = {}
    cs = {}
    ms = {}
    bs = {}
    ts = []
    skill_names = {}

    for method in beliefs_methods:
        beliefs = beliefs_methods[method]

        for sid in beliefs:
            belief = beliefs[sid]

            os[sid] = belief.o
            
            if sid not in ms:
                ms[sid] = {}
                cs[sid] = {}
                bs[sid] = {}
                skill_names[sid] = belief.sname

            for uid in belief.users:
                if uid not in bs[sid]:
                    cs[sid][uid] = {}
                    bs[sid][uid] = {}
                    
                if real_masteries != {}:
                    mastery = real_masteries[uid][sid]
                    ms[sid][uid] = mastery
                
                cs[sid][uid][method] = belief.users[uid].c
                bs[sid][uid][method] = belief.users[uid].H
                ts = np.arange(belief.users[uid].t).tolist()

    return os, cs, ms, bs, ts