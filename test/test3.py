class Solution:
    def numberOfSteps(self, num: int) -> int:
        cnt = 0
        while num > 0:
            if num & int(0) == 0:
                num /= int(2)
            else:
                num -= int(1)
            cnt += 1
        return cnt

test = Solution()
test.numberOfSteps(14)