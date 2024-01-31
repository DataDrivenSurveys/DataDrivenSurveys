import React, { createContext, useState, useContext, useCallback } from 'react'
import SnackbarFeedback from '../components/feedback/SnackbarFeedback'

const SnackbarContext = createContext()
export const useSnackbar = () => useContext(SnackbarContext)

const defaultPosition = {
  vertical: 'bottom',
  horizontal: 'left',
}
export const SnackbarProvider = ({ children }) => {
  const [snackbar, setSnackbar] = useState({
    open: false,
    position: defaultPosition,
    message: '',
  })

  const show = useCallback((message, severity = "success") => {
    setSnackbar({
      position: defaultPosition,
      open: true,
      message,
      severity,
    })
  }, [])

  const showAt = useCallback((position, message, severity = "success") => {
    setSnackbar({
      position,
      open: true,
      message,
      severity,
    })
  }, [])

  const showTopRight = useCallback((message, severity = "success") => {
    setSnackbar({
      position: {
        vertical: 'top',
        horizontal: 'right',
      },
      open: true,
      message,
      severity,
    })
  }, [])

  const showTopCenter = useCallback((message, severity = "success") => {
    setSnackbar({
      position: {
        vertical: 'top',
        horizontal: 'center',
      },
      open: true,
      message,
      severity,
    })
  }, [])

  const showBottomCenter = useCallback((message, severity = "success") => {
    setSnackbar({
      position: {
        vertical: 'bottom',
        horizontal: 'center',
      },
      open: true,
      message,
      severity,
    })
  }, [])

  const hide = () => {
    setSnackbar({ ...snackbar, open: false, message: '', severity: 'success' })
  }

  return (
    <SnackbarContext.Provider
      value={{
        snackbar,
        show,
        showAt,
        showTopRight,
        showTopCenter,
        showBottomCenter,
        hide,
      }}
    >
      {children}
      <SnackbarFeedback />
    </SnackbarContext.Provider>
  )
}
