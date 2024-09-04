import React from "react";
import {useTranslation} from "react-i18next";

interface LogoProps {
  name: string;
  size?: number;
}

const Logo: React.FC<LogoProps> = ({name, size = 24}) => {
  const {t} = useTranslation();
  return (
    <img src={`/svg/logo/${name.toLowerCase()}-logo.svg`} alt={t(`ui.badges.${name}.alt`)} style={{
      width: size,
      height: size
    }}/>
  )
}


interface LogoLabelProps {
  logoName: string;
  logoSize?: number;
  label: string;
}


const LogoLabel: React.FC<LogoLabelProps> = ({logoName, logoSize = 24, label}) => {

  return (
    <>
      <Logo name={logoName} size={logoSize}/>{" "}{label}
    </>
  )
}

export {LogoLabel};

export default Logo;
