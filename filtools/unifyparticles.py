import numpy as np
from math import isnan

from filtools import parse_star
from utils.plotfit import *

def unify_tilt(starfile_path, plot_changes = False, save_changes = True):
    '''
    Super basic function that resets all tilt angles such that they equal the
    median tilt angle
    '''

    filament_data = parse_star.readFilamentsFromStarFile(starfile_path)

    for filament_no in range(filament_data.number_of_filaments):

        original_tilt_angles = filament_data.getNumpyFilamentColumn(filament_no, 'rlnAngleTilt')
        tilt_median = np.full(len(original_tilt_angles), np.median(original_tilt_angles), dtype = 'float16')

        filament_data.addFilamentDataColumn(filament_no, tilt_median, 'rlnAngleTilt')

    filament_data.writeFilamentsToStarFile()


def reset_tilt(starfile_path, plot_changes = False, save_changes = True):
    '''
    Function to reset the tilt values for all particles to 90 degrees
    '''

    filament_data = parse_star.readFilamentsFromStarFile(starfile_path)

    for filament_no in range(filament_data.number_of_filaments):

        tilt_original = filament_data.getNumpyFilamentColumn(filament_no, 'rlnAngleTilt')

        reset_tilt = np.full(len(tilt_original), 90, dtype = 'float16')
        filament_data.addFilamentDataColumn(filament_no, reset_tilt, 'rlnAngleTilt')

    print('The tilt angles for all filaments have been fitted')

    filament_data.writeFilamentsToStarFile()

    if plot_changes:
        plot_changes()

def unify_rot(starfile_path, twist, rise = 4.75, apix = 1.05, plot_changes = False):
    '''
    Function that fits the rot angles for all filaments - VERY slow at the moment
    '''
    initial_gradient = twist/(rise/apix)

    filament_data = parse_star.readFilamentsFromStarFile(starfile_path)
    #print('Filaments with less than 5 particles will be removed')
    #filament_data.removeShortFilaments(5)
    print('There are %s filaments to process' % filament_data.number_of_filaments)

    m_list = np.linspace((initial_gradient - (initial_gradient/2)), (initial_gradient+(initial_gradient/2)), 40)

    #np_lin_reg = np.vectorize(linearRegression, otypes = [float])

    for filament_no in range(filament_data.number_of_filaments):

        rot_angles = filament_data.getNumpyFilamentColumn(filament_no, 'rlnAngleRot')
        rln_score = filament_data.getNumpyFilamentColumn(filament_no, 'rlnMaxValueProbDistribution')
        tracklength = filament_data.getNumpyFilamentColumn(filament_no, 'rlnHelicalTrackLengthAngst')
        psi_angles = filament_data.getNumpyFilamentColumn(filament_no, 'rlnAnglePsi')
        xsh = filament_data.getNumpyFilamentColumn(filament_no, 'rlnOriginXAngst')
        ysh = filament_data.getNumpyFilamentColumn(filament_no, 'rlnOriginYAngst')

        #This makes everything take ages but is necessary
        number_of_particles = len(ysh)
        search_limit = number_of_particles*(tracklength[1]*0.1*2)

        #find the best linear plot with a gradient of 4 by changing the y-intercept
        search_limit = number_of_particles*(tracklength[1]*0.1*2)
        y_intercepts = np.arange((-180 - search_limit),(180 + search_limit),0.1)
        #Exhaustive search for gradient 4 and -4:
        pos_m4_search = exhaustiveLinearSearch(initial_gradient, y_intercepts, tracklength, rot_angles, rln_score, 4)
        neg_m4_search = exhaustiveLinearSearch(-initial_gradient, y_intercepts, tracklength, rot_angles, rln_score, 4)

        top_scored_plots = np.concatenate((pos_m4_search[-20:], neg_m4_search[-20:]))
        top_y_intercepts = np.hsplit(top_scored_plots,2)[0]

        best_plot = optimiseLinearGradient(m_list,top_y_intercepts, tracklength, rot_angles, rln_score, 4)

        best_gradient = best_plot[0]
        y_intercept = best_plot[1]

        line_of_best_fit = linRegress(tracklength,y_intercept,best_gradient)

        adjusted_rot_angles = adjustAngletoLOBF(line_of_best_fit, rot_angles, 4)

        filament_data.addFilamentDataColumn(filament_no, adjusted_rot_angles, 'rlnAngleRot')

        if filament_no % 100 == 0:
            print('Tube %s completed' % (filament_no))

    filament_data.writeFilamentsToStarFile()

