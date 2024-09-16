import { Breakpoint } from '@mui/material';
import Button, { ButtonProps } from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import React, { JSX } from 'react';
import { useTranslation } from 'react-i18next';

import { LogoLabel, LogoLabelProps } from '../Logo';

export interface ConfirmationDialogProps {
  open: boolean;
  title: string;
  titleLogo?: LogoLabelProps;
  content: JSX.Element;
  disableConfirm?: boolean;
  maxWidth?: false | Breakpoint;
  onClose?: () => void;
  onConfirm?: () => void;
  cancelProps?: ButtonProps;
  confirmProps?: ButtonProps;
  cancelText?: string;
  confirmText?: string;
}

export const ConfirmationDialog = ({
  open,
  title,
  titleLogo,
  content,
  disableConfirm = false,
  maxWidth = false,
  onClose,
  onConfirm,
  cancelProps = {},
  confirmProps = {},
  cancelText,
  confirmText,
}: ConfirmationDialogProps): JSX.Element => {
  const { t } = useTranslation();

  const handleCancel = (): void => {
    if (onClose) {
      onClose();
    }
  };

  const handleConfirm = (): void => {
    if (onConfirm) {
      onConfirm();
    }
    if (onClose) {
      onClose();
    }
  };

  const mergedCancelProps: ButtonProps = {
    variant: 'text',
    ...cancelProps,
  };

  const mergedConfirmProps: ButtonProps = {
    variant: 'outlined',
    color: 'primary',
    ...confirmProps,
  };

  const finalCancelText = cancelText || t('ui.dialog.cancel');
  const finalConfirmText = confirmText || t('ui.dialog.confirm');

  return (
    <Dialog
      open={open}
      onClose={handleCancel}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
      maxWidth={maxWidth}
    >
      <DialogTitle id="alert-dialog-title">
        {title}
        {titleLogo && (<LogoLabel {...titleLogo} />)}
      </DialogTitle>
      <DialogContent>{content}</DialogContent>
      <DialogActions>
        <Button
          {...mergedCancelProps}
          onClick={handleCancel}>
          {finalCancelText}
        </Button>
        {onConfirm && (
          <Button
            {...mergedConfirmProps}
            onClick={handleConfirm}
            disabled={disableConfirm}
            autoFocus
          >
            {finalConfirmText}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationDialog;
