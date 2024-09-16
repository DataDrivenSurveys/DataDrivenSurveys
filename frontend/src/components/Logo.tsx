import React from 'react';
import { useTranslation } from 'react-i18next';

export interface LogoProps {
  name: string;
  size?: number;
}

export const Logo = ({ name, size = 24 }: LogoProps): JSX.Element => {
  const { t } = useTranslation();
  return (
    <img
      src={`/svg/logo/${name.toLowerCase()}-logo.svg`}
      alt={t(`ui.badges.${name}.alt`)}
      style={{
        width: size,
        height: size,
      }} />
  );
};

export interface LogoLabelProps {
  logoName: string;
  logoSize?: number;
  label: string;
}

export const LogoLabel = ({ logoName, logoSize = 24, label }: LogoLabelProps): JSX.Element => {
  return (
    <>
      <Logo name={logoName} size={logoSize} />{' '}{label}
    </>
  );
};

export default Logo;
