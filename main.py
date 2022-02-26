import json
import os


class TreeItem:
    def __init__(self, data, widget):
        self.data = data
        self.widget = widget
        self.left = None
        self.right = None


class Status:
    def __init__(self):
        self.tree_root = None
        self.tree_dict = None


def dfs(tree: TreeItem, str_list: str, str_dict: dict):
    if tree.left is None:
        str_dict.setdefault(tree.data, str_list)
    else:
        dfs(tree.left, str_list + '0', str_dict)
        dfs(tree.right, str_list + '1', str_dict)


def tree_print(s: Status):
    tree_file_name = 'TreePrint.txt'
    tree_file = open(tree_file_name, 'w')
    if s.tree_root is None:
        print('No tree found')
    tree_root = s.tree_root
    tree_queue = list()
    tree_queue.append(tree_root)
    new_tree_queue = list()
    while not len(tree_queue) == 0:
        if tree_queue[0] is not None:
            if tree_queue[0].data is not None:
                print(tree_queue[0].data, tree_queue[0].widget, end='  ')
                tree_file.write(str(tree_queue[0].data) + ' ' + str(tree_queue[0].widget) + '  ')
            else:
                print('*', tree_queue[0].widget, end='  ')
                tree_file.write('* ' + str(tree_queue[0].widget) + '  ')
            new_tree_queue.append(tree_queue[0].left)
            new_tree_queue.append(tree_queue[0].right)
            if len(tree_queue) == 1:
                print('')
                tree_file.write('\n')
                tree_queue = tree_queue + new_tree_queue
                new_tree_queue.clear()
        tree_queue.pop(0)
    print('')


def to_bytes(data):
    b = bytearray()
    end_length = len(data) % 8
    for i in range(0, len(data) - end_length, 8):
        b.append(int(data[i:i + 8], 2))
    b.append(int(data[len(data) - end_length:len(data)], 2))
    b.append(int(bin(end_length), 2))
    return bytes(b)


def read_text_from_file(filename: str):
    trans_file = open(filename, mode='r')
    trans = trans_file.readlines()
    word = str()
    for i in trans:
        word = word + i
    return word


def initialization(s: Status):
    print('Initializing tree')
    method = eval(input('1.from console 2.from file 3.from input dict directly\n'))
    word = str()
    word_dict = dict()
    if method == 1 or method == 2:
        if method == 1:
            in_line = input() + '\n'
            while ':q' not in in_line:
                word += in_line
                in_line = input() + '\n'
            word += in_line.split(':q')[0]
        elif method == 2:
            word = read_text_from_file('ToBeTran.txt')
        for i in word:
            if i not in word_dict.keys():
                word_dict.setdefault(i, 1)
            else:
                word_dict[i] += 1
    elif method == 3:
        print('Example:\nA 64\nB 13\n...\ninput # for end')
        user_input=input()
        while(not user_input.startswith('#')):
            key,value=user_input.split(' ')

            if key=='':
                word_dict.setdefault(' ',eval(value))
            else:
                value=eval(value)
                word_dict.setdefault(key,value)
            user_input=input()
    else:
        raise KeyError


    tree_item_list = list()
    for i in word_dict.items():
        tree_item_list.append(TreeItem(i[0], i[1]))
    while not len(tree_item_list) == 1:
        tree_item_list.sort(key=lambda e: -e.widget)
        left = tree_item_list.pop()
        right = tree_item_list.pop()
        new_tree_item = TreeItem(None, left.widget + right.widget)
        new_tree_item.left = left
        new_tree_item.right = right
        tree_item_list.append(new_tree_item)
    tree_root = tree_item_list[0]
    s.tree_root = tree_root
    tree_trans_dict = dict()
    dfs(tree_root, '', tree_trans_dict)
    if len(tree_trans_dict.items()) == 1:
        tree_trans_dict[list(tree_trans_dict.keys())[0]] = '0'
    s.tree_dict = tree_trans_dict
    file_name = 'hfmTree.json'
    fp = open(file=file_name, mode='w')
    json.dump(tree_trans_dict, fp)
    print('the encode answer has saved to', file_name)


