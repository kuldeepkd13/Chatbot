from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
import os
from dotenv import load_dotenv
from .forms import PdfUploadForm
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import pickle

# Create your views here.


# Load environment variables from .env file
load_dotenv()

def home(request):
    return render(request, 'home.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Logged in successfully.', extra_tags='success')
            return redirect('home')
        else:
            # Check if the username exists in the database
            if auth.models.User.objects.filter(username=username).exists():
                messages.error(request, 'Invalid password for the provided username.', extra_tags='error')
            else:
                messages.error(request, 'Invalid username or password.', extra_tags='error')
            return redirect('login')
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.', extra_tags='error')
                return redirect('register')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()
                messages.success(request, 'User registered successfully.', extra_tags='success')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.', extra_tags='error')
            return redirect('register')
    else:
        return render(request, 'signup.html')
    

def logout_user(request):
    username = request.user.username  # Get the username of the logged-out user
    auth.logout(request)
    messages.success(request, f"Thanks, {username}, for visiting our website!", extra_tags='success')
    return redirect('home')





# Load or create an empty chat history list in the session
def get_or_create_chat_history(request):
    chat_history = request.session.get('chat_history', [])
    return chat_history

def process_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text=text)
    store_name = pdf_file.name[:-4]  # Extract the name without the '.pdf' extension
    return chunks, store_name

def pdf_upload_view(request):
    pdf_name = None
    if request.method == 'POST':
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['pdf_file']
            chunks, pdf_name = process_pdf(pdf_file)
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open(f"{pdf_name}.pkl", "wb") as f:
                pickle.dump(VectorStore, f)
            return render(request, 'upload_template.html', {'pdf_name': pdf_name})
    else:
        form = PdfUploadForm()

    context = {'form': form}
    return render(request, 'upload_template.html', context)

def chat_view(request):
    pdf_name = request.GET.get('pdf_name')
    chat_history = get_or_create_chat_history(request)  # Get or create chat history

    if pdf_name:
        with open(f"{pdf_name}.pkl", "rb") as f:
            VectorStore = pickle.load(f)
        query = request.GET.get('query', '')

        if query:
            docs = VectorStore.similarity_search(query=query, k=3)

            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
            response_text = response.get('output_text', "No answer found.")

            # Append the current question and its response to the chat history
            chat_history.append({'question': query, 'response': response_text})

            # Update the chat history in the session
            request.session['chat_history'] = chat_history
        else:
            response_text = ""

        context = {'pdf_name': pdf_name, 'query': query, 'response_text': response_text, 'chat_history': chat_history}
        return render(request, 'chat_template.html', context)
    else:
        return render(request, 'error_template.html', {'error_message': 'PDF name not provided.'})


def end_chat_view(request):
    if request.method == 'POST':
        pdf_name = request.POST.get('pdf_name')
        if pdf_name:
            try:
                os.remove(f"{pdf_name}.pkl")  # Delete the .pkl file
            except OSError:
                pass

            # Clear the chat history from the session
            request.session['chat_history'] = []

        return redirect('upload')
  