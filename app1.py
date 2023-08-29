import streamlit as st
from dotenv import load_dotenv
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

def main():
    load_dotenv()

    st.set_page_config(page_title="Chat with Text", page_icon=":pencil:")

    st.header("Chat with Script 💬")

    # Text Input
    user_text = st.text_area("Paste or type your text data here:")

    if user_text:
        # Split into chunks (you can adjust parameters as needed)
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(user_text)

        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)
        st.success("Embeddings created!")

        user_question = st.text_input("Ask a question about the text:")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)

            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

            st.write(response['output_text'])

if __name__ == '__main__':
    main()
