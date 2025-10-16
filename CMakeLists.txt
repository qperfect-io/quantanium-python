#
# Copyright © 2022-2024 University of Strasbourg. All Rights Reserved.
# Copyright © 2032-2024 QPerfect. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

cmake_minimum_required(VERSION 3.15...3.28)

# ---------------------------------------------------------------------------
# Start QuantaniumPy project
# ---------------------------------------------------------------------------
set(QUANTANIUMPY_VERSION 1.12.0)
option(QUANTANIUMPY_WITH_CUDA "Build Python wrapper with CUDA support" ON)

# Optional: let users override CUDA arch list from the command line
set(QUANTANIUMPY_CUDA_ARCHS "75;80;86;89" CACHE STRING "CUDA architectures")

# Disable optimization - important for CUDA for avoiding fatbinData errors"
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION FALSE CACHE BOOL "" FORCE)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-lto")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -fno-lto")

# Pick project languages based on the toggle - include CUDA, if selected
if(QUANTANIUMPY_WITH_CUDA)
  project(QuantaniumPy VERSION ${QUANTANIUMPY_VERSION} LANGUAGES CXX CUDA)
  # Default arch list - user can override via -D
  set(CMAKE_CUDA_ARCHITECTURES "${QUANTANIUMPY_CUDA_ARCHS}" CACHE STRING "" FORCE)
else()
  project(QuantaniumPy VERSION ${QUANTANIUMPY_VERSION} LANGUAGES CXX)
endif()


set(LOGO [=[
░Q░U░A░N░T░A░N░I░U░M░  .-=-.
░█░█░█░█░█░█░█░█░█░█░ /(o o)\ 
░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░ ^^ ^^ ^^
]=])
message("${LOGO}")
message(STATUS "Build ${PROJECT_NAME} v${QUANTANIUMPY_VERSION} (CUDA=${QUANTANIUMPY_WITH_CUDA})")

# ---------------------------------------------------------------------------
# Set default build to release
# ---------------------------------------------------------------------------
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose Release or Debug" FORCE)
endif()

