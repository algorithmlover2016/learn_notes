# -*- coding: utf-8 -*-
import random
from copy import deepcopy
from time import time

import numpy as np
from numpy.linalg import norm

from collections import Counter

Counter([0, 1, 1, 2, 2, 3, 3, 4, 3, 3]).most_common(1)


def partition_sort(arr, k, key=lambda x: x):
    """
    以枢纽(位置k)为中心将数组划分为两部分, 枢纽左侧的元素不大于枢纽右侧的元素

    :param arr: 待划分数组
    :param p: 枢纽前部元素个数
    :param key: 比较方式
    :return: None
    """
    start, end = 0, len(arr) - 1
    assert 0 <= k <= end
    while True:
        i, j, pivot = start, end, deepcopy(arr[start])
        while i < j:
            # 从右向左查找较小元素
            while i < j and key(pivot) <= key(arr[j]):
                j -= 1
            if i == j: break
            arr[i] = arr[j]
            i += 1
            # 从左向右查找较大元素
            while i < j and key(arr[i]) <= key(pivot):
                i += 1
            if i == j: break
            arr[j] = arr[i]
            j -= 1
        arr[i] = pivot

        if i == k:
            return
        elif i < k:
            start = i + 1
        else:
            end = i - 1


def max_heapreplace(heap, new_node, key=lambda x: x[1]):
    """
    大根堆替换堆顶元素

    :param heap: 大根堆/列表
    :param new_node: 新节点
    :return: None
    """
    heap[0] = new_node
    root, child = 0, 1
    end = len(heap) - 1
    while child <= end:
        if child < end and key(heap[child]) < key(heap[child + 1]):
            child += 1
        if key(heap[child]) <= key(new_node):
            break
        heap[root] = heap[child]
        root, child = child, 2 * child + 1
    heap[root] = new_node


def max_heappush(heap, new_node, key=lambda x: x[1]):
    """
    大根堆插入元素

    :param heap: 大根堆/列表
    :param new_node: 新节点
    :return: None
    """
    heap.append(new_node)
    pos = len(heap) - 1
    while 0 < pos:
        parent_pos = pos - 1 >> 1
        if key(new_node) <= key(heap[parent_pos]):
            break
        heap[pos] = heap[parent_pos]
        pos = parent_pos
    heap[pos] = new_node


class KDNode(object):
    """kd树节点"""

    def __init__(self, data=None, label=None, left=None, right=None, axis=None, parent=None):
        """
        构造函数

        :param data: 数据
        :param label: 数据标签
        :param left: 左孩子节点
        :param right: 右孩子节点
        :param axis: 分割轴
        :param parent: 父节点
        """
        self.data = data
        self.label = label
        self.left = left
        self.right = right
        self.axis = axis
        self.parent = parent


class KDTree(object):
    """kd树"""

    def __init__(self, X, y=None):
        """
        构造函数

        :param X: 输入特征集, n_samples*n_features
        :param y: 输入标签集, 1*n_samples
        """
        self.root = None
        self.y_valid = False if y is None else True
        self.create(X, y)

    def create(self, X, y=None):
        """
        构建kd树

        :param X: 输入特征集, n_samples*n_features
        :param y: 输入标签集, 1*n_samples
        :return: KDNode
        """

        def create_(X, axis, parent=None):
            """
            递归生成kd树

            :param X: 合并标签后输入集
            :param axis: 切分轴
            :param parent: 父节点
            :return: KDNode
            """
            n_samples = np.shape(X)[0]
            if n_samples == 0:
                return None
            mid = n_samples >> 1
            partition_sort(X, mid, key=lambda x: x[axis])

            if self.y_valid:
                kd_node = KDNode(X[mid][:-1], X[mid][-1], axis=axis, parent=parent)
            else:
                kd_node = KDNode(X[mid], axis=axis, parent=parent)

            next_axis = (axis + 1) % k_dimensions
            kd_node.left = create_(X[:mid], next_axis, kd_node)
            kd_node.right = create_(X[mid + 1:], next_axis, kd_node)
            return kd_node

        print('building kd-tree...')
        k_dimensions = np.shape(X)[1]
        if y is not None:
            X = np.hstack((np.array(X), np.array([y]).T)).tolist()
        self.root = create_(X, 0)

    def search_knn(self, point, k, dist=None):
        """
        kd树中搜索k个最近邻样本

        :param point: 样本点
        :param k: 近邻数
        :param dist: 度量方式
        :return:
        """

        def search_knn_(kd_node):
            """
            搜索k近邻节点

            :param kd_node: KDNode
            :return: None
            """
            if kd_node is None:
                return
            data = kd_node.data
            distance = p_dist(data)
            if len(heap) < k:
                # 向大根堆中插入新元素
                max_heappush(heap, (kd_node, distance))
            elif distance < heap[0][1]:
                # 替换大根堆堆顶元素
                max_heapreplace(heap, (kd_node, distance))

            axis = kd_node.axis
            if abs(point[axis] - data[axis]) < heap[0][1] or len(heap) < k:
                # 当前最小超球体与分割超平面相交或堆中元素少于k个
                search_knn_(kd_node.left)
                search_knn_(kd_node.right)
            elif point[axis] < data[axis]:
                search_knn_(kd_node.left)
            else:
                search_knn_(kd_node.right)

        if self.root is None:
            raise Exception('kd-tree must be not null.')
        if k < 1:
            raise ValueError("k must be greater than 0.")

        # 默认使用2范数度量距离
        if dist is None:
            p_dist = lambda x: norm(np.array(x) - np.array(point))
        else:
            p_dist = lambda x: dist(x, point)

        heap = []
        search_knn_(self.root)
        return sorted(heap, key=lambda x: x[1])

    def search_nn(self, point, dist=None):
        """
        搜索point在样本集中的最近邻

        :param point:
        :param dist:
        :return:
        """
        return self.search_knn(point, 1, dist)[0]

    def pre_order(self, root=KDNode()):
        """先序遍历"""
        if root is None:
            return
        elif root.data is None:
            root = self.root

        yield root
        for x in self.pre_order(root.left):
            yield x
        for x in self.pre_order(root.right):
            yield x

    def lev_order(self, root=KDNode(), queue=None):
        """层次遍历"""
        if root is None:
            return
        elif root.data is None:
            root = self.root

        if queue is None:
            queue = []

        yield root
        if root.left:
            queue.append(root.left)
        if root.right:
            queue.append(root.right)
        if queue:
            for x in self.lev_order(queue.pop(0), queue):
                yield x

    @classmethod
    def height(cls, root):
        """kd-tree深度"""
        if root is None:
            return 0
        else:
            return max(cls.height(root.left), cls.height(root.right)) + 1


