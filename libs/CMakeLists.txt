#== CMakeLists.txt ---------------------------------------------------------==#
#
#                             Quantanium by MIMIQ
#
# Copyright (C) 2023-2024 QPerfect. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
#
#==------------------------------------------------------------------------==#

# Python
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)


# Pybind11
if (QUANTANIUM_USE_EXTENAL_PYBIND11)
    find_package(pybind11 CONFIG REQUIRED)
else()
    add_subdirectory(pybind11)
endif()

# QUantanium
if (QUANTANIUM_USE_EXTERNAL_QUANTANIUM)
  find_package(quantanium REQUIRED)
else()
  add_subdirectory(quantanium)
endif()
