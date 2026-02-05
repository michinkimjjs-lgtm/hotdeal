import re

samples = [
    "[네이버]구글플레이 기프트카드 1만원(네이버멤버십8,730원/무료)",
    "[11번가] 티코 말차 510ml, 3개 (15,960원/무료)",
    "[소프라노] 드래곤퀘스트7 리이매진드 스위치2버전 (69,800원/2,500)",
    "[알리] 코인딜 고속 충전 케이블 0.5~3m (1074~ 1815원)",
    "그냥 제목입니다. (가격없음)",
    "[G마켓] 상품명 (12,345원)"
]

# Current regex assumption (simplified)
regex_current = r'\((\d{1,3}(?:,\d{3})*)원\)'
regex_improved = r'\(.*?(\d{1,3}(?:,\d{3})*).*?(?:원|/|무료).*?\)'

print("--- Testing Regex ---")

# Improved Regex to capture the first price-like number in parens
# Looks for open paren, optional text, digits with commas, optional text, then '원' OR '/' OR '무료' inside parens
pattern = re.compile(r'\((?:.*?)(\d{1,3}(?:,\d{3})*)(?:.*?)(?:원|/|무료)(?:.*?)\)')

for s in samples:
    match = pattern.search(s)
    if match:
        print(f"Match: '{s}' -> {match.group(1)}")
    else:
        print(f"No match: '{s}'")
