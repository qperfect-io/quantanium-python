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

# Pick project languages based on the toggle
if(QUANTANIUMPY_WITH_CUDA)
  project(QuantaniumPy VERSION ${QUANTANIUMPY_VERSION} LANGUAGES CXX CUDA)
  # Default arch list (user can override via -D)
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

# Common links (CPU path)
target_link_libraries(_core
  PRIVATE
    pybind11::headers
    quantanium::quantanium
    quantanium::proto
)

# CUDA path (link extra bits only when enabled)
if(QUANTANIUMPY_WITH_CUDA)
  find_package(CUDAToolkit REQUIRED)
  set_target_properties(_core PROPERTIES CUDA_SEPARABLE_COMPILATION ON)
  target_link_libraries(_core
    PRIVATE
      quantanium::quantanium_gpu
      CUDA::cudart
  )
endif()


target_compile_definitions(_core PRIVATE
  QUANTANIUM_USE_CUDA=$<IF:$<BOOL:${QUANTANIUMPY_WITH_CUDA}>,1,0>
)

target_compile_features(_core PRIVATE cxx_std_17)
set_target_properties(_core PROPERTIES CXX_VISIBILITY_PRESET hidden VISIBILITY_INLINES_HIDDEN ON)

# Install as quantanium/_core.*.so
install(TARGETS _core DESTINATION quantanium)

