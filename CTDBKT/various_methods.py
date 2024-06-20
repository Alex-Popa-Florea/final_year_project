from matplotlib import pyplot as plt
import numpy as np

# User Independent Single Time Step BKT
class UISTS_BKT():
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

    def step(self, o_t, c_t, other_H, other_c_t, other_L):
        self.c.append(o_t)
        self.o.append(o_t)
        
        if self.t >= self.E_k:
            p_mastered = self.p_L * self.p_o_given_L(o_t) / self.p_o(o_t)
            self.H.append(p_mastered)
        else:
            self.H.append(self.p_L)
        self.t += 1

    def p_o_given_L(self, o_t):
        if o_t:
            return 1 - self.p_S
        else:
            return self.p_S

    def p_o(self, o_t):
        if o_t:
            return self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
        else:
            return self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}' 

class UIETS_BKT():
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
        self.H = [self.p_L * self.p_o_given_L(0) / self.p_o(0)]
        self.t = 1

    def step(self, o_t, c_t, other_H, other_c_t, other_L):
        self.c.append(o_t)
        self.o.append(o_t)
        
        p_mastered = self.p_L * self.p_o_given_L(o_t) / self.p_o(o_t)
        self.H.append(p_mastered)

        self.t += 1

    def p_o_given_L(self, o_t):
        if o_t:
            return 1 - self.p_S
        else:
            return self.p_S

    def p_o(self, o_t):
        if o_t:
            return self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
        else:
            return self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}' 


# Time-Dependant Baysean Knowledge Tracing (Salomons N, Scassellati B. Time-dependant bayesian knowledge trac-ing—robots that model user skills over time. Frontiers in Robotics and AI.2024 Feb;10.)
class TD_BKT():
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

    def step(self, o_t, c_t, other_H, other_c_t, other_L):
        H_t = 0
        self.c.append(o_t)
        self.o.append(o_t)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_given_L_o_i(i)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1
            
    def p_H_given_L_o_i(self, i):
        return self.p_L * self.p_o_given_L(self.o[i], i) / self.p_o(self.o[i], i)

    def p_o_given_L(self, o_t, t):
        p_o_L_A1 = self.p_o_given_L_A(o_t, A = True) * self.p_A_given_t(t)
        p_o_L_A0 = self.p_o_given_L_A(o_t, A = False) * (1 - self.p_A_given_t(t))
        return p_o_L_A1 + p_o_L_A0

    def p_o_given_L_A(self, o_t, A):
        if A:
            if o_t:
                return 1 - self.p_S
            else:
                return self.p_S
        else:
            if o_t:
                return 0
            else:
                return 1

    def p_o(self, o_t, t):
        p_o_A1 = self.p_o_given_A(o_t, A = True) * self.p_A_given_t(t)
        p_o_A0 = self.p_o_given_A(o_t, A = False) * (1 - self.p_A_given_t(t))
        return p_o_A1 + p_o_A0

    def p_o_given_A(self, o_t, A):
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
    
# Collaborative Time-Dependant Baysean Knowledge Tracing
class CTD_BKT():
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

    def step(self, o_t, c_t, other_H, other_c_t, other_L):
        H_t = 0
        self.c.append(o_t)
        self.o.append(o_t)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_given_L_o_i(i, other_L)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1
            
    def p_H_given_L_o_i(self, i, other_L):
        return self.p_L * self.p_o_given_L(self.o[i], i, other_L) / self.p_o(self.o[i], i, other_L)

    def p_o_given_L(self, o_t, t, other_L):
        p_o_L_A1 = self.p_o_given_L_A(o_t, True, other_L) * self.p_A_given_t(t)
        p_o_L_A0 = self.p_o_given_L_A(o_t, False, other_L) * (1 - self.p_A_given_t(t))
        return p_o_L_A1 + p_o_L_A0

    def p_o_given_L_A(self, o_t, A, other_L):
        o_1_u = 1 - self.p_S
        o_1_other_u = other_L * (1 - self.p_S) + (1 - other_L) * self.p_G
        o_0_u = self.p_S
        o_0_other_u = other_L * self.p_S + (1 - other_L) * (1 - self.p_G)

        if A:
            if o_t:
                return o_1_u + o_1_other_u - o_1_u * o_1_other_u
            else:
                return o_0_u * o_0_other_u
        else:
            if o_t:
                return 0
            else:
                return 1

    def p_o(self, o_t, t, other_L):
        p_o_A1 = self.p_o_given_A(o_t, True, other_L) * self.p_A_given_t(t)
        p_o_A0 = self.p_o_given_A(o_t, False, other_L) * (1 - self.p_A_given_t(t))
        return p_o_A1 + p_o_A0

    def p_o_given_A(self, o_t, A, other_L):
        o_1_u = self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
        o_1_other_u = other_L * (1 - self.p_S) + (1 - other_L) * self.p_G
        o_0_u = self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)
        o_0_other_u = other_L * self.p_S + (1 - other_L) * (1 - self.p_G)

        if A:
            if o_t:
                return o_1_u + o_1_other_u - o_1_u * o_1_other_u
            else:
                return o_0_u * o_0_other_u
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


