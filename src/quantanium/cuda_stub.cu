#include <cuda_runtime.h>
#include <cuComplex.h>
#include "quantanium/impl/gates/device_utils.cuh"

extern "C" __global__ void __qt_cuda_stub() {}

/// Force host reference to device code so that nvlink keeps fatbinData
void __qt_force_link_gpu_symbols() {
    /// any call is enough; it will be removed by the optimizer
    if (false) {
        quantanium::square_cplx_d(nullptr, 0, nullptr);
        quantanium::scale_cplx_d(nullptr, 0.0, 0, nullptr);
        quantanium::square_cplx_f(nullptr, 0, nullptr);
        quantanium::scale_cplx_f(nullptr, 0.0f, 0, nullptr);
    }
}

