#include "hx.h"

#include <cassert>
#include <iostream>

int main() {
  const auto h0 = hx::to_hex(2, 2);
  assert(0 == hx::distance(h0, h0));
  const auto h1 = hx::to_hex(1, 3);
  assert(1 == hx::distance(h0, h1));
  const auto h2 = hx::to_hex(4, 5);
  std::cout << hx::distance(h0, h2) << std::endl;
  assert(4 == hx::distance(h0, h2));
}
