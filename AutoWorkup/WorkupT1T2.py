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

#############################################################################
#############################################################################
## Utility functions for the pipeline
#############################################################################
#############################################################################
def get_first_T1_and_T2(in_files,T1_count):
    '''
    Returns the first T1 and T2 file in in_files, based on offset in T1_count.
    '''
    return in_files[0],in_files[T1_count]

def GetExtensionlessBaseName(filename):
    '''
    Get the filename without the extension.  Works for .ext and .ext.gz
    '''
    import os
    currBaseName = os.path.basename(filename)
    currExt = os.path.splitext(currBaseName)[1]
    currBaseName = os.path.splitext(currBaseName)[0]
    if currExt == ".gz":
        currBaseName = os.path.splitext(currBaseName)[0]
        currExt = os.path.splitext(currBaseName)[1]
    return currBaseName


def get_list_element( nestedList, index ):
    return nestedList[index]

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def getFirstT1(uid, dbfile):
    from cPickle import load
    with open(dbfile) as fp:
        db = load(fp)
    print("uid:= {0}, dbfile: {1}".format(uid,dbfile))
    print("result:= {0}".format(db[uid]["T1-30"]))
    return db[uid]["T1-30"][0]

def getT1s(uid, dbfile):
    from cPickle import load
    with open(dbfile) as fp:
        db = load(fp)
    #print("uid:= {0}, dbfile: {1}".format(uid,dbfile))
    #print("result:= {0}".format(db[uid]["T1-30"]))
    return db[uid]["T1-30"]

def getT1sLength(uid, dbfile):
    from cPickle import load
    with open(dbfile) as fp:
        db = load(fp)
    #print("uid:= {0}, dbfile: {1}".format(uid,dbfile))
    #print("result:= {0}".format(db[uid]["T1-30"]))
    return len(db[uid]["T1-30"])

def getT2s(uid, dbfile):
    from cPickle import load
    with open(dbfile) as fp:
        db = load(fp)
    #print("uid:= {0}, dbfile: {1}".format(uid,dbfile))
    #print("result:= {0}".format(db[uid]["T1-30"]))
    return db[uid]["T2-30"]

def getT1sT2s(uid, dbfile,altT1):
    from cPickle import load
    with open(dbfile) as fp:
        db = load(fp)
    #print("uid:= {0}, dbfile: {1}".format(uid,dbfile))
    #print("result:= {0}".format(db[uid]["T1-30"]))
    temp=db[uid]["T1-30"]
    temp.append(db[uid]["T2-30"])
    temp[0]=altT1
    return temp

def MakeList(firstElement,secondElement):
    return [firstElement, secondElement]

def createDBFile(subject_data_file,subjectDatabaseFile,mountPrefix):
    print "Building Subject List: " + subject_data_file
    subjData=csv.reader(open(subject_data_file,'rb'), delimiter=',', quotechar='"')
    myDB=dict()
    ExperimentDatabase=AutoVivification()  #This should be replaced by a more nested dictionary
    nestedDictionary=AutoVivification()
    for row in subjData:
        currDict=dict()
        validEntry=True
        if len(row) == 4:
            site=row[0]
            subj=row[1]
            session=row[2]
            rawDict=eval(row[3])
            currDict={}
            for imageType in rawDict.keys():
                fullPaths=[ mountPrefix+i for i in rawDict[imageType] ]
                if len(fullPaths) < 1:
                    print("Invalid Entry!  {0}".format(currDict))
                    validEntry=False
                for i in fullPaths:
                    if not os.path.exists(i):
                        print("Missing File: {0}".format(i))
                        validEntry=False
                currDict[imageType]=fullPaths
            currDict['site']=site
            currDict['subj']=subj
            currDict['session']=session

            if validEntry == True:
                myDB[session]=currDict
                UNIQUE_ID=site+"_"+subj+"_"+session
                nestedDictionary[site][subj][session]=currDict
                ExperimentDatabase[UNIQUE_ID]=currDict
        else:
            print "ERROR:  Invalid number of elements in row"
            print row
    print "DICTIONARY",ExperimentDatabase
    from cPickle import dump
    dump(ExperimentDatabase, open(subjectDatabaseFile,'w'))
    return ExperimentDatabase

