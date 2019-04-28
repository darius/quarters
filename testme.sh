#!/bin/sh
set -eu; IFS=$'\n\t'  # 'strict mode': e=errexit, u=nounset

./meta.sh meta.meta >foo
diff -u meta.asm foo
rm foo

./meta.sh infix.meta >infix.asm
python assemble.py <infix.asm >infix.obj
echo '(a+b)*c+d*d to c' | python meta.py infix.obj >foo
echo ' a @ b @ + c @ * d @ d @ * + c !' >bar
diff -u foo bar
rm foo bar

./meta.sh renly.meta >renly.asm
python assemble.py <renly.asm >renly.obj
echo 'fun fib(n) = if n < 2 then 1 else fib(n-1) + fib(n-2). fib(5).' | python meta.py renly.obj >fib.asm
diff -u - fib.asm <<EOF
   goto SKIP0
fib
   parameters n
   load n
   push 2
   lt
   if-false F1
   push 1
   goto E2
F1
   load n
   push 1
   sub
   call fib
   load n
   push 2
   sub
   call fib
   add
E2
   return
SKIP0
   push 5
   call fib
   halt
EOF
rm fib.asm