def encoding(s: Status):
    trans_file_name = 'ToBeTran.txt'
    answer_file_name = 'CodeFile.bin'
    tree_file_name = 'hfmTree.json'
    ans_file = open(answer_file_name, mode='wb')
    tree: dict
    if s.tree_dict is None:
        print('Tree not find in memory, trying to read from file')
        try:
            tree_file = open(tree_file_name, mode='r')
        except FileNotFoundError:
            print('read file error')
            return
        tree = json.load(tree_file)
    else:
        print('Find tree in memory')
        tree = s.tree_dict
    tran_word = read_text_from_file(trans_file_name)
    tree_string = str()
    for i in tran_word:
        tree_string = tree_string + tree[i]
    try:
        ans_file.write(to_bytes(tree_string))
        print('Successfully encode the text')
        ans_file.close()
        trans_file_size = os.path.getsize(trans_file_name)
        answer_file_size = os.path.getsize(answer_file_name)
        print(f'Original file: {trans_file_size} bytes')
        print(f'Compressed file: {answer_file_size} bytes')
        print(
            'Compression rate: {}%'.format(round((((trans_file_size - answer_file_size) / trans_file_size) * 100), 0)))
    except KeyError:
        print('The tree file or memory don\'t match the trans file')


def decoding(s: Status):
    ans_file_name = 'TextFile.txt'
    if s.tree_dict is None:
        print('No tree find, please initialize first')
        return
    ans_file = open(ans_file_name, mode='w')
    tree = s.tree_dict
    tree_reverse = dict(zip(tree.values(), tree.keys()))
    code_file_name = 'CodeFile.bin'
    code_file = open(code_file_name, mode='rb')
    code_str = code_file.read()
    tree_word_bin = format(int.from_bytes(code_str, byteorder='big', signed=False),
                           '#0' + str(len(code_str) * 8 + 2) + 'b')[2:]
    end_length_bin = tree_word_bin[len(tree_word_bin) - 8:len(tree_word_bin)]
    end_length = int(end_length_bin, 2)
    tree_word_bin = tree_word_bin[0:-8]
    tree_word_bin = tree_word_bin[0:-8] + tree_word_bin[len(tree_word_bin) - end_length:len(tree_word_bin)]
    temp = str()
    tree_word = str()
    for i in tree_word_bin:
        temp = temp + i
        try:
            tree_word = tree_word + tree_reverse[temp]
            temp = ''
        except KeyError:
            pass
    print(tree_word)
    ans_file.write(tree_word)


def print_answer(s: Status):
    code_file_name = 'CodeFile.bin'
    code_print_file_name = 'CodePrin.txt'
    code_file = open(code_file_name, mode='rb')
    code_print_file = open(code_print_file_name, mode='w')
    code_str = code_file.read()
    tree_word_bin = format(int.from_bytes(code_str, byteorder='big', signed=False),
                           '#0' + str(len(code_str) * 8 + 2) + 'b')[2:]
    print(tree_word_bin)
    code_print_file.write(tree_word_bin)
    return 0


def get_input():
    print('[I]Initialization')
    print('[E]Encoding')
    print('[D]Decoding')
    print('[P]Print')
    print('[T]Tree printing')
    print('[Q]Quit')
    i = input()
    while True:
        if len(i) == 1:
            return i.upper()
        else:
            print('Input error, please input again')
            i = input()


if __name__ == '__main__':
    switch = {'I': initialization, 'E': encoding, 'D': decoding, 'P': print_answer, 'T': tree_print}
    decision = get_input()
    status = Status()
    while not decision == 'Q':
        switch.get(decision)(status)
        decision = get_input()