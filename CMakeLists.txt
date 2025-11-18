# POTK - Polynomial Optics to Karma
# CMake build configuration

cmake_minimum_required(VERSION 3.12)
project(POTK VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)  # C++17 for structured bindings
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# =============================================================================
# Options
# =============================================================================

option(BUILD_PYTHON_BINDINGS "Build Python bindings with pybind11" ON)
option(BUILD_SHARED_LIBS "Build shared libraries" ON)

# =============================================================================
# Find Dependencies
# =============================================================================

# Find Houdini SDK (optional, for HDK integration)
# Uncomment if building HDK plugins
# find_package(Houdini)

# Find Python (for bindings)
if(BUILD_PYTHON_BINDINGS)
    # Prefer Houdini's bundled Python if available
    if(DEFINED ENV{HFS})
        set(Python3_ROOT_DIR "$ENV{HFS}/python")
    endif()

    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    message(STATUS "Found Python: ${Python3_VERSION} at ${Python3_EXECUTABLE}")

    # Find or fetch pybind11
    find_package(pybind11 CONFIG)
    if(NOT pybind11_FOUND)
        message(STATUS "pybind11 not found, fetching from GitHub...")
        include(FetchContent)
        FetchContent_Declare(
            pybind11
            GIT_REPOSITORY https://github.com/pybind/pybind11.git
            GIT_TAG v2.11.1
        )
        FetchContent_MakeAvailable(pybind11)
    endif()
endif()

# =============================================================================
# polynomial-optics Library Setup
# =============================================================================

# Check if polynomial-optics exists
set(POLYNOMIAL_OPTICS_DIR "${CMAKE_SOURCE_DIR}/ext/lentil/polynomial-optics")
if(NOT EXISTS "${POLYNOMIAL_OPTICS_DIR}")
    message(FATAL_ERROR
        "\n"
        "polynomial-optics library not found!\n"
        "\n"
        "Please run the setup script first:\n"
        "  ./setup_potk.sh\n"
        "\n"
        "This will clone the required polynomial-optics library.\n"
    )
endif()

message(STATUS "Found polynomial-optics at: ${POLYNOMIAL_OPTICS_DIR}")

# Set up include directories
set(POLYNOMIAL_OPTICS_INCLUDE_DIR "${POLYNOMIAL_OPTICS_DIR}/src")
set(EIGEN3_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/ext/lentil/Eigen")
set(FMT_DIR "${CMAKE_SOURCE_DIR}/ext/lentil/fmt")
set(FMT_INCLUDE_DIR "${FMT_DIR}/include")
set(JSON_INCLUDE_DIR "${POLYNOMIAL_OPTICS_DIR}/ext")

message(STATUS "Eigen3 directory: ${EIGEN3_INCLUDE_DIR}")
message(STATUS "fmt directory: ${FMT_INCLUDE_DIR}")

# Verify Eigen exists
if(NOT EXISTS "${EIGEN3_INCLUDE_DIR}")
    message(FATAL_ERROR "Eigen not found at ${EIGEN3_INCLUDE_DIR}")
endif()

# Add fmt as subdirectory (it has CMakeLists.txt)
add_subdirectory(${FMT_DIR} ${CMAKE_BINARY_DIR}/fmt EXCLUDE_FROM_ALL)

# =============================================================================
# Python Bindings
# =============================================================================

if(BUILD_PYTHON_BINDINGS)
    message(STATUS "Building Python bindings")

    # Python binding source
    set(PYTHON_BINDING_SOURCE
        src/python_bindings.cpp
    )

    # Create Python module
    pybind11_add_module(polynomial_optics_binding ${PYTHON_BINDING_SOURCE})

    # Include directories
    target_include_directories(polynomial_optics_binding PRIVATE
        ${POLYNOMIAL_OPTICS_INCLUDE_DIR}
        ${EIGEN3_INCLUDE_DIR}
        ${FMT_INCLUDE_DIR}
        ${JSON_INCLUDE_DIR}
        ${CMAKE_SOURCE_DIR}/src
    )

    # Link fmt library
    target_link_libraries(polynomial_optics_binding PRIVATE fmt::fmt-header-only)

    # Compiler flags
    target_compile_options(polynomial_optics_binding PRIVATE
        -Wall
        -Wextra
        -Wno-unused-parameter
        -Wno-missing-field-initializers
    )

    # Install Python module to python/potk directory
    install(TARGETS polynomial_optics_binding
        LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/python/potk
    )

    message(STATUS "Python module will be installed to: ${CMAKE_SOURCE_DIR}/python/potk")
endif()

# =============================================================================
# Installation
# =============================================================================

# Install Python package
install(DIRECTORY python/potk
    DESTINATION python
    FILES_MATCHING PATTERN "*.py"
)

# Install VEX templates
install(DIRECTORY vex/templates
    DESTINATION vex
    FILES_MATCHING PATTERN "*.vfl"
)

# Install tools
install(DIRECTORY tools
    DESTINATION .
    FILES_MATCHING PATTERN "*.py"
    PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ
                GROUP_EXECUTE GROUP_READ
                WORLD_EXECUTE WORLD_READ
)

# =============================================================================
# Build Summary
# =============================================================================

message(STATUS "")
message(STATUS "========================================")
message(STATUS "POTK Build Configuration")
message(STATUS "========================================")
message(STATUS "Version:                ${PROJECT_VERSION}")
message(STATUS "Build type:             ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ standard:           ${CMAKE_CXX_STANDARD}")
message(STATUS "Python bindings:        ${BUILD_PYTHON_BINDINGS}")
if(BUILD_PYTHON_BINDINGS)
    message(STATUS "  Python version:       ${Python3_VERSION}")
    message(STATUS "  Python executable:    ${Python3_EXECUTABLE}")
endif()
message(STATUS "polynomial-optics:      ${POLYNOMIAL_OPTICS_DIR}")
message(STATUS "Eigen3:                 ${EIGEN3_INCLUDE_DIR}")
message(STATUS "========================================")
message(STATUS "")

