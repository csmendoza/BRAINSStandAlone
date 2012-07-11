project(ReferenceAtlas)
cmake_minimum_required(VERSION 2.8.5)

#-----------------------------------------------------------------------
# Setup locations to find externally maintained test data.
#-----------------------------------------------------------------------
list(APPEND ExternalData_URL_TEMPLATES
  # Local data store populated by the ITK pre-commit hook
  "file:///${${PROJECT_NAME}_SOURCE_DIR}/.ExternalData/%(algo)/%(hash)"
  # Data published by Iowa Psychiatry web interface
  "http://www.psychiatry.uiowa.edu/users/brainstestdata/ctestdata/%(algo)/%(hash)"
  # Data published by MIDAS
  "http://midas.kitware.com/api/rest/midas.bitstream.by.hash?hash=%(hash)&algorithm=%(algo)"
  # Data published by developers using git-gerrit-push.
  "http://www.itk.org/files/ExternalData/%(algo)/%(hash)"
)

# Tell ExternalData commands to transform raw files to content links.
set(ExternalData_LINK_CONTENT MD5)
set(ExternalData_SOURCE_ROOT ${${PROJECT_NAME}_SOURCE_DIR})
include(ExternalData)


## ReferenceAtlas_XML_DIR defined from calling environment

# Define the atlas subdirectory in one place
set(ATLAS_NAME Atlas/Atlas_${ATLAS_VERSION})
set(ATLAS_DIRECTORY ${CMAKE_INSTALL_PREFIX}/bin/${ATLAS_NAME})
set(ATLAS_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR})

#
# In order to test need an XML file
configure_file(${ATLAS_SOURCE_DIR}/AtlasPVDefinition.xml.in ${ATLAS_DIRECTORY}/AtlasPVDefinition.xml @ONLY IMMEDIATE)
file(COPY ${ATLAS_SOURCE_DIR}/AtlasPVDefinition.xml.in DESTINATION ${ATLAS_DIRECTORY}/ USE_SOURCE_PERMISSIONS)
install( FILES  ${ATLAS_DIRECTORY}/AtlasPVDefinition.xml DESTINATION bin/${ATLAS_NAME} )

macro(process_md5s md5_list DESTINATION_PATH)
  set(all_images "")
  foreach(CURRFILE_MD5 ${md5_list})
    get_filename_component(pathn  ${CURRFILE_MD5} PATH)
    get_filename_component(filenmd5 ${CURRFILE_MD5} NAME)
    string(REPLACE ".md5" "" filen ${filenmd5})
    ExternalData_expand_arguments(${PROJECT_NAME}FetchData CURRFILE DATA{${pathn}/${filen}})
    #file(COPY ${CURRFILE} DESTINATION ${DESTINATION_PATH}/ USE_SOURCE_PERMISSIONS)
    list(APPEND all_images ${CURRFILE})
  endforeach()
  message(STATUS "#### ${all_images}")
install(FILES ${all_images} DESTINATION bin/${ATLAS_NAME})

endmacro()


message(STATUS " ---- ${ATLAS_SOURCE_DIR}")
file(GLOB AtlasImageFiles "${ATLAS_SOURCE_DIR}/*.nii.gz.md5")
message(STATUS " ---- ${AtlasImageFiles}")
process_md5s("${AtlasImageFiles}" "${ATLAS_DIRECTORY}")

if ( 0 )
file(GLOB AtlasColorLookupTableFiles "${ATLAS_SOURCE_DIR}/*.txt.md5")
foreach(LUTS_MD5 ${AtlasColorLookupTableFiles})
  get_filename_component(lut ${LUTS_MD5} NAME_WE)
  ExternalData_expand_arguments(${PROJECT_NAME}FetchData LUTS DATA{${LUTS}})
  file(COPY ${LUTS} DESTINATION ${ATLAS_DIRECTORY}/ USE_SOURCE_PERMISSIONS)
endforeach()
install( FILES ${AtlasColorLookupTableFiles} DESTINATION bin/${ATLAS_NAME} )

