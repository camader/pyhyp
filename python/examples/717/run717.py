# Parameter to determine if morphed winglet surface is used.
USE_WINGLET = True

from pyhyp import pyHyp
if USE_WINGLET:
    from pygeo import pyBlock, DVGeometry
    from pyspline import pySpline
    import numpy

ffd_file = 'mdo_tutorial_ffd.fmt'
fileName = '717_small.fmt'

options= {

    # ---------------------------
    #        Input Parameters
    # ---------------------------
    'inputFile':fileName,
    'unattachedEdgesAreSymmetry':True,
    'outerFaceBC':'farField',
    'autoConnect':True,
    'BC':{},
    'families':'wall',

    # ---------------------------
    #        Grid Parameters
    # ---------------------------
    'N': 81,
    's0':5e-6,
    'marchDist':325,

    # ---------------------------
    #   Pseudo Grid Parameters
    # ---------------------------
    'ps0':-1,
    'pGridRatio':-1,
    'cMax':4,

    # ---------------------------
    #   Smoothing parameters
    # ---------------------------
    'epsE': 3.0,
    'epsI': 6.0,
    'theta': 3.0,
    'volCoef': .25,
    'volBlend': 0.0005,
    'volSmoothIter': 250,
}

# Create the hyp object
hyp = pyHyp(options=options)

if USE_WINGLET:
    def winglet(val, geo):
        # Move the last point on ref axis:
        C = geo.extractCoef('wing')
        s = geo.extractS('wing')

        C[-1,0] += val[0]
        C[-1,1] += val[1]
        C[-1,2] += val[2]

        # Also need to get "dihedreal" angle for this section
        theta = numpy.arctan(val[1]/(C[-1,2] - C[-2,2]))
        geo.rot_x['wing'].coef[-1] = -theta*180/numpy.pi
        geo.restoreCoef(C, 'wing')

        # Set the chord as well
        geo.scale['wing'].coef[-1] = val[3]

    coords = hyp.getSurfaceCoordinates()
    DVGeo = DVGeometry(ffd_file)
    coef = DVGeo.FFD.vols[0].coef.copy()

    # First determine the reference chord lengths:
    nSpan = coef.shape[2]
    ref = numpy.zeros((nSpan,3))

    for k in xrange(nSpan):
        max_x = numpy.max(coef[:,:,k,0])
        min_x = numpy.min(coef[:,:,k,0])

        ref[k,0] = min_x + 0.25*(max_x-min_x)
        ref[k,1] = numpy.average(coef[:,:,k,1])
        ref[k,2] = numpy.average(coef[:,:,k,2])

    c0 = pySpline.Curve(X=ref,k=2)
    DVGeo.addRefAxis('wing', c0)
    DVGeo.addGeoDVGlobal('winglet',[0,0,0,1], winglet, lower=-5, upper=5)
    DVGeo.addPointSet(coords, 'coords')
    DVGeo.setDesignVars({'winglet': [1.5,2.5,-2.0,.60]})
    hyp.setSurfaceCoordinates( DVGeo.update('coords'))

# Run and write grid
hyp.run()
hyp.writeCGNS('717.cgns')
