import {Stack, Typography} from "@mui/material";
import Logo from "../Logo";
import { useTranslation } from "react-i18next";


const ConnectionBadge = ({name, size}) => {

  const { t } = useTranslation();

  return (
    <Stack direction="row" spacing={1} alignItems={"center"} justifyContent={"flex-start"}>
      <Logo name={name} size={size}/>
      <Typography variant={"body1"}><b>{t(`ui.badges.${name.toLowerCase()}.label`)}</b></Typography>
    </Stack>
  )
}



export default ConnectionBadge;
