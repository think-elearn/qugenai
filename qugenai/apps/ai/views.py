import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from openai import OpenAI
from pydantic import BaseModel

from .forms import QGenForm

client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.8
MAX_TOKENS = 2048


class Options(BaseModel):
    A: str
    B: str
    C: str
    D: str


class Question(BaseModel):
    question: str
    options: Options
    correct_option: str
    rationale: str
    tags: list[str]


class ExamQuestionsResponse(BaseModel):
    subject: str
    questions: list[Question]


@login_required
def generate_exam_questions(request):
    exam_questions = None
    if request.method == "POST":
        form = QGenForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            system_prompt = """You are an exam question generator.
            You are tasked with creating multiple choice questions for an exam.
            The questions should be challenging but fair.
            There should be four answer options for each question.
            There must be only one correct answer.
            Do not use "all of the above" or "none of the above" as answer options.
            Do not use a combination of answer options as an answer option.
            Include the rationale for the correct answer and the incorrect options.
            The subject is: """
            response = client.beta.chat.completions.parse(
                model=MODEL,
                messages=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": subject},
                ],
                response_format=ExamQuestionsResponse,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            logger.info("response: %s", response)

            try:
                content = response.choices[0].message.content
                if response.choices[0].message.refusal is not None:
                    logger.error(
                        "Refused to generate exam questions: %s",
                        response.choices[0].message.refusal,
                    )
                    return JsonResponse(
                        {"error": response.choices[0].message.refusal},
                        status=400,
                    )
                exam_questions = json.loads(content)
            except (KeyError, json.JSONDecodeError):
                logger.exception("Failed to parse response")
                return JsonResponse({"error": "Failed to parse response"}, status=500)

        else:
            return JsonResponse({"error": "Invalid form data"}, status=400)
    else:
        form = QGenForm()

    return render(
        request,
        "ai/qugen.html",
        {"form": form, "exam_questions": exam_questions},
    )
