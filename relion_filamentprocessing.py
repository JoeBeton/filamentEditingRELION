import numpy as np
import os
import argparse

from filtools import(
            unifyparticles,
            plotparticles,
            get_helixinimodel2d_angles,
            )
#from utils import csparc_ctf

parser = argparse.ArgumentParser()

parser.add_argument('--input', '--i', nargs = '+', help = 'Input star file(s)')

parser.add_argument('--unify_tilt', '--tilt', action = 'store_true', help = 'Unify the tilt values for filaments')
parser.add_argument('--unify_rot', '--rot', type = float, help = 'Unify the rot values for filaments')
parser.add_argument('--unify_psi', '--psi', action = 'store_true', help = 'Unify the psi values for filaments')

parser.add_argument('--select_angles', '--sel', nargs = 3, metavar = '[Starfile Header] [Lower limit] [Upper limit]', help = 'Function to select particles with alignment angles that fall within the specified range')
parser.add_argument('--order_filaments', '--order', action = 'store_true', help = 'Save stafile with filaments ordered')
parser.add_argument('--remove_duplicates', action = 'store_true', help = 'Remove duplicate particles from starfiles')

parser.add_argument('--reset_tilt', action = 'store_true', help = 'Option to fit the tilt values for each filament')
parser.add_argument('--remove_shortfils', type = int, help = 'Option to remove the particles from filaments shorter than the stated value')

parser.add_argument('--make_superparticles', type = int, metavar = '*Specify windowing range*', help = 'Option to generate superparticles')

parser.add_argument('--plot_changes', action = 'store_true', help = 'Option to save pdf plots showing the old and updated angles for each filament')
parser.add_argument('--plot_pdf', '--p', action = 'store_true', help = 'Plot the particle data from filaments into a pdf file')
parser.add_argument('--plot_fillenhist', action = 'store_true', help = 'Plot a histogram of the filament lengths')
parser.add_argument('--compare_starfiles', action = 'store_true', help = 'Plot a histogram of the filament lengths')
parser.add_argument('--merge_stars', action = 'store_true',help = 'Merge 2 starfiles keeping the two sets of filaments seperate')
parser.add_argument('--fix_expanded_particles', nargs = 1, type = str, help = 'Merge 2 starfiles keeping the two sets of filaments seperate')

parser.add_argument('--get_helixinimodel2d_angles', nargs = 1, help = '[angpix] Specialised function for me')
parser.add_argument('--update_angles', nargs = 1, help = 'Specialised function for me')
parser.add_argument('--update_ctf', nargs = 1, help = 'Specialised function for me')
parser.add_argument('--update_csparc_ctf', action = 'store_true', help = '[angpix] Specialised function for me')

args=parser.parse_args()


do_plots = args.plot_changes

if args.reset_tilt:
    for starfile in args.input:
        unifyparticles.reset_tilt(starfile, do_plots)

if args.remove_shortfils:
    for starfile in args.input:
        unifyparticles.removeShortFilsFromStarfile(starfile, args.remove_shortfils)

if args.select_angles:
    for starfile in args.input:
        unifyparticles.selectParticlesbyAlignmentAngleRange(starfile, args.select_angles[0], int(args.select_angles[1]), int(args.select_angles[2]))

if args.unify_tilt:
    for starfile in args.input:
        unifyparticles.unify_tilt(starfile, do_plots)

if args.unify_rot:
    for starfile in args.input:
        unifyparticles.unify_rot(starfile, args.unify_rot, plot_changes = do_plots)

if args.unify_psi:
    for starfile in args.input:
        unifyparticles.unify_psi(starfile, do_plots)

if args.order_filaments:
    for starfile in args.input:
        unifyparticles.orderFilaments(starfile)

if args.remove_duplicates:
    for starfile in args.input:
        unifyparticles.removeDuplicates(starfile)

if args.make_superparticles:
    from filtools import superparticles
    for starfile in args.input:
        superparticles.make_superparticles(starfile, args.make_superparticles)

if args.merge_stars:
    if len(args.input) != 2:
        quit('Please provide two starfiles for this function')

    unifyparticles.mergeStarFiles(args.input[0], args.input[1])

if args.fix_expanded_particles:
    if len(args.input) != 1:
        raise AttributeError('This function requires a particle expanded starfile as input, please provide one e.g. --i path/to/expanded/starfile.star')
    if len(args.fix_expanded_particles) != 1:
        raise AttributeError('Please provide a reference starfile using the --fix_expanded_particles option e.g. --fix_expanded_particles path/to/starfile.star')

    unifyparticles.correctExpandedParticles(args.input[0], args.fix_expanded_particles[0])

if args.update_angles:
    if args.subtracted:
        unifyparticles.updateAlignments(args.input[0], args.update_angles[0], subtracted=True)
    else:
        unifyparticles.updateAlignments(args.input[0], args.update_angles[0], subtracted=False)

if args.update_ctf:
    if args.subtracted:
        unifyparticles.updateCTF(args.input[0], args.update_angles[0], subtracted=True)
    else:
        unifyparticles.updateCTF(args.input[0], args.update_angles[0], subtracted=False)


#if args.update_csparc_ctf:
#    for starfile in args.input:
#        csparc_ctf.readCsparcCTF(starfile)

if args.plot_pdf:
    for starfile in args.input:
        plotparticles.plot_filament_pdf(starfile)
if args.plot_fillenhist:
    for starfile in args.input:
        plotparticles.plotFilamentLengthHistogram(starfile)
if args.compare_starfiles:
    if len(args.input) != 2:
        quit('Please provide two starfiles for this function')
    else:
        plotparticles.compareFilamentNumbers(args.input[0], args.input[1])

if args.get_helixinimodel2d_angles:
    if len(args.input) != 2:
        quit('Please provide two starfiles for this function')
    else:
        get_helixinimodel2d_angles.getAngles(args.input[0], args.input[1], args.get_helixinimodel2d_angles[0])
