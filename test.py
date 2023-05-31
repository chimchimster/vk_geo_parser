# import os
# import asyncio
# import requests
# import argparse
# from dotenv import load_dotenv
#
# load_dotenv()
# x = os.environ.get('VK_TOKEN')
# print(x)
#
#
#
# parser = argparse.ArgumentParser(description='Hello, World!')
# parser.add_argument('-p', '--print_args', help='Prints arguments ma fa ka', default='Simple string', nargs='*')
# args = parser.parse_args()
# print(args.print_args)
#
# async def get_resp(url):
#     return requests.get(url).text
#
#
# async def main():
#     task = asyncio.create_task(get_resp('https://google.com'))
#     done, pending = await asyncio.wait({task})
#
#     if task in done:
#         print('WORK IS DONE!')
#
# asyncio.run(main())
#
# print(os.environ['HOME'])
# from datetime import datetime
# print(datetime.now())
# print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
# print(datetime(1970, 1, 1))
import time

# x = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
# print('-'.join([_ for _ in x]))

x = time.time()
print(x)

print(x - 84000)

print(len({805320192, 783009799, -142793720, 672861577, 567331346, -171967853, -200954860, 805393173, -40609134, 248959511, 647443477, 477492894, -36881376, 783999138, 793556515, 740870436, 692282154, 788364593, 768572595, -204620748, 743290806, 235471542, 165163832, 449851832, -220801473, -194299709, 297032444, 805487557, 646764228, 412231623, 649411272, 156265285, 274473802, 759760333, 562737102, 341861711, 805421518, -211055411, 805327826, -105703085, 352019924, 478574804, 805096914, 659856344, 251727321, 674030814, 805416928, 805455073, -197124896, 278486883, 801687141, 280624488, 805491305, -190301462, 370868591, 805491440, 786262643, 805337076, 354606457, 614080122, 593818876, 802133501, 206178174}))