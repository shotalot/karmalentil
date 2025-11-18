# POTK - Polynomial Optics to Karma
# CMake build configuration

cmake_minimum_required(VERSION 3.12)
project(POTK VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 11)
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

# Find Eigen (header-only linear algebra library)
find_package(Eigen3 3.3 QUIET)
if(NOT Eigen3_FOUND)
    message(STATUS "Eigen3 not found, will use bundled version from polynomial-optics")
    # polynomial-optics includes Eigen as submodule
    set(EIGEN3_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/ext/lentil/polynomial-optics/ext/Eigen")
endif()

# =============================================================================
# polynomial-optics Library
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

# Add polynomial-optics as subdirectory (if it has CMakeLists.txt)
# OR compile its sources directly
# This depends on polynomial-optics library structure

# For now, we'll include it as header-only and link sources manually
# TODO: Update this based on actual polynomial-optics build structure

set(POLYNOMIAL_OPTICS_INCLUDE_DIR "${POLYNOMIAL_OPTICS_DIR}/include")
set(POLYNOMIAL_OPTICS_SRC_DIR "${POLYNOMIAL_OPTICS_DIR}/src")

# =============================================================================
# POTK Core Library
# =============================================================================

# Collect polynomial-optics source files
# file(GLOB_RECURSE POLYNOMIAL_OPTICS_SOURCES
#     "${POLYNOMIAL_OPTICS_SRC_DIR}/*.cpp"
# )

# POTK C++ sources (will be created in Phase 2)
set(POTK_SOURCES
    # src/lens_system.cpp
    # src/polynomial_fitter.cpp
    # src/vex_generator.cpp
)

# Create POTK library (when we have C++ sources)
# add_library(potk_core ${POTK_SOURCES} ${POLYNOMIAL_OPTICS_SOURCES})
# target_include_directories(potk_core PUBLIC
#     ${POLYNOMIAL_OPTICS_INCLUDE_DIR}
#     ${EIGEN3_INCLUDE_DIR}
#     ${CMAKE_SOURCE_DIR}/src
# )

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
    # pybind11_add_module(polynomial_optics_binding ${PYTHON_BINDING_SOURCE})
    # target_link_libraries(polynomial_optics_binding PRIVATE potk_core)
    # target_include_directories(polynomial_optics_binding PRIVATE
    #     ${POLYNOMIAL_OPTICS_INCLUDE_DIR}
    #     ${EIGEN3_INCLUDE_DIR}
    # )

    # Install Python module
    # install(TARGETS polynomial_optics_binding
    #     LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/python/potk
    # )
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

# =============================================================================
# Notes
# =============================================================================

# TODO Phase 1 (Current):
# - [ ] Verify polynomial-optics directory structure
# - [ ] Create initial C++ wrapper sources
# - [ ] Build Python bindings
# - [ ] Test basic functionality

# TODO Phase 2:
# - [ ] Implement lens import C++ classes
# - [ ] Implement polynomial fitting interface
# - [ ] Add validation tools

# TODO Phase 3:
# - [ ] Implement VEX code generator
# - [ ] Add per-lens optimization

# TODO Phase 4:
# - [ ] Optional HDK plugin
# - [ ] Houdini integration helpers
