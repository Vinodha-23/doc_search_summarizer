# src/summarize.py
from ollama import chat, ChatResponse

def summarize_text_ollama(documents, length="medium"):
    """
    Summarizes a list of documents into a single coherent summary.
    Returns a fallback message if documents are empty.
    """
    if not documents or not isinstance(documents, list) or len(documents) == 0:
        return "I do not have enough information to summarize this topic."

    if length == "short":
        target = "in 2-3 sentences"
    elif length == "long":
        target = "in a few paragraphs"
    else:
        target = "in 5-6 sentences"

    individual_summaries = []
    for i, doc in enumerate(documents):
        prompt = (
            f"You are an expert summarizer. Summarize the following document factually {target}. "
            f"Do NOT add any information not present in the text.\n\n{doc}"
        )
        try:
            response: ChatResponse = chat(
                model="llama3.1", 
                # use model="gpt-oss:latest" for better accuracy
                messages=[{"role": "user", "content": prompt}]
            )
            individual_summaries.append(response.message.content.strip())
        except Exception as e:
            individual_summaries.append(f"Error summarizing document {i+1}: {str(e)}")

    combined_prompt = (
        "Combine the following individual summaries into a single, coherent, factual summary. "
        "Do NOT include any Acknowledgement\n\n"
        "Do NOT include anything not in the original summaries.\n\n" +
        "\n\n".join(individual_summaries)
    )

    try:
        combined_response: ChatResponse = chat(
            model="llama3.1",
            messages=[{"role": "user", "content": combined_prompt}]
        )
        final_summary = combined_response.message.content.strip()
    except Exception as e:
        final_summary = f"Error combining summaries: {str(e)}"

    return final_summary


def answer_question_ollama(documents, question):
    """
    Answers a question strictly based on the provided documents.
    Returns fallback message if documents are empty or question is out of context.
    """
    if not documents or not isinstance(documents, list) or len(documents) == 0:
        return "I do not have information on this topic."

    prompt = (
        "Answer the question based ONLY on the following documents. "
        "If the answer is not contained in the documents, respond with: 'I do not have information on this topic.'\n\n"
        f"Documents:\n" + "\n\n".join([f"{i+1}. {doc}" for i, doc in enumerate(documents)]) +
        f"\n\nQuestion: {question}\nAnswer:"
    )

    try:
        response: ChatResponse = chat(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.message.content.strip()
    except Exception as e:
        return f"Error answering question: {str(e)}"
