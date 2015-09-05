#include "hx.h"

#include <cassert>
#include <iostream>

#include <boost/test/unit_test.hpp>

BOOST_AUTO_TEST_CASE(distance) {
  const auto h0 = hx::to_hex(2, 2);
  BOOST_CHECK_EQUAL(0, hx::distance(h0, h0));
  const auto h1 = hx::to_hex(1, 3);
  BOOST_CHECK_EQUAL(1, hx::distance(h0, h1));
  const auto h2 = hx::to_hex(4, 5);
  BOOST_CHECK_EQUAL(4, hx::distance(h0, h2));
}