def unifyXY(starfile_path, plot_changes = False, rot_outliers = []):
    '''
    Fairly basic function to fit the x and y shifts using a polynomial

    Need to implement selective changes i.e. only changing particles that are
    outliers
    '''

    filament_data = parse_star.readFilamentsFromStarFile(starfile_path)

    for filament_no in range(filament_data.number_of_filaments):

        xsh = filament_data.getNumpyFilamentColumn(filament_no, 'rlnOriginXAngst')
        ysh = filament_data.getNumpyFilamentColumn(filament_no, 'rlnOriginYAngst')
        tracklength = filament_data.getNumpyFilamentColumn(filament_no, 'rlnHelicalTrackLengthAngst')

        if len(rot_outliers) > 1:
            #Do the selective changes
            pass
        else:
            uniX, uniY = fitPolynomial(Xsh,Ysh,xax)

        #Checks if the "flatten and cluster" function failed - in which case the shifts are all 'nan'
        if math.isnan(uniX[1]):
            uniX = Xsh
        if math.isnan(uniY[1]):
            uniY = Ysh

        filament_data.addFilamentDataColumn(filament_no, uniX, 'rlnOriginXAngst')
        filament_data.addFilamentDataColumn(filament_no, uniY, 'rlnOriginYAngst')

    filament_data.writeFilamentsToStarFile()


def unify_psi(starfile_path, plot_changes = False):

    filament_data = parse_star.readFilamentsFromStarFile(starfile_path)

    for filament_no in range(filament_data.number_of_filaments):

        psi_original = filament_data.getNumpyFilamentColumn(filament_no, 'rlnAnglePsi')
        relion_score = filament_data.getNumpyFilamentColumn(filament_no, 'rlnMaxValueProbDistribution')
        tracklength = filament_data.getNumpyFilamentColumn(filament_no, 'rlnHelicalTrackLengthAngst')

        psi_low_bound = int(sorted(psi_original)[0])
        psi_high_bound = int(sorted(psi_original)[-1])
        psi_low_bound_search = np.arange(psi_low_bound - 8, psi_low_bound + 8, 0.5)
        psi_high_bound_search = np.arange(psi_high_bound - 8, psi_high_bound + 8, 0.5)
        y_intercepts = np.concatenate((psi_low_bound_search, psi_high_bound_search))

        sorted_plots = exhaustiveLinearSearch(0, y_intercepts, tracklength, psi_original, relion_score, 5)

        best_plot = sorted_plots[-1]
        #line_of_best_fit = linRegress(tracklength, np.full(len(tracklength),best_plot[0]),np.full(len(tracklength),0))
        line_of_best_fit = linRegress(tracklength, best_plot[0],0)
        unified_psi_angles = adjustAngletoLOBF(line_of_best_fit, psi_original, 5)

        filament_data.addFilamentDataColumn(filament_no, unified_psi_angles, 'rlnAnglePsi')

    filament_data.writeFilamentsToStarFile()

