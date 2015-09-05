cmake_minimum_required(VERSION 3.0)

find_package(Boost COMPONENTS unit_test_framework REQUIRED)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

add_library(icfp STATIC hx.h hx.cpp)

add_executable(icfp_test hx_test.cpp)
set_target_properties(icfp_test PROPERTIES COMPILE_FLAGS "-DBOOST_TEST_DYN_LINK -DBOOST_TEST_MAIN")
add_test(NAME icfp_test COMMAND icfp_test)
target_link_libraries(icfp_test
  icfp
  ${Boost_UNIT_TEST_FRAMEWORK_LIBRARY}
  )

enable_testing()