class KB:
    def __init__(self):
        self.c = []
        self.steps = 0

    def add(self, cl):
        if cl not in self.c:
            self.c.append(cl)

    def tell(self, x, y, b, s, r, c):
        n = self.neigh(x, y, r, c)

        self.add({f"P{x}_{y}": False})
        self.add({f"W{x}_{y}": False})

        if b:
            self.add({f"P{i}_{j}": True for i, j in n})
        else:
            for i, j in n:
                self.add({f"P{i}_{j}": False})

        if s:
            self.add({f"W{i}_{j}": True for i, j in n})
        else:
            for i, j in n:
                self.add({f"W{i}_{j}": False})

    def neigh(self, x, y, r, c):
        res = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < r and 0 <= ny < c:
                res.append((nx, ny))
        return res

    def resolve(self, a, b):
        out = []
        for k in a:
            if k in b and a[k] != b[k]:
                self.steps += 1
                c = {**a, **b}
                del c[k]
                out.append(c)
        return out

    def prove(self, lit, val):
        kb = [dict(x) for x in self.c]
        kb.append({lit: not val})
        new = []

        while True:
            for i in range(len(kb)):
                for j in range(i+1, len(kb)):
                    for r in self.resolve(kb[i], kb[j]):
                        if not r:
                            return True
                        if r not in kb and r not in new:
                            new.append(r)

            if all(x in kb for x in new):
                return False
            kb += new

    def safe(self, x, y):
        return self.prove(f"P{x}_{y}", False) and self.prove(f"W{x}_{y}", False)
