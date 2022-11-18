import copy


class FieldState:
    def __init__(self):
        self.state = [None] * 8

    def set(self, fp, v):
        z = 0
        for i in range(fp.last + 1):
            z = fp.path[i]
            y = len(self.state)
            if y < z + 2:
                k = [None] * max(z + 2, y * 2)
                self.state = copy.deepcopy(k)
                self.state = k

            if i == fp.last:
                if self.state[z] == None:
                    self.state[z] = v

                return

            if self.state[z] == None:
                self.state[z] = FieldState()