def removeShortFilsFromStarfile(starfile_path, minimum_length):

    print('Removing short filaments from %s' % starfile_path)

    filament_data = parse_star.readFilamentsFromStarFile(starfile_path)

    '''Remove filaments with less than specified number of particles '''
    print('There are %i filaments in the input star file' % filament_data.number_of_filaments)

    for fil_no in range(filament_data.number_of_filaments):
        #This is just to ensure that the starfile name is correctly updated and data structure is maintained
        filament_data.addFilamentDataColumn(fil_no, filament_data.getNumpyFilamentColumn(fil_no,'rlnAngleRot'), 'noShortFilaments')

        if len(filament_data.getNumpyFilamentColumn(fil_no, 'rlnAngleRot')) < minimum_length:
            del filament_data.filaments[fil_no]

    #remake the filaments dictionary with sequential keys
    temp_filaments = {}
    filament_data.number_of_filaments = 0
    for num, key in enumerate(sorted(filament_data.filaments.keys())):
        temp_filaments[num] = filament_data.filaments[key]
        filament_data.number_of_filaments += 1

    filament_data.filaments = temp_filaments

    print('There are %i filaments in the saved star file' % filament_data.number_of_filaments)

    filament_data.writeFilamentsToStarFile(suffix = '_noShortFils')

def removeShortFilsFromObject(filament_object, minimum_length):

    '''Remove filaments with less than specified number of particles '''

    print('There are %i filaments in the input star file' % filament_object.number_of_filaments)

    for fil_no in range(filament_object.number_of_filaments):
        #This is just to ensure that the starfile name is correctly updated and data structure is maintained
        filament_object.addFilamentDataColumn(fil_no, filament_object.getNumpyFilamentColumn(fil_no,'rlnAngleRot'), 'noShortFilaments')

        if len(filament_object.getNumpyFilamentColumn(fil_no, 'rlnAngleRot')) < minimum_length:
            del filament_object.filaments[fil_no]

    #remake the filaments dictionary with sequential keys
    temp_filaments = {}
    filament_object.number_of_filaments = 0
    for num, key in enumerate(sorted(filament_object.filaments.keys())):
        temp_filaments[num] = filament_object.filaments[key]
        filament_object.number_of_filaments += 1

    filament_object.filaments = temp_filaments

    if verbose:
        print('There are %i filaments in the saved star file' % filament_object.number_of_filaments)


def selectParticlesbyAlignmentAngleRange(starfile_path, rln_header_identifier, lower_limit, upper_limit):

    particle_data = parse_star.readBlockDataFromStarfile(starfile_path)

    particle_data.selectAngularRange(rln_header_identifier, lower_limit, upper_limit)
    particle_data.writeBlockDatatoStar()

def orderFilaments(starfile):
    fil_data = parse_star.readFilamentsFromStarFile(starfile)
    fil_data.writeFilamentsToStarFile()

def removeDuplicates(starfile):

    fil_data = parse_star.readFilamentsFromStarFile(starfile)
    starting_particles = fil_data.number_of_particles

    for fil_no in sorted(fil_data.filaments.keys()):
        fil_data.removeFilamentDuplicateParticles(fil_no)

        '''
        hel_track_lengths = fil_data.getHelicalTrackLengthList(fil_no)
        number_of_duplicates = len(hel_track_lengths) - len(set(hel_track_lengths))

        if number_of_duplicates > 0:
            for duplicate in range(number_of_duplicates):
                for i, track_length in enumerate(hel_track_lengths):
                    try:
                        duplicate_position = hel_track_lengths.index(track_length, i+1)
                        hel_track_lengths.pop(i)
                        fil_data.removeParticleData(fil_no, i)
                        break
                    except ValueError:
                        continue
        '''
    print('%i duplicate particles were removed from the starfile' % (starting_particles - fil_data.number_of_particles))
    fil_data.writeFilamentsToStarFile(suffix = '_duplicates_removed')

