import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import React from 'react';
import {useTranslation} from "react-i18next";


const DialogFeedback = ({ open, title, content, onClose, onConfirm,
                        cancelProps = null, confirmProps = null,
                        cancelText = null, confirmText = null}) => {
  const {t} = useTranslation();

  const handleCancel = () => {
    onClose && onClose()
  }

  const handleConfirm = () => {
    onConfirm && onConfirm()
    onClose && onClose()
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

  if (!cancelText) {
    cancelText = t('ui.dialog.cancel');
  }

  if (!confirmText) {
    confirmText = t('ui.dialog.confirm');
  }

  return (
    <div>
      <Dialog
        open={open}
        onClose={handleCancel}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{title}</DialogTitle>
        <DialogContent>{content}</DialogContent>
        <DialogActions>
          <Button
            {...cancelProps}
            onClick={handleCancel}>
            {cancelText}
          </Button>
          {onConfirm && (
            <Button
              {...confirmProps}
              onClick={handleConfirm}
              autoFocus
            >
              {confirmText}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </div>
  )
}

export default DialogFeedback
