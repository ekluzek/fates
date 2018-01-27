#!/usr/bin/env python

#### this script modifies a FATES parameter file. It accepts the following flags
# --var or --variable: variable.
# --pft or --PFT: PFT number. If this is missing, script will assume that its a global variable that is being modified.
# --input or --fin: input filename.
# --output or --fout: output filename.  If missing, will assume its directly modifying the input file, and will prompt unless -O is specified
# --O or --overwrite: overwrite output file without asking.
# --value or --val: value to put in variable
# --s or --silent: don't write anything on successful execution.
####


# =======================================================================================
# =======================================================================================

import numpy as np
import os
from scipy.io import netcdf as nc
import argparse
import shutil

# ========================================================================================
# ========================================================================================
#                                        Main
# ========================================================================================
# ========================================================================================

def main():
    parser = argparse.ArgumentParser(description='Parse command line arguments to this script.')
    #
    parser.add_argument('--var','--variable', dest='varname', type=str, help="What variable to modify? Required.", required=True)
    parser.add_argument('--pft','--PFT', dest='pftnum', type=int, help="PFT number to modify. If this is missing, will assume a global variable.")
    parser.add_argument('--fin', '--input', dest='inputfname', type=str, help="Input filename.  Required.", required=True)
    parser.add_argument('--fout','--output', dest='outputfname', type=str, help="Output filename.  Required.", required=True)
    parser.add_argument('--val', '--value', dest='val', type=float, help="New value of PFT variable.  Required.", required=True)
    parser.add_argument('--O','--overwrite', dest='overwrite', help="If present, automatically overwrite the output file.", action="store_true")
    parser.add_argument('--silent', '--s', dest='silent', help="prevent writing of output.", action="store_true")
    #
    args = parser.parse_args()
    # print(args.varname, args.pftnum, args.inputfname, args.outputfname, args.val, args.overwrite)
    #
    # check to see if output file exists
    if os.path.isfile(args.outputfname):
        if args.overwrite:
            if not args.silent:
                print('replacing file: '+args.outputfname)
            os.remove(args.outputfname)
        else:
            raise ValueError('Output file already exists and overwrite flag not specified for filename: '+args.outputfname)
    #
    shutil.copyfile(args.inputfname, args.outputfname)
    #
    ncfile = nc.netcdf_file(args.outputfname, 'a')
    #
    var = ncfile.variables[args.varname]
    #
    ### check to make sure that, if a PFT is specified, the variable has a PFT dimension, and if not, then it doesn't. and also that shape is reasonable.
    ndim_file = len(var.dimensions)
    ispftvar = False
    for i in range(ndim_file):
        if var.dimensions[i] == 'fates_pft':
            ispftvar = True
            npft_file = var.shape[i]
            pftdim = 0
        else:
            npft_file = None
            pftdim = None
    if args.pftnum == None and ispftvar:
        raise ValueError('pft value is missing but variable has pft dimension.')
    if args.pftnum != None and not ispftvar:
        raise ValueError('pft value is present but variable does not have pft dimension.')
    if ndim_file > 1:
        raise ValueError('variable dimensionality is too high for this script')
    if ndim_file == 1 and not ispftvar:
        raise ValueError('variable dimensionality is too high for this script')
    if args.pftnum != None and ispftvar:
        if args.pftnum > npft_file:
            raise ValueError('PFT specified ('+str(args.pftnum)+') is larger than the number of PFTs in the file ('+str(npft_file)+').')
        if pftdim == 0:
            if not args.silent:
                print('replacing prior value of variable '+args.varname+', for PFT '+str(args.pftnum)+', which was '+str(var[args.pftnum-1])+', with new value of '+str(args.val))
            var[args.pftnum-1] = args.val
    elif args.pftnum == None and not ispftvar:
        if not args.silent:
            print('replacing prior value of variable '+args.varname+', which was '+str(var[:])+', with new value of '+str(args.val))
        var[:] = args.val
    else:
        raise ValueError('Nothing happened somehow.')
    #
    #
    ncfile.close()




# =======================================================================================
# This is the actual call to main
   
if __name__ == "__main__":
    main()