def mergeStarFiles(starfile1, starfile2):

    starfile1_obj = parse_star.readFilamentsFromStarFile(starfile1)
    starfile2_obj = parse_star.readFilamentsFromStarFile(starfile2)

    combined_number_of_particles = starfile1_obj.number_of_particles + starfile2_obj.number_of_particles
    combined_number_of_filaments = starfile1_obj.number_of_filaments + starfile2_obj.number_of_filaments

    print('There are %i number of particles in %i filaments from starfile %s' % (starfile1_obj.number_of_particles, starfile1_obj.number_of_filaments, starfile1))
    print('There are %i number of particles in %i filaments from starfile %s' % (starfile2_obj.number_of_particles, starfile2_obj.number_of_filaments, starfile2))

    for fil_no in range(starfile2_obj.number_of_filaments):
        starfile1_obj.addNewFilamentFromOtherStar(starfile2_obj, fil_no)

    no_of_particles_before_dupremove = starfile1_obj.number_of_particles
    for fil_no in sorted(starfile1_obj.filaments.keys()):
        starfile1_obj.removeFilamentDuplicateParticles(fil_no)
    no_of_particles_after_dupremove = starfile1_obj.number_of_particles

    print('There are %i particles from %i filaments in the new starfile' % (starfile1_obj.number_of_particles, starfile1_obj.number_of_filaments))
    if no_of_particles_before_dupremove - no_of_particles_after_dupremove != 0:
        print('%i duplicate particles were removed from the merged starfile' % (no_of_particles_before_dupremove - no_of_particles_after_dupremove))
    else:
        print('No duplicate particles detected in new combined starfile')

    try:
        starfile_2_job_name = starfile2.split('/')[-2]
    except IndexError: #directory layout doesn't follow the RELION format
        starfile_2_job_name = ''

    starfile1_obj.writeFilamentsToStarFile(suffix = '_merged' + starfile_2_job_name)

def correctExpandedParticles(expanded_starfile, reference_starfile):

    reference_star_object = parse_star.readFilamentsFromStarFile(reference_starfile)
    expanded_star = parse_star.readFilamentsFromStarFile(expanded_starfile)

    expansion_factor = expanded_star.number_of_particles/reference_star_object.number_of_particles

    expansion_factor = int(expansion_factor)

    print('There are %i particles from %i filaments in the expanded starfile' % (expanded_star.number_of_particles, expanded_star.number_of_filaments))
    print('There are %i particles from %i filaments in the reference starfile' % (reference_star_object.number_of_particles, reference_star_object.number_of_filaments))
    print('The particles have been expanded by a factor of %i' % (int(expansion_factor)))

    for fil_no in range(expanded_star.number_of_filaments):
        expanded_star.fixExpansionOneFilament(fil_no, reference_star_object, expansion_factor)

    #remove the remaining non-fixed fils
    expanded_star.removeMultipleFilaments([i for i in range(reference_star_object.number_of_filaments)])
    #for fil_no in range(reference_star_object.number_of_filaments):
    #    expanded_star.removeFilament(fil_no)

    print('There are %i particles from %i filaments in the expanded starfile' % (expanded_star.number_of_particles, expanded_star.number_of_filaments))

    expanded_star.writeFilamentsToStarFile(suffix = '_unexpanded')

