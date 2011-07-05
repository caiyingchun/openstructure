if (PYTHON_NUMPY_INCLUDE_DIR)
  # in cache already
  set (PYTHON_NUMPY_FIND_QUIETLY TRUE)
endif (PYTHON_NUMPY_INCLUDE_DIR)

#INCLUDE(FindPython)

IF(PYTHON_BINARY)
    EXEC_PROGRAM ("${PYTHON_BINARY}"
      ARGS "-c 'import numpy; print numpy.get_include()'"
      OUTPUT_VARIABLE PYTHON_NUMPY_INCLUDE_DIR
      RETURN_VALUE PYTHON_NUMPY_NOT_FOUND)

    if (PYTHON_NUMPY_INCLUDE_DIR)
      set (PYTHON_NUMPY_FOUND TRUE)
      set (PYTHON_NUMPY_INCLUDE_DIR ${PYTHON_NUMPY_INCLUDE_DIR} CACHE STRING "Numpy include path")
    else (PYTHON_NUMPY_INCLUDE_DIR)
      set(PYTHON_NUMPY_FOUND FALSE)
    endif (PYTHON_NUMPY_INCLUDE_DIR)
ENDIF(PYTHON_BINARY)

if (PYTHON_NUMPY_FOUND)
  if (NOT PYTHON_NUMPY_FIND_QUIETLY)
    message (STATUS "Numpy headers found")
  endif (NOT PYTHON_NUMPY_FIND_QUIETLY)
else (PYTHON_NUMPY_FOUND)
  if (PYTHON_NUMPY_FIND_REQUIRED)
    message (FATAL_ERROR "Numpy headers missing")
  endif (PYTHON_NUMPY_FIND_REQUIRED)
endif (PYTHON_NUMPY_FOUND)

MARK_AS_ADVANCED (PYTHON_NUMPY_INCLUDE_DIR)