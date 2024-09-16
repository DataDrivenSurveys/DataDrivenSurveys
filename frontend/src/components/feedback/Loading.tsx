import { Stack, Typography } from '@mui/material';
import React, { JSX } from 'react';
import { useTranslation } from 'react-i18next';


export interface LoadingAnimationProps {
  content?: React.ReactNode;
  failed?: boolean; // If true, display a failed icon instead of a loading one. Default is false.
}

const LoadingAnimationComponent = ({
  content = null,
  failed = false,
}: LoadingAnimationProps): JSX.Element => (
  <Stack
    alignItems="stretch"
    justifyContent="center"
    spacing={2}
    flex={1}
    p={2}
  >
    <Stack alignItems="center" justifyContent="center" spacing={2}>
      <img
        alt="Loading..."
        src={failed ? '/svg/exclamation-mark.svg' : '/svg/loading.svg'}
        width="80px"
        height="80px"
      />
      <Stack alignItems="center">{content}</Stack>
    </Stack>
  </Stack>
);

export const LoadingAnimation = React.memo(LoadingAnimationComponent);


export interface LoadingProps {
  children?: React.ReactNode;
  errors?: Error[];
  loading?: boolean;
  content?: React.ReactNode; // Content to be displayed when loading is true. Default is empty.
}

const LoadingComponent = ({
  children = <></>,
  errors = [],
  loading = true,
  content = <></>,
}: LoadingProps): JSX.Element => {
  // find first error that is not undefined or null
  const error = errors.find((error) => error !== undefined && error !== null);
  if (error) {
    return <LoadingAnimation content={error.message} failed={true} />;
  }
  if (loading) {
    return (
      <LoadingAnimation content={content} failed={false} />
    );
  }
  return <>{children}</>;
};

export const Loading = React.memo(LoadingComponent);

const LoadingPageContentComponent = (): JSX.Element => {
  const { t } = useTranslation();

  return (
    <Stack width={'100vw'} height={'100vh'} justifyContent={'center'} alignItems={'center'}>
      <LoadingAnimation content={<Typography variant="body2">{t('ui.feedback.loading')}</Typography>} />
    </Stack>
  );
};

export const LoadingPageContent = React.memo(LoadingPageContentComponent);