# ---------------------------------------------------------------------------
# Prohibit in-source builds.
# ---------------------------------------------------------------------------
if(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
  message(FATAL_ERROR "In-source builds are not allowed. Please use a separate build directory.")
endif()

# ---------------------------------------------------------------------------
# Extenral dependencies
# ---------------------------------------------------------------------------
# Make sure the submodule sees the CUDA option (forward it)
set(QUANTANIUM_WITH_CUDA ${QUANTANIUMPY_WITH_CUDA} CACHE BOOL "Enable CUDA in Quantanium core" FORCE)

# option(QUANTANIUM_WITH_CUQUANTUM "Enable cuQuantum in Quantanium core" ON)
add_subdirectory(libs)

# ---------------------------------------------------------------------------
# QuantaniumPy with pybind11
# ---------------------------------------------------------------------------
pybind11_add_module(_core MODULE src/QuantaniumPY.cpp)
# Disable global LTO early and explicitly for this module
set_property(TARGET _core PROPERTY INTERPROCEDURAL_OPTIMIZATION FALSE)

target_compile_options(_core PRIVATE
  $<$<COMPILE_LANGUAGE:CXX>:-fno-lto>
  $<$<COMPILE_LANGUAGE:CUDA>:-Xcompiler=-fno-lto>
)

target_link_options(_core PRIVATE -fno-lto)

# Common links (CPU path)
target_link_libraries(_core
  PRIVATE
    pybind11::headers
    quantanium::quantanium
    quantanium::proto
    Boost::headers
)

# CUDA path (CUDA-enabled Python extension, if selected)
if(QUANTANIUMPY_WITH_CUDA)
  set(CUBLAS_RPATH "\$$ORIGIN/../nvidia/cublas/lib")
  set(CUBLAS_LIB "-Wl,-rpath,'${CUBLAS_RPATH}'")
  enable_language(CUDA)
  find_package(CUDAToolkit REQUIRED)

  message(STATUS "Building QuantaniumPy with CUDA support")
  message(STATUS "Using NVCC at: ${CUDAToolkit_NVCC_EXECUTABLE}")


  set(CMAKE_CUDA_HOST_COMPILER "${CMAKE_CXX_COMPILER}")

  # Force CUDA linker for core_
  set_target_properties(_core PROPERTIES
      LINKER_LANGUAGE CUDA
      CUDA_RESOLVE_DEVICE_SYMBOLS ON
      CUDA_SEPARABLE_COMPILATION ON
      POSITION_INDEPENDENT_CODE ON
  )
  # Force CUDA linker for quantanium_cuda
  set_target_properties(quantanium_cuda PROPERTIES
    CUDA_SEPARABLE_COMPILATION ON
    CUDA_RESOLVE_DEVICE_SYMBOLS ON
  )

  # Add CUDA stub and device object
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/quantanium_cuda_link.o
    COMMAND ${CUDAToolkit_NVCC_EXECUTABLE}
        -dlink
        -Xcompiler=-fPIC
        $<TARGET_OBJECTS:quantanium_cuda>
        -o ${CMAKE_CURRENT_BINARY_DIR}/quantanium_cuda_link.o
        -lcudadevrt -lcudart_static
    DEPENDS quantanium_cuda
    COMMENT "Device linking CUDA objects for _core"
  )
  # Define source - stub and quantanium_cuda - object library with CUDA kernels
  target_sources(_core PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/quantanium_cuda_link.o
    $<TARGET_OBJECTS:quantanium_cuda>
    src/quantanium/cuda_stub.cu
  )

  # Link
  target_link_libraries(_core PRIVATE
    quantanium::quantanium
    quantanium::proto
	  quantanium::quantanium_gpu
    CUDA::cudart
    ${CUBLAS_LIB}
  )
  # Link cuQuantum manually
  if (CUSTATEVEC_LIB)
    message(STATUS "Linking _core explicitly with cuStateVec: ${CUSTATEVEC_LIB}")
    target_link_libraries(_core PRIVATE ${CUSTATEVEC_LIB})
    get_filename_component(CUSTATEVEC_DIR ${CUSTATEVEC_LIB} DIRECTORY)
    set_target_properties(_core PROPERTIES
      BUILD_RPATH "${CUBLAS_RPATH}"
      INSTALL_RPATH "${CUBLAS_RPATH}"
        # BUILD_RPATH "${CUSTATEVEC_DIR}"
        # INSTALL_RPATH "${CUSTATEVEC_DIR}"
    )
  endif()

  target_compile_definitions(_core PRIVATE QUANTANIUM_USE_CUDA=1)

  # Disable LTO safely for _core target - not really needed - just double check
  if(CMAKE_INTERPROCEDURAL_OPTIMIZATION)
    set_property(TARGET _core PROPERTY INTERPROCEDURAL_OPTIMIZATION FALSE)
  endif()
  target_compile_options(_core PRIVATE
    -fno-lto
  )

  # Make sure nvcc passes this correctly to the host compiler
  # set_target_properties(_core PROPERTIES
  #   CUDA_ARCHITECTURES "75;80;86;89"
  #   CUDA_SEPARABLE_COMPILATION ON
  # )

  # NVCC expand link
  set(NVCC_LINK_SCRIPT "${CMAKE_SOURCE_DIR}/nvcc_link_expand.cmake")
  if(NOT EXISTS "${NVCC_LINK_SCRIPT}")
    message(FATAL_ERROR "NVCC helper script not found at: ${NVCC_LINK_SCRIPT}")
  endif()
  set_target_properties(_core PROPERTIES
    LINK_FLAGS_RELEASE ""
    LINK_FLAGS_RELWITHDEBINFO ""
    LINK_FLAGS_MINSIZEREL ""
  )
  set(CMAKE_STRIP "")
  set(CMAKE_SKIP_RPATH FALSE)

  add_custom_command(
      TARGET _core
      POST_BUILD
      COMMAND ${CMAKE_COMMAND} -E echo "Preparing NVCC relink..."
      COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/nvcc_vars

      COMMAND ${CMAKE_COMMAND} -E echo "set(CUDA_EXE ${CUDAToolkit_NVCC_EXECUTABLE} CACHE FILEPATH \"\")" > ${CMAKE_CURRENT_BINARY_DIR}/nvcc_vars/vars.cmake
      COMMAND ${CMAKE_COMMAND} -E echo "set(OUTPUT_FILE $<TARGET_FILE:_core> CACHE FILEPATH \"\")" >> ${CMAKE_CURRENT_BINARY_DIR}/nvcc_vars/vars.cmake

      COMMAND ${CMAKE_COMMAND} -E echo "set(CORE_OBJ $<JOIN:$<TARGET_OBJECTS:_core>,;>)" >> ${CMAKE_CURRENT_BINARY_DIR}/nvcc_vars/vars.cmake
      COMMAND ${CMAKE_COMMAND} -E echo "set(CUDA_OBJ $<JOIN:$<TARGET_OBJECTS:quantanium_cuda>,;>)" >> ${CMAKE_CURRENT_BINARY_DIR}/nvcc_vars/vars.cmake

      # Run the NVCC link helper
          COMMAND ${CMAKE_COMMAND} -P ${CMAKE_SOURCE_DIR}/nvcc_link_expand.cmake
      WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
      COMMENT "Re-linking _core with NVCC to register fatbins"
      VERBATIM
      )
else()
  target_compile_definitions(_core PRIVATE QUANTANIUM_USE_CUDA=0)
endif()

target_compile_definitions(_core PRIVATE
  QUANTANIUM_USE_CUDA=$<IF:$<BOOL:${QUANTANIUMPY_WITH_CUDA}>,1,0>
)

target_compile_features(_core PRIVATE cxx_std_17)
set_target_properties(_core PROPERTIES CXX_VISIBILITY_PRESET hidden VISIBILITY_INLINES_HIDDEN ON)

# Install as quantanium/_core.*.so
install(TARGETS _core DESTINATION quantanium)

