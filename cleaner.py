import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize

from logger import logger


# remove empty articles from the dataFrame
def remove_empty_articles(data):
    logger.info("removing empty articles")
    empty_article = []
    for index, article in data['article'].items():
        if not article:  # check if it is a empty string
            empty_article.append(index)  # append the index of the row
    data = data.drop(empty_article)
    return data


def tokenize_articles(data):
    logger.info("tokenizing articles")
    # makes a list with a list of tokenized articles
    articles = []
    for article in data.loc[:, 'article']:
        articles.append(sent_tokenize(str(article)))
    data.loc[:, 'tokenized_articles'] = articles
    return data


def make_list_sentences(data):
    logger.info("generating sentence list")
    # make a list with every sentence
    sentences = []
    article_nrs = []
    for index, article in data.loc[:, 'tokenized_articles'].items():
        for sentence in article:
            sentences.append(sentence)
            article_nrs.append(index)
    return pd.DataFrame(list(zip(sentences, article_nrs)), columns=['sentences', 'article_nr'])


def remove_bad_words(data):
    logger.info("removing bad sentences")
    # Remove sentences with bad_words
    bad_words = ['seeking', 'premium', 'subscribe', 'payable', 'follow', 'submitted', 'copyright']
    for index, sentence in data['sentences'].items():
        for word in sentence.replace(".", " ").replace(";", " ").replace("\'", " ").split(" "):
            if word.lower() in bad_words:
                data = data.drop(index)
                break  # continue with the outer loop
    return data


def remove_short_sentences(data):
    logger.info("removing short sentences")
    # sentence length has to be minimum of three words after cleaning
    data['sentences'] = pd.Series([sentence for sentence in data['sentences'] if len(sentence.split(" ")) >= 5])
    data = data.dropna()
    return data


def remove_duplicate_sentences(data):
    logger.info("removing duplicated sentences")
    # remove duplicates from scentences
    data = data.drop_duplicates()
    return data


def clean_sentence(data):
    logger.info("cleaning sentences")
    # replace special characters
    data['sentences'] = pd.Series(data['sentences']).str.replace(r"[\[\]]", "", regex=True) \
        .str.replace(",\'", "", regex=False) \
        .str.replace("\',", "", regex=False) \
        .str.replace("\",", "", regex=False) \
        .str.replace("\"", "", regex=False) \
        .str.replace(r"^ ", "", regex=True) \
        .str.replace(r"^\'", "", regex=True)
    return data


def clean_clean_sentence(data):
    # remove numbers, spaces, special characters and punctuation
    data['clean_sentences'] = pd.Series(data['sentences']).str.replace("[^a-zA-Z]", " ") \
        .str.replace("\s+", " ") \
        .str.replace("^\s", "") \
        .str.replace("\s$", "")
    return data


def lowercase_sentences(data):
    # change to lowercase
    data['clean_sentences'] = data['clean_sentences'].str.lower()
    return data


def remove_stopwords(data):
    # remove stopwords
    stop_words = stopwords.words('english')
    filtered_sentences = []
    for sentence in data['clean_sentences']:
        filtered_words = []
        for word in sentence.split(" "):
            if word not in stop_words:
                filtered_words.append(word)
        filtered_sentences.append(" ".join(filtered_words))
    data['clean_sentences'] = filtered_sentences
    return data


def combine_to_article(data):
    grp = data.groupby('article_nr')  # group cleaned sentences by article nr
    articles = pd.DataFrame()
    articles['article'] = grp['sentences'].apply(list)  # generate list of sentences per article
    articles['clean_article'] = grp['clean_sentences'].apply(list) # generate cleaned list of sentences per article
    return articles


# Pipeline for cleaning articles
def get_clean_articles(data):
    return (data
            .pipe(remove_empty_articles)
            .pipe(tokenize_articles)
            .pipe(make_list_sentences)
            .pipe(remove_bad_words)
            .pipe(remove_short_sentences)
            .pipe(remove_duplicate_sentences)
            .pipe(clean_sentence)
            .pipe(clean_clean_sentence)
            .pipe(lowercase_sentences)
            .pipe(remove_stopwords)
            .pipe(combine_to_article))
