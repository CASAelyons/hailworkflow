#!/usr/bin/env python

import sys
import os
import pwd
import time
from Pegasus.DAX3 import *
from datetime import datetime
from argparse import ArgumentParser

class composite_hail_workflow(object):
    def __init__(self, outdir, cart_files):
        self.outdir = outdir
        self.cart_files = cart_files

    def generate_dax(self):
        "Generate a composite workflow"
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        dax = ADAG("composite_hail_wf-%s" % ts)
        dax.metadata("name", "CASA Composite Hail")

        cart_inputs = []
        
        for f in self.cart_files:
            cart_inputs.append(f)

        inputtxtfilename = "/home/ldm/hailworkflow/input/composite_cart_input.txt"
        inputtxt = open(inputtxtfilename, "w")
        for f in cart_inputs:
            inputtxt.write(f)
            inputtxt.write("\n")
        inputtxt.close()

        inputtxtfile = File(inputtxtfilename)

        string_end = self.cart_files[0].find("-")
        file_time = self.cart_files[0][string_end+1:string_end+16]
        file_ymd = file_time[0:8]
        file_hms = file_time[9:15]
        print file_time
        print file_ymd
        print file_hms

        composite_outputfilename = "COMPOSITE_" + file_time + ".nc"
        composite_outputfile = File(composite_outputfilename)
        
        composite_job = Job("hc_composite")
        composite_job.addArguments(inputtxtfilename, composite_outputfilename)
        composite_job.uses(inputtxtfile, link=Link.INPUT)
        composite_job.uses(composite_outputfile, link=Link.OUTPUT, transfer=False, register=False)
        dax.addJob(composite_job)

        #netcdf2png_colorscalefilename = "standard_hmc_single.png"
        #netcdf2png_colorscalefile = File(netcdf2png_colorscalefilename)
        #netcdf2png_outputfilename = radarloc + "-" + file_ymd + "-" + file_hms + "-hmc.png"
        #netcdf2png_outputfile = File(netcdf2png_outputfilename)
        
        #netcdf2png_job = Job("netcdf2png")
        #netcdf2png_job.addArguments("-p", "-39.7,-39.7,0:-39.7,+39.7,0:+39.7,-39.7,0", "-t", "hmc", "-c", netcdf2png_colorscalefilename, "-q", "245", "-o", netcdf2png_outputfilename)
        #netcdf2png_job.addArguments(hydroclass_outputfilename)
        #netcdf2png_job.uses(netcdf2png_colorscalefile, link=Link.INPUT)
        #netcdf2png_job.uses(hydroclass_outputfile, link=Link.INPUT)
        #netcdf2png_job.uses(netcdf2png_outputfile, link=Link.OUTPUT, transfer=True, register=False)
	#dax.addJob(netcdf2png_job)
        
        # Write the DAX file
        daxfile = os.path.join(self.outdir, dax.name+".dax")
        dax.writeXMLFile(daxfile)
        print daxfile

    def generate_workflow(self):
        # Generate dax
        self.generate_dax()
        
if __name__ == '__main__':
    parser = ArgumentParser(description="Composite Hail Workflow")
    parser.add_argument("-f", "--files", metavar="INPUT_FILES", type=str, nargs="+", help="Cart Files", required=True)
    parser.add_argument("-o", "--outdir", metavar="OUTPUT_LOCATION", type=str, help="DAX Directory", required=True)

    args = parser.parse_args()
    outdir = os.path.abspath(args.outdir)
    
    if not os.path.isdir(args.outdir):
        os.makedirs(outdir)

    workflow = composite_hail_workflow(outdir, args.files)
    workflow.generate_workflow()
