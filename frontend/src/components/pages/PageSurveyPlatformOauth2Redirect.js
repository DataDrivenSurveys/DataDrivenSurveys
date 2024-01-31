import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useSnackbar } from "../../context/SnackbarContext";
import { useTranslation } from "react-i18next";
import { useEffect, useState } from "react";
import { POST } from "../../code/http_requests";
import { Alert, Button, Stack } from "@mui/material";
import LoadingAnimation from "../feedback/LoadingAnimation";

const PageSurveyPlatformOauth2Redirect = () => {

    const { t } = useTranslation();
    
    const location = useLocation();
    const navigate = useNavigate();

    const [ status, setStatus ] = useState({
        failed: false,
        message: t('ui.project.survey_platform.code_exchange.redirecting')
    });
    
    const { surveyPlatform } = useParams();
    
    // Use the useSnackbar hook to show a snackbar notification. This is useful to
    // display a message after a successful login or logout.
    const { showBottomCenter } = useSnackbar();
    
    // Get the authorization code from the URL query parameters.
    const code = new URLSearchParams(location.search).get("code");


    useEffect(() => {
    
        // Define an async function that will call the OAuth callback endpoint
        (async () => {

            // get the fileds from the local storage

            const fields = JSON.parse(localStorage.getItem("surveyPlatformFields", []));


            const fieldValues = fields.reduce((acc, field) => {
                acc[field.name] = field.value;
                return acc;
              }, {});
        
            // Send the authorization code to the backend to exchange it for an access token
            const response = await POST(`/survey-platforms/${surveyPlatform}/exchange-code`, {
                fields: fieldValues,
                code: code,
                survey_platform: surveyPlatform
            });

            response.on('2xx', async (status, response) => {
                if(status === 200) {
                    showBottomCenter(t(response.message.id), 'success');
                    const preAuthLocation = JSON.parse(localStorage.getItem('preAuthLocation'));
                    localStorage.removeItem('preAuthLocation');
                    navigate(`${preAuthLocation?.pathname}?survey_platform=${surveyPlatform}&access_token=${response.entity?.data?.access_token}`);
                }
            });

            response.on('4xx', (_, data) => {
                setStatus({
                    failed: true,
                    message: t(data.message.id)
                });
            });

            response.on('5xx', (_, data) => {
                setStatus({
                    failed: true,
                    message: t(data.message.id)
                });
            });
            
        })();
        
    }, [code, navigate, showBottomCenter, surveyPlatform, t]);
    
    return  (
        <Stack sx={{ width: '100%', height: '100vh', justifyContent: 'center', alignItems: 'center' }}>
            <LoadingAnimation
                content={
                    <Stack spacing={1}>
                        <Alert severity={status.failed ? 'error' : 'info'} sx={{ width: '100%' }}>
                            {status.message}
                        </Alert> 
                        {status.failed && <Button onClick={() => navigate(`/create`)}>{t('ui.project.survey_platform.code_exchange.connection.button.go_back')}</Button>}
                    </Stack>
                }
                failed={status.failed}
            />
        </Stack>
    )
};

export default PageSurveyPlatformOauth2Redirect;