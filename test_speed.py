import time
import random

def calc_mac_old(filter_matrix, pattern_matrix):
    total_score = 0.0
    rows = len(filter_matrix)
    for i in range(rows):
        cols = len(filter_matrix[i])
        for j in range(cols):
            total_score += filter_matrix[i][j] * pattern_matrix[i][j]
    return total_score

def calc_mac_new(filter_matrix, pattern_matrix):
    flat_filter = [i for r in filter_matrix for i in r]
    flat_pattern = [i for r in pattern_matrix for i in r]
    return sum(f * p for f, p in zip(flat_filter, flat_pattern))

def calc_mac_zip_only(filter_matrix, pattern_matrix):
    return sum(f * p for r1, r2 in zip(filter_matrix, pattern_matrix) for f, p in zip(r1, r2))

size = 25
dummy_matrix = [[random.random() for _ in range(size)] for _ in range(size)]

n = 1000

t0 = time.perf_counter()
for _ in range(n):
    calc_mac_old(dummy_matrix, dummy_matrix)
t1 = time.perf_counter()
print(f"Old (2x FOR): {(t1-t0)*1000:.2f} ms")

t0 = time.perf_counter()
for _ in range(n):
    calc_mac_new(dummy_matrix, dummy_matrix)
t1 = time.perf_counter()
print(f"New (Flatten + zip): {(t1-t0)*1000:.2f} ms")

t0 = time.perf_counter()
for _ in range(n):
    calc_mac_zip_only(dummy_matrix, dummy_matrix)
t1 = time.perf_counter()
print(f"Zip only (no iter tools): {(t1-t0)*1000:.2f} ms")
