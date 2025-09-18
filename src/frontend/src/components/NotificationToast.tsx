import React, { useState, useEffect } from 'react';
import { Alert, Snackbar, AlertColor } from '@mui/material';

interface NotificationToastProps {
  open: boolean;
  message: string;
  severity: AlertColor;
  onClose: () => void;
  duration?: number;
}

const NotificationToast: React.FC<NotificationToastProps> = ({
  open,
  message,
  severity,
  onClose,
  duration = 6000
}) => {
  const [isVisible, setIsVisible] = useState(open);

  useEffect(() => {
    setIsVisible(open);
  }, [open]);

  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setIsVisible(false);
    onClose();
  };

  return (
    <Snackbar
      open={isVisible}
      autoHideDuration={duration}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert
        onClose={handleClose}
        severity={severity}
        variant="filled"
        sx={{ width: '100%' }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
};

export default NotificationToast;
