### Armadillo pretty printer for LLDB
### https://github.com/fantaosha/LLDB-Eigen-Pretty-Printer 
### And various lldb examples
### While pretty printing in command line would work fine, 
### Currently this breaks in the XCode visual debugger
### E.g.:
### Only a summary is not compatible with XCode visual debugger (freezes) 
### Was not able to recover SBValue data once a SyntheticProvider is created (n_cols, etc are all 0)
### One hack is to use the `internal_dict` object (which should not be used), but 
### Anyhow a Python RecursionError occurs if trying to print a std::vector of vecs

### Add to .lldbinit
### command script import ~/lldb_scripts/lldb_arma_pretty_printer.py

import lldb
import re
import os
from functools import partial

def __lldb_init_module (debugger, dict):
    
    debugger.HandleCommand('type summary add -e -x "arma::Col<.+>$" -F\
                        lldb_arma_pretty_printer.arma_matrix_summary -w armadillo')
    debugger.HandleCommand('type synthetic add -l lldb_arma_pretty_printer.MatrixProvider -x "arma::Col<.+>$" -w armadillo')
    debugger.HandleCommand('type summary add -e -x "arma::Mat<.+>$" -F\
                        lldb_arma_pretty_printer.arma_matrix_summary -w armadillo')
    debugger.HandleCommand('type synthetic add -l lldb_arma_pretty_printer.MatrixProvider -x "arma::Mat<.+>$" -w armadillo')
    
    debugger.HandleCommand("type category enable armadillo")
    print('Imported lldb_arma_pretty_printer')


class MatrixProvider:
    def __init__(self, val, dict):
        #logger = lldb.formatters.Logger.Logger()
        print('building provider')
        try:
            self.val = val
            self.update()

            # Hack, not supposed to use this, but all values seem to be zeroed out otherwise when 
            # creating a synthetic provider 
            dict['n_rows'] = self.n_rows
            dict['n_cols'] = self.n_cols
            dict['n_elem'] = self.n_elem
        except:
            print('Error in provider')
    def num_children(self):
        #logger = lldb.formatters.Logger.Logger()
        return self.n_rows*self.n_cols
        
    def get_child_index(self, name):
        try:
            return int(name.lstrip('[').rstrip(']'))
        except:
            return -1

    
    def get_child_at_index(self,index):
        #logger = lldb.formatters.Logger.Logger()
        #print("Retrieving child " + str(index))
        if index < 0:
            return None
        if index >= self.num_children():
            return None
        
        try:
            val = self.val.GetValueForExpressionPath(".mem["+str(index)+"]")
            return val
        except:
            print('Failed retrieving index: ' + str(index))

        return None
    
    def has_children(self):
        return True

    def update(self):
        #logger = lldb.formatters.Logger.Logger()

        try:
            self.n_rows = self.val.GetValueForExpressionPath(".n_rows").GetValueAsSigned()
            self.n_cols = self.val.GetValueForExpressionPath(".n_cols").GetValueAsSigned()
            self.n_elem = self.val.GetValueForExpressionPath(".n_elem").GetValueAsSigned()
            self.data = self.val.GetValueForExpressionPath(".mem")
        except:
            print("MatrixProvider.update failed")
            self.n_rows = 0
            self.n_cols = 0
            self.n_elem = 0
            self.data = None

    # def get_value(self):
    #     print('get value called')
    #     #print(self.val)
    #     return self.val
    
def arma_matrix_summary(valobj, internal_dict):
    try:
        n_rows = internal_dict['n_rows']
        n_cols = internal_dict['n_cols']
        n_elem = internal_dict['n_elem']
    except:
        print('Failed reading internal dict (hack)')
        n_rows = 0
        n_cols = 0
        n_elem = 0
    # if synth is not None:
    #     n_rows = synth.GetValueForExpressionPath(".n_rows").GetValueAsSigned()
    #     n_cols = synth.GetValueForExpressionPath(".n_cols").GetValueAsSigned()
    #     n_elem = synth.GetValueForExpressionPath(".n_elem").GetValueAsSigned()
    # else:
    #     n_rows = valobj.GetValueForExpressionPath(".n_rows").GetValueAsSigned()
    #     n_cols = valobj.GetValueForExpressionPath(".n_cols").GetValueAsSigned()
    #     n_elem = valobj.GetValueForExpressionPath(".n_elem").GetValueAsSigned()
        
    return 'n_rows=%d\nn_cols=%d\nn_elem=%d\n'%(n_rows, n_cols, n_elem)
