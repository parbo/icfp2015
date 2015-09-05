#pragma once

#include <cmath>
#include <vector>

namespace hx {

struct Hex {
  Hex(int x, int y, int z) : x(x), y(y), z(z) {}
  int x = 0;
  int y = 0;
  int z = 0;
};

enum class Turn {
  CW,
  CCW
};

const Hex DIRECTION_E = Hex(1, -1, 0);
const Hex DIRECTION_W = Hex(-1, 1, 0);
const Hex DIRECTION_SE = Hex(0, -1, 1);
const Hex DIRECTION_SW = Hex(-1, 0, 1);
const Hex DIRECTION_NE = Hex(1, 0, -1);
const Hex DIRECTION_NW = Hex(0, 1, -1);

const Hex DIRECTIONS[6] = {
  DIRECTION_E,
  DIRECTION_W,
  DIRECTION_SE,
  DIRECTION_SW,
  DIRECTION_NE,
  DIRECTION_NW,
};

Hex add(const Hex &a, const Hex &b) {
  return Hex(a.x + b.x, a.y + b.y, a.z + b.z);
}

Hex sub(const Hex &a, const Hex &b) {
  return Hex(a.x - b.x, a.y - b.y, a.z - b.z);
}

Hex scale(int s, const Hex &a) {
  return Hex(s * a.x, s * a.y, s * a.z);
}

int distance(const Hex &h0, const Hex &h1) {
  return (std::abs(h1.x - h0.x) + std::abs(h1.y - h0.y) + std::abs(h1.z - h0.z)) / 2;
}

Hex rotate(const Hex &pivot, const Hex &h, Turn turn) {
  const auto vect = sub(h, pivot);
  if (turn == Turn::CW) {
    return add(pivot, Hex(-vect.z, -vect.x, -vect.y));
  } else {
    return add(pivot, Hex(-vect.y, -vect.z, -vect.x));
  }
}

int abs_rotation_distance(const Hex &v0, const Hex &v1) {
  const auto l0 = std::sqrt(v0.x * v0.x + v0.y * v0.y + v0.z * v0.z);
  const auto l1 = std::sqrt(v1.x * v1.x + v1.y * v1.y + v1.z * v1.z);
  const auto s = v0.x * v1.x + v0.y * v1.y + v0.z * v1.z;
  const auto fact = l0 * l1;
  if (s > 0.8 * fact) {
    return 0;
  } else if (s > 0.0) {
    return 1;
  } else if ( s > -0.8 * fact) {
    return 2;
  } else {
    return 3;
  }
}

std::vector<Hex> circle(const Hex &center, int radius) {
  std::vector<Hex> members;
  auto h = add(center, scale(radius, DIRECTION_NW));
  for (const auto &direction : DIRECTIONS) {
    for (int step = 0; step < radius; ++step) {
      members.push_back(h);
      h = add(h, direction);
    }
  }
  return members;
}

Hex to_hex(int col, int row) {
  const auto x = col - (row - (row % 2)) / 2;
  const auto z = row;
  const auto y = -x - z;
  return Hex(x, y, z);
}

}  // namespace hx