class KNeighborsClassifier(object):
    """K近邻分类器"""

    def __init__(self, k, dist=None):
        """构造函数"""
        self.k = k
        self.dist = dist
        self.kd_tree = None

    def fit(self, X, y):
        """建立kd树"""
        print('fitting...')
        X = self._data_processing(X)
        self.kd_tree = KDTree(X, y)

    def predict(self, X):
        """预测类别"""
        if self.kd_tree is None:
            raise TypeError('Classifier must be fitted before predict!')
        search_knn = lambda x: self.kd_tree.search_knn(point=x, k=self.k, dist=self.dist)
        y_ptd = []
        X = (X - self.x_min) / (self.x_max - self.x_min)
        for x in X:
            # reference to https://www.kite.com/python/docs/collections.Counter.most_common
            y = Counter(r[0].label for r in search_knn(x)).most_common(1)[0][0]
            y_ptd.append(y)
        return y_ptd

    def score(self, X, y):
        """预测正确率"""
        y_ptd = self.predict(X)
        correct_nums = len(np.where(np.array(y_ptd) == np.array(y))[0])
        return correct_nums / len(y)

    def _data_processing(self, X):
        """数据归一化"""
        X = np.array(X)
        self.x_min = np.min(X, axis=0)
        self.x_max = np.max(X, axis=0)
        X = (X - self.x_min) / (self.x_max - self.x_min)
        return X


if __name__ == '__main__':
    """测试程序正确性
    使用kd-tree和计算全部距离, 比对两种结果是否一致"""
    N = 100000
    X = [[np.random.random() * 100 for _ in range(3)] for _ in range(N)]
    kd_tree = KDTree(X)

    for x in X[:10]:
        res1 = ([list(node[0].data) for node in kd_tree.search_knn(x, 20)])
        distances = norm(np.array(X) - np.array(x), axis=1)
        res2 = ([list(X[i]) for _, i in sorted(zip(distances, range(N)))[:20]])
        if all(x in res2 for x in res1):
            print('correct ^_^ ^_^')
        else:
            print('error >_< >_<')
    print('\n')

    """10万个样本集中查找10个实例的最近邻"""
    n = 10
    indices = random.sample(range(N), n)
    # 1、kd-tree搜索, 0.19251227378845215s
    tm = time()
    for i, index in enumerate(indices):
        kd_tree.search_nn(X[index])
    print('kd-tree search: {}s'.format(time() - tm))

    # 2、numpy计算全部样本与新实例的距离, 0.5163719654083252s
    tm = time()
    for i, index in enumerate(indices):
        min(norm(X - np.array(X[index]), axis=0))
    print('numpy search: {}s'.format(time() - tm))

    # 3、python循环计算距离, 7.144993782043457s
    tm = time()
    for i, index in enumerate(indices):
        min([norm(np.array(X[index]) - np.array(x)) for x in X])
    print('python search: {}s'.format(time() - tm))
    print('\n\n')

'''
if __name__ == '__main__':
    """模型测试"""
    X, y = [], []
    with open(r"C:\Users\MERLIN\Desktop\knn_dataset.txt") as f:
        for line in f:
            tmp = line.strip().split('\t')
            X.append(tmp[:-1])
            y.append(tmp[-1])
    X = np.array(X, dtype=np.float64)
    y = np.array(y, dtype=np.float64)

    """训练误差"""
    knc = KNeighborsClassifier(10)
    knc.fit(X, y)
    print(knc.score(X, y))  # 0.963
    print('\n')

    """测试误差"""
    X_train, X_test = X[:980], X[-20:]
    y_train, y_test = y[:980], y[-20:]
    knc = KNeighborsClassifier(10)
    knc.fit(X_train, y_train)
    print(knc.score(X_test, y_test))  # 1.0
'''
