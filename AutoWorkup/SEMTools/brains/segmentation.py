# -*- coding: utf8 -*-
"""Autogenerated file - DO NOT EDIT
If you spot a bug, please report it on the mailing list and/or change the generator."""

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, SEMLikeCommandLine, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os


class SimilarityIndexInputSpec(CommandLineInputSpec):
    outputCSVFilename = File(desc="output CSV Filename", exists=True, argstr="--outputCSVFilename %s")
    ANNContinuousVolume = File(desc="ANN Continuous volume to be compared to the manual volume", exists=True, argstr="--ANNContinuousVolume %s")
    inputManualVolume = File(desc="input manual(reference) volume", exists=True, argstr="--inputManualVolume %s")
    thresholdInterval = traits.Float(desc="Threshold interval to compute similarity index between zero and one", argstr="--thresholdInterval %f")


class SimilarityIndexOutputSpec(TraitedSpec):
    pass


class SimilarityIndex(SEMLikeCommandLine):
    """title: BRAINSCut:SimilarityIndexComputation

category: BRAINS.Segmentation

description: Automatic analysis of BRAINSCut Output

version:  1.0

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: Eunyoung Regin Kim

"""

    input_spec = SimilarityIndexInputSpec
    output_spec = SimilarityIndexOutputSpec
    _cmd = " SimilarityIndex "
    _outputs_filenames = {}
