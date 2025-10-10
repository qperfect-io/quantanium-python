{ pkgs ? import <nixpkgs> { config.allowUnfree = true; } }:

let
  cuda = pkgs.cudaPackages_12;
  nvidiaLib = pkgs.linuxPackages.nvidia_x11;

  pythonEnv = pkgs.python311.withPackages (ps: [
    ps.pip
    ps.setuptools
    ps.wheel
  ]);
in
pkgs.mkShell {
  name = "quantanium-gpu";

  buildInputs = [
    pkgs.cmake
    pkgs.gcc12
    pkgs.git
    pkgs.boost
    pkgs.eigen
    pkgs.protobuf
    pkgs.micromamba 
    pythonEnv        
    cuda.cudatoolkit
    cuda.cuda_nvcc
    cuda.cuda_cudart
    nvidiaLib
  ];

  shellHook = ''
    echo "Quantanium GPU dev shell ready"
    echo "CUDA toolkit: ${cuda.cudatoolkit.version}"

    export CUQUANTUM_ROOT=$PWD/.conda-env 
    export CC=${pkgs.gcc12}/bin/gcc
    export CXX=${pkgs.gcc12}/bin/g++
    export CXXFLAGS="-I$PWD/libs/spdlog/include -I$PWD/libs/catch/src $CXXFLAGS"
    export CUDACXX=${cuda.cuda_nvcc}/bin/nvcc
    export CMAKE_CUDA_HOST_COMPILER=$CXX
    export CUDACXX=${cuda.cuda_nvcc}/bin/nvcc
    export CMAKE_CUDA_RUNTIME_LIBRARY=Shared
  

    export LD_LIBRARY_PATH=${nvidiaLib}/lib:$LD_LIBRARY_PATH
  
  
    if [ ! -d .conda-env ]; then
      echo "Creating local cuQuantum env..."
      micromamba create -y -p ./.conda-env -c nvidia -c conda-forge \
        cuquantum custatevec cutensornet 
    fi

    export CUQUANTUM_ROOT=$PWD/.conda-env
    export LD_LIBRARY_PATH=$PWD/.conda-env/lib:${nvidiaLib}/lib:$LD_LIBRARY_PATH
    
    echo "cuQuantum available at $PWD/.conda-env"

    echo "Using Python: $(which python)"
    echo "Python version: $(python --version)"
  '';
}

