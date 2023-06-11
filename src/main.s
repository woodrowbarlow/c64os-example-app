    .include "os/h/modules.h"

    #inc_s "app"

    *= appbase

    .word start

start

loop
    inc $d020
    jmp loop
