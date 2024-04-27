
class SkillMastery():
    def __init__(self, p_L_0, p_S, p_G, E_k, n) -> None:
        self.p_L_0 = p_L_0
        self.p_L = p_L_0
        self.p_S = p_S
        self.p_G = p_G
        self.E_k = E_k
        self.n = n

        self.o = [False]
        self.H = [p_L_0]
        self.t = 1

    def step(self, o_t):
        H_t = 0
        self.o.append(o_t)

        range_size = 0
        for i in range(max(self.t - self.n, 0), self.t + 1):
            if i == 0:
                H_t += self.p_L_0
            else:
                H_t += self.p_H_i_given_L_o_i_i(i)
            range_size += 1
        
        self.H.append(H_t / range_size)
        self.t += 1

    def p_H_i_given_L_o_i_i(self, i):
        p_L = self.p_L
        p_S = self.p_S

        if self.o[i]:
            p_observation_given_o_1_A_1 = self.p_observation_given_A(o_t = True, A = True)
            return (p_L * (1 - p_S)) / (p_observation_given_o_1_A_1)
        else:
            p_A_given_i = self.p_A_given_t(i)
            p_observation_given_o_0_A_1 = self.p_observation_given_A(o_t = False, A = True)
            return (p_L * (p_A_given_i * p_S + (1 - p_A_given_i))) / (p_A_given_i * p_observation_given_o_0_A_1 + (1 - p_A_given_i))

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

    def get_H(self):
        return self.H

    def __str__(self):
        return f'o: {self.o}, \nH: {self.H}, \nt: {self.t}' 

class ContributionSkillMastery():
    def __init__(self, p_L_0, p_S, p_G, E_k, n) -> None:
        self.p_L_0 = p_L_0
        self.p_L = p_L_0
        self.p_S = p_S
        self.p_G = p_G
        self.E_k = E_k
        self.n = n

        self.o = [False]
        self.c = [0]
        self.H = [p_L_0]
        self.t = 1

    def step(self, c_t):
        H_t = 0
        self.c.append(c_t)

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

    def get_H(self):
        return self.H

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}' 

class GroupSkillMastery():
    def __init__(self, num_students, p_L_0, p_S, p_G, p_T, p_F, n, discussion_time, solve_time) -> None:
        self.students = []
        self.num_students = num_students
        self.t = 1

        self.p_T = p_T
        self.p_F = p_F
        self.o = [0]

        for i in range(self.num_students):
            student = LearnContributionSkillMastery(p_L_0=p_L_0, p_S=p_S, p_G=p_G, p_T=p_T, p_F=p_F, E_k=discussion_time + solve_time, n=n)
            self.students.append(student)

    def step(self, o_t, c_ts):
        self.o.append(o_t)
        current_Hs = []
        sum_H = 0
        for i in range(self.num_students):
            current_Hs.append(self.students[i].H[self.t - 1])
            sum_H += current_Hs[i]

        for i in range(self.num_students):
            other_H = (sum_H - self.students[i].H[self.t - 1]) / (self.num_students - 1)
            self.students[i].step(c_ts[i], other_H)
        
        self.t += 1

class LearnContributionSkillMastery():
    def __init__(self, p_L_0, p_S, p_G, p_T, p_F, E_k, n) -> None:
        self.p_L_0 = p_L_0
        self.p_L = p_L_0
        self.p_S = p_S
        self.p_G = p_G
        self.E_k = E_k
        self.n = n

        self.p_T = p_T
        self.p_F = p_F

        self.o = [False]
        self.c = [0]
        self.H = [p_L_0]
        self.t = 1

    def step(self, c_t, other_H):
        H_t = 0
        self.c.append(c_t)

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

        return p_H_given_o * (1 - (self.p_F * (1 - other_H) * self.p_A_given_t(self.t))) + (1 - p_H_given_o) * (self.p_T * other_H * self.p_A_given_t(self.t)) 
            

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

    def get_H(self):
        return self.H

    def __str__(self):
        return f'c: {self.c}, \nH: {self.H}, \nt: {self.t}' 