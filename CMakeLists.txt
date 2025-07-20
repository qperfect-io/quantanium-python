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

# ---------------------------------------------------------------------------------------
# Start QuantaniumPy project
# ---------------------------------------------------------------------------------------

set(QUANTANIUM_VERSION 1.0.0)

project(QuantaniumPy VERSION ${QUANTANIUMPY_VERSION} LANGUAGES CXX)

set(LOGO [=[
░Q░U░A░N░T░A░N░I░U░M░  .-=-.
░█░█░█░█░█░█░█░█░█░█░ /(o o)\ 
░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░ ^^ ^^ ^^
]=])
message(${LOGO})
message(STATUS "Build ${PROJECT_NAME}: ${QUANTANIUMPY_VERSION}")

# ---------------------------------------------------------------------------------------
# Define the package information.
# ---------------------------------------------------------------------------------------
set(PACKAGE_DESCRIPTION
    "Python wrapper for the MIMIQ Quantanium statevector engine."
)
set(PACKAGE_AUTHOR "QPerfect")

# ---------------------------------------------------------------------------------------
# Set default build to release
# ---------------------------------------------------------------------------------------
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose Release or Debug" FORCE)
endif()

# ---------------------------------------------------------------------------------------
# Prohibit in-source builds.
# ---------------------------------------------------------------------------------------
if(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
  message(FATAL_ERROR "In-source builds are not allowed."
                      "Please make a separate build directory.")
endif()

# ---------------------------------------------------------------------------------------
# Set QUANTANIUMPY_MASTER_PROJECT to ON if we are building Quatanium
# ---------------------------------------------------------------------------------------
# Check if Quantanium is being used directly or via add_subdirectory, but allow overriding
if(NOT DEFINED QUANTANIUMPY_MASTER_PROJECT)
    if(CMAKE_CURRENT_SOURCE_DIR STREQUAL CMAKE_SOURCE_DIR)
        set(QUANTANIUMPY_MASTER_PROJECT ON)
    else()
        set(QUANTANIUMPY_MASTER_PROJECT OFF)
    endif()
endif()

# ---------------------------------------------------------------------------------------
# Extenral dependencies
# ---------------------------------------------------------------------------------------
add_subdirectory(libs)

# ---------------------------------------------------------------------------------------
# QuantaniumPy with pybind11
# ---------------------------------------------------------------------------------------
pybind11_add_module(_core MODULE src/QuantaniumPY.cpp)
target_link_libraries(_core
    PRIVATE
    pybind11::headers
    quantanium::quantanium
    quantanium::proto
)

install(TARGETS _core DESTINATION quantanium)
