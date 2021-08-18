# gdb-scripts
Scripts to simplify debug with gdb

## load example
```
(gdb) source ~/repo/gdb-scripts/optimized-out.py
Loading global optimized-out variables support.
```

Put it into `~/.gdbinit` for autoload

## optimized-out.py
Used to detect address of global optimized out variables

Example usage:
```
(gdb) p pools
$1 = <optimized out>

(gdb) p fibers
$2 = {tqh_first = 0x7f7253dbf000, tqh_last = 0x7f72590c6368}

(gdb) detect-symbol-address pools fibers
Variable `pools' is located at 0x7f726314f3d0

(gdb) set variable $pools = (struct palloc_pool_head *)0x7f726314f3d0
(gdb) p $pools->slh_first->cfg.name
$3 = 0x7f7253dbf02c "zombie_fiber"
```
