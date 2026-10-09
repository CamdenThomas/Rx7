/* test_vectors.cpp - the CAN map held to the record (Y8).
 *
 * can_vectors.h is generated from can_messages.csv / can_fields.csv by gen_vectors.py;
 * can_map.h is the firmware's hand-written map. Every static_assert below fails to COMPILE
 * when the two disagree, so a frame id, a timeout or a bit the record moves cannot be built
 * into a Teensy until can_map.h follows it. There is nothing to run: compiling is the test.
 */
#include <cstdint>
#include <cstdio>
#include "../icu/can_map.h"
#include "can_vectors.h"

#define SAME_ID(S)  static_assert(ID_##S == V_ID_##S, "frame id " #S " disagrees with the record")
#define SAME_TMO(S) static_assert(TMO_##S == V_TMO_##S, "timeout " #S " disagrees with the record")
#define SAME_BIT(M) static_assert(M == (1u << V_##M), "bit " #M " disagrees with the record")

SAME_ID(PMU_STATE);   SAME_ID(PMU_POWER);   SAME_ID(PMU_OUTPUTS); SAME_ID(PMU_CHANNEL);
SAME_ID(ICU_SENSORS); SAME_ID(ICU_HEALTH);  SAME_ID(ICU_BODY);    SAME_ID(ICU_BATT);
SAME_ID(ICU_CELLS);   SAME_ID(ICU_BATT_EXT); SAME_ID(DCU_CLIMATE); SAME_ID(DCU_COMFORT);
SAME_ID(DCU_RADAR);   SAME_ID(PANEL_KEYS);

SAME_TMO(PMU_STATE);  SAME_TMO(PMU_POWER);  SAME_TMO(PMU_OUTPUTS); SAME_TMO(ICU_SENSORS);
SAME_TMO(ICU_BODY);   SAME_TMO(ICU_BATT);   SAME_TMO(DCU_CLIMATE); SAME_TMO(DCU_COMFORT);
SAME_TMO(PANEL_KEYS);

SAME_BIT(WAKE_ACC);  SAME_BIT(WAKE_RUN);  SAME_BIT(WAKE_DOOR); SAME_BIT(WAKE_A8);
SAME_BIT(WAKE_SELF); SAME_BIT(WAKE_BRAKE); SAME_BIT(WAKE_DCU);
SAME_BIT(FAULT_SOFTFUSE); SAME_BIT(FAULT_UNDERVOLT); SAME_BIT(FAULT_OVERVOLT); SAME_BIT(FAULT_OVERTEMP);
SAME_BIT(INFAULT_A1); SAME_BIT(INFAULT_A2); SAME_BIT(INFAULT_A3); SAME_BIT(INFAULT_A4);
SAME_BIT(INFAULT_A5); SAME_BIT(INFAULT_A6); SAME_BIT(INFAULT_A8); SAME_BIT(INFAULT_A15);
SAME_BIT(SENS_RPM); SAME_BIT(SENS_WATER); SAME_BIT(SENS_OILTEMP); SAME_BIT(SENS_OILPRESS);
SAME_BIT(SENS_VSS); SAME_BIT(SENS_FUEL);
SAME_BIT(SFAULT_OPEN); SAME_BIT(SFAULT_SHORT); SAME_BIT(SFAULT_RANGE); SAME_BIT(SFAULT_IMPLAUSIBLE);
SAME_BIT(CANH_PMU); SAME_BIT(CANH_DCU); SAME_BIT(CANH_AFR);
SAME_BIT(TT_CHARGE); SAME_BIT(TT_BRAKE); SAME_BIT(TT_TURN_L); SAME_BIT(TT_TURN_R); SAME_BIT(TT_HIGH_BEAM);
SAME_BIT(BATT_ADV_FRESH); SAME_BIT(BATT_GATT_CONN); SAME_BIT(BATT_CELLS_FRESH);
SAME_BIT(BATT_CSUM_FAILED); SAME_BIT(BATT_RADIO_LOST);
SAME_BIT(BAND_X); SAME_BIT(BAND_K); SAME_BIT(BAND_KA); SAME_BIT(BAND_LASER);
SAME_BIT(PK_DEFOG); SAME_BIT(PK_HATCH); SAME_BIT(PK_FUEL_DOOR); SAME_BIT(PK_HVAC_MODE);
SAME_BIT(PK_RECIRC); SAME_BIT(PK_WIN_DRV_UP); SAME_BIT(PK_WIN_DRV_DN); SAME_BIT(PK_WIN_PASS_UP);
SAME_BIT(PK_WIN_PASS_DN); SAME_BIT(PK_MIRROR_PRESS);

/* the key-position enum carries the record's FAULT value (0x100 byte 0, R11) */
static_assert(KEY_FAULT == 4, "KEY_FAULT must be 4 (can_fields 0x100/0)");

int main() {
    std::printf("CAN map vectors: every frame id, timeout and bit in can_map.h agrees with the record\n");
    return 0;
}
