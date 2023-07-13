# class Solution1:
#     def numberOfSteps(self, num: int) -> int:
#         cnt = 0
#         while num > 0:
#             num = num - 1 if num & 1 else num >> 1
#             print(num)
#             cnt += 1
#         return cnt

# sol = Solution1()
# print(f'Total: {sol.numberOfSteps(14)}')

# class Solution2:
#     def test(self, l: dict) -> int:
#         return l.get('3')

# sol = Solution2()
# print(sol.test({'0': 0 , '1': 1 , '2': 2}))

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __str__(self):
        return self.val

    __repr__ = __str__
        
class Solution3:
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = fast = head
        cnt = 0
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            cnt += 1
        return slow

# sol = Solution3()
# x1 = ListNode(1)
# x2 = ListNode(2)
# x3 = ListNode(3)
# x4 = ListNode(4)
# x5 = ListNode(5)
# x6 = ListNode(6)

# x1.next = x2
# x2.next = x3
# x3.next = x4
# x4.next = x5
# x5.next = x6

# print(x1.next.next.next.next.next.next)

# print(sol.middleNode([x1 , x2 , x3 , x4 , x5 , x6]))