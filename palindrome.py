def is_palindrome(s: str):
        return s == s[::-1]
def longestPalindrome(s: str) -> str:
        pal = []
        first = 0
        last = len(s) - 1
        if is_palindrome(s):
            return s
        
        index = 0
        while index < last:
            if s[first + index] == s[last]:
                if is_palindrome(s[first + index:]):
                    pal.append(s[first + index:])
            print("first")
            index += 1
    
        index = 0
        while index < last:
            if s[first] == s[last - index]:
                if is_palindrome(s[first:last - index]):
                    pal.append(s[first:(last-index) + 1])
            index += 1
            print("second")
        index = 0
        while index <= len(s) // 2:
            if s[first + index] == s[last - index]:
                if is_palindrome(s[first+index:(last-index)+1]):
                    pal.append(s[first+index:(last-index) + 1])
                    break            
            index += 1

        result = list(sorted(pal ,key=lambda m: len(m), reverse=True))
        return result

print(longestPalindrome("babad"))