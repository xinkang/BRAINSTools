# -*- coding: utf8 -*-
"""Autogenerated file - DO NOT EDIT
If you spot a bug, please report it on the mailing list and/or change the generator."""

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, SEMLikeCommandLine, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os


class AverageBrainGeneratorInputSpec(CommandLineInputSpec):
    inputDirectory = File(desc="Image To Warp", exists=True, argstr="--inputDirectory %s")
    templateVolume = File(desc="Reference image defining the output space", exists=True, argstr="--templateVolume %s")
    resolusion = traits.Str(desc="The resolusion.", argstr="--resolusion %s")
    iteration = traits.Str(desc="The iteration.", argstr="--iteration %s")
    pixelType = traits.Enum("uchar", "short", "ushort", "int", "uint", "float", desc="Specifies the pixel type for the input/output images", argstr="--pixelType %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Resulting deformed image", argstr="--outputVolume %s")


class AverageBrainGeneratorOutputSpec(TraitedSpec):
    outputVolume = File(desc="Resulting deformed image", exists=True)


class AverageBrainGenerator(SEMLikeCommandLine):
    """title: Average Brain Generator

category: Registration

description:
This programs creates synthesized average brain.


version: 0.1

documentation-url: http:://mri.radiology.uiowa.edu/mriwiki

license: NEED TO ADD

contributor: This tool was developed by Yongqiang Zhao.

"""

    input_spec = AverageBrainGeneratorInputSpec
    output_spec = AverageBrainGeneratorOutputSpec
    _cmd = " AverageBrainGenerator "
    _outputs_filenames = {'outputVolume': 'outputVolume'}
