import {useTranslation} from "react-i18next";

const Logo = ({name, size = 24}) => {
  const {t} = useTranslation();
  return (
    <img src={`/svg/logo/${name.toLowerCase()}-logo.svg`} alt={t(`ui.badges.${name}.alt`)} style={{
      width: size,
      height: size
    }}/>
  )
}


const LogoLabel = ({logoName, logoSize = 24, label}) => {

  return (
    <>
      <Logo name={logoName} size={logoSize}/>{" "}{label}
    </>
  )
}

export {LogoLabel};

export default Logo;
