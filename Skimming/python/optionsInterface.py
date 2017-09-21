"""
Simple, somewhat more Pythonic interface to FWCore.ParameterSet.VarParsing.

Allows defining CMSSW options using native Python types instead of the
clunky `VarParsing.varType` types...


Usage example:

# -- begin example --
from Kappa.Skimming.optionsInterface import options, register_option

register_option('myFancyOption',
                default=False,
                type_=bool,   # use native Python type directly instead of VarParsing type
                description="True if fancy option is enabled, False if it is not (default: False)")

# add all other options here...

options.parseArguments()
# -- end example --

The options can then be accessed as normal attributes of the
global/module variable `options`:

options.myFancyOption
"""

from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('python')

# map Python types to VarParsing types
_VPTypes = {
    str  : VarParsing.varType.string,
    int  : VarParsing.varType.int,
    bool : VarParsing.varType.bool
}

def register_option(name, default, type_, description, multiplicity='singleton'):
    global options
    _vp_type = _VPTypes.get(type_, None)
    if _vp_type is None:
        raise Exception("Cannot register option with Python type '{}': "
                        "no corresponding type defined in "
                        "'FWCore.ParameterSet.VarParsing.varType'".format(type_))
    if multiplicity == 'list':
        _vp_mult = VarParsing.multiplicity.list
    elif multiplicity == 'singleton':
        _vp_mult = VarParsing.multiplicity.singleton
    else:
        raise ValueError("Unknown option multiplicity '{}': "
                         "possible values are 'singleton' "
                         "and 'list'.".format(multiplicity))
    options.register(name,
                     default,
                     _vp_mult,
                     _vp_type,
                     description)
