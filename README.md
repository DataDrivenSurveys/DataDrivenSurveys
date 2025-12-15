# Data-Driven Surveys

A platform supporting the creation of data-driven surveys.

## Demo Videos

### Survey Designer/Researcher Demo

This video shows a demo of how DDS can be used to design data-driven surveys:

[![DDS: Survey Designer/Researcher Flow Demo](https://img.youtube.com/vi/BljK855zT1k/0.jpg)](https://youtu.be/BljK855zT1k)

### Survey Participant Demo

This video shows the demo of how a participant would experience taking a data-driven survey powered by DDS:

[![DDS: Participant Flow Demo](https://img.youtube.com/vi/Dc8AGJXDT4U/0.jpg)](https://youtu.be/Dc8AGJXDT4U)

## Manual

The manual for this project is maintained as a [wiki](https://github.com/DataDrivenSurveys/DataDrivenSurveys/wiki).

[The wiki](https://github.com/DataDrivenSurveys/DataDrivenSurveys/wiki) contains a variety of tutorials and explanations for things such as deployment, adding new data-providers, variables, survey platforms, etc.

## Quick Setup Guide

This project requires the following software:

- `git`: For code version control. Installation instructions: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- `node`: For working on the `frontend`. Install instructions: [https://nodejs.org/en/download/prebuilt-installer/current](https://nodejs.org/en/download/prebuilt-installer/current)
- `uv`: For python project management of the `ddsurveys` module. Installation instructions: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
- `docker`: For development and production deployment. Installation instructions: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

## Citation

Here is how you should cite this repository, in the ACM Reference Format:

```text
Lev Velykoivanenko, Kavous Salehzadeh Niksirat, Stefan Teofanovic, Bertil Chapuis, Michelle L. Mazurek, and Kévin Huguenin. 2024. Designing a Data-Driven Survey System: Leveraging Participants' Online Data to Personalize Surveys. In Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI '24). Association for Computing Machinery, New York, NY, USA, Article 498, 1–22. https://doi.org/10.1145/3613904.3642572
```

Here is the citation in bibtex format:

```bibtex
@inproceedings{10.1145/3613904.3642572,
  author = {Velykoivanenko, Lev and Salehzadeh Niksirat, Kavous and Teofanovic, Stefan and Chapuis, Bertil and Mazurek, Michelle L. and Huguenin, K\'{e}vin},
  title = {Designing a Data-Driven Survey System: Leveraging Participants' Online Data to Personalize Surveys},
  year = {2024},
  isbn = {9798400703300},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  url = {https://doi.org/10.1145/3613904.3642572},
  doi = {10.1145/3613904.3642572},
  abstract = {User surveys are essential to user-centered research in many fields, including human-computer interaction (HCI). Survey personalization—specifically, adapting questionnaires to the respondents’ profiles and experiences—can improve reliability and quality of responses. However, popular survey platforms lack usable mechanisms for seamlessly importing participants’ data from other systems. This paper explores the design of a data-driven survey system to fill this gap. First, we conducted formative research, including a literature review and a survey of researchers (N = 52), to understand researchers’ practices, experiences, needs, and interests in a data-driven survey system. Then, we designed and implemented a minimum viable product called Data-Driven Surveys (DDS), which enables including respondents’ data from online service accounts (Fitbit, Instagram, and GitHub) in survey questions, answers, and flow/logic on existing survey platforms (Qualtrics and SurveyMonkey). Our system is open source and can be extended to work with more online service accounts and survey platforms. It can enhance the survey research experience for both researchers and respondents. A demonstration video is available here: https://doi.org/10.17605/osf.io/vedbj},
  booktitle = {Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI '24)},
  articleno = {498},
  numpages = {22},
  keywords = {artefact, online accounts, surveys, user interfaces},
  location = {<conf-loc>, <city>Honolulu</city>, <state>HI</state>, <country>USA</country>, </conf-loc>},
  series = {CHI '24},
  langid = {english},
}
```

You can also refer to `CITAITON.cff`. Reference managers such as [Zotero](https://www.zotero.org/) should be able to parse it automatically to create a conference paper entry.
