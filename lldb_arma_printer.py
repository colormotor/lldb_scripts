### Armadillo pretty printer for LLDB, initially adapted from 
### https://github.com/fantaosha/LLDB-Eigen-Pretty-Printer 
### And lldb examples 
### https://github.com/llvm-mirror/lldb/tree/master/examples/python

### Add to .lldbinit
### command script import ~/lldb_scripts/lldb_arma_printer.py

import lldb
import argparse

import re
import os
from functools import partial

def __lldb_init_module(debugger, unused):
    debugger.HandleCommand("command script add -c lldb_arma_printer.PrintArmadillo parma")
    print('Importing Armadillo Printer, command: parma varname')

class PrintArmadillo:
    def __init__(self, debugger, unused):
        return

    def __call__(self, debugger, command, exe_ctx, result):
        # Always get program state from the lldb.SBExecutionContext passed
        # in as exe_ctx
        frame = exe_ctx.GetFrame()
        if not frame.IsValid():
            result.SetError("invalid frame")
            return
        
        # Try to evaluate input, this may be also for instance an element of a a std::vector
        try:
            sbval = frame.EvaluateExpression(command)
        except:
            result.SetError("Could not evaluate %s in frame"%command)
            return

        # Need to figure out how to detect errors in EvaluateExpression
        if sbval.GetByteSize()==0:
            result.SetError("Could not evaluate %s in frame"%command)
            return

        get = lambda i: sbval.GetValueForExpressionPath(".mem["+str(i)+"]").GetValue()

        try: 
            n_rows = sbval.GetValueForExpressionPath(".n_rows").GetValueAsSigned()
            n_cols = sbval.GetValueForExpressionPath(".n_cols").GetValueAsSigned()

            padding = 1
            for i in range(0, n_rows * n_cols):
                padding = max(padding, len(str(get(i))))

            output = "rows: %d, cols: %d\n [" % (n_rows, n_cols)
    
            ## Visualize as row if a column vector
            transpose = ''
            if n_cols == 1:
                n_cols = n_rows
                n_rows = 1
                transpose = '.T'

            for i in range(0, n_rows):
                if i!=0:
                    output += " "
                output += '['
                for j in range(0, n_cols):
                    val = get(i + j*n_rows)
                    if j!=0:
                        output += val.rjust(padding+2, ' ')
                    else:
                        output += val.rjust(padding+1, ' ')
                output += ']'
                if i!=n_rows-1:
                    output += ",\n"

            output+="]" + transpose + "\n"
            print(output)
        except:
            result.SetError("Error not find variable %s in frame"%command)
        
    def get_short_help(self):
        return "Prints an Armadillo matrix or vector\n"


