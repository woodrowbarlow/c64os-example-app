    *= $0900

    .word start

start

loop
    inc $d020
    jmp loop