# Multi-contribution Collaborative TD-BKT
class MCCTD_BKT():
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

    def step(self, o_t, c_t, other_H, other_c_t, other_L):
        H_t = 0
        if c_t > self.p_G:
            self.c.append(1)
        else:
            self.c.append(0)
        self.o.append(o_t)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_given_L_c_i(i)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1
            
    def p_H_given_L_c_i(self, i):
        prob = self.p_L * self.p_c_given_L(self.c[i], i) / self.p_c(self.c[i], i)
        return prob + (1 - prob) * self.p_T * self.o[i]

    def p_c_given_L(self, c_t, t):
        p_c_L_A1 = self.p_c_given_L_A(c_t, A = True) * self.p_A_given_t(t)
        p_c_L_A0 = self.p_c_given_L_A(c_t, A = False) * (1 - self.p_A_given_t(t))
        return p_c_L_A1 + p_c_L_A0

    def p_c_given_L_A(self, c_t, A):
        if A:
            if c_t:
                return 1 - self.p_S
            else:
                return self.p_S
        else:
            if c_t:
                return 0
            else:
                return 1

    def p_c(self, c_t, t):
        p_c_A1 = self.p_c_given_A(c_t, A = True) * self.p_A_given_t(t)
        p_c_A0 = self.p_c_given_A(c_t, A = False) * (1 - self.p_A_given_t(t))
        return p_c_A1 + p_c_A0

    def p_c_given_A(self, c_t, A):
        if A:
            if c_t:
                return self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
            else:
                return self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)
        else:
            if c_t:
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

# Single-contribution Collaborative TD-BKT
class SCCTD_BKT():
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
        self.other_c = [0]
        self.H = [p_L_0]
        self.t = 1

    def step(self, o_t, c_t, other_H, other_c_t, other_L):
        H_t = 0
        self.o.append(o_t)

        if c_t >= 0.5:
            self.c.append(1)
        else:
            self.c.append(0)

        if other_c_t > 0.5:
            self.other_c.append(1)
        else:
            self.other_c.append(0)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_given_L_c_other_c_i(self.c[i], self.other_c[i], other_L, i)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1

    def p_H_given_L_c_other_c_i(self, c_i, other_c_i, other_L, i):
        p_L = self.p_L
        p_c_other_c_given_L = self.p_c_other_c_given_L(c_i, other_c_i, other_L, i)
        p_c_other_c = self.p_c_other_c(c_i, other_c_i, other_L, i)
        

        prob = (p_c_other_c_given_L * p_L) / p_c_other_c
        return min(prob + (1 - prob) * self.p_T * self.o[i], 1)

    def p_c_other_c_given_L(self, c_t, other_c_i, other_L, t):
        p_c_L_A1 = self.p_c_other_c_given_L_A(c_t, other_c_i, other_L, A = True) * self.p_A_given_t(t)
        p_c_L_A0 = self.p_c_other_c_given_L_A(c_t, other_c_i, other_L, A = False) * (1 - self.p_A_given_t(t))
        return p_c_L_A1 + p_c_L_A0
    
    def p_c_other_c(self, c_t, other_c_i, other_L, t):
        p_c_L_A1 = self.p_c_other_c_A(c_t, other_c_i, other_L, A = True) * self.p_A_given_t(t)
        p_c_L_A0 = self.p_c_other_c_A(c_t, other_c_i, other_L, A = False) * (1 - self.p_A_given_t(t))
        return p_c_L_A1 + p_c_L_A0

    def p_c_other_c_given_L_A(self, c_t, other_c_t, other_L, A):
        p_other_u_c1 = other_L * (1 - self.p_S) + (1 - other_L) * self.p_G
        p_other_u_c0 = other_L * self.p_S + (1 - other_L) * (1 - self.p_G)
        
        p_u_c1 = 1 - self.p_S
        p_u_c0 = self.p_S

        p_conflict = p_other_u_c1 * p_u_c1 * 0.5

        if A:
            if c_t == 1 and other_c_t == 0:
                return p_u_c1 * p_other_u_c0 + p_conflict
            elif c_t == 0 and other_c_t == 1:
                return p_u_c0 * p_other_u_c1 + p_conflict
            elif c_t == 0 and other_c_t == 0:
                return p_u_c0 * p_other_u_c0
            elif c_t == 1 and other_c_t == 1:
                assert False
        else:
            if c_t == 0 and other_c_t == 0:
                return 1
            else:
                return 0

    def p_c_other_c_A(self, c_t, other_c_t, other_L, A):
        p_other_u_c1 = other_L * (1 - self.p_S) + (1 - other_L) * self.p_G
        p_other_u_c0 = other_L * self.p_S + (1 - other_L) * (1 - self.p_G)
        
        p_u_c1 = self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
        p_u_c0 = self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)

        p_conflict = p_other_u_c1 * p_u_c1 * 0.5

        if A:
            if c_t == 1 and other_c_t == 0:
                return p_u_c1 * p_other_u_c0 + p_conflict
            elif c_t == 0 and other_c_t == 1:
                return p_u_c0 * p_other_u_c1 + p_conflict
            elif c_t == 0 and other_c_t == 0:
                return p_u_c0 * p_other_u_c0
            elif c_t == 1 and other_c_t == 1:
                assert False
        else:
            if c_t == 0 and other_c_t == 0:
                return 1
            else:
                return 0
        
    def p_A_given_t(self, t):
        if t <= self.E_k:
            return t / self.E_k
        else:
            return 1

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}'  

