from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

from models import Task


def suggest_similar_tasks(tasks_df: pd.DataFrame, target: Task | None = None, top_n: int = 5):
    '''
    This function suggests tasks similar to the target task or based on the transition probabilities 
    between tasks. The function first checks if a sequence of tasks can be predicted using the transition 
    probabilities (Markov chain model). If a predicted task sequence is found, it will be returned along 
    with similar tasks. If no predicted sequence is found, the function will suggest similar tasks based on 
    text similarity using TF-IDF and cosine similarity.

    Parameters
    ----------
    tasks_df : pd.DataFrame
        The dataframe containing task data with the following columns:
        - `title`: The task's title.
        - `description`: The task's description.
        - `due_date`: The task's due date.
    target : Task | None, optional
        A target `Task` object. If provided, the function will find similar tasks to the target based on its title and description.
        If None, the function will not use a specific task to find similar tasks.
    top_n : int, optional
        The number of similar tasks to return. Defaults to 5.

    Returns
    -------
    list[Task]
        A list of `Task` objects representing the most similar tasks. If a predicted sequence is found, it will 
        be returned along with similar tasks. If no sequence is predicted, only similar tasks will be returned.
    '''

    tasks_df["combined_text"] = tasks_df.title + " " + tasks_df.description.fillna("")
    tasks_df['next_combined_text'] = tasks_df.combined_text.shift(-1)

    found_sequence = _searching_for_sequences(tasks_df)
    if found_sequence is None:
        return _suggest_similar_texts(tasks_df, target, top_n)
    else:
        if top_n -1 > 0:
            found_similar_texts = _suggest_similar_texts(tasks_df, target, top_n-1)
            found_similar_texts.insert(0, found_sequence, )
            return found_similar_texts
        else:
            return [found_sequence]


def _suggest_similar_texts(tasks_df: pd.DataFrame, target: Task | None = None, top_n: int = 5) -> list[Task]:
    '''
    This function suggests the most similar tasks from the given DataFrame based on their textual content 
    (title and description). It calculates similarity using TF-IDF vectorization and cosine similarity.

    The function returns the top `n` tasks with the highest similarity to the target task. If no target task is 
    provided, it calculates the similarity for all tasks within the dataset.

    Parameters
    ----------
    tasks_df : pd.DataFrame
        The dataframe containing task data with the following columns:
        - `combined_text`: A concatenated text (e.g., title and description) of the task.
        - `title`: The task's title.
        - `description`: The task's description.
        - `due_date`: The task's due date.

    target : Task | None, optional (default: None)
        A target task to compare against. If None, the function will consider all tasks for similarity.
    
    top_n : int, optional (default: 5)
        The number of similar tasks to return. The function will return the top `n` most similar tasks.

    Returns
    -------
    list[Task]
        A list of `Task` objects representing the most similar tasks to the input `target` task, 
        or the most similar tasks in general if no target is provided.
    '''

    input_text = "" if target is None else " ".join(e for e in [target.title, target.description] if e is not None)

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(tasks_df.combined_text)

    if input_text == "":
        similarity_matrix = cosine_similarity(X=tfidf_matrix)
    else:
        input_vector = vectorizer.transform([input_text])
        similarity_matrix = cosine_similarity(X=input_vector, Y=tfidf_matrix)

    top_n_idx = np.argsort(similarity_matrix[0])[::-1][:top_n]
    top_matches = tasks_df.iloc[top_n_idx][["title", "description", "due_date"]]

    return [ Task(title=row["title"], description=row["description"], due_date=row["due_date"]) for _, row in top_matches.iterrows() ]


def _searching_for_sequences(tasks_df: pd.DataFrame) -> Task | None:
    '''
    This function predicts the next task based on the available data by considering the transition probabilities 
    between tasks. It uses Markov chain model.

    The function calculates the probabilities for the next task based on the most recent task and selects the 
    task with the highest probability. If the probability is at least 0.5, the function returns the predicted task. 
    Otherwise, it returns None.

    Parameters
    ----------
    tasks_df : pd.DataFrame
        The dataframe containing task data with the following columns:
        - `combined_text`: A concatenated text (e.g., title and description) of the task.
        - `next_combined_text`: The concatenated text of the next task.
        - `title`: The task's title.
        - `description`: The task's description.
        - `due_date`: The task's due date.

    Returns
    -------
    Task | None
        Returns a `Task` object representing the predicted next task if the probability is at least 0.5 and the 
        next task is not NaN. If the conditions are not met, it returns None.
    '''

    transitions = pd.crosstab(tasks_df.combined_text, tasks_df.next_combined_text, dropna=False)
    transition_probabilities = transitions.div(transitions.sum(axis=1), axis=0).fillna(0)

    last_event = tasks_df.combined_text.iloc[-1]
    probabilities = transition_probabilities.loc[last_event]

    predicted_combined_text = probabilities.idxmax()
    predicted_probability = probabilities.max()

    if predicted_probability >= 0.5 and not pd.isna(predicted_combined_text):
        row = tasks_df[tasks_df.combined_text == predicted_combined_text].iloc[0]
        return Task(title=row.title, description=row.description, due_date=row.due_date)