def GenerateOutputPattern(ExperimentDatabase,DefaultNodeName,uidIsFirst=True):
    """ This function generates output path substitutions for workflows and nodes that conform to a common standard.
    """
    patternList=[]
    for key in ExperimentDatabase.keys():
        currDictionary=ExperimentDatabase[key]
        if uidIsFirst == True:
            find_pat=os.path.join(DefaultNodeName,'_uid_'+key)
        else:
            find_pat=os.path.join('_uid_'+key,DefaultNodeName)
        replace_pat=os.path.join(currDictionary['site'],currDictionary['subj'],currDictionary['session'],DefaultNodeName)
        patternList.append( (find_pat,replace_pat) )
    return patternList

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
def WorkupT1T2(mountPrefix,ExperimentBaseDirectoryCache, ExperimentBaseDirectoryResults, subject_data_file, atlas_fname_wpath, BCD_model_path,
               InterpolationMode="Linear", Mode=10,DwiList=[],WORKFLOW_COMPONENTS=[],CLUSTER_QUEUE=''):
    """
    Run autoworkup on all subjects data defined in the subject_data_file

    This is the main function to call when processing a data set with T1 & T2
    data.  ExperimentBaseDirectoryPrefix is the base of the directory to place results, T1Images & T2Images
    are the lists of images to be used in the auto-workup. atlas_fname_wpath is
    the path and filename of the atlas to use.
    """

    subjectDatabaseFile=os.path.join( ExperimentBaseDirectoryCache,'InternalWorkflowSubjectDB.pickle')
    ExperimentDatabase=createDBFile(subject_data_file,subjectDatabaseFile,mountPrefix)

    print "Building Pipeline"
    ########### PIPELINE INITIALIZATION #############
    baw200 = pe.Workflow(name="BAW_20120530")
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

    """TODO: Determine if we want to pass subjectID and scanID, always require full
    paths, get them from the output path, or something else.
    """
    uidSource = pe.Node(interface=IdentityInterface(fields=['uid']),name='99_siteSource')
    uidSource.iterables = ('uid', ExperimentDatabase.keys() )

    BAtlas = MakeAtlasNode(atlas_fname_wpath) ## Call function to create node

    if 'BASIC' in WORKFLOW_COMPONENTS:
        from WorkupT1T2LandmarkInitialization import CreateLandmarkInitializeWorkflow
        DoReverseMapping = False   # Set to true for debugging outputs
        if 'AUXLMK' in WORKFLOW_COMPONENTS:
            DoReverseMapping = True
        myLocalLMIWF= CreateLandmarkInitializeWorkflow("LandmarkInitialize", BCD_model_path, InterpolationMode,DoReverseMapping)
        baw200.connect( [ (uidSource, myLocalLMIWF, [(('uid', getFirstT1, subjectDatabaseFile ), 'InputSpec.inputVolume')] ), ])
        baw200.connect( BAtlas, 'template_landmarks_31_fcsv', myLocalLMIWF,'InputSpec.atlasLandmarkFilename')
        baw200.connect( BAtlas, 'template_landmark_weights_31_csv', myLocalLMIWF,'InputSpec.atlasWeightFilename')
        if 'AUXLMK' in WORKFLOW_COMPONENTS:
            baw200.connect(BAtlas,'template_t1',myLocalLMIWF,'InputSpec.atlasVolume')

        ### Now define where the final organized outputs should go.
        BASIC_DataSink=pe.Node(nio.DataSink(),name="BASIC_DS")
        BASIC_DataSink.inputs.base_directory=ExperimentBaseDirectoryResults
        BASIC_DataSink.inputs.regexp_substitutions = GenerateOutputPattern(ExperimentDatabase,'ACPCAlign')

        baw200.connect(myLocalLMIWF,'OutputSpec.outputLandmarksInACPCAlignedSpace',BASIC_DataSink,'ACPCAlign.@outputLandmarksInACPCAlignedSpace')
        baw200.connect(myLocalLMIWF,'OutputSpec.outputResampledVolume',BASIC_DataSink,'ACPCAlign.@outputResampledVolume')
        baw200.connect(myLocalLMIWF,'OutputSpec.outputLandmarksInInputSpace',BASIC_DataSink,'ACPCAlign.@outputLandmarksInInputSpace')
        baw200.connect(myLocalLMIWF,'OutputSpec.outputTransform',BASIC_DataSink,'ACPCAlign.@outputTransform')
        baw200.connect(myLocalLMIWF,'OutputSpec.atlasToSubjectTransform',BASIC_DataSink,'ACPCAlign.@atlasToSubjectTransform')

    if 'TISSUE_CLASSIFY' in WORKFLOW_COMPONENTS:
        from WorkupT1T2TissueClassifiy import CreateTissueClassifyWorkflow
        myLocalTCWF= CreateTissueClassifyWorkflow("TissueClassify",CLUSTER_QUEUE,InterpolationMode)
        baw200.connect( [ (uidSource, myLocalTCWF, [(('uid', getT1s, subjectDatabaseFile ), 'InputSpec.T1List')] ), ])
        baw200.connect( [ (uidSource, myLocalTCWF, [(('uid', getT2s, subjectDatabaseFile ), 'InputSpec.T2List')] ), ])
        baw200.connect( [ (uidSource, myLocalTCWF, [(('uid', getT1sLength, subjectDatabaseFile ), 'InputSpec.T1_count')] ), ])
        baw200.connect(BAtlas,'AtlasPVDefinition_xml',myLocalTCWF,'InputSpec.atlasDefinition')
        baw200.connect( myLocalLMIWF, 'OutputSpec.outputResampledVolume', myLocalTCWF, 'InputSpec.PrimaryT1' )
        baw200.connect( myLocalLMIWF,'OutputSpec.atlasToSubjectTransform',myLocalTCWF,'InputSpec.atlasToSubjectInitialTransform')

        ### Now define where the final organized outputs should go.
        TC_DataSink=pe.Node(nio.DataSink(),name="TISSUE_CLASSIFY_DS")
        TC_DataSink.inputs.base_directory=ExperimentBaseDirectoryResults
        TC_DataSink.inputs.regexp_substitutions = GenerateOutputPattern(ExperimentDatabase,'TissueClassify')
        baw200.connect(myLocalTCWF, 'OutputSpec.TissueClassifyOutputDir', TC_DataSink,'TissueClassify.@TissueClassifyOutputDir')

    ## Make deformed Atlas image space
    if 'ANTS' in WORKFLOW_COMPONENTS:
        from WorkupT1T2ANTS import CreateANTSRegistrationWorkflow
        myLocalAntsWF = CreateANTSRegistrationWorkflow("ANTSRegistration",CLUSTER_QUEUE,-1)
        baw200.connect( myLocalTCWF,'OutputSpec.t1_corrected',myLocalAntsWF,"InputSpec.fixedVolumesList")
        baw200.connect( BAtlas,'template_t1',    myLocalAntsWF,"InputSpec.movingVolumesList")
        baw200.connect(myLocalLMIWF,'OutputSpec.atlasToSubjectTransform',myLocalAntsWF,'InputSpec.initial_moving_transform')
        # Must register the entire head, not just the brain!
        baw200.connect(myLocalTCWF,'OutputSpec.outputHeadLabels',myLocalAntsWF,'InputSpec.fixedBinaryVolume')
        baw200.connect(BAtlas,'template_headregion',myLocalAntsWF,'InputSpec.movingBinaryVolume')

        ### Now define where the final organized outputs should go.
        ANTS_DataSink=pe.Node(nio.DataSink(),name="ANTSRegistration_DS")
        ANTS_DataSink.inputs.base_directory=ExperimentBaseDirectoryResults
        ANTS_DataSink.inputs.regexp_substitutions = GenerateOutputPattern(ExperimentDatabase,'ANTSRegistration')
        baw200.connect(myLocalAntsWF, 'OutputSpec.warped_image', ANTS_DataSink,'ANTSRegistration.@warped_image')
        baw200.connect(myLocalAntsWF, 'OutputSpec.inverse_warped_image', ANTS_DataSink,'ANTSRegistration.@inverse_warped_image')
        baw200.connect(myLocalAntsWF, 'OutputSpec.affine_transform', ANTS_DataSink,'ANTSRegistration.@affine_transform')
        baw200.connect(myLocalAntsWF, 'OutputSpec.warp_transform', ANTS_DataSink,'ANTSRegistration.@warp_transform')
        baw200.connect(myLocalAntsWF, 'OutputSpec.inverse_warp_transform', ANTS_DataSink,'ANTSRegistration.@inverse_warp_transform')

    if 'SEGMENTATION' in WORKFLOW_COMPONENTS:
        def getListIndex( imageList, index):
            return imageList[index]
        from WorkupT1T2BRAINSCut import CreateBRAINSCutWorkflow
        myLocalSegWF = CreateBRAINSCutWorkflow("Segmentation",CLUSTER_QUEUE,BAtlas) ##Note:  Passing in the entire BAtlas Object here!
        baw200.connect( [ ( myLocalTCWF, myLocalSegWF, [ (( 'OutputSpec.outputAverageImages', getListIndex, 0 ), "InputSpec.T1Volume")] ), ] )
        baw200.connect( [ ( myLocalTCWF, myLocalSegWF, [ (( 'OutputSpec.outputAverageImages', getListIndex, 1 ), "InputSpec.T2Volume")] ), ] )
        baw200.connect( myLocalTCWF,'OutputSpec.atlasToSubjectTransform',myLocalSegWF,'InputSpec.atlasToSubjectTransform')

        ### Now define where the final organized outputs should go.
        SEGMENTATION_DataSink=pe.Node(nio.DataSink(),name="SEGMENTATION_DS")
        SEGMENTATION_DataSink.inputs.base_directory=ExperimentBaseDirectoryResults
        SEGMENTATION_DataSink.inputs.regexp_substitutions = GenerateOutputPattern(ExperimentDatabase,'BRAINSCut')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryLeftAccumben',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryLeftAccumben')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryRightAccumben',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryRightAccumben')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryLeftCaudate',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryLeftCaudate')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryRightCaudate',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryRightCaudate')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryLeftGlobus',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryLeftGlobus')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryRightGlobus',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryRightGlobus')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryLeftHippocampus',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryLeftHippocampus')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryRightHippocampus',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryRightHippocampus')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryLeftPutamen',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryLeftPutamen')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryRightPutamen',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryRightPutamen')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryLeftThalamus',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryLeftThalamus')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputBinaryRightThalamus',SEGMENTATION_DataSink, 'BRAINSCut.@outputBinaryRightThalamus')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputLabelImageName', SEGMENTATION_DataSink,'BRAINSCut.@outputLabelImageName')
        baw200.connect(myLocalSegWF, 'OutputSpec.outputCSVFileName', SEGMENTATION_DataSink,'BRAINSCut.@outputCSVFileName')

    if 'FREESURFER' in WORKFLOW_COMPONENTS:
        RunAllFSComponents=True ## A hack to avoid 26 hour run of freesurfer
        from WorkupT1T2FreeSurfer import CreateFreeSurferWorkflow
        myLocalFSWF= CreateFreeSurferWorkflow("Level1_FSTest",CLUSTER_QUEUE,RunAllFSComponents)
        baw200.connect(uidSource,'uid',myLocalFSWF,'InputSpec.subject_id')
        baw200.connect(myLocalTCWF,'OutputSpec.t1_corrected',myLocalFSWF,'InputSpec.T1_files')
        baw200.connect(myLocalTCWF,'OutputSpec.t2_corrected',myLocalFSWF,'InputSpec.T2_files')
        baw200.connect(myLocalTCWF,'OutputSpec.outputLabels',myLocalFSWF,'InputSpec.label_file')
        #baw200.connect(myLocalTCWF,'OutputSpec.outputLabels',myLocalFSWF,'InputSpec.mask_file') #Yes, the same file as label_file!

        ### Now define where the final organized outputs should go.
        if RunAllFSComponents == True:
            baw200DataSink=pe.Node(nio.DataSink(),name="FREESURFER_DS")
            baw200DataSink.inputs.base_directory=ExperimentBaseDirectoryResults
            baw200DataSink.inputs.regexp_substitutions = [
                ('/_uid_(?P<myuid>[^/]*)',r'/\g<myuid>')
                ]
            baw200.connect(myLocalFSWF, 'OutputSpec.FreesurferOutputDirectory', baw200DataSink,'FREESURFER_SUBJ.@FreesurferOutputDirectory')
        ### Now define where the final organized outputs should go.
        FSPREP_DataSink=pe.Node(nio.DataSink(),name="FREESURFER_PREP")
        FSPREP_DataSink.inputs.base_directory=ExperimentBaseDirectoryResults
	FREESURFER_PREP_PATTERNS = GenerateOutputPattern(ExperimentDatabase,'FREESURFER_PREP')
        FSPREP_DataSink.inputs.regexp_substitutions = FREESURFER_PREP_PATTERNS
        print "========================="
        print "========================="
        print "========================="
        print FREESURFER_PREP_PATTERNS
        print "========================="
        print "========================="
        print "========================="
        baw200.connect(myLocalFSWF, 'OutputSpec.cnr_optimal_image', FSPREP_DataSink,'FREESURFER_PREP.@cnr_optimal_image')

    else:
        print "Skipping freesurfer"


    return baw200



