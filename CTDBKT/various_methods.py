from matplotlib import pyplot as plt
import numpy as np

class GenericGroupSkillBelief():
    def __init__(self, sname, sid, uids, p_L_0s, p_S, p_G, p_T, n, discussion_time, solve_time, usb) -> None:
        self.sname = sname
        self.sid = sid
        self.users = {}
        self.p_L_0s = p_L_0s
        self.t = 1

        self.p_T = p_T
        self.o = [0]

        for uid in uids:
            user = usb(uid=uid, sname=sname, sid=sid, p_L_0=p_L_0s[uid], p_S=p_S, p_G=p_G, p_T=p_T, E_k=discussion_time + solve_time, n=n)
            self.users[uid] = user

    def step(self, o_t, c_ts):
        self.o.append(o_t)
        current_Hs = []
        sum_H = 0
        sum_c = 0

        for uid in c_ts:
            current_Hs.append(self.users[uid].H[self.t - 1])
            sum_H += current_Hs[uid]
            sum_c += c_ts[uid]

        for uid in c_ts:
            if len(self.users) > 1:
                other_H = (sum_H - self.users[uid].H[self.t - 1]) / (len(self.users) - 1)
                other_c_t = sum_c - c_ts[uid]
            else:
                other_H = 0.5
                other_c_t = 0
            self.users[uid].step(o_t, c_ts[uid], other_H, other_c_t)
        
        self.t += 1

class KUserSkillBelief():
    def __init__(self, uid, sname, sid, p_L_0, p_S, p_G, p_T, E_k, n) -> None:
        self.sname = sname

        self.uid = uid
        self.sid = sid

        self.p_L_0 = p_L_0
        self.p_L = p_L_0
        self.p_S = p_S
        self.p_G = p_G
        self.E_k = E_k
        self.n = n

        self.p_T = p_T

        self.o = [0]
        self.c = [0]
        self.H = [p_L_0]
        self.t = 1

    def step(self, o_t, c_t, other_H):
        H_t = 0
        self.c.append(c_t)
        self.o.append(o_t)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_i_given_L_o_i_i(i, other_H)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1

    def p_H_i_given_L_o_i_i(self, i, other_H):
        p_L = self.p_L
        p_S = self.p_S

        p_observation_given_o_1_A_1 = self.p_observation_given_A(o_t = True, A = True)
        contributed = (p_L * (1 - p_S)) / (p_observation_given_o_1_A_1)

        p_A_given_i = self.p_A_given_t(i)
        p_observation_given_o_0_A_1 = self.p_observation_given_A(o_t = False, A = True)
        not_contributed = (p_L * (p_A_given_i * p_S + (1 - p_A_given_i))) / (p_A_given_i * p_observation_given_o_0_A_1 + (1 - p_A_given_i))

        p_H_given_o = self.c[i] * contributed + (1 - self.c[i]) * not_contributed

        p_H_given_o + (1 - p_H_given_o) * (self.p_T * other_H * self.p_A_given_t(self.t)) 

            

    def p_observation_given_A(self, o_t, A):
        if A:
            if o_t:
                return self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
            else:
                return self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)
        else:
            if o_t:
                return 0
            else:
                return 1
        
    def p_A_given_t(self, t):
        if t <= self.E_k:
            return t / self.E_k
        else:
            return 1

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}' 
    

class OUserSkillBelief():
    def __init__(self, uid, sname, sid, p_L_0, p_S, p_G, p_T, E_k, n) -> None:
        self.sname = sname

        self.uid = uid
        self.sid = sid

        self.p_L_0 = p_L_0
        self.p_L = p_L_0
        self.p_S = p_S
        self.p_G = p_G
        self.E_k = E_k
        self.n = n

        self.p_T = p_T

        self.o = [0]
        self.c = [0]
        self.H = [p_L_0]
        self.t = 1

    def step(self, o_t, c_t, other_H):
        H_t = 0
        self.c.append(c_t)
        self.o.append(o_t)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_i_given_L_o_i_i(i)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1

    def p_H_i_given_L_o_i_i(self, i):
        p_L = self.p_L
        p_S = self.p_S

        p_observation_given_o_1_A_1 = self.p_observation_given_A(o_t = True, A = True)
        contributed = (p_L * (1 - p_S)) / (p_observation_given_o_1_A_1)

        p_A_given_i = self.p_A_given_t(i)
        p_observation_given_o_0_A_1 = self.p_observation_given_A(o_t = False, A = True)
        not_contributed = (p_L * (p_A_given_i * p_S + (1 - p_A_given_i))) / (p_A_given_i * p_observation_given_o_0_A_1 + (1 - p_A_given_i))

        p_H_given_o = self.c[i] * contributed + (1 - self.c[i]) * not_contributed

        return p_H_given_o + (1 - p_H_given_o) * (self.p_T * self.o[i]) 
            

    def p_observation_given_A(self, o_t, A):
        if A:
            if o_t:
                return self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
            else:
                return self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)
        else:
            if o_t:
                return 0
            else:
                return 1
        
    def p_A_given_t(self, t):
        if t <= self.E_k:
            return t / self.E_k
        else:
            return 1

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}' 
    


class TDBKT():
    def __init__(self, uid, sname, sid, p_L_0, p_S, p_G, p_T, E_k, n) -> None:
        self.sname = sname

        self.uid = uid
        self.sid = sid

        self.p_L_0 = p_L_0
        self.p_L = p_L_0
        self.p_S = p_S
        self.p_G = p_G
        self.E_k = E_k
        self.n = n

        self.p_T = p_T

        self.o = [0]
        self.c = [0]
        self.H = [p_L_0]
        self.t = 1

    def step(self, o_t, c_t, other_H, other_c_t):
        H_t = 0
        self.c.append(c_t)
        self.o.append(o_t)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_i_given_L_o_i_i(i)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1

    def p_H_i_given_L_o_i_i(self, i):
        p_L = self.p_L
        p_S = self.p_S

        p_observation_given_o_1_A_1 = self.p_observation_given_A(o_t = True, A = True)
        contributed = (p_L * (1 - p_S)) / (p_observation_given_o_1_A_1)

        p_A_given_i = self.p_A_given_t(i)
        p_observation_given_o_0_A_1 = self.p_observation_given_A(o_t = False, A = True)
        not_contributed = (p_L * (p_A_given_i * p_S + (1 - p_A_given_i))) / (p_A_given_i * p_observation_given_o_0_A_1 + (1 - p_A_given_i))

        p_H_given_o = self.o[i] * contributed + (1 - self.o[i]) * not_contributed

        return p_H_given_o
            

    def p_observation_given_A(self, o_t, A):
        if A:
            if o_t:
                return self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
            else:
                return self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)
        else:
            if o_t:
                return 0
            else:
                return 1
        
    def p_A_given_t(self, t):
        if t <= self.E_k:
            return t / self.E_k
        else:
            return 1

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}' 