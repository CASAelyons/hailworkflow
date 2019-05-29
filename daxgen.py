#!/usr/bin/env python

import sys
import os
import pwd
import time
from Pegasus.DAX3 import *
from datetime import datetime
from argparse import ArgumentParser

def get_radar_config(radname):
    radarconf = {
        "arlington.tx": "HC_XUTA.tx.ini",
        "mesquite.tx": "HC_XUTA.tx.ini",
        "ftworth.tx": "HC_XUTA.tx.ini",
        "midlothian.tx": "HC_XMDL.tx.ini",
    }
    radarassoc = radarconf.get(radname, lambda: "HC_XUTA.tx.ini");
    return radarassoc

class single_hail_workflow(object):
    def __init__(self, outdir, nc_fn):
        self.outdir = outdir
        self.nc_fn = nc_fn

    def generate_dax(self):
        "Generate a workflow"
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        dax = ADAG("casa_hail_wf-%s" % ts)
        dax.metadata("name", "CASA Hail")

        for f in self.nc_fn:
            f = f.split("/")[-1]
            if f.endswith(".gz"):
                radar_input = f[:-3]
                unzip = Job("gunzip")
                unzip.addArguments(f)
                unzip.uses(f, link=Link.INPUT)
                unzip.uses(radar_input, link=Link.OUTPUT, transfer=False, register=False)
                dax.addJob(unzip)
            else:
                radar_input = f;

            string_end = self.nc_fn[-1].find("-")
            file_time = self.nc_fn[-1][string_end+1:string_end+16]
            file_ymd = file_time[0:8]
            file_hms = file_time[9:15]
            
            #print file_ymd
            #print file_hms
                
            radarloc = self.nc_fn[-1][0:string_end]
            #print radarloc

            radarconfigfilename = get_radar_config(radarloc)
            #print radarconfigfilename
            radarconfigfile = File(radarconfigfilename)
            
            soundingfile = File("current_sounding.txt")
                
            hydroclass_outputfile = File(radarloc + "-" + file_ymd + "-" + file_hms + ".hc.netcdf");
            hydroclass_cfradial = File(radarloc + "-" + file_ymd + "-" + file_hms + ".hc.netcdf.cfradial");
            #print hydroclass_outputfile
            
            hydroclass_job = Job("hydroclass")
            hydroclass_job.addArguments("-c", radarconfigfile, "-o", hydroclass_outputfile, "-t", "1", "-m", "VHS", "-d", "membership_functions/", "-s", soundingfile);

            hydroclass_job.uses(radar_input, link=Link.INPUT)
            hydroclass_job.uses(radarconfigfile, link=Link.INPUT)
            hydroclass_job.uses(soundingfile, link=Link.INPUT)
            hydroclass_job.uses(hydroclass_outputfile, link=Link.OUTPUT, transfer=True, register=False)
            hydroclass_job.uses(hydroclass_cfradial, link=Link.OUTPUT, transfer=True, register=False)
            #hydroclass_job.profile("pegasus", "label", "label")
            dax.addJob(hydroclass_job)

        # Write the DAX file
        daxfile = os.path.join(self.outdir, dax.name+".dax")
        dax.writeXMLFile(daxfile)
        print daxfile

    def generate_workflow(self):
        # Generate dax
        self.generate_dax()
        
if __name__ == '__main__':
    parser = ArgumentParser(description="Single Hail Workflow")
    parser.add_argument("-f", "--files", metavar="INPUT_FILE", type=str, nargs="+", help="Forecast Filename", required=True)
    parser.add_argument("-o", "--outdir", metavar="OUTPUT_LOCATION", type=str, help="DAX Directory", required=True)

    args = parser.parse_args()
    outdir = os.path.abspath(args.outdir)
    
    if not os.path.isdir(args.outdir):
        os.makedirs(outdir)

    workflow = single_hail_workflow(outdir, args.files)
    workflow.generate_workflow()