def updateAlignments(star1, star2, subtracted=True):
    """
    Function to update the angles/translations from starfile1 using the
    angles from starfile 2

    Currently very naive - assumes that particles are in identical sequence in
    both starfiles. This could obviously lead to bugs and will fix at some point
    """
    number_of_skipped_particles = 0

    star1_data = parse_star.readBlockDataFromStarfile(star1, index_particles = True)
    star2_data = parse_star.readBlockDataFromStarfile(star2, index_particles = True)

    if star1_data.number_of_particles != star2_data.number_of_particles:
        raise InputError('Two starfiles do not have the same number of particles')

    for p_no in range(star1_data.number_of_particles):
        ps1_micname = star1_data.getParticleMicrograph(p_no)
        if subtracted:
            ps1_imagename = star1_data.getParticleValue(p_no, 'rlnImageOriginalName')
        else:
            ps1_imagename = star1_data.getParticleImageName(p_no)

        try:
            p_no_s2 = star2_data.getParticleNumber(ps1_micname, ps1_imagename)
        except KeyError:
            number_of_skipped_particles +=1
            continue

        new_rot = star2_data.getParticleValue(p_no_s2, 'rlnAngleRot')
        star1_data.setParticleValue(p_no, 'rlnAngleRot', new_rot)

        new_psi = star2_data.getParticleValue(p_no_s2, 'rlnAnglePsi')
        star1_data.setParticleValue(p_no, 'rlnAnglePsi', new_psi)

        new_tilt = star2_data.getParticleValue(p_no_s2, 'rlnAngleTilt')
        star1_data.setParticleValue(p_no, 'rlnAngleTilt', new_tilt)

        new_xtrans = star2_data.getParticleValue(p_no_s2, 'rlnOriginXAngst')
        star1_data.setParticleValue(p_no, 'rlnOriginXAngst', new_xtrans)

        new_ytrans = star2_data.getParticleValue(p_no_s2, 'rlnOriginYAngst')
        star1_data.setParticleValue(p_no, 'rlnOriginYAngst', new_ytrans)

    if number_of_skipped_particles > 0:
        print('There were %i particles that could not be found in the updating star file %s' %(number_of_skipped_particles, star2))

    star1_data.writeBlockDatatoStar(
                                    save_updated_data=True,
                                    suffix='_updatedAlignments'
                                    )

def updateCTF(star1, star2, subtracted=True):
    """
    Function to update the angles/translations from starfile1 using the
    angles from starfile 2

    Currently very naive - assumes that particles are in identical sequence in
    both starfiles. This could obviously lead to bugs and will fix at some point
    """
    number_of_skipped_particles = 0

    star1_data = parse_star.readBlockDataFromStarfile(star1, index_particles = True)
    star2_data = parse_star.readBlockDataFromStarfile(star2, index_particles = True)

    if star1_data.number_of_particles != star2_data.number_of_particles:
        raise InputError('Two starfiles do not have the same number of particles')

    for p_no in range(star1_data.number_of_particles):
        ps1_micname = star1_data.getParticleMicrograph(p_no)
        if subtracted:
            ps1_imagename = star1_data.getParticleValue(p_no, 'rlnImageOriginalName')
        else:
            ps1_imagename = star1_data.getParticleImageName(p_no)

        try:
            p_no_s2 = star2_data.getParticleNumber(ps1_micname, ps1_imagename)
        except KeyError:
            number_of_skipped_particles +=1
            continue

        new_defu = star2_data.getParticleValue(p_no_s2, 'rlnDefocusU')
        star1_data.setParticleValue(p_no, 'rlnDefocusU', new_defu)

        new_defv = star2_data.getParticleValue(p_no_s2, 'rlnDefocusV')
        star1_data.setParticleValue(p_no, 'rlnDefocusV', new_defv)

        new_def_ang = star2_data.getParticleValue(p_no_s2, 'rlnDefocusAngle')
        star1_data.setParticleValue(p_no, 'rlnDefocusAngle', new_def_ang)

        new_ctfB = star2_data.getParticleValue(p_no_s2, 'rlnCtfBfactor')
        star1_data.setParticleValue(p_no, 'rlnCtfBfactor', new_ctfB)

        new_ctf_scale = star2_data.getParticleValue(p_no_s2, 'rlnCtfScalefactor')
        star1_data.setParticleValue(p_no, 'rlnCtfScalefactor', new_ctf_scale)

    if number_of_skipped_particles > 0:
        print('There were %i particles that could not be found in the updating star file %s' %(number_of_skipped_particles, star2))

    star1_data.writeBlockDatatoStar(
                                    save_updated_data=True,
                                    suffix='_updatedCTF'
                                    )
