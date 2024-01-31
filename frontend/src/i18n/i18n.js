import i18n from "i18next";
import { initReactI18next, Trans } from "react-i18next";
import resources from "./resources.json";

// the translations
// (tip move them in a JSON file and import them,
// or even better, manage them separated from your code: https://react.i18next.com/guides/multiple-translation-files)

i18n
  .use(initReactI18next) // passes i18n down to react-i18next
  .init({
    resources,
    lng: "en", // language to use, more information here: https://www.i18next.com/overview/configuration-options#languages-namespaces-resources
    fallbackLng: 'en',
    // you can use the i18n.changeLanguage function to change the language manually: https://www.i18next.com/overview/api#changelanguage
    // if you're using a language detector, do not define the lng option

    interpolation: {
      escapeValue: false // react already safe from xss
    }
  });


export const I18Link = ({ i18nKey, url, link_text = null }) => {

  if (!link_text) {
    link_text = url;
  }

  return (
    <Trans
     i18nKey={i18nKey}
     values={{ url: url, link_text: link_text}}
     components={[
        <a href={url} target="_blank" rel="noreferrer">
           {link_text}
        </a>,
     ]}>
  </Trans>
  );
};


  export default i18n;
