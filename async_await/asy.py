import time
import asyncio
async def brewCoffee():
    print("start coffee")
    await asyncio.sleep(10)
    print("end coffee")
    return "coffee ready"

async def toastBread():
    print("start bread")
    await asyncio.sleep(3)
    print("end bread")
    return "bread ready"
async def main():
    st=time.time()
    # batch  = asyncio.gather(brewCoffee(),toastBread())
    # c,b= await batch
    c= asyncio.create_task(brewCoffee())
    b= asyncio.create_task(toastBread())
    await asyncio.sleep(1)
    print("lets see")
    e=await b
    print("thereee")
    d=await c
    print("hereee")
    et=time.time()
    elt=et-st
    print(f"res cofee{d}")
    print(f"res brad{e}")
    print(f"total time {elt:2f}")
asyncio.run(main())


# import requests
# for i in range (5):
#     r = requests.get(f'http://127.0.0.1:8000/js')
#     print(r.json())
