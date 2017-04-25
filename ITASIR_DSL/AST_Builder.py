class Node:
    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        return self.type + ":\n\t" + self.parts_str().replace("\n", "\n\t")

    def add_parts(self, parts):
        self.parts += parts
        return self

    def __init__(self, type, parts):
        self.type = type
        self.parts = parts

if __name__ == "__main__":
    test = dict({("11", "21"): 1})
    test.update({("22", "22"): 2})
    test.update({("33", "33"): 3})

    val = test.get(("22", "22"))
    print(val)

