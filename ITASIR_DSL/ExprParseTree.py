from pythonds.basic.stack import Stack
from pythonds.trees.binaryTree import BinaryTree

class treeNode(object):
    def __init__(self, value, children = []):
        self.value = value
        self.children = children

    def __str__(self, level=0):
        ret = "\t"*level+repr(self.value)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return '<tree node representation>'

def buildParseTree(fpexp, aviableOperators=["and", "And", "or", "Or", ")"]):
    fplist = fpexp.split()
    pStack = Stack()
    eTree = BinaryTree('')
    pStack.push(eTree)
    currentTree = eTree
    for i in fplist:
        if i == '(':
            currentTree.insertLeft('')
            pStack.push(currentTree)
            currentTree = currentTree.getLeftChild()
        elif i not in aviableOperators:
            currentTree.setRootVal(int(i))
            parent = pStack.pop()
            currentTree = parent
        elif i in aviableOperators:
            currentTree.setRootVal(i)
            currentTree.insertRight('')
            pStack.push(currentTree)
            currentTree = currentTree.getRightChild()
        elif i == ')':
            currentTree = pStack.pop()
        else:
            raise ValueError
    return eTree

if __name__ == "__main__":
    pt = buildParseTree("( ( 10 and 5 ) or 3 )")
    print("pythonds: inorder tree elements output")
    pt.inorder()
    print("pythonds: postorder tree elements output")
    pt.postorder()  #defined and explained in the next section
    print("output in tree view")
    pt.printexp()

    #root = treeNode(pt.getRootVal())
    #root.children = [pt.getLeftChild(), pt.getRightChild()]

    print("--- tree ---")
    print("root")
    print(pt.getRootVal())
    print("right")
    print(pt.getRightChild())
    print("left")
    print(pt.isLeaf())
    print("left2")
    print(pt.getLeftChild())
    #print(root)