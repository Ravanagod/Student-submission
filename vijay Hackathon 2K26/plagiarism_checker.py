from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_plagiarism(texts):

    vectorizer = TfidfVectorizer()

    tfidf = vectorizer.fit_transform(texts)

    similarity_matrix = cosine_similarity(tfidf)

    results = []

    for i in range(len(texts)):
        for j in range(i+1,len(texts)):

            similarity = similarity_matrix[i][j]

            results.append({
                "submission1": i,
                "submission2": j,
                "similarity": round(similarity*100,2)
            })

    return results