# Continuous Multi-contribution Collaborative TD-BKT
class CMCCTD_BKT():
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

    def step(self, o_t, c_t, other_H, other_c_t, other_L):
        H_t = 0
        self.c.append(min(c_t * 2, 1))
        self.o.append(o_t)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_given_L_c_i(i)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1
            
    def p_H_given_L_c_i(self, i):
        contributed = self.p_L * self.p_c_given_L(1, i) / self.p_c(1, i)
        not_contributed = self.p_L * self.p_c_given_L(0, i) / self.p_c(0, i)
        prob = contributed * self.c[i] + not_contributed * (1 - self.c[i])
        return prob + (1 - prob) * self.p_T * self.o[i]

    def p_c_given_L(self, c_t, t):
        p_c_L_A1 = self.p_c_given_L_A(c_t, A = True) * self.p_A_given_t(t)
        p_c_L_A0 = self.p_c_given_L_A(c_t, A = False) * (1 - self.p_A_given_t(t))
        return p_c_L_A1 + p_c_L_A0

    def p_c_given_L_A(self, c_t, A):
        if A:
            if c_t:
                return 1 - self.p_S
            else:
                return self.p_S
        else:
            if c_t:
                return 0
            else:
                return 1

    def p_c(self, c_t, t):
        p_c_A1 = self.p_c_given_A(c_t, A = True) * self.p_A_given_t(t)
        p_c_A0 = self.p_c_given_A(c_t, A = False) * (1 - self.p_A_given_t(t))
        return p_c_A1 + p_c_A0

    def p_c_given_A(self, c_t, A):
        if A:
            if c_t:
                return self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
            else:
                return self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)
        else:
            if c_t:
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

