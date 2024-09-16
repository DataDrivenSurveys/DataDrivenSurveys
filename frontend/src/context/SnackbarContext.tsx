import React, { createContext, JSX, useCallback, useContext, useState } from 'react';

import SnackbarFeedback from '../components/feedback/SnackbarFeedback';

interface Position {
  vertical: 'top' | 'bottom';
  horizontal: 'left' | 'center' | 'right';
}

type Severity = 'success' | 'error' | 'warning' | 'info';

interface SnackbarState {
  open: boolean;
  position: Position;
  message: string;
  severity?: Severity;
}

interface SnackbarContextType {
  snackbar: SnackbarState;
  show: (message: string, severity?: Severity) => void;
  showAt: (position: Position, message: string, severity?: Severity) => void;
  showTopRight: (message: string, severity?: Severity) => void;
  showTopCenter: (message: string, severity?: Severity) => void;
  showBottomCenter: (message: string, severity?: Severity) => void;
  hide: () => void;
}

const SnackbarContext = createContext<SnackbarContextType | undefined>(undefined);

export const useSnackbar = (): SnackbarContextType => {
  const context = useContext(SnackbarContext);
  if (context === undefined) {
    throw new Error('useSnackbar must be used within a SnackbarProvider');
  }
  return context;
};

const defaultPosition: Position = {
  vertical: 'bottom',
  horizontal: 'left',
};

interface SnackbarProviderProps {
  children: React.ReactNode;
}

export const SnackbarProvider = ({ children }: SnackbarProviderProps): JSX.Element => {
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    position: defaultPosition,
    message: '',
  });

  const show = useCallback((message: string, severity: Severity = 'success') => {
    setSnackbar({
      position: defaultPosition,
      open: true,
      message,
      severity,
    });
  }, []);

  const showAt = useCallback(
    (position: Position, message: string, severity: Severity = 'success') => {
      setSnackbar({
        position,
        open: true,
        message,
        severity,
      });
    }, []);

  const showTopRight = useCallback((message: string, severity: Severity = 'success') => {
    setSnackbar({
      position: {
        vertical: 'top',
        horizontal: 'right',
      },
      open: true,
      message,
      severity,
    });
  }, []);

  const showTopCenter = useCallback((message: string, severity: Severity = 'success') => {
    setSnackbar({
      position: {
        vertical: 'top',
        horizontal: 'center',
      },
      open: true,
      message,
      severity,
    });
  }, []);

  const showBottomCenter = useCallback((message: string, severity: Severity = 'success') => {
    setSnackbar({
      position: {
        vertical: 'bottom',
        horizontal: 'center',
      },
      open: true,
      message,
      severity,
    });
  }, []);

  const hide = useCallback(() => {
    setSnackbar((prev) => ({ ...prev, open: false, message: '', severity: 'success' }));
  }, []);

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
  );
};
