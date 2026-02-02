#include <fanuc_eth_ip/fanuc_eth_ip.hpp>

#include <iostream>
#include <iomanip>

int main(int argc, char** argv)
{
  if (argc < 2) {
    std::cerr << "Usage: " << argv[0] << " <robot_ip>\n";
    return 1;
  }

  fanuc_eth_ip robot(argv[1]);

  for (int reg = 4; reg <= 9; ++reg) {
    auto b = robot.read_register_bytes(reg);

    std::cout << "REG[" << reg << "] bytes: ";
    for (auto v : b) {
      std::cout << "0x" << std::hex << std::setw(2) << std::setfill('0')
                << static_cast<int>(v) << " ";
    }
    std::cout << std::dec << "\n";

    std::cout << "  int32        = " << robot.read_register_int32(reg) << "\n";
    std::cout << "  float(native)= " << robot.read_register_float_native(reg) << "\n";
    std::cout << "  float(wswap) = " << robot.read_register_float_wordswap(reg) << "\n";
    std::cout << "---------------------------------------------\n";
  }

  return 0;
}
