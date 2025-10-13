cmake_minimum_required(VERSION 3.16)

# Read variables from vars.cmake 
set(VARS_FILE "${CMAKE_CURRENT_BINARY_DIR}/nvcc_vars/vars.cmake")
if(EXISTS "${VARS_FILE}")
  include("${VARS_FILE}")
else()
  message(FATAL_ERROR "vars.cmake not found at: ${VARS_FILE}")
endif()

# Verify NVCC path 
if(NOT CUDA_EXE OR NOT EXISTS "${CUDA_EXE}")
  message(FATAL_ERROR "NVCC not found or CUDA_EXE not defined: ${CUDA_EXE}")
endif()

# Converting : CORE_OBJ and CUDA_OBJ may contain either “;” or spaces
string(REPLACE "\"" "" CORE_OBJ "${CORE_OBJ}")
string(REPLACE "\"" "" CUDA_OBJ "${CUDA_OBJ}")

# Split on spaces in case the list was collapsed
separate_arguments(CORE_OBJ)
separate_arguments(CUDA_OBJ)

message(STATUS "Re-linking _core with NVCC:")
foreach(f ${CORE_OBJ})
  message(STATUS "     CORE_OBJ += ${f}")
endforeach()
foreach(f ${CUDA_OBJ})
  message(STATUS "     CUDA_OBJ += ${f}")
endforeach()
message(STATUS "   OUT: ${OUTPUT_FILE}")

# Device linking 
set(_cmd_dlink ${CUDA_EXE}
    -dlink
    -Xcompiler=-fPIC
    ${LINK_LIBS}
    -o ${CMAKE_CURRENT_BINARY_DIR}/quantanium_dlink.o
)
list(APPEND _cmd_dlink ${CUDA_OBJ})
list(APPEND _cmd_dlink -lcudadevrt -lcudart_static)

execute_process(
  COMMAND ${_cmd_dlink}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  RESULT_VARIABLE _res_dlink
)
if(NOT _res_dlink EQUAL 0)
  message(FATAL_ERROR "Device linking failed with code ${_res_dlink}")
endif()


# Device registration only - here we just produce an object that registers the fatbin, not a new .so
set(_cmd_link ${CUDA_EXE}
    -dlink
    -Xcompiler=-fPIC
    -o ${CMAKE_CURRENT_BINARY_DIR}/quantanium_cuda_link.o
)
list(APPEND _cmd_link ${CUDA_OBJ})
list(APPEND _cmd_link ${CMAKE_CURRENT_BINARY_DIR}/quantanium_dlink.o)
list(APPEND _cmd_link -lcudadevrt -lcudart_static)

# Make the object available for CMake to link into _core
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/nvcc_vars/link_output.txt"
     "${CMAKE_CURRENT_BINARY_DIR}/quantanium_cuda_link.o")
message(STATUS "NVCC device link complete (fatbin registered)")

execute_process(
  COMMAND ${_cmd_link}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  RESULT_VARIABLE _res_link
)

if(NOT _res_link EQUAL 0)
  message(FATAL_ERROR "NVCC link failed with code ${_res_link}")
endif()

message(STATUS " NVCC relink completed successfully")


