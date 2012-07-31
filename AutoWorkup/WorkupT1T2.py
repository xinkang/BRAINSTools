#!/usr/bin/python
#################################################################################
## Program:   BRAINS (Brain Research: Analysis of Images, Networks, and Systems)
## Language:  Python
##
## Author:  Hans J. Johnson
##
##      This software is distributed WITHOUT ANY WARRANTY; without even
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
##      PURPOSE.  See the above copyright notices for more information.
##
#################################################################################

import os
import csv
import sys
import string
import argparse
#"""Import necessary modules from nipype."""
#from nipype.utils.config import config
#config.set('logging', 'log_to_file', 'false')
#config.set_log_dir(os.getcwd())
#--config.set('logging', 'workflow_level', 'DEBUG')
#--config.set('logging', 'interface_level', 'DEBUG')
#--config.set('execution','remove_unnecessary_outputs','false')

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory
from nipype.interfaces.base import traits, isdefined, BaseInterface
from nipype.interfaces.utility import Merge, Split, Function, Rename, IdentityInterface
import nipype.interfaces.io as nio   # Data i/o
import nipype.pipeline.engine as pe  # pypeline engine
from nipype.interfaces.freesurfer import ReconAll

from nipype.utils.misc import package_check
#package_check('nipype', '5.4', 'tutorial1') ## HACK: Check nipype version
package_check('numpy', '1.3', 'tutorial1')
package_check('scipy', '0.7', 'tutorial1')
package_check('networkx', '1.0', 'tutorial1')
package_check('IPython', '0.10', 'tutorial1')

from BRAINSTools import *
from BRAINSTools.ANTSWrapper import *
from BRAINSTools.WarpAllAtlas import *
from BRAINSTools.ants.normalize import WarpImageMultiTransform

from WorkupT1T2AtlasNode import MakeAtlasNode


###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
## WorkupT1T2 is the main workflow to be run
###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
def WorkupT1T2(mountPrefix,ExperimentBaseDirectoryCache, ExperimentBaseDirectoryResults, subjectDatabaseFile, atlas_fname_wpath, BCD_model_path,
               InterpolationMode="Linear", Mode=10,DwiList=[],WORKFLOW_COMPONENTS=[],CLUSTER_QUEUE=''):
    """
    Run autoworkup on all subjects data defined in the subjectDatabaseFile

    This is the main function to call when processing a data set with T1 & T2
    data.  ExperimentBaseDirectoryPrefix is the base of the directory to place results, T1Images & T2Images
    are the lists of images to be used in the auto-workup. atlas_fname_wpath is
    the path and filename of the atlas to use.
    """

    print "Building Pipeline"
    ########### PIPELINE INITIALIZATION #############
    baw200 = pe.Workflow(name="BAW_20120730")
    baw200.config['execution'] = {
                                     'plugin':'Linear',
                                     #'stop_on_first_crash':'true',
                                     #'stop_on_first_rerun': 'true',
                                     'stop_on_first_crash':'false',
                                     'stop_on_first_rerun': 'false',      ## This stops at first attempt to rerun, before running, and before deleting previous results.
                                     'hash_method': 'timestamp',
                                     'single_thread_matlab':'true',       ## Multi-core 2011a  multi-core for matrix multiplication.
                                     'remove_unnecessary_outputs':'false',
                                     'use_relative_paths':'false',         ## relative paths should be on, require hash update when changed.
                                     'remove_node_directories':'false',   ## Experimental
                                     'local_hash_check':'true',           ##
                                     'job_finished_timeout':15            ##
                                     }
    baw200.config['logging'] = {
      'workflow_level':'DEBUG',
      'filemanip_level':'DEBUG',
      'interface_level':'DEBUG',
      'log_directory': ExperimentBaseDirectoryCache
    }
    baw200.base_dir = ExperimentBaseDirectoryCache


    BAtlas = MakeAtlasNode(atlas_fname_wpath) ## Call function to create node
    import WorkupT1T2Single
    import SessionDB
    dbObject=SessionDB.SessionDB(subjectDatabaseFile)
    MergeT1s=dict()
    for subjectid in dbObject.getAllSubjects():
        oneSubjWorkflow=dict()
        subjInfoNode=dict()
        allSessions = dbObject.getSessionsFromSubject(subjectid)
        for sessionid in allSessions:
            projectid = dbObject.getProjFromSession(sessionid)
            print("PROJECT: {0} SUBJECT: {1} SESSION: {2}".format(projectid,subjectid,sessionid))
            subjInfoNode[sessionid] = pe.Node(interface=IdentityInterface(fields=
                    ['sessionid','subjectid','projectid',
                     'allT1s',
                     'allT2s',
                     'allPDs',
                     'allOthers']),
                    run_without_submitting=True,
                    name='99_SubjInfoNode_'+str(subjectid)+"_"+str(sessionid) )
            subjInfoNode[sessionid].inputs.projectid=projectid
            subjInfoNode[sessionid].inputs.subjectid=subjectid
            subjInfoNode[sessionid].inputs.sessionid=sessionid
            subjInfoNode[sessionid].inputs.allT1s=dbObject.getFilenamesByScantype(sessionid,['T1-30','T1-15'])
            subjInfoNode[sessionid].inputs.allT2s=dbObject.getFilenamesByScantype(sessionid,['T2-30','T2-15'])
            subjInfoNode[sessionid].inputs.allPDs=dbObject.getFilenamesByScantype(sessionid,['PD-30','PD-15'])
            subjInfoNode[sessionid].inputs.allOthers=dbObject.getFilenamesByScantype(sessionid,['OTHER-30','OTHER-15'])

            oneSubjWorkflow[sessionid]=WorkupT1T2Single.MakeOneSubWorkFlow(
                              projectid, subjectid, sessionid,
                              BAtlas, WORKFLOW_COMPONENTS,
                              BCD_model_path, InterpolationMode, CLUSTER_QUEUE,
                              ExperimentBaseDirectoryResults)
            baw200.connect(subjInfoNode[sessionid],'projectid',oneSubjWorkflow[sessionid],'InputSpec.projectid')
            baw200.connect(subjInfoNode[sessionid],'subjectid',oneSubjWorkflow[sessionid],'InputSpec.subjectid')
            baw200.connect(subjInfoNode[sessionid],'sessionid',oneSubjWorkflow[sessionid],'InputSpec.sessionid')
            baw200.connect(subjInfoNode[sessionid],'allT1s',oneSubjWorkflow[sessionid],'InputSpec.allT1s')
            baw200.connect(subjInfoNode[sessionid],'allT2s',oneSubjWorkflow[sessionid],'InputSpec.allT2s')
            baw200.connect(subjInfoNode[sessionid],'allPDs',oneSubjWorkflow[sessionid],'InputSpec.allPDs')
            baw200.connect(subjInfoNode[sessionid],'allOthers',oneSubjWorkflow[sessionid],'InputSpec.allOthers')
        numSessions=len(allSessions)
        mergeSubjectSessionNames="99_MergeAllSessions"+str(subjectid)
        MergeT1s[subjectid] = pe.Node(interface=Merge(numSessions),
                                      run_without_submitting=True,
                                      name=mergeSubjectSessionNames)
        for sessionid in allSessions:
            pass

    return baw200
