import sys
import platform
import torch
import torch_directml

print("=" * 60)
print("SYSTEM ARCHITECTURE")
print("=" * 60)
print(f"Platform: {platform.platform()}")
print(f"Machine: {platform.machine()}")
print(f"Processor: {platform.processor()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

print("\n" + "=" * 60)
print("PYTORCH CONFIGURATION")
print("=" * 60)
print(f"PyTorch version: {torch.__version__}")
print(f"PyTorch compiled for: {torch.__config__.show()}")

print("\n" + "=" * 60)
print("DIRECTML GPU ACCELERATION")
print("=" * 60)
try:
    print(f"torch-directml version: {torch_directml.__version__}")
except AttributeError:
    print(f"torch-directml installed (version info not available)")

# Check if DirectML device is available
try:
    dml_device = torch_directml.device()
    print(f"✅ DirectML device available: {dml_device}")
    
    # Test GPU tensor creation
    x = torch.randn(100, 100).to(dml_device)
    print(f"✅ Successfully created tensor on DirectML device")
    
    # Test simple operation
    y = x @ x.T
    print(f"✅ Successfully performed matrix multiplication on GPU")
    
    # Benchmark
    import time
    
    # CPU benchmark
    x_cpu = torch.randn(1000, 1000)
    t0 = time.time()
    for _ in range(10):
        _ = x_cpu @ x_cpu.T
    cpu_time = (time.time() - t0) / 10
    
    # GPU benchmark
    x_gpu = torch.randn(1000, 1000).to(dml_device)
    t0 = time.time()
    for _ in range(10):
        _ = x_gpu @ x_gpu.T
    gpu_time = (time.time() - t0) / 10
    
    print(f"\n📊 Performance Comparison (1000x1000 matrix multiply):")
    print(f"   CPU: {cpu_time*1000:.2f}ms")
    print(f"   GPU (DirectML): {gpu_time*1000:.2f}ms")
    print(f"   Speedup: {cpu_time/gpu_time:.2f}x")
    
except Exception as e:
    print(f"❌ DirectML device error: {e}")

print("\n" + "=" * 60)
print("ARCHITECTURE VERIFICATION")
print("=" * 60)

# Check if running native ARM64 or emulated x86
import struct
is_64bit = struct.calcsize("P") * 8 == 64
arch = platform.machine().lower()

if 'arm' in arch or 'aarch64' in arch:
    print(f"✅ Running native ARM64 architecture")
elif arch in ['amd64', 'x86_64', 'x86']:
    print(f"⚠️  Running x86/x64 architecture (likely emulated on ARM via Prism)")
    print(f"   This will be slower. Consider using native ARM64 Python if available.")
else:
    print(f"❓ Unknown architecture: {arch}")

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)
print("For best performance on Snapdragon:")
print("1. ✅ Use DirectML device for GPU acceleration")
print("2. Set DEVICE=privateuseone:0 in .env (DirectML device)")
print("3. Ensure Python is ARM64 native (not x86 emulated)")
