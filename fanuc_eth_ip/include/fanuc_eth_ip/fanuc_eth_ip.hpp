#include <EIPScanner/MessageRouter.h>
#include <EIPScanner/utils/Logger.h>
#include <EIPScanner/utils/Buffer.h>

using eipScanner::SessionInfo;
using eipScanner::MessageRouter;
using namespace eipScanner::cip;
using namespace eipScanner::utils;
#include <array>  // add at top of header



enum RegisterEnum 
{
    MotionStatus  = 1, 
    DpmStatus       = 9,
    GripperMove     = 10, 
    GripperPos      = 11, 
    GripperVel      = 12, 
    GripperEff      = 13, 
    GripperActivate = 15,
    CollabActive    = 99,  
};

enum StatusEnum 
{
    Inactive    = 0,
    Ros         = 1,
    Dpm         = 2,
};

class fanuc_eth_ip
{
private:
    std::string ip_;
    std::shared_ptr< eipScanner::SessionInfo > si_;
    std::shared_ptr< eipScanner::MessageRouter > messageRouter_ = std::make_shared< eipScanner::MessageRouter >();

public:
  std::array<uint8_t, 4> read_register_bytes(const int& reg) const;
  int32_t read_register_int32(const int& reg) const;
  float read_register_float_native(const int& reg) const;
  float read_register_float_wordswap(const int& reg) const;
    fanuc_eth_ip(std::string ip);
    ~fanuc_eth_ip();
    std::vector<double> get_current_joint_pos();
    std::vector<double> get_current_pose();
    int read_register(const int& reg);
    void write_register(const int val, const int reg = 1);
    void write_pos_register(const std::vector<double> j_vals, const int reg = 1);
    bool write_DI(const Buffer buffer);
    bool write_flag(const bool val, const int pos);
    void activateDPM(const bool activate = true);
    void deactivateDPM();
    bool writeDPM(const std::vector<int> vals);
    bool writeDPMScaled(const std::vector<double> vals, const double scale = 0.01);
    void setCurrentPos();
    float read_register_real(const int& reg);   // ADDED


};
