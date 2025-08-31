import re

class dorm_info:
    campus: str       # 沙河, 西土城
    bld: str          # "5", "S2"
    floor: int        # 1
    room: str         # "204"
    canonical_id: str # 1-204
    def __init__(self, canonical_id: str):
        # "5-102"  -> ["西土城", "5", 1, "5-102"]
        # "S1-201" -> ["沙河", "S2", 2, "S2-201"]
        bad_id = RuntimeError("Bad Canonical ID")
        if canonical_id.count("-") != 1:
            raise bad_id
        self.canonical_id = canonical_id
        self.bld, self.room = canonical_id.split("-")
        # TODO: check is_number
        if len(self.room) not in (3, 4):
            raise bad_id
        xtc_bld = {"1","2","3","4","5","6","8","9","10","11","13","29"}
        shh_bld = {"A", "B", "C", "D1", "D2", "E", "S2", "S3", "S4", "S5", "S6"}
        if self.bld not in xtc_bld and self.bld not in shh_bld:
            raise bad_id
        self.campus = "西土城" if self.bld in xtc_bld else "沙河"
        
        match_res = re.match(r'\d+', self.room)
        if not match_res:
            raise bad_id
        self.floor = int(match_res.group()[:-2]) # "1" or "11"
    
    def is_new_backend(self) -> bool:
        if self.bld in ("9", "11"):
            return True
        if self.bld == "10" and (125 <= int(self.room) <= 146 or 229 <= int(self.room) <= 252): # TODO: fix this
            return True
        return False
    
class FetchFailure(RuntimeError):
    pass

# class QueryFailure(RuntimeError):
#     pass

def to_cn_number(num: int):
        return {
            1: "一",
            2: "二",
            3: "三",
            4: "四",
            5: "五",
            6: "六",
            7: "七",
            8: "八",
            9: "九",
            10: "十",
            11: "十一",
            12: "十二",
            13: "十三",
            14: "十四",
            15: "十五",
            29: "二十九",
        }[num]
        
        
        