file(GLOB AtlasColorLookupTableFiles "${ATLAS_SOURCE_DIR}/*.fcsv.md5")
foreach(LUTS_MD5 ${AtlasColorLookupTableFiles})
  get_filename_component(lut ${LUTS_MD5} NAME_WE)
  ExternalData_expand_arguments(${PROJECT_NAME}FetchData LUTS DATA{${LUTS}})
  file(COPY ${LUTS} DESTINATION ${ATLAS_DIRECTORY}/ USE_SOURCE_PERMISSIONS)
endforeach()
install( FILES ${AtlasColorLookupTableFiles} DESTINATION bin/${ATLAS_NAME} )

file(GLOB AtlasColorLookupTableFiles "${ATLAS_SOURCE_DIR}/*.csv.md5")
foreach(LUTS_MD5 ${AtlasColorLookupTableFiles})
  get_filename_component(lut ${LUTS_MD5} NAME_WE)
  ExternalData_expand_arguments(${PROJECT_NAME}FetchData LUTS DATA{${LUTS}})
  file(COPY ${LUTS} DESTINATION ${ATLAS_DIRECTORY}/ USE_SOURCE_PERMISSIONS)
endforeach()
install( FILES ${AtlasColorLookupTableFiles} DESTINATION bin/${ATLAS_NAME} )

file(GLOB AtlasColorLookupTableFiles "${ATLAS_SOURCE_DIR}/modelFiles/*.md5")
foreach(LUTS_MD5 ${AtlasColorLookupTableFiles})
  get_filename_component(lut ${LUTS_MD5} NAME_WE)
  ExternalData_expand_arguments(${PROJECT_NAME}FetchData LUTS DATA{${LUTS}})
  file(COPY ${LUTS} DESTINATION ${ATLAS_DIRECTORY}/modelFiles/ USE_SOURCE_PERMISSIONS)
endforeach()
install( FILES ${AtlasColorLookupTableFiles} DESTINATION bin/${ATLAS_NAME}/modelFiles )

file(GLOB AtlasColorLookupTableFiles "${ATLAS_SOURCE_DIR}/probabilityMaps/*.md5")
foreach(LUTS_MD5 ${AtlasColorLookupTableFiles})
  get_filename_component(lut ${LUTS_MD5} NAME_WE)
  ExternalData_expand_arguments(${PROJECT_NAME}FetchData LUTS DATA{${LUTS}})
  file(COPY ${LUTS} DESTINATION ${ATLAS_DIRECTORY}/probabilityMaps/ USE_SOURCE_PERMISSIONS)
endforeach()
install( FILES ${AtlasColorLookupTableFiles} DESTINATION bin/${ATLAS_NAME}/probabilityMaps )

file(GLOB AtlasColorLookupTableFiles "${ATLAS_SOURCE_DIR}/spatialImages/*.md5")
foreach(LUTS_MD5 ${AtlasColorLookupTableFiles})
  get_filename_component(lut ${LUTS_MD5} NAME_WE)
  ExternalData_expand_arguments(${PROJECT_NAME}FetchData LUTS DATA{${LUTS}})
  file(COPY ${LUTS} DESTINATION ${ATLAS_DIRECTORY}/spatialImages/ USE_SOURCE_PERMISSIONS)
endforeach()
install( FILES ${AtlasColorLookupTableFiles} DESTINATION bin/${ATLAS_NAME}/spatialImages )

file(GLOB AtlasSurfaceToolsFile "${ATLAS_SOURCE_DIR}/SurfaceAtlas/*.vtk.md5")
foreach(LUTS_MD5 ${AtlasSurfaceToolsFile})
  get_filename_component(lut ${LUTS_MD5} NAME_WE)
  ExternalData_expand_arguments(${PROJECT_NAME}FetchData LUTS DATA{${LUTS}})
  file(COPY ${LUTS} DESTINATION ${ATLAS_DIRECTORY}/SurfaceAtlas/ USE_SOURCE_PERMISSIONS)
endforeach()
install( FILES ${AtlasSurfaceToolsFile} DESTINATION bin/${ATLAS_NAME}/SurfaceAtlas )
endif(0)

ExternalData_add_target( ${PROJECT_NAME}FetchData )  # Name of data management target
