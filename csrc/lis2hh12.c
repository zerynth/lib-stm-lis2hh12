//#define ZERYNTH_PRINTF
#include "zerynth.h"

//#define printf(...) vbl_printf_stdout(__VA_ARGS__)

C_NATIVE(_lis2hh12_write_reg8){
    NATIVE_UNWARN();
    int32_t spi;
    int32_t reg;
    int32_t value;
    int32_t err = ERR_OK;

    if (parse_py_args("iii", nargs, args, &spi, &reg, &value) != 3)
        return ERR_TYPE_EXC;

    *res = MAKE_NONE();

    RELEASE_GIL();
    
    uint8_t tosend[2] = { reg & 0x7F, value & 0xFF };
    if (vhalSpiExchange(spi, tosend, NULL, 2) != 0)
        err = ERR_IOERROR_EXC;

    ACQUIRE_GIL();
    return err;
}

C_NATIVE(_lis2hh12_read_reg8){
    NATIVE_UNWARN();
    int32_t spi;
    int32_t reg;
    int32_t err = ERR_OK;

    if (parse_py_args("ii", nargs, args, &spi, &reg) != 2)
        return ERR_TYPE_EXC;

    RELEASE_GIL();
    uint8_t toread[2];
    uint8_t tosend[2] = { (reg & 0x7F) | 0x80, 0 };
    
    if (vhalSpiExchange(spi, tosend, toread, 2) != 0)
        err = ERR_IOERROR_EXC;

    ACQUIRE_GIL();
    if (err == ERR_OK)
        *res = PSMALLINT_NEW(toread[1]);
    else
        *res = MAKE_NONE();
    return err;
}

C_NATIVE(_lis2hh12_write_reg16){
    NATIVE_UNWARN();
    int32_t spi;
    int32_t reg;
    int32_t value;
    int32_t err = ERR_OK;

    if (parse_py_args("iii", nargs, args, &spi, &reg, &value) != 3)
        return ERR_TYPE_EXC;

    *res = MAKE_NONE();

    RELEASE_GIL();
    
    uint8_t tosend[3] = { reg & 0x7F, value & 0xFF, (value >> 8) & 0xFF };
    if (vhalSpiExchange(spi, tosend, NULL, 3) != 0)
        err = ERR_IOERROR_EXC;

    ACQUIRE_GIL();
    return err;
}

C_NATIVE(_lis2hh12_read_reg16){
    NATIVE_UNWARN();
    int32_t spi;
    int32_t reg;
    int32_t err = ERR_OK;

    if (parse_py_args("ii", nargs, args, &spi, &reg) != 2)
        return ERR_TYPE_EXC;

    RELEASE_GIL();
    uint8_t toread[3];
    uint8_t tosend[3] = { (reg & 0x7F) | 0x80, 0, 0 };
    
    if (vhalSpiExchange(spi, tosend, toread, 3) != 0)
        err = ERR_IOERROR_EXC;

    ACQUIRE_GIL();
    if (err == ERR_OK)
        *res = PSMALLINT_NEW((int16_t)(toread[1] + toread[2] * 256));
    else
        *res = MAKE_NONE();
    return err;
}

C_NATIVE(_lis2hh12_read_reg16x3){
    NATIVE_UNWARN();
    int32_t spi;
    int32_t reg;
    int32_t err = ERR_OK;

    if (parse_py_args("ii", nargs, args, &spi, &reg) != 2)
        return ERR_TYPE_EXC;

    RELEASE_GIL();
    uint8_t toread[7];
    uint8_t tosend[7] = { (reg & 0x7F) | 0x80, 0, 0, 0, 0, 0, 0 };
    
    if (vhalSpiExchange(spi, tosend, toread, 7) != 0)
        err = ERR_IOERROR_EXC;

    ACQUIRE_GIL();
    if (err == ERR_OK) {
        PTuple* tpl = ptuple_new(3, NULL);
        PTUPLE_SET_ITEM(tpl,0,PSMALLINT_NEW((int16_t)(toread[1] + toread[2] * 256)));
        PTUPLE_SET_ITEM(tpl,1,PSMALLINT_NEW((int16_t)(toread[3] + toread[4] * 256)));
        PTUPLE_SET_ITEM(tpl,2,PSMALLINT_NEW((int16_t)(toread[5] + toread[6] * 256)));
        *res = tpl;
    }
    else
        *res = MAKE_NONE();
    return err;
}
