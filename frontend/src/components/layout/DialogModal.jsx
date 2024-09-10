import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import React from 'react';
import {useTranslation} from 'react-i18next';

import {LogoLabel} from "../Logo";


const DialogModal = ({
                       open, title, titleLogo, content, disableConfirm = false,
                       maxWidth = false, onClose, onConfirm,
                       cancelProps = null, confirmProps = null
                     }) => {

  const {t} = useTranslation();

  const handleCancel = () => {
    onClose && onClose();
  }

  const handleConfirm = () => {
    onConfirm && onConfirm();
    onClose && onClose();
  }

  if (!cancelProps) {
    cancelProps = {
      variant: 'text',
    }
  } else {
    if (!cancelProps.variant) {
      cancelProps.variant = 'text'
    }
  }

  if (!confirmProps) {
    confirmProps = {
      variant: 'outlined',
      color: 'primary',
    }
  } else {
    if (!confirmProps.variant) {
      confirmProps.variant = 'outlined'
    }
    if (!confirmProps.color) {
      confirmProps.color = 'primary'
    }
  }


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
          {...cancelProps}
          onClick={handleCancel}>
          {t('ui.dialog_modal.button.cancel')}
        </Button>
        {onConfirm && (
          <Button
            {...confirmProps}
            onClick={handleConfirm}
            disabled={disableConfirm}
            autoFocus
          >
            {t('ui.dialog_modal.button.confirm')}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}

export default DialogModal