#############
## The following are just notes, and not really part of this script.
##
        #baw200.connect(myLocalLMIWF, 'OutputSpec.outputLandmarksInACPCAlignedSpace', baw200DataSink,'foo.@outputLandmarksInACPCAlignedSpace')
        #baw200.connect(myLocalLMIWF, 'OutputSpec.outputResampledVolume', baw200DataSink,'foo.@outputResampledVolume')
        #baw200.connect(myLocalLMIWF, 'OutputSpec.outputLandmarksInInputSpace', baw200DataSink,'foo.@outputLandmarksInInputSpace')
        #baw200.connect(myLocalLMIWF, 'OutputSpec.outputTransform', baw200DataSink,'foo.@outputTransform')
        #baw200.connect(myLocalLMIWF, 'OutputSpec.outputMRML', baw200DataSink,'foo.@outputMRML')
"""
    subs=r'test/\g<project>/\g<subject>/\g<session>'
pe.sub(subs,test)
pat=r'foo/_uid_(?P<project>PHD_[0-9][0-9][0-9])_(?P<subject>[0-9][0-9][0-9][0-9])_(?P<session>[0-9][0-9][0-9][0-9][0-9])'
pe=re.compile(pat)
pe.sub(subs,test)
test
test='foo/_uid_PHD_024_0003_12345'
pe.sub(subs,test)
pat=r'(?P<modulename>[^/]*)/_uid_(?P<project>PHD_[0-9][0-9][0-9])_(?P<subject>[0-9][0-9][0-9][0-9])_(?P<session>[0-9][0-9][0-9][0-9][0-9])'
subs=r'test/\g<project>/\g<subject>/\g<session>/\g<modulename>'
pe.sub(subs,test)
pe=re.compile(pat)
pe.sub(subs,test)

    if 'PERSISTANCE_CHECK' in WORKFLOW_COMPONENTS:
        from WorkupT1T2PERSISTANCE_CHECK import CreatePERSISTANCE_CHECKWorkflow
        myLocalPERSISTANCE_CHECKWF= CreatePERSISTANCE_CHECKWorkflow("999999_PersistanceCheckingWorkflow")
        PERSISTANCE_CHECKWF.connect(SplitAvgBABC,'avgBABCT1',myLocalPERSISTANCE_CHECKWF,'fixedVolume')
        PERSISTANCE_CHECKWF.connect(myLocalTCWF,'OutputSpec.outputLabels',myLocalPERSISTANCE_CHECKWF,'fixedBinaryVolume')
        PERSISTANCE_CHECKWF.connect(BAtlas,'template_t1',myLocalPERSISTANCE_CHECKWF,'movingVolume')
        PERSISTANCE_CHECKWF.connect(BAtlas,'template_brain',myLocalPERSISTANCE_CHECKWF,'movingBinaryVolume')
        PERSISTANCE_CHECKWF.connect(myLocalLMIWF,'OutputSpec.atlasToSubjectTransform',myLocalPERSISTANCE_CHECKWF,'initialTransform')
"""