# Continuous Single-contribution Collaborative TD-BKT
class CSCCTD_BKT():
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
        self.other_c = [0]
        self.H = [p_L_0]
        self.t = 1

    def step(self, o_t, c_t, other_H, other_c_t, other_L):
        H_t = 0
        self.o.append(o_t)

        if o_t == 1:
            self.c.append(min(c_t * 2, 1))
            self.other_c.append(1 - min(c_t * 2, 1))
        else:
            self.c.append(0)
            self.other_c.append(0)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t_inst = self.p_L_0
            else:
                H_t_inst = self.p_H_given_L_c_other_c_i(self.c[i], self.other_c[i], other_L, i)
            H_t += H_t_inst
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1

    def p_H_given_L_c_other_c_i(self, c_i, other_c_i, other_L, i):
        p_L = self.p_L

        if c_i == 0 and other_c_i == 0:
            p_c_other_c_given_L = self.p_c_other_c_given_L(0, 0, other_L, i)
            p_c_other_c = self.p_c_other_c(0, 0, other_L, i)
            prob = (p_c_other_c_given_L * p_L) / p_c_other_c
        else:
            p_c_other_c_given_L = self.p_c_other_c_given_L(1, 0, other_L, i)
            p_c_other_c = self.p_c_other_c(1, 0, other_L, i)
            contributed = ((p_c_other_c_given_L * p_L) / p_c_other_c) * c_i
            p_c_other_c_given_L = self.p_c_other_c_given_L(0, 1, other_L, i)
            p_c_other_c = self.p_c_other_c(0, 1, other_L, i)
            not_contributed = ((p_c_other_c_given_L * p_L) / p_c_other_c) * (1 - c_i)
            prob = contributed + not_contributed

        return min(prob + (1 - prob) * self.p_T * self.o[i], 1)

    def p_c_other_c_given_L(self, c_t, other_c_i, other_L, t):
        p_c_L_A1 = self.p_c_other_c_given_L_A(c_t, other_c_i, other_L, A = True) * self.p_A_given_t(t)
        p_c_L_A0 = self.p_c_other_c_given_L_A(c_t, other_c_i, other_L, A = False) * (1 - self.p_A_given_t(t))
        return p_c_L_A1 + p_c_L_A0
    
    def p_c_other_c(self, c_t, other_c_i, other_L, t):
        p_c_L_A1 = self.p_c_other_c_A(c_t, other_c_i, other_L, A = True) * self.p_A_given_t(t)
        p_c_L_A0 = self.p_c_other_c_A(c_t, other_c_i, other_L, A = False) * (1 - self.p_A_given_t(t))
        return p_c_L_A1 + p_c_L_A0

    def p_c_other_c_given_L_A(self, c_t, other_c_t, other_L, A):
        p_other_u_c1 = other_L * (1 - self.p_S) + (1 - other_L) * self.p_G
        p_other_u_c0 = other_L * self.p_S + (1 - other_L) * (1 - self.p_G)
        
        p_u_c1 = 1 - self.p_S
        p_u_c0 = self.p_S

        p_conflict = p_other_u_c1 * p_u_c1 * 0.5

        if A:
            if c_t == 1 and other_c_t == 0:
                return p_u_c1 * p_other_u_c0 + p_conflict
            elif c_t == 0 and other_c_t == 1:
                return p_u_c0 * p_other_u_c1 + p_conflict
            elif c_t == 0 and other_c_t == 0:
                return p_u_c0 * p_other_u_c0
            elif c_t == 1 and other_c_t == 1:
                assert False
        else:
            if c_t == 0 and other_c_t == 0:
                return 1
            else:
                return 0

    def p_c_other_c_A(self, c_t, other_c_t, other_L, A):
        p_other_u_c1 = other_L * (1 - self.p_S) + (1 - other_L) * self.p_G
        p_other_u_c0 = other_L * self.p_S + (1 - other_L) * (1 - self.p_G)
        
        p_u_c1 = self.p_L * (1 - self.p_S) + (1 - self.p_L) * self.p_G
        p_u_c0 = self.p_L * self.p_S + (1 - self.p_L) * (1 - self.p_G)

        p_conflict = p_other_u_c1 * p_u_c1 * 0.5

        if A:
            if c_t == 1 and other_c_t == 0:
                return p_u_c1 * p_other_u_c0 + p_conflict
            elif c_t == 0 and other_c_t == 1:
                return p_u_c0 * p_other_u_c1 + p_conflict
            elif c_t == 0 and other_c_t == 0:
                return p_u_c0 * p_other_u_c0
            elif c_t == 1 and other_c_t == 1:
                assert False
        else:
            if c_t == 0 and other_c_t == 0:
                return 1
            else:
                return 0
        
    def p_A_given_t(self, t):
        if t <= self.E_k:
            return t / self.E_k
        else:
            return 1

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}'  



all_methods = {
    "UISTS_BKT": {"usb": UISTS_BKT, "use_history": False},
    "UIETS_BKT": {"usb": UIETS_BKT, "use_history": False},
    "TD_BKT": {"usb": TD_BKT, "use_history": False},
    "CTD_BKT": {"usb": CTD_BKT, "use_history": False},
    "MCCTD_BKT": {"usb": MCCTD_BKT, "use_history": False},
    "SCCTD_BKT": {"usb": SCCTD_BKT, "use_history": False},
    "CMCCTD_BKT": {"usb": CMCCTD_BKT, "use_history": True},
    "CSCCTD_BKT": {"usb": CSCCTD_BKT, "use_history": True},
}

