import heapq

def max_n(l, n):
    """
    Given a list of numbers a, and an integer b, return the b highest numbers in a.
    Example: max_n([1,2,3], 2)=[2,3]
    """
    heapq.heapify(l)
    return heapq.nlargest(n, l)

def min_n(l, n):
    heapq.heapify(l)
    return heapq.nsmallest(n, l)

if __name__ == '__main__':
    print(max_n([1, 2, 3], 4))
    print(min_n([10, 4, 3000], 2))