The files contained in this directory are derived from the "NAC Brain Atlas" (see refrence
copied to the bottom of this README).

Here is a description of the files located in this directory:

### ACPC aligned version of the original NAC images
ReferenceAtlas_20110511/template_t1.nii.gz
ReferenceAtlas_20110511/template_t2.nii.gz

##  Automatically generated landmarks from BRAINSConstellationDetector
ReferenceAtlas_20110511/template_landmarks.fcsv

### A tissue classified image in the BRAINS2 continuous labeling system
ReferenceAtlas_20110511/template_class.nii.gz

### The average of ~700 subject scans to the template_t1.nii.gz/template_t2.nii.gz
### using BRAINSFit with BSpline warping, and then average them all together
ReferenceAtlas_20110511/avg_t1.nii.gz
ReferenceAtlas_20110511/avg_t2.nii.gz

### Binary images for defining regions of interest
-- A brain mask
ReferenceAtlas_20110511/template_brain.nii.gz
-- Region where vetricles are, but not necessarily the ventricles
ReferenceAtlas_20110511/template_ventricles.nii.gz
-- The left/right hemisphere of the IMAGE.  It devides the head & background regions into left/right hemispheres
ReferenceAtlas_20110511/template_rightHemisphere.nii.gz
ReferenceAtlas_20110511/template_leftHemisphere.nii.gz
-- The area where the cerebellum can be found, including the back of the neck and background outside the posterior of head
ReferenceAtlas_20110511/template_cerebellum.nii.gz
-- A gross mask that includes the entire head, but a consistent amount of background.
ReferenceAtlas_20110511/template_headregion.nii.gz

### Prior probility distributions for tissues types (Used in BRAINSABC), Generated from ~700 tissue classified images
-- AIR/Backgorund
ReferenceAtlas_20110511/ALLPVAIR.nii.gz
-- Basal tissue regions that are not csf or only white matter (putamen/caudate/thalmus/etc)
ReferenceAtlas_20110511/ALLPVBASALTISSUE.nii.gz
-- Cerebellar grey matter
ReferenceAtlas_20110511/ALLPVCRBLGM.nii.gz
-- Cerebellar white matter
ReferenceAtlas_20110511/ALLPVCRBLWM.nii.gz
-- Intracranial CSF
ReferenceAtlas_20110511/ALLPVCSF.nii.gz
-- Intracranial surface grey matter
ReferenceAtlas_20110511/ALLPVSURFGM.nii.gz
-- Intracranial venous blood
ReferenceAtlas_20110511/ALLPVVB.nii.gz
-- Intracranial white matter
ReferenceAtlas_20110511/ALLPVWM.nii.gz
-- Extra cranial CSF (eyes or CSF like contrast)
ReferenceAtlas_20110511/ALLPVNOTCSF.nii.gz
-- Extra cranial tissue that looks like grey matter
ReferenceAtlas_20110511/ALLPVNOTGM.nii.gz
-- Extra cranial tissue that looks like Venous blood
ReferenceAtlas_20110511/ALLPVNOTVB.nii.gz
-- Extra cranial tissue that looks like white matter
ReferenceAtlas_20110511/ALLPVNOTWM.nii.gz

## Label Maps for different purposes
-- Tissue label map automatically generated from BRAINSABC
ReferenceAtlas_20110511/template_ABC_lables.nii.gz
-- Demons Warp Mori white matter atlas onto NAC
ReferenceAtlas_20110511/template_WMPM2_labels.nii.gz
ReferenceAtlas_20110511/template_WMPM2_labels.txt
-- ACPC aligned nac labels
ReferenceAtlas_20110511/template_nac_lables.nii.gz
ReferenceAtlas_20110511/template_nac_lables.txt


## Atlas definition file for BRAINSABC
ReferenceAtlas_20110511/AtlasPVDefinition.xml.in

## CMake Helper file for inclusion in exteranl packages with External_add commands from CMake
ReferenceAtlas_20110511/CMakeLists.txt

Neuroimage Analysis Center
Computational Clinical Anatomy Core
Surgical Planning Lab, Brigham and Women's Hospital Boston
NIH/NCRR grant number P41 RR013218


NAC Brain Atlas

This directory contains the data files for the NAC brain atlas.  The
atlas consists of MRI data from a healthy subject. The current data
set includes the following elements:

* MPRAGE and T2-weighted MRI acquisitions at 0.75mm isotropic resolution,
* downsampled versions of the same scan volumes at 1mm isotropic resolution,
* per-voxel labels for structures found in the 1mm volumes,
* polygonal models of the brain structures,
* a color file mapping structure voxel value to RadLex ontology-derived name and color,
* MRML scene files to visualize the atlas in 3D Slicer version 3.6 or higher.

We will continue to refine this data and add new modalities and scans to it.

LICENSE:

Distribution and use of this atlas data is covered under terms of the 3D Slicer License, Part B:
http://www.slicer.org/pages/LicenseText

