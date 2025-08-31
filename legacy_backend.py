import requests
from datetime import datetime
from util import dorm_info, to_cn_number, FetchFailure

class legacy_backend:
    cookies: dict
    num_map: dict
    def __init__(self, cookies: dict):
        self.cookies = cookies
    
    def query(self, dorm: dorm_info) -> tuple[float, datetime]:
        assert not dorm.is_new_backend()
        # fetch_failure = RuntimeError("Fetch Failure")
        if dorm.campus == "沙河":
            p = "南" if dorm.bld.startswith("S") else "北"
            partment_id = f"沙河校区雁{p}园{dorm.bld}楼"
            floor_id = f"{dorm.floor}层"
            area_id = "2"
            # fetch dorm_id
            res = requests.post(
                "https://app.bupt.edu.cn/buptdf/wap/default/drom",
                data={
                    "partmentId": partment_id,
                    "floorId": floor_id,
                    "areaid": area_id
                },
                cookies=self.cookies,
                headers={
                    'Referer': "https://app.bupt.edu.cn/buptdf/wap/default/chong",
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            
            r = res.json()
            # {
            #     'e': 0, 
            #     'm': '操作成功',
            #     'd': {
            #         'data': [
            #             {'dromName': 'A楼201', 'dromNum': '190807009124'}, 
            #             {'dromName': 'A楼202', 'dromNum': '190807009137'},
            #             ...
            #         ]
            #     }
            # }
            if r["e"] != 0:
                raise FetchFailure(r["m"])
            dorm_ids: list[dict[str, str]] = r["d"]["data"]
            dorm_id = next(o["dormNum"] for o in dorm_ids if dorm.room in o["dormName"])
        else:
            part_name = f"学{to_cn_number(int(dorm.bld))}楼"
            floor_id = f"{dorm.floor}层"
            area_id = "1"
            dorm_id = dorm.canonical_id
            
            # fetch partment id
            res = requests.post(
                "https://app.bupt.edu.cn/buptdf/wap/default/part",
                data={
                    "areaid": area_id
                },
                cookies=self.cookies,
                headers={
                    'Referer': "https://app.bupt.edu.cn/buptdf/wap/default/chong",
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            
            r = res.json()
            # {
            #     "e": 0,
            #     "m": "操作成功",
            #     "d": {
            #         "data": [
            #         {
            #             "partmentId": "c526d2367cd24fcdac2538975d1bec75",
            #             "partmentName": "学四楼",
            #             "prartmentFloor": "12",
            #             "prartmentWeixiu": "董玉芳",
            #             "prartmentWxphone": "62284810"
            #         },
            #         # ...
            #         ]
            #     }
            # }
            if r["e"] != 0:
                raise FetchFailure(r["m"])
            part_ids: list[dict[str, str]] = r["d"]["data"]
            part_id = next(o["partmentId"] for o in part_ids if o["partmentName"] == part_name)
            
        # fetch balance
        
        res = requests.post(
            "https://app.bupt.edu.cn/buptdf/wap/default/search",
            data={
                "partmentId": part_id,
                "floorId": floor_id,
                "dromNumber": dorm_id,
                "areaid": area_id,
            },
            cookies=self.cookies,
            headers={
                'Referer': "https://app.bupt.edu.cn/buptdf/wap/default/chong",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        
        r = res.json()
        if r["e"] != 0:
            raise FetchFailure(r["m"])
        data = r["d"]["data"]
        kwh = data["surplus"] + data["freeEnd"]  # 剩余电量 + 剩余赠送电量
        ts = datetime.fromisoformat(data["time"])
        return kwh, ts
    
if __name__ == "__main__":
    from secret import legacy_backend_cookies as cookies
    b = legacy_backend(cookies)
    d = dorm_info("6-120")
    q = b.query(d)
    print(q)