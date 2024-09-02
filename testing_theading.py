import threading
import time

from scripts.globals import GREEN

RED: str = '\033[91m'
GREEN: str = '\033[92m'
BLUE: str = '\033[94m'
CYAN: str = '\033[96m'
WHITE: str = '\033[97m'
YELLOW: str = '\033[93m'
MAGENTA: str = '\033[95m'
GREY: str = '\033[90m'
BLACK: str = '\033[90m'
DEFAULT: str = '\033[0m'
FATAL = "\033[41m"

def color_print(msg, color):
    print(color + msg + DEFAULT)

def calc_square(numbers):
    for n in numbers:
        color_print(f'{n} ^ 2 = {n*n}', RED)
        time.sleep(0.1)

def calc_cube(numbers):
    for n in numbers:
        color_print(f'{n} ^ 3 = {n*n*n}', GREEN)
        time.sleep(0.1) # this can be Popen() then pull and see if its done

numbers = [2, 3, 5, 8]
start = time.perf_counter()
square_thread = threading.Thread(target=calc_square, args=(numbers,))
cube_thread = threading.Thread(target=calc_cube, args=(numbers,))
square_thread.start()
cube_thread.start()
square_thread.join()
cube_thread.join()
end = time.perf_counter()
elapsed_time = end - start
print(f"|--------------- Time elapsed: {elapsed_time:.2f} seconds ---------------|")

start = time.perf_counter()
calc_square(numbers)
calc_cube(numbers)
end = time.perf_counter()
elapsed_time = end - start
print(f"|--------------- Time elapsed: {elapsed_time:.2f} seconds ---------------|")