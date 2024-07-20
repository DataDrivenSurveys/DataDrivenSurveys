#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-07-19 15:08

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""


TEXTS = {
    None: "",
    "en": """This is the first paragraph. It has two sentences.
This is the second paragraph. It also has two sentences.

Here is the third paragraph, which contains only one sentence.""",
    "zh": """这是第一段。它有两个句子。
这是第二段。它也有两个句子。

这是第三段，只有一个句子。""",
    "hi": """यह पहला पैराग्राफ है। इसमें दो वाक्य हैं।
यह दूसरा पैराग्राफ है। इसमें भी दो वाक्य हैं।

यह तीसरा पैराग्राफ है, जिसमें केवल एक वाक्य है।""",
    "es": """Este es el primer párrafo. Tiene dos oraciones.
Este es el segundo párrafo. También tiene dos oraciones.

Aquí está el tercer párrafo, que contiene solo una oración.
""",
    "fr": """Ceci est le premier paragraphe. Il a deux phrases.
Ceci est le deuxième paragraphe. Il a aussi deux phrases.

Voici le troisième paragraphe, qui ne contient qu'une seule phrase.
""",
    "ar": """هذه هي الفقرة الأولى. تحتوي على جملتين.
هذه هي الفقرة الثانية. تحتوي أيضاً على جملتين.

ها هي الفقرة الثالثة، التي تحتوي على جملة واحدة فقط.
""",
    "bn": """এটি প্রথম অনুচ্ছেদ। এতে দুটি বাক্য রয়েছে।
এটি দ্বিতীয় অনুচ্ছেদ। এতে দুটি বাক্যও রয়েছে।

এখানে তৃতীয় অনুচ্ছেদ, যা কেবল একটি বাক্য নিয়ে গঠিত।
""",
    "pt": """Este é o primeiro parágrafo. Ele tem duas frases.
Este é o segundo parágrafo. Ele também tem duas frases.

Aqui está o terceiro parágrafo, que contém apenas uma frase.
""",
    "ru": """Это первый абзац. В нем два предложения.
Это второй абзац. В нем также два предложения.

Вот третий абзац, который содержит только одно предложение.
""",
    "ur": """یہ پہلا پیراگراف ہے۔ اس میں دو جملے ہیں۔
یہ دوسرا پیراگراف ہے۔ اس میں بھی دو جملے ہیں۔

یہ تیسرا پیراگراف ہے، جس میں صرف ایک جملہ ہے۔
""",
    "id": """Ini adalah paragraf pertama. Ini memiliki dua kalimat.
Ini adalah paragraf kedua. Ini juga memiliki dua kalimat.

Ini adalah paragraf ketiga, yang hanya berisi satu kalimat.
""",
    "de": """Dies ist der erste Absatz. Er hat zwei Sätze.
Dies ist der zweite Absatz. Er hat auch zwei Sätze.

Hier ist der dritte Absatz, der nur einen Satz enthält.
""",
    "ja": """これは最初の段落です。2つの文があります。
これは2番目の段落です。これも2つの文があります。

ここに、1つの文しか含まれていない3番目の段落があります。
""",
    "ko": """이것은 첫 번째 문단입니다. 두 개의 문장이 있습니다.
이것은 두 번째 문단입니다. 또한 두 개의 문장이 있습니다.

여기에 단 하나의 문장만 포함된 세 번째 문단이 있습니다.
""",
    "zh-tw": """這是第一段。它有兩個句子。
這是第二段。它也有兩個句子。

這是第三段，只有一個句子。
""",
}

expected_stats = {
  None: {"words": 0, "sentences": 0, "paragraphs": 0},
  "en": {"words": 29, "sentences": 5, "paragraphs": 3},
  "zh": {"words": 23, "sentences": 5, "paragraphs": 3},
  "hi": {"words": 26, "sentences": 5, "paragraphs": 3},
  "es": {"words": 27, "sentences": 5, "paragraphs": 3},
  "fr": {"words": 30, "sentences": 5, "paragraphs": 3},
  "ar": {"words": 25, "sentences": 5, "paragraphs": 3},
  "be": {"words": 23, "sentences": 5, "paragraphs": 3},
  "pt": {"words": 29, "sentences": 5, "paragraphs": 3},
  "ru": {"words": 23, "sentences": 5, "paragraphs": 3},
  "ur": {"words": 29, "sentences": 5, "paragraphs": 3},
  "in": {"words": 26, "sentences": 5, "paragraphs": 3},
  "de": {"words": 29, "sentences": 5, "paragraphs": 3},
  "ja": {"words": 75, "sentences": 5, "paragraphs": 3},
  "ko": {"words": 26, "sentences": 5, "paragraphs": 3},
  "zh-tw": {"words": 40, "sentences": 5, "paragraphs": 3}
}
