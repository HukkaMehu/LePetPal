import torch
import sys

print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"CPU count: {torch.get_num_threads()}")
print(f"MKL available: {torch.backends.mkl.is_available()}")
print(f"OpenMP available: {torch.backends.openmp.is_available()}")

# Test inference speed
import time
import numpy as np

print("\nTesting inference speed...")
x = torch.randn(1, 3, 256, 256)
model = torch.nn.Conv2d(3, 64, 3, padding=1)

# Warmup
for _ in range(3):
    with torch.no_grad():
        _ = model(x)

# Time it
times = []
for _ in range(10):
    t0 = time.time()
    with torch.no_grad():
        _ = model(x)
    times.append(time.time() - t0)

avg_time = np.mean(times) * 1000
print(f"Average inference time: {avg_time:.2f}ms")
print(f"Expected: <10ms for good CPU performance")

if avg_time > 50:
    print("\n⚠️  WARNING: Very slow! Possible issues:")
    print("  - CPU throttling / power saving mode")
    print("  - Background processes using CPU")
    print("  - PyTorch not using optimized libraries (MKL/OpenMP)